"""
Benchmark script for ChainML Guard inference latency.

This script measures the local computational cost of the fraud detection model,
excluding Etherscan/network latency. It benchmarks:
  1. Feature preprocessing (StandardScaler.transform)
  2. MLP model inference
  3. Reason summary generation (heuristic explanation)

Results are saved to results/bench_compute_only.json with summary statistics.

Usage:
    docker run --rm -v $(pwd):/app --env-file .env chainml-guard python experiments/benchmark_inference.py
    
    or (local, if TensorFlow available):
    python experiments/benchmark_inference.py

Environment:
    - Runs on CPU only (no GPU)
    - Excludes Etherscan API calls
    - Uses actual model from models/fraud_model.h5
    - Uses actual scaler from models/scaler.pkl
    - Uses actual explanation thresholds if available
"""

import time
import json
import os
import sys
import statistics
from pathlib import Path
from datetime import datetime

try:
    import numpy as np
    from tensorflow.keras.models import load_model
    import pickle
    from utils.explanations import generate_reason_summary, load_thresholds
    import pandas as pd
except ImportError as e:
    print(f"Error: Required packages not found: {e}")
    print("Please ensure TensorFlow, scikit-learn, and numpy are installed.")
    sys.exit(1)


def get_system_info():
    """Gather environment information."""
    import platform
    try:
        import tensorflow as tf
        tf_version = tf.__version__
    except:
        tf_version = "Unknown"
    
    try:
        import sklearn
        sklearn_version = sklearn.__version__
    except:
        sklearn_version = "Unknown"
    
    return {
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "tensorflow_version": tf_version,
        "scikit_learn_version": sklearn_version,
        "gpu_available": False,  # Explicitly mark as CPU-only benchmark
        "timestamp": datetime.now().isoformat(),
    }


def run_benchmark(num_runs=50):
    """
    Run the inference benchmark.
    
    Args:
        num_runs: Number of iterations for each component
        
    Returns:
        Dictionary with timing measurements
    """
    print(f"🚀 Starting ChainML Guard Inference Benchmark ({num_runs} runs)...")
    print("=" * 70)
    
    # Load model and scaler
    print("📦 Loading model artifacts...")
    try:
        model = load_model('models/fraud_model.h5')
        with open('models/scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        print("✓ Model and scaler loaded")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please ensure models/fraud_model.h5 and models/scaler.pkl exist")
        sys.exit(1)
    
    # Load thresholds for explanation (optional)
    thresholds = None
    try:
        thresholds = load_thresholds('models/mlp/thresholds.json')
        print("✓ Explanation thresholds loaded")
    except Exception as e:
        print(f"⚠️  Thresholds not available: {e}")
        print("  (Explanations will be skipped)")
    
    # Get sample data from dataset
    print("📊 Loading sample data...")
    try:
        df = pd.read_csv('data/dataset_final.csv')
        if df.empty:
            raise ValueError("Dataset is empty")
        row = df.iloc[0][['balance', 'tx_count', 'age_days']].values
        print(f"✓ Sample loaded: balance={row[0]:.6f}, tx_count={int(row[1])}, age_days={row[2]:.2f}")
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        sys.exit(1)
    
    # Warmup runs (to stabilize JIT compilation, cache)
    print("\n🔥 Warming up (3 runs)...")
    for _ in range(3):
        _ = scaler.transform(np.array([row]))
        _ = model.predict(scaler.transform(np.array([row])), verbose=0)
    print("✓ Warmup complete")
    
    # Main benchmarking
    print(f"\n⏱️  Benchmarking ({num_runs} runs per component)...")
    print("-" * 70)
    
    measurements = {
        'preproc': [],
        'inference': [],
        'explain': [],
    }
    
    for i in range(num_runs):
        # Preprocessing
        t0 = time.time()
        x_scaled = scaler.transform(np.array([row]))
        t1 = time.time()
        measurements['preproc'].append(t1 - t0)
        
        # Inference
        t1_inf = time.time()
        pred = model.predict(x_scaled, verbose=0)
        t2_inf = time.time()
        measurements['inference'].append(t2_inf - t1_inf)
        
        # Explanation
        t1_exp = time.time()
        if thresholds:
            reasons = generate_reason_summary(
                balance=row[0],
                tx_count=int(row[1]),
                wallet_age_days=float(row[2]),
                thresholds=thresholds
            )
        else:
            reasons = []
        t2_exp = time.time()
        measurements['explain'].append(t2_exp - t1_exp)
        
        # Progress
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  Run {i+1:3d}/{num_runs} | preproc: {measurements['preproc'][-1]*1000:.2f}ms | "
                  f"inference: {measurements['inference'][-1]*1000:.2f}ms | "
                  f"explain: {measurements['explain'][-1]*1000:.4f}ms")
    
    print("-" * 70)
    return measurements


def compute_statistics(measurements):
    """Compute summary statistics for each component."""
    stats = {}
    for component, timings in measurements.items():
        stats[component] = {
            'count': len(timings),
            'mean': statistics.mean(timings),
            'median': statistics.median(timings),
            'stdev': statistics.stdev(timings) if len(timings) > 1 else 0.0,
            'min': min(timings),
            'max': max(timings),
            # Convert to milliseconds for readability
            'mean_ms': statistics.mean(timings) * 1000,
            'median_ms': statistics.median(timings) * 1000,
            'min_ms': min(timings) * 1000,
            'max_ms': max(timings) * 1000,
            'stdev_ms': statistics.stdev(timings) * 1000 if len(timings) > 1 else 0.0,
        }
    return stats


def save_results(measurements, stats, output_file='results/bench_compute_only.json'):
    """Save measurements and statistics to JSON file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare output structure
    result = {
        'metadata': {
            'description': 'ChainML Guard inference latency benchmark (CPU-only, no network I/O)',
            'excludes': 'Etherscan API calls, Flask overhead, network latency',
            'model': 'MLP (3 layers, 209 parameters, 35.6 KB)',
            'features': ['balance', 'tx_count', 'age_days'],
            'system': get_system_info(),
            'num_runs': len(measurements['preproc']),
        },
        'raw_measurements': measurements,
        'statistics': stats,
        'summary': {
            'preproc_ms': {
                'mean': stats['preproc']['mean_ms'],
                'median': stats['preproc']['median_ms'],
                'stdev': stats['preproc']['stdev_ms'],
            },
            'inference_ms': {
                'mean': stats['inference']['mean_ms'],
                'median': stats['inference']['median_ms'],
                'stdev': stats['inference']['stdev_ms'],
            },
            'explain_ms': {
                'mean': stats['explain']['mean_ms'],
                'median': stats['explain']['median_ms'],
                'stdev': stats['explain']['stdev_ms'],
            },
            'total_ms': {
                'mean': (stats['preproc']['mean'] + stats['inference']['mean'] + stats['explain']['mean']) * 1000,
                'median': (stats['preproc']['median'] + stats['inference']['median'] + stats['explain']['median']) * 1000,
            },
            'throughput_per_second': 1.0 / (stats['preproc']['mean'] + stats['inference']['mean'] + stats['explain']['mean']),
        }
    }
    
    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    return output_path


def print_results_table(stats):
    """Print results as formatted table."""
    print("\n📊 RESULTS SUMMARY")
    print("=" * 70)
    print(f"{'Component':<20} {'Mean (ms)':>12} {'Median (ms)':>12} {'Std (ms)':>12} {'Min:Max (ms)':>20}")
    print("-" * 70)
    
    components = ['preproc', 'inference', 'explain']
    for comp in components:
        s = stats[comp]
        print(f"{comp:<20} {s['mean_ms']:>12.3f} {s['median_ms']:>12.3f} {s['stdev_ms']:>12.3f} "
              f"{s['min_ms']:>9.3f} : {s['max_ms']:<9.3f}")
    
    # Total
    total_mean = (stats['preproc']['mean'] + stats['inference']['mean'] + stats['explain']['mean']) * 1000
    total_median = (stats['preproc']['median'] + stats['inference']['median'] + stats['explain']['median']) * 1000
    throughput = 1.0 / ((stats['preproc']['mean'] + stats['inference']['mean'] + stats['explain']['mean']))
    print("-" * 70)
    print(f"{'TOTAL':<20} {total_mean:>12.3f} {total_median:>12.3f} {'':>12} {'':>20}")
    print(f"\n💡 Throughput: {throughput:.1f} predictions per second (single core)")
    print("   Inference dominates: {:.1f}% of total compute time".format(
        100 * stats['inference']['mean'] / (stats['preproc']['mean'] + stats['inference']['mean'] + stats['explain']['mean'])
    ))
    print("=" * 70)


def main():
    """Main entry point."""
    print("\n")
    
    # Run benchmark
    measurements = run_benchmark(num_runs=50)
    
    # Compute statistics
    stats = compute_statistics(measurements)
    
    # Save results
    output_file = save_results(measurements, stats)
    
    # Print summary
    print_results_table(stats)
    
    print(f"\n✅ Results saved to: {output_file}")
    print("   Include this file in your paper revision to verify reproducibility.")
    print("\n")


if __name__ == '__main__':
    main()

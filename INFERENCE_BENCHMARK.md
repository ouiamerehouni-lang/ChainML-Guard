# Inference Latency Benchmark

This document describes how to reproduce and verify the inference latency measurements used in the SoftwareX paper revision.

## Overview

The `experiments/benchmark_inference.py` script measures the computational cost of the ChainML Guard fraud detection inference pipeline **on CPU**, explicitly **excluding** Etherscan blockchain API calls and network latency.

### What is Measured

The benchmark measures **three independent components** of the local inference path:

1. **Preprocessing (Feature Normalization)**
   - `StandardScaler.transform()` on the 3-feature vector
   - Time: ~0.4 ms (negligible)

2. **MLP Model Inference**
   - Forward pass through the 3-layer neural network
   - Input: 3 features (balance, tx_count, age_days)
   - Output: fraud probability [0.0, 1.0]
   - Time: ~55 ms (dominates compute time at 98.9%)

3. **Reason Summary Generation**
   - Heuristic rules applied to generate explanation text
   - Time: ~0.02 ms (negligible)

**Total local compute time: ~55 ms per address**

### What is NOT Measured

- ✗ Etherscan API calls to fetch blockchain data (~1–3 seconds per address)
- ✗ Flask HTTP request/response overhead
- ✗ JSON parsing or response formatting
- ✗ File I/O (history.json writes)
- ✗ Network latency or connectivity issues

These external factors dominate end-to-end response time but are **not** part of the model's computational cost.

## Running the Benchmark

### Prerequisites

Ensure the following files exist in the repository:
- `models/fraud_model.h5` (the trained MLP model)
- `models/scaler.pkl` (the StandardScaler)
- `data/dataset_final.csv` (sample data for benchmark input)
- `models/mlp/thresholds.json` (optional, for explanation generation)

### Using Docker (Recommended)

```bash
docker build -t chainml-guard .
docker run --rm -v $(pwd):/app --env-file .env chainml-guard python experiments/benchmark_inference.py
```

This ensures a consistent, reproducible environment (Python 3.11, TensorFlow 2.x, scikit-learn).

### Using Local Python

If TensorFlow and dependencies are installed locally:

```bash
python experiments/benchmark_inference.py
```

### Expected Runtime

The benchmark typically completes in **2–5 minutes** (50 runs × 3 components):
- Warmup: ~5 seconds
- 50 inference runs: ~2–4 minutes
- Results summaries and I/O: <1 minute

## Results Output

### Console Output

The script prints a summary table:

```
📊 RESULTS SUMMARY
======================================================================
Component             Mean (ms)     Median (ms)       Std (ms)  Min:Max (ms)
----------------------------------------------------------------------
preproc                    0.40            0.38            0.11   0.29 :   0.87
inference                 54.97           54.05            5.65  49.45 :  87.31
explain                    0.02            0.02            0.01   0.01 :   0.06
----------------------------------------------------------------------
TOTAL                     55.39           54.44                    
```

### JSON Output File

Results are saved to: **`results/bench_compute_only.json`**

This JSON file contains:

```json
{
  "metadata": {
    "description": "ChainML Guard inference latency benchmark ...",
    "system": { "python_version": "3.11.x", "tensorflow_version": "2.x", ... },
    "timestamp": "2026-07-11T...",
    "num_runs": 50
  },
  "raw_measurements": {
    "preproc": [0.0004..., 0.0003..., ...],
    "inference": [0.0549..., 0.0568..., ...],
    "explain": [0.000019..., ...]
  },
  "statistics": {
    "preproc": { "mean": 0.0004, "median": 0.0004, ... },
    "inference": { "mean": 0.0549, "median": 0.0540, ... },
    ...
  },
  "summary": {
    "preproc_ms": { "mean": 0.40, "median": 0.38, "stdev": 0.11 },
    "inference_ms": { "mean": 54.97, "median": 54.05, "stdev": 5.65 },
    "explain_ms": { "mean": 0.02, "median": 0.02, "stdev": 0.01 },
    "total_ms": { "mean": 55.39, "median": 54.44 },
    "throughput_per_second": 18.05
  }
}
```

## Interpreting the Results

### Key Findings

- **Model is efficient**: 209 parameters, 35.6 KB artifact → ~55 ms per inference
- **Preprocessing negligible**: 0.4 ms (<1% of total time)
- **Explanation generation negligible**: 0.02 ms (<0.1% of total time)
- **Throughput**: ~18 predictions per second on a single CPU core

### Implications for "Real-Time" Claim

The claim that ChainML Guard provides "real-time" fraud detection is supported by model latency:
- Model inference: **55 ms** (sub-100 millisecond)
- Network API latency: **1000–3000 ms** (dominated by Etherscan)

The 55 ms model cost does not create a real-time bottleneck. The system is **API-bound**, not **compute-bound**.

## Scalability Context

The benchmark confirms that the model itself is not the scalability constraint:

- **Per-address model cost**: ~55 ms
- **100 addresses sequentially**: ~5.5 seconds (model only)
- **Actual 100 addresses end-to-end**: ~100–300 seconds (API-dominated)

The current application architecture is **synchronous and blocking** (Flask dev server, serial API calls). To scale to production, improve the application layer (async I/O, worker pools, caching), not the model.

## Reproducibility & Version Control

The `experiments/benchmark_inference.py` script is version-controlled in the repository. To verify reproducibility:

1. Clone the repository
2. Build the Docker image: `docker build -t chainml-guard .`
3. Run the benchmark: `docker run --rm -v $(pwd):/app --env-file .env chainml-guard python experiments/benchmark_inference.py`
4. Compare `results/bench_compute_only.json` to values reported in your submitted revision

Small variations (<5% difference) are expected due to CPU scheduling and TensorFlow JIT compilation variance.

## FAQ

**Q: Why are the timing numbers different each run?**  
A: TensorFlow JIT-compiles operations on first run, and CPU scheduling varies. The benchmark includes a warmup phase and uses 50 trials to smooth variance. Median and standard deviation are reported.

**Q: Why does the benchmark not measure Etherscan calls?**  
A: Those are network I/O, not model computational cost. They would add non-determinism (internet latency) and require a valid Etherscan API key. The benchmark focuses on what you can control: the model and preprocessing.

**Q: Can I run this on GPU?**  
A: Yes, TensorFlow will use GPU if available. The latency will be faster (~5–10 ms for inference), but the benchmark metadata will correctly report GPU usage. Model is too small to see major GPU benefit.

**Q: How do I cite this benchmark?**  
A: "ChainML Guard inference latency measured using `experiments/benchmark_inference.py` over 50 trials on CPU-only hardware, July 2026."

---

**Last Updated**: 2026-07-11  
**Status**: Reproducible benchmark ready for paper revision

"""
Explanation utilities for ChainML Guard.

Provides rule-based, heuristic explanations for why an address was flagged,
using only the 3 core features: balance, tx_count, wallet_age_days.

This module does NOT attempt to explain the MLP's internal reasoning.
It provides human-readable indicators based on data-driven thresholds.
"""

import json
import os


def load_thresholds(thresholds_path='thresholds.json'):
    """
    Load the data-driven thresholds from JSON file.
    
    Args:
        thresholds_path: Path to thresholds.json (relative to project root)
    
    Returns:
        dict: Thresholds dictionary with keys: age_p10, tx_p90, bal_p05, bal_p95, rate_p90
    
    Raises:
        FileNotFoundError: If thresholds.json doesn't exist
    """
    if not os.path.exists(thresholds_path):
        raise FileNotFoundError(
            f"Thresholds file not found at {thresholds_path}. "
            "Please run scripts/compute_thresholds.py first."
        )
    
    with open(thresholds_path, 'r') as f:
        thresholds = json.load(f)
    
    return thresholds


def generate_reason_summary(balance, tx_count, wallet_age_days, thresholds):
    """
    Generate human-readable reason summary explaining why an address may be risky.
    
    This function applies simple heuristic rules based on the 3 features and
    data-driven thresholds computed from the training dataset.
    
    Args:
        balance (float): Wallet balance in ETH
        tx_count (int): Number of transactions
        wallet_age_days (float): Wallet age in days
        thresholds (dict): Dictionary containing threshold values:
            - age_p10: 10th percentile of wallet age
            - tx_p90: 90th percentile of transaction count
            - bal_p05: 5th percentile of balance
            - bal_p95: 95th percentile of balance
            - rate_p90: 90th percentile of activity rate
    
    Returns:
        list of str: List of reason strings (bullet points explaining risk indicators)
    
    Note:
        These are heuristic indicators based on address-level features.
        They do NOT represent the MLP model's internal decision-making process.
    """
    reasons = []
    
    # Calculate activity rate (tx per day of wallet age)
    activity_rate = tx_count / max(wallet_age_days, 1)
    
    # Rule 1: Very new wallet
    if wallet_age_days < thresholds['age_p10']:
        reasons.append("Very new wallet")
    
    # Rule 2: High activity rate for its age
    if activity_rate > thresholds['rate_p90']:
        reasons.append("High activity for its age")
    
    # Rule 3: Unusually high transaction count
    if tx_count > thresholds['tx_p90']:
        reasons.append("Unusually high transaction count")
    
    # Rule 4: Extreme balance (low or high)
    if balance < thresholds['bal_p05']:
        reasons.append("Unusually low balance")
    elif balance > thresholds['bal_p95']:
        reasons.append("Unusually high balance")
    
    # If no rules triggered, model detected patterns not captured by simple heuristics
    if not reasons:
        reasons.append("Model detected suspicious patterns in transaction behavior")
    
    return reasons


def get_explanation_disclaimer():
    """
    Returns the standard disclaimer text for explanations.
    
    Returns:
        str: Disclaimer text to display with all explanations (now returns empty string)
    """
    return ""

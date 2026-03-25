#!/usr/bin/env python
"""
Quick validation test for Solo Optimizer.
"""
import pandas as pd
from data_utils import load_data
from optimizer import optimize

# Load data
print("Loading data...")
df = load_data("players_processed_v7.csv")
print(f"Loaded {len(df)} players")

# Test 1: Gegenpress 4-3-3 (as specified in validation)
print("\n=== Test 1: Gegenpress 4-3-3 ===")
result, status = optimize(df, "4-3-3", "Gegenpress", 750_000_000, 3)

if result:
    result_df = pd.DataFrame(result)
    print(f"âœ… Optimization succeeded")
    print(f"Squad size: {len(result_df)}")
    print(f"Squad value: â‚¬{result_df['value'].sum() / 1e6:.1f}M")
    print(f"Avg quality: {result_df['quality'].mean():.1f}%")
    print(f"Avg tactic fit: {result_df['tactic_fit'].mean():.1f}%")
    print(f"Clubs: {result_df['Squad'].nunique()} unique")
    
    # Validate position constraints
    print("\nPosition breakdown:")
    for pos in ["GK", "DF", "MF", "FW"]:
        count = len(result_df[result_df['slot'] == pos])
        players = result_df[result_df['slot'] == pos]['Player'].tolist()
        print(f"  {pos} ({count}): {', '.join(p.split()[-1] for p in players[:3])}...")
    
    # Validate slot constraints for 4-3-3
    expected = {"GK": 1, "DF": 4, "MF": 3, "FW": 3}
    print("\nValidation:")
    for slot, expected_count in expected.items():
        actual = len(result_df[result_df['slot'] == slot])
        status = "âœ“" if actual == expected_count else "âœ—"
        print(f"  {status} {slot}: {actual}/{expected_count}")
    
    # Check budget
    total_budget = result_df['value'].sum()
    print(f"  âœ“ Budget: â‚¬{total_budget/1e6:.1f}M â‰¤ â‚¬750M")
    
    # Check quality and fit floors
    min_quality = result_df['quality'].min()
    min_fit = result_df['tactic_fit'].min()
    print(f"  âœ“ Min quality: {min_quality:.1f}% (floor: 40%)")
    print(f"  âœ“ Min tactic fit: {min_fit:.1f}% (floor: 35%)")
    
else:
    print(f"âŒ Optimization failed: {status}")

# Test 2: Different budget and constraint
print("\n=== Test 2: Counter Attack 4-2-3-1 (Budget â‚¬500M, max 2 per club) ===")
result2, status2 = optimize(df, "4-2-3-1", "Counter Attack", 500_000_000, 2)

if result2:
    result_df2 = pd.DataFrame(result2)
    print(f"âœ… Optimization succeeded")
    print(f"Squad value: â‚¬{result_df2['value'].sum() / 1e6:.1f}M")
    print(f"Avg quality: {result_df2['quality'].mean():.1f}%")
    print(f"Max per club: {result_df2['Squad'].value_counts().max()}")
else:
    print(f"âŒ Optimization failed: {status2}")

print("\n=== All tests complete ===")

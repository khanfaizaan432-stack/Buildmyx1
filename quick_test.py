#!/usr/bin/env python
"""Quick test to validate data loading and optimizer basics."""
import sys
sys.path.insert(0, '.')

try:
    print("Step 1: Importing modules...")
    from data_utils import load_data
    from optimizer import optimize
    print("âœ“ Imports successful")
    
    print("\nStep 2: Loading data...")
    df = load_data("players_processed_v7.csv")
    print(f"âœ“ Loaded {len(df)} players")
    print(f"  Columns: {df.columns.tolist()[-10:]}")
    print(f"  Has position: {'position' in df.columns}")
    print(f"  Has quality_final: {'quality_final' in df.columns}")
    print(f"  Has sub_position: {'sub_position' in df.columns}")
    
    print("\nStep 3: Checking data types...")
    print(f"  Position values (sample): {df['position'].unique()[:5]}")
    print(f"  Sub-position values (sample): {df['sub_position'].dropna().unique()[:5]}")
    print(f"  Quality final range: {df['quality_final'].min():.2f} - {df['quality_final'].max():.2f}")
    print(f"  Final value range: â‚¬{df['final_value'].min():.0f} - â‚¬{df['final_value'].max()/1e6:.1f}M")
    
    print("\nStep 4: Testing optimizer...")
    result, status = optimize(df, "4-3-3", "Gegenpress", 750_000_000, 3)
    
    if result:
        print(f"âœ“ Optimization succeeded!")
        print(f"  Squad size: {len(result)}")
        if len(result) >= 11:
            import pandas as pd
            result_df = pd.DataFrame(result)
            print(f"  Squad value: â‚¬{result_df['value'].sum() / 1e6:.1f}M")
            print(f"  Avg quality: {result_df['quality'].mean():.1f}%")
            print(f"  Avg tactic fit: {result_df['tactic_fit'].mean():.1f}%")
            print(f"  Formation check:")
            for pos in ["GK", "DF", "MF", "FW"]:
                count = len(result_df[result_df['slot'] == pos])
                print(f"    {pos}: {count}")
        else:
            print(f"  ERROR: Expected 11 players, got {len(result)}")
    else:
        print(f"âœ— Optimization failed: {status}")
        
except Exception as e:
    print(f"\nâœ— ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

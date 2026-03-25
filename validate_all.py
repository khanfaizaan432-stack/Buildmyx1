#!/usr/bin/env python
"""
Comprehensive validation script.
"""
import sys
import os

os.chdir('c:\\Users\\khanf\\OneDrive\\Documents\\Buildmyx1')

def test_imports():
    """Test that all modules can be imported."""
    print("=" * 60)
    print("STEP 1: Testing Module Imports")
    print("=" * 60)
    try:
        import config
        print("âœ“ config.py imports successfully")
        
        import data_utils
        print("âœ“ data_utils.py imports successfully")
        
        import optimizer
        print("âœ“ optimizer.py imports successfully")
        
        import draft
        print("âœ“ draft.py imports successfully")
        
        import pitch_viz
        print("âœ“ pitch_viz.py imports successfully")
        
        import app
        print("âœ“ app.py imports successfully")
        
        return True
    except Exception as e:
        print(f"âœ— Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_loading():
    """Test loading the CSV data."""
    print("\n" + "=" * 60)
    print("STEP 2: Testing Data Loading")
    print("=" * 60)
    try:
        from data_utils import load_data
        df = load_data("players_processed_v7.csv")
        print(f"âœ“ Loaded {len(df)} players")
        
        # Check key columns
        required_cols = ['Player', 'Squad', 'Nation', 'position', 'sub_position', 
                        'quality_final', 'final_value', 'player_image_url',
                        'fit_gegenpress', 'fit_high_press', 'fit_tiki_taka', 
                        'fit_counter_attack', 'fit_park_the_bus', 'fit_long_ball',
                        'fit_high_line', 'fit_false_9']
        
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            print(f"âœ— Missing columns: {missing}")
            return False
        
        print(f"âœ“ All required columns present")
        print(f"  - Position values: {df['position'].unique()[:5]}")
        print(f"  - Sample sub_position: {df['sub_position'].dropna().unique()[:3]}")
        print(f"  - Quality final range: {df['quality_final'].min():.2f} - {df['quality_final'].max():.2f}")
        
        return True
    except Exception as e:
        print(f"âœ— Data loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_optimizer():
    """Test the ILP optimizer."""
    print("\n" + "=" * 60)
    print("STEP 3: Testing Optimizer")
    print("=" * 60)
    try:
        from data_utils import load_data
        from optimizer import optimize
        
        df = load_data("players_processed_v7.csv")
        print("Testing 4-3-3 Gegenpress formation...")
        
        result, status = optimize(df, "4-3-3", "Gegenpress", 750_000_000, 3)
        
        if result is None:
            print(f"âœ— Optimizer failed: {status}")
            return False
        
        print(f"âœ“ Optimization successful")
        print(f"  - Squad size: {len(result)}/11")
        
        if len(result) != 11:
            print(f"âœ— Expected 11 players, got {len(result)}")
            return False
        
        import pandas as pd
        result_df = pd.DataFrame(result)
        
        # Check formation
        print(f"  - Formation breakdown:")
        for pos in ["GK", "DF", "MF", "FW"]:
            count = len(result_df[result_df['slot'] == pos])
            print(f"    {pos}: {count}")
        
        expected_formation = {"GK": 1, "DF": 4, "MF": 3, "FW": 3}
        for pos, expected in expected_formation.items():
            actual = len(result_df[result_df['slot'] == pos])
            if actual != expected:
                print(f"âœ— Formation mismatch: {pos} expected {expected}, got {actual}")
                return False
        
        total_value = result_df['value'].sum()
        print(f"  - Total value: â‚¬{total_value / 1e6:.1f}M (budget: â‚¬750M)")
        
        if total_value > 750_000_000:
            print(f"âœ— Budget exceeded")
            return False
        
        max_per_club = result_df['Squad'].value_counts().max()
        print(f"  - Max per club: {max_per_club} (limit: 3)")
        
        if max_per_club > 3:
            print(f"âœ— Max per club exceeded")
            return False
        
        print(f"  - Avg quality: {result_df['quality'].mean():.1f}%")
        print(f"  - Avg tactic fit: {result_df['tactic_fit'].mean():.1f}%")
        
        return True
    except Exception as e:
        print(f"âœ— Optimizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Data Loading", test_data_loading()))
    results.append(("Optimizer", test_optimizer()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "âœ“ PASS" if passed else "âœ— FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    sys.exit(0 if all_passed else 1)

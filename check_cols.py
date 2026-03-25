#!/usr/bin/env python
import pandas as pd

df = pd.read_csv('players_processed_v7.csv', nrows=2)

# Find key columns
print("Total columns:", len(df.columns))
print("\nKey columns:")
for col in df.columns:
    if any(k in col.lower() for k in ['position', 'sub_pos', 'final_value', 'quality', 'fit_', 'player_image', 'squad', 'nation']):
        val_sample = str(df[col].iloc[0])[:30] if len(df) > 0 else "N/A"
        print(f"  {col:40s} = {val_sample}")

# Check which position column exists
print("\nPosition-like columns:", [c for c in df.columns if 'position' in c.lower() or c == 'Pos'])
print("Quality-like columns:", [c for c in df.columns if 'quality' in c.lower()])

#!/usr/bin/env python
"""Analyze CSV column structure."""
import csv

with open('players_processed_v7.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    print(f"Total columns: {len(header)}")
    print("\nSearching for key columns:")
    
    for i, col in enumerate(header):
        if any(key in col.lower() for key in ['position', 'sub_pos', 'final_value', 'quality_final', 'fit_', 'player_image']):
            print(f"  Col {i:3d}: {col}")

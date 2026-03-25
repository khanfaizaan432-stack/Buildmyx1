import pandas as pd
import numpy as np

def compute_adjusted_quality(df):
    # Fallback only: if quality_final is missing in source data,
    # derive it directly from quality_score percentile within position.
    quality_base = pd.to_numeric(df.get("quality_score", pd.Series(0, index=df.index)), errors="coerce").fillna(0)
    df["quality_adjusted"] = quality_base
    df["quality_final"] = quality_base.groupby(df["position"]).rank(pct=True)
    return df

def load_data(csv_path="players_processed_v7.csv"):
    df = pd.read_csv(csv_path)

    # Standardize column names (Pos â†’ position if needed)
    if "Pos" in df.columns and "position" not in df.columns:
        df["position"] = df["Pos"]
    elif "position" not in df.columns:
        df["position"] = ""

    # If quality_final doesn't already exist, compute it
    if "quality_final" not in df.columns:
        df = compute_adjusted_quality(df)

    # fill missing tactic fit columns with 0
    tactic_cols = [
        "fit_gegenpress","fit_high_press","fit_tiki_taka","fit_counter_attack",
        "fit_park_the_bus","fit_long_ball","fit_high_line","fit_false_9"
    ]
    for c in tactic_cols:
        if c not in df.columns:
            df[c] = 0.0
        else:
            df[c] = df[c].fillna(0)

    # fill missing values
    if "final_value" in df.columns:
        df["final_value"] = pd.to_numeric(df["final_value"], errors="coerce").fillna(0)
        # Handle conversion if needed (if max is small, multiply by 1M)
        if df["final_value"].max() < 1000:
            df["final_value"] = df["final_value"] * 1000000
    else:
        df["final_value"] = 0.0
    
    df["player_image_url"] = df.get("player_image_url", pd.Series("", index=df.index)).fillna("")
    df["alt_position"]     = df.get("alt_position", pd.Series("", index=df.index)).fillna("")
    df["sub_position"]     = df.get("sub_position", pd.Series("", index=df.index)).fillna("")

    return df

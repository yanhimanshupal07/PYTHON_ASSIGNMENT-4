# ---------------------------------------------------------------------
# Air Quality Data Visualizer - Unit 4 Assignment
# Author: Kunal Lohia
# Course: Problem Solving with Python (BCA AI & DS - Semester 1)
# Faculty: Dr. Satinder Pal Singh
# ---------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

FNAME = "cleaned_pollution.csv"  # put your file here

def ask_map(cols):
    print("Columns found in file:", cols)
    print("If automatic mapping fails you will be asked to type the exact column name.")
    return

def pick_column(cols, candidates):
    # return first real column name that contains any candidate substring
    low = [c.lower() for c in cols]
    for cand in candidates:
        for i, name in enumerate(low):
            if cand in name:
                return cols[i]
    return None

def main():
    if not os.path.exists(FNAME):
        print(f"Error: '{FNAME}' not found in current folder: {os.getcwd()}")
        sys.exit(1)

    df = pd.read_csv(FNAME, low_memory=False)
    cols = list(df.columns)
    ask_map(cols)

    # auto-detect common column names
    date_col = pick_column(cols, ["date", "time", "timestamp"])
    pm25_col = pick_column(cols, ["pm2.5", "pm25", "pm_2_5", "pm2"])
    pm10_col = pick_column(cols, ["pm10", "pm_10"])
    aqi_col  = pick_column(cols, ["aqi", "air quality", "air_quality"])

    # prompt user only for missing mappings
    if date_col is None:
        date_col = input("Type the column name that contains the date/time: ").strip()
    if pm25_col is None:
        pm25_col = input("Type the column name for PM2.5 (or leave empty to skip): ").strip() or None
    if pm10_col is None:
        pm10_col = input("Type the column name for PM10 (or leave empty to skip): ").strip() or None
    if aqi_col is None:
        aqi_col = input("Type the column name for AQI (or leave empty to skip): ").strip() or None

    print("\nUsing columns:")
    print(" Date ->", date_col)
    print(" PM2.5 ->", pm25_col)
    print(" PM10 ->", pm10_col)
    print(" AQI ->", aqi_col)

    # Basic checks
    if date_col not in df.columns:
        print("ERROR: Date column not found. Exiting.")
        sys.exit(1)

    # Convert Date
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).sort_values(by=date_col).reset_index(drop=True)

    # Work only with the columns that exist
    use_cols = [date_col]
    for c in (pm25_col, pm10_col, aqi_col):
        if c and c in df.columns:
            use_cols.append(c)

    df = df[use_cols].copy()

    # Convert pollutant columns to numeric and fill na with mean
    for c in use_cols:
        if c == date_col:
            continue
        df[c] = pd.to_numeric(df[c], errors="coerce")
        mean_val = df[c].mean(skipna=True)
        if pd.isna(mean_val):
            print(f"Warning: column '{c}' has no numeric values; it will remain NaN.")
        else:
            df[c] = df[c].fillna(mean_val)

    # Save cleaned CSV
    cleaned_name = "cleaned_pollution.csv"
    df.to_csv(cleaned_name, index=False)
    print(f"Saved cleaned data to {cleaned_name}")

    # Create plots (only if columns exist)
    try:
        if aqi_col and aqi_col in df.columns:
            plt.figure(figsize=(10,4))
            plt.plot(df[date_col], df[aqi_col])
            plt.title("Daily AQI Trend")
            plt.xlabel("Date")
            plt.ylabel("AQI")
            plt.tight_layout()
            plt.savefig("aqi_trend.png")
            plt.close()
            print("Saved aqi_trend.png")

        if pm25_col and pm25_col in df.columns:
            # monthly average
            df['Month'] = df[date_col].dt.to_period('M')
            monthly = df.groupby('Month')[pm25_col].mean()
            plt.figure(figsize=(10,4))
            monthly.index = monthly.index.astype(str)
            monthly.plot(kind='bar')
            plt.title("Monthly Avg PM2.5")
            plt.xlabel("Month")
            plt.ylabel("PM2.5")
            plt.tight_layout()
            plt.savefig("monthly_pm25.png")
            plt.close()
            print("Saved monthly_pm25.png")

        if pm25_col and pm10_col and pm25_col in df.columns and pm10_col in df.columns:
            plt.figure(figsize=(6,5))
            plt.scatter(df[pm25_col], df[pm10_col], s=8)
            plt.title("PM2.5 vs PM10")
            plt.xlabel("PM2.5")
            plt.ylabel("PM10")
            plt.tight_layout()
            plt.savefig("scatter_pm25_pm10.png")
            plt.close()
            print("Saved scatter_pm25_pm10.png")
    except Exception as e:
        print("Plotting error:", e)

    # Simple report
    with open("report.txt","w") as f:
        f.write("Simple Air Quality Report\n")
        f.write("=========================\n")
        f.write(f"Rows after cleaning: {len(df)}\n\n")
        if pm25_col and pm25_col in df.columns:
            f.write(f"Mean PM2.5: {df[pm25_col].mean():.2f}\n")
        if pm10_col and pm10_col in df.columns:
            f.write(f"Mean PM10: {df[pm10_col].mean():.2f}\n")
        if aqi_col and aqi_col in df.columns:
            f.write(f"AQI min/max: {df[aqi_col].min():.2f} / {df[aqi_col].max():.2f}\n")
    print("Saved report.txt")
    print("Done.")

if __name__ == "__main__":
    main()
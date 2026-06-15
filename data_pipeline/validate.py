import pandas as pd
import numpy as np
import os

CLEAN_DATA_DIR = "data/clean"
OUTPUT_REPORT = os.path.join(CLEAN_DATA_DIR, "validation_report.txt")

def validate_completeness():
    df = pd.read_csv(os.path.join(CLEAN_DATA_DIR, "maule_master.csv"), parse_dates=["date"])

    decades = [(1960 + i*10, 1969 + i*10) for i in range(7)]
    variables = {
        "flow_m3s": "discharge_m3s",
        "enso_mei": "enso_mei",
        "pdo_index": "pdo_index",
        "swe_mm": "snowpack_swe",
        "precip_mm": "era5_precip"
    }

    report_lines = []
    report_lines.append("MAULE DATA COMPLETENESS REPORT")
    report_lines.append("================================")
    header = "Variable         | " + " | ".join([f"{d[0]}s" for d in decades])
    report_lines.append(header)

    completeness_results = {}

    for var_col, var_name in variables.items():
        line = f"{var_name:<16} | "
        decade_stats = []
        for start, end in decades:
            mask = (df["date"].dt.year >= start) & (df["date"].dt.year <= end)
            if mask.sum() == 0:
                coverage = 0
            else:
                coverage = df.loc[mask, var_col].notna().mean() * 100
            decade_stats.append(coverage)
            line += f"{coverage:>4.0f}%  | "
        report_lines.append(line)
        completeness_results[var_col] = decade_stats

    report_lines.append("\nWARNINGS:")
    # discharge coverage < 70% in any decade 1980–2024
    for i, (start, end) in enumerate(decades):
        if start >= 1980:
            if completeness_results["flow_m3s"][i] < 70:
                report_lines.append(f"- discharge_m3s: coverage in {start}s ({completeness_results['flow_m3s'][i]:.0f}%) below 70% threshold!")

    # ENSO MEI coverage < 95% any decade 1970–2024
    for i, (start, end) in enumerate(decades):
        if start >= 1970:
            if completeness_results["enso_mei"][i] < 95:
                report_lines.append(f"- enso_mei: coverage in {start}s ({completeness_results['enso_mei'][i]:.0f}%) below 95% threshold!")

    # ERA5 precip coverage < 95% any decade 1960–2024
    for i, (start, end) in enumerate(decades):
        if completeness_results["precip_mm"][i] < 95:
             report_lines.append(f"- era5_precip: coverage in {start}s ({completeness_results['precip_mm'][i]:.0f}%) below 95% threshold!")

    report_text = "\n".join(report_lines)
    print(report_text)

    with open(OUTPUT_REPORT, "w") as f:
        f.write(report_text)

    # Gate check — raise exception if threshold breached
    for i, (start, end) in enumerate(decades):
        if start >= 1980 and completeness_results["flow_m3s"][i] < 70:
            raise Exception(f"CRITICAL: Discharge coverage in {start}s too low.")
        if start >= 1970 and completeness_results["enso_mei"][i] < 95:
             raise Exception(f"CRITICAL: ENSO coverage in {start}s too low.")
        if completeness_results["precip_mm"][i] < 95:
             raise Exception(f"CRITICAL: ERA5 coverage in {start}s too low.")

def main():
    validate_completeness()

if __name__ == "__main__":
    main()

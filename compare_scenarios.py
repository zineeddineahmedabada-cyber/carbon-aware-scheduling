
from pathlib import Path

import pandas as pd

from src.scheduler import generate_candidates, compare_strategies


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "carbon_intensity.csv"
OUTPUT_DIR = ROOT / "output"

carbon = pd.read_csv(DATA_FILE)

scenarios = [
    {
        "name": "A - Urgent task",
        "earliest_start_hour": 8,
        "deadline_hour": 12,
        "missing_hour": None,
    },
    {
        "name": "B - Flexible deadline",
        "earliest_start_hour": 8,
        "deadline_hour": 18,
        "missing_hour": None,
    },
    {
        "name": "C - Missing carbon data",
        "earliest_start_hour": 8,
        "deadline_hour": 18,
        "missing_hour": 10,
    },
    {
        "name": "D - Impossible deadline",
        "earliest_start_hour": 8,
        "deadline_hour": 10,
        "missing_hour": None,
    },
]

power_kw = 5
duration_hours = 3
comparison_rows = []

for scenario in scenarios:
    scenario_carbon = carbon.copy()
    missing_hour = scenario["missing_hour"]

    if missing_hour is not None:
        scenario_carbon = scenario_carbon[
            scenario_carbon["hour"] != missing_hour
        ]

    candidates = generate_candidates(
        carbon=scenario_carbon,
        power_kw=power_kw,
        duration_hours=duration_hours,
        deadline_hour=scenario["deadline_hour"],
        earliest_start_hour=scenario["earliest_start_hour"],
    )

    row = {
        "Scenario": scenario["name"],
        "Earliest start": scenario["earliest_start_hour"],
        "Deadline": scenario["deadline_hour"],
        "Duration (h)": duration_hours,
        "Feasible": not candidates.empty,
        "Baseline window": None,
        "Baseline (gCO2)": None,
        "Optimized window": None,
        "Optimized (gCO2)": None,
        "Avoided (gCO2)": None,
        "Reduction (%)": None,
    }

    if not candidates.empty:
        comparison = compare_strategies(candidates)

        row.update({
            "Baseline window": (
                f"{comparison['baseline_start_hour']}:00-"
                f"{comparison['baseline_end_hour']}:00"
            ),
            "Baseline (gCO2)": round(
                comparison["baseline_emissions_g"], 2
            ),
            "Optimized window": (
                f"{comparison['optimized_start_hour']}:00-"
                f"{comparison['optimized_end_hour']}:00"
            ),
            "Optimized (gCO2)": round(
                comparison["optimized_emissions_g"], 2
            ),
            "Avoided (gCO2)": round(
                comparison["emissions_avoided_g"], 2
            ),
            "Reduction (%)": round(
                comparison["reduction_percent"], 2
            ),
        })

    comparison_rows.append(row)

comparison_table = pd.DataFrame(comparison_rows)

print("\nCARBON-AWARE SCHEDULING")
print("SCENARIO COMPARISON")
print("=" * 110)
print(comparison_table.to_string(index=False, na_rep="N/A"))

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
output_file = OUTPUT_DIR / "scenario_comparison.csv"
comparison_table.to_csv(output_file, index=False)

print(f"\nComparison table saved to: {output_file}")

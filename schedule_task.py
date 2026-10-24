
from pathlib import Path

import pandas as pd

from src.scheduler import generate_candidates, compare_strategies


def validate_carbon_data(carbon):
    required = {"hour", "carbon_intensity_g_per_kwh"}

    missing_columns = required - set(carbon.columns)
    if missing_columns:
        raise ValueError(
            f"Missing columns: {sorted(missing_columns)}"
        )

    if carbon.empty:
        raise ValueError("Carbon dataset is empty.")

    carbon = carbon.copy()

    carbon["hour"] = pd.to_numeric(
        carbon["hour"], errors="coerce"
    )
    carbon["carbon_intensity_g_per_kwh"] = pd.to_numeric(
        carbon["carbon_intensity_g_per_kwh"],
        errors="coerce",
    )

    if carbon["hour"].isna().any():
        raise ValueError("Hours must be numeric and present.")

    if carbon["carbon_intensity_g_per_kwh"].isna().any():
        raise ValueError(
            "Carbon intensities must be numeric and present."
        )

    if (carbon["hour"] % 1 != 0).any():
        raise ValueError("Hours must be whole numbers.")

    carbon["hour"] = carbon["hour"].astype(int)

    if carbon["hour"].duplicated().any():
        raise ValueError("Duplicate hour values.")

    if (carbon["carbon_intensity_g_per_kwh"] < 0).any():
        raise ValueError(
            "Carbon intensity cannot be negative."
        )

    carbon = carbon.sort_values("hour").reset_index(drop=True)



    print("Carbon data validation passed.")
    return carbon


ROOT = Path(__file__).resolve().parent
carbon = pd.read_csv(ROOT / "data" / "carbon_intensity.csv")
carbon = validate_carbon_data(carbon)

# Task configuration
power_kw = 5
duration_hours = 3
deadline_hour = 18

# Generate all feasible schedules

results = generate_candidates(
    carbon=carbon,
    power_kw=power_kw,
    duration_hours=duration_hours,
    deadline_hour=deadline_hour,
)

if results.empty:
    print("No feasible schedule found before the deadline.")
else:
    comparison = compare_strategies(results)

    print("Carbon-aware workload scheduling")
    print("\nBaseline strategy")
    print(
        f"Start: {comparison['baseline_start_hour']}:00"
    )
    print(
        f"Finish: {comparison['baseline_end_hour']}:00"
    )
    print(
        f"Emissions: {comparison['baseline_emissions_g']:.0f} gCO2"
    )

    print("\nCarbon-aware strategy")
    print(
        f"Start: {comparison['optimized_start_hour']}:00"
    )
    print(
        f"Finish: {comparison['optimized_end_hour']}:00"
    )
    print(
        f"Emissions: {comparison['optimized_emissions_g']:.0f} gCO2"
    )

    print("\nEnvironmental impact")
    print(
        f"Emissions avoided: "
        f"{comparison['emissions_avoided_g']:.0f} gCO2"
    )
    print(
        f"Reduction: {comparison['reduction_percent']:.2f}%"
    )

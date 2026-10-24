
from pathlib import Path

import pandas as pd

from src.carbon_data import (
    validate_timestamped_carbon,
    get_fresh_carbon_data,
)


ROOT = Path(__file__).resolve().parent

carbon = pd.read_csv(
    ROOT / "data" / "carbon_intensity_timestamped.csv"
)

# Fixed reference time for a reproducible experiment
reference_time = "2026-10-24 15:00:00"

validated = validate_timestamped_carbon(
    carbon,
    reference_time=reference_time,
    max_age_minutes=60,
)

print("Timestamped carbon data")
print(
    validated[
        [
            "timestamp",
            "intensity_g_per_kwh",
            "observed_at",
            "age_minutes",
            "is_fresh",
        ]
    ].to_string(index=False)
)

fresh = get_fresh_carbon_data(validated)

print(f"\nTotal measurements: {len(validated)}")
print(f"Fresh measurements: {len(fresh)}")
print(f"Stale measurements: {len(validated) - len(fresh)}")

print("\nData retained for scheduling:")
print(fresh.to_string(index=False))

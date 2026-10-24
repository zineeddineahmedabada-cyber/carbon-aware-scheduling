
from pathlib import Path

import pandas as pd

from src.carbon_data import (
    validate_timestamped_carbon,
    prepare_fresh_carbon_for_scheduler,
)
from src.scheduler import generate_candidates


ROOT = Path(__file__).resolve().parent

carbon = pd.read_csv(
    ROOT / "data" / "carbon_forecast_demo.csv"
)

validated = validate_timestamped_carbon(
    carbon,
    reference_time="2026-10-24 15:00:00",
    max_age_minutes=60,
)

scheduler_data = prepare_fresh_carbon_for_scheduler(validated)

print("Fresh data passed to scheduler:")
print(scheduler_data.to_string(index=False))

candidates = generate_candidates(
    carbon=scheduler_data,
    power_kw=5,
    duration_hours=3,
    earliest_start_hour=15,
    deadline_hour=19,
)

print("\nFeasible scheduling candidates:")
print(candidates.to_string(index=False))

if candidates.empty:
    print("\nNo feasible schedule: insufficient consecutive fresh data.")

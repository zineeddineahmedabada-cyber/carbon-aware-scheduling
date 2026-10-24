
import pandas as pd

from src.emissions import calculate_emissions


def generate_candidates(
    carbon,
    power_kw,
    duration_hours,
    deadline_hour,
    earliest_start_hour=0,
):
    if duration_hours <= 0:
        raise ValueError("Duration must be positive.")

    if power_kw < 0:
        raise ValueError("Power cannot be negative.")

    required = {"hour", "carbon_intensity_g_per_kwh"}
    missing = required - set(carbon.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    carbon = carbon.sort_values("hour").reset_index(drop=True)

    candidates = []

    for start_idx in range(len(carbon) - duration_hours + 1):
        window = carbon.iloc[
            start_idx:start_idx + duration_hours
        ]

        start_hour = int(window.iloc[0]["hour"])
        end_hour = start_hour + duration_hours
        # Do not schedule before the task becomes available
        if start_hour < earliest_start_hour:
            continue

        # Reject windows that exceed the deadline
        if end_hour > deadline_hour:
            continue

        # Ensure the hours in the window are consecutive
        expected_hours = list(
            range(start_hour, end_hour)
        )

        actual_hours = window["hour"].astype(int).tolist()

        if actual_hours != expected_hours:
            continue

        emissions = sum(
            calculate_emissions(
                power_kw,
                1,
                float(intensity),
            )
            for intensity in window[
                "carbon_intensity_g_per_kwh"
            ]
        )

        candidates.append({
            "start_hour": start_hour,
            "end_hour": end_hour,
            "emissions_g": emissions,
        })

    return pd.DataFrame(
        candidates,
        columns=["start_hour", "end_hour", "emissions_g"],
    )

def compare_strategies(candidates):
    if candidates.empty:
        raise ValueError("Cannot compare strategies without candidates.")

    # Baseline: execute at the earliest feasible start time
    baseline = candidates.loc[
        candidates["start_hour"].idxmin()
    ]

    # Carbon-aware: choose the candidate with minimum emissions
    optimized = candidates.loc[
        candidates["emissions_g"].idxmin()
    ]

    baseline_emissions = float(baseline["emissions_g"])
    optimized_emissions = float(optimized["emissions_g"])

    emissions_avoided = baseline_emissions - optimized_emissions

    reduction_percent = (
        emissions_avoided / baseline_emissions * 100
        if baseline_emissions > 0
        else 0.0
    )

    return {
        "baseline_start_hour": int(baseline["start_hour"]),
        "baseline_end_hour": int(baseline["end_hour"]),
        "baseline_emissions_g": baseline_emissions,
        "optimized_start_hour": int(optimized["start_hour"]),
        "optimized_end_hour": int(optimized["end_hour"]),
        "optimized_emissions_g": optimized_emissions,
        "emissions_avoided_g": emissions_avoided,
        "reduction_percent": reduction_percent,
    }


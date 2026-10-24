
import pandas as pd


REQUIRED_COLUMNS = {
    "timestamp",
    "intensity_g_per_kwh",
    "observed_at",
}


def validate_timestamped_carbon(
    carbon,
    reference_time,
    max_age_minutes=60,
):
    """
    Validate timestamps and assess carbon-data freshness.

    A measurement is fresh when its age is between
    0 and max_age_minutes, inclusive.

    Returns a copy of the dataset with:
    - parsed timestamps
    - age_minutes
    - is_fresh
    """
    if max_age_minutes < 0:
        raise ValueError("Maximum age cannot be negative.")

    missing = REQUIRED_COLUMNS - set(carbon.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    data = carbon.copy()

    data["timestamp"] = pd.to_datetime(
        data["timestamp"], errors="coerce"
    )
    data["observed_at"] = pd.to_datetime(
        data["observed_at"], errors="coerce"
    )

    if data["timestamp"].isna().any():
        raise ValueError("Invalid or missing timestamps.")

    if data["observed_at"].isna().any():
        raise ValueError(
            "Invalid or missing observation timestamps."
        )

    data["intensity_g_per_kwh"] = pd.to_numeric(
        data["intensity_g_per_kwh"],
        errors="coerce",
    )

    if data["intensity_g_per_kwh"].isna().any():
        raise ValueError(
            "Carbon intensities must be numeric and present."
        )

    if (data["intensity_g_per_kwh"] < 0).any():
        raise ValueError(
            "Carbon intensity cannot be negative."
        )

    if data["timestamp"].duplicated().any():
        raise ValueError("Duplicate measurement timestamps.")

    reference_time = pd.Timestamp(reference_time)

    if reference_time.tz is not None:
        raise ValueError(
            "Use timezone-naive timestamps consistently "
            "for this initial simulation."
        )

    age = reference_time - data["observed_at"]
    data["age_minutes"] = age.dt.total_seconds() / 60

    if (data["age_minutes"] < 0).any():
        raise ValueError(
            "Observation timestamps cannot be in the future."
        )

    data["is_fresh"] = (
        data["age_minutes"] <= max_age_minutes
    )

    return data


def get_fresh_carbon_data(validated_data):
    """Return only measurements that pass the freshness check."""
    return validated_data.loc[
        validated_data["is_fresh"]
    ].copy()
def prepare_fresh_carbon_for_scheduler(validated_data):
    """
    Convert fresh timestamped measurements to the scheduler format.
    """
    fresh = get_fresh_carbon_data(validated_data)

    if fresh.empty:
        raise ValueError(
            "No fresh carbon measurements available for scheduling."
        )

    scheduler_data = pd.DataFrame({
        "hour": fresh["timestamp"].dt.hour,
        "carbon_intensity_g_per_kwh": (
            fresh["intensity_g_per_kwh"]
        ),
    })

    return scheduler_data.sort_values(
        "hour"
    ).reset_index(drop=True)
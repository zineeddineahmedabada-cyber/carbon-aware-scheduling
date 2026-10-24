
import unittest
import pandas as pd
from src.carbon_data import prepare_fresh_carbon_for_scheduler
from src.carbon_data import (
    validate_timestamped_carbon,
    get_fresh_carbon_data,
)


class TestCarbonDataFreshness(unittest.TestCase):

    def setUp(self):
        self.reference_time = pd.Timestamp(
            "2026-10-24 10:00:00"
        )

        self.carbon = pd.DataFrame({
            "timestamp": [
                "2026-10-24 09:00:00",
                "2026-10-24 10:00:00",
                "2026-10-24 11:00:00",
            ],
            "intensity_g_per_kwh": [100, 200, 300],
            "observed_at": [
                "2026-10-24 09:55:00",
                "2026-10-24 09:00:00",
                "2026-10-24 08:59:00",
            ],
        })

    def test_recent_measurement_is_fresh(self):
        result = validate_timestamped_carbon(
            self.carbon,
            self.reference_time,
            max_age_minutes=60,
        )

        self.assertTrue(result.iloc[0]["is_fresh"])
        self.assertEqual(result.iloc[0]["age_minutes"], 5)

    def test_measurement_exactly_60_minutes_old_is_fresh(self):
        result = validate_timestamped_carbon(
            self.carbon,
            self.reference_time,
            max_age_minutes=60,
        )

        self.assertTrue(result.iloc[1]["is_fresh"])
        self.assertEqual(result.iloc[1]["age_minutes"], 60)

    def test_measurement_older_than_60_minutes_is_stale(self):
        result = validate_timestamped_carbon(
            self.carbon,
            self.reference_time,
            max_age_minutes=60,
        )

        self.assertFalse(result.iloc[2]["is_fresh"])
        self.assertEqual(result.iloc[2]["age_minutes"], 61)

    def test_future_observation_is_rejected(self):
        invalid = self.carbon.copy()
        invalid.loc[0, "observed_at"] = "2026-10-24 10:01:00"

        with self.assertRaises(ValueError):
            validate_timestamped_carbon(
                invalid,
                self.reference_time,
                max_age_minutes=60,
            )

    def test_invalid_timestamp_is_rejected(self):
        invalid = self.carbon.copy()
        invalid.loc[0, "timestamp"] = "not-a-date"

        with self.assertRaises(ValueError):
            validate_timestamped_carbon(
                invalid,
                self.reference_time,
                max_age_minutes=60,
            )

    def test_fresh_data_filter(self):
        validated = validate_timestamped_carbon(
            self.carbon,
            self.reference_time,
            max_age_minutes=60,
        )

        fresh = get_fresh_carbon_data(validated)

        self.assertEqual(len(fresh), 2)
        self.assertTrue(fresh["is_fresh"].all())
    
    def test_prepare_fresh_data_for_scheduler(self):
        validated = pd.DataFrame({
            "timestamp": pd.to_datetime([
                "2026-10-24 15:00:00",
            ]),
            "intensity_g_per_kwh": [150],
            "observed_at": pd.to_datetime([
                "2026-10-24 14:55:00",
            ]),
            "age_minutes": [5.0],
            "is_fresh": [True],
        })

        result = prepare_fresh_carbon_for_scheduler(validated)

        self.assertEqual(
            list(result.columns),
            ["hour", "carbon_intensity_g_per_kwh"],
        )
        self.assertEqual(result.iloc[0]["hour"], 15)
        self.assertEqual(
            result.iloc[0]["carbon_intensity_g_per_kwh"], 150
        )

    def test_prepare_fresh_data_rejects_empty_data(self):
        validated = pd.DataFrame({
            "timestamp": pd.to_datetime([
                "2026-10-24 14:00:00",
            ]),
            "intensity_g_per_kwh": [100],
            "observed_at": pd.to_datetime([
                "2026-10-24 12:00:00",
            ]),
            "age_minutes": [120.0],
            "is_fresh": [False],
        })

        with self.assertRaisesRegex(
            ValueError, "No fresh carbon measurements"
        ):
            prepare_fresh_carbon_for_scheduler(validated)
if __name__ == "__main__":
    unittest.main()



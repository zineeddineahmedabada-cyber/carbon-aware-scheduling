
import unittest

import pandas as pd
from src.scheduler import compare_strategies
from src.scheduler import generate_candidates


class TestScheduler(unittest.TestCase):
    
    def test_earliest_start_hour_is_respected(self):
        candidates = generate_candidates(
            carbon=self.carbon,
            power_kw=5,
            duration_hours=2,
            deadline_hour=14,
            earliest_start_hour=10,
        )

        self.assertFalse(candidates.empty)
        self.assertTrue(
            (candidates["start_hour"] >= 10).all()
        )

    def test_missing_hour_prevents_crossing_window(self):
        incomplete_carbon = pd.DataFrame({
            "hour": [8, 9, 11, 12],
            "carbon_intensity_g_per_kwh": [100, 200, 300, 400],
        })

        candidates = generate_candidates(
            carbon=incomplete_carbon,
            power_kw=5,
            duration_hours=3,
            deadline_hour=13,
            earliest_start_hour=8,
        )

        self.assertTrue(candidates.empty)

    def test_impossible_deadline_returns_no_candidates(self):
        candidates = generate_candidates(
            carbon=self.carbon,
            power_kw=5,
            duration_hours=3,
            deadline_hour=10,
            earliest_start_hour=8,
        )

        self.assertTrue(candidates.empty)

    def test_carbon_aware_is_not_worse_than_baseline(self):
        candidates = generate_candidates(
            carbon=self.carbon,
            power_kw=1,
            duration_hours=2,
            deadline_hour=14,
        )

        comparison = compare_strategies(candidates)

        self.assertLessEqual(
            comparison["optimized_emissions_g"],
            comparison["baseline_emissions_g"],
        )

        self.assertGreaterEqual(
            comparison["emissions_avoided_g"],
            0,
        )

    def test_comparison_rejects_empty_candidates(self):
        empty_candidates = pd.DataFrame(
            columns=["start_hour", "end_hour", "emissions_g"]
        )

        with self.assertRaises(ValueError):
            compare_strategies(empty_candidates)

    
    def test_no_schedule_before_deadline(self):
        candidates = generate_candidates(
            carbon=self.carbon,
            power_kw=1,
            duration_hours=3,
            deadline_hour=9,
        )

        self.assertTrue(candidates.empty)

    def test_missing_hour_is_not_used(self):
        incomplete_carbon = pd.DataFrame({
            "hour": [8, 9, 11, 12],
            "carbon_intensity_g_per_kwh": [100, 200, 50, 60],
        })

        candidates = generate_candidates(
            carbon=incomplete_carbon,
            power_kw=1,
            duration_hours=2,
            deadline_hour=14,
        )

        # No candidate should cross the missing hour 10
        for _, candidate in candidates.iterrows():
            self.assertFalse(
                candidate["start_hour"] == 9
                and candidate["end_hour"] == 11
            )

    def test_zero_duration_is_rejected(self):
        with self.assertRaises(ValueError):
            generate_candidates(
                carbon=self.carbon,
                power_kw=1,
                duration_hours=0,
                deadline_hour=14,
            )

    def setUp(self):
        self.carbon = pd.DataFrame({
            "hour": [8, 9, 10, 11, 12, 13, 14],
            "carbon_intensity_g_per_kwh": [
                100, 200, 300, 500, 50, 50, 100
            ],
        })

    def test_deadline_is_respected(self):
        candidates = generate_candidates(
            carbon=self.carbon,
            power_kw=1,
            duration_hours=2,
            deadline_hour=14,
        )

        self.assertFalse(candidates.empty)

        # Every candidate must finish by the deadline
        self.assertTrue(
            (candidates["end_hour"] <= 14).all()
        )

    def test_selects_minimum_emissions(self):
        candidates = generate_candidates(
            carbon=self.carbon,
            power_kw=1,
            duration_hours=2,
            deadline_hour=14,
        )

        best = candidates.loc[
            candidates["emissions_g"].idxmin()
        ]

        self.assertEqual(int(best["start_hour"]), 12)
        self.assertEqual(int(best["end_hour"]), 14)
        self.assertAlmostEqual(best["emissions_g"], 100)

        # The selected candidate must be the cheapest one
        self.assertEqual(
            best["emissions_g"],
            candidates["emissions_g"].min(),
        )


if __name__ == "__main__":
    unittest.main()

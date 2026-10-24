
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

DATA_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)


def generate_carbon_profile():
    """Create a synthetic 24-hour grid carbon-intensity profile."""
    hours = list(range(24))

    # Illustrative values in grams of CO2 per kWh.
    # These are not measurements from a real electricity grid.
    intensity = [
        420, 410, 400, 390, 380, 370,
        360, 350, 330, 300, 260, 220,
        190, 180, 200, 240, 300, 370,
        430, 460, 450, 440, 430, 420,
    ]

    return pd.DataFrame({
        "hour": hours,
        "carbon_intensity_g_per_kwh": intensity,
    })


def generate_workload():
    """Create a small synthetic workload."""
    tasks = [
        {
            "task_id": "T01",
            "release_hour": 0,
            "duration_hours": 2,
            "power_kw": 4.0,
            "deadline_hour": 8,
        },
        {
            "task_id": "T02",
            "release_hour": 2,
            "duration_hours": 3,
            "power_kw": 6.0,
            "deadline_hour": 12,
        },
        {
            "task_id": "T03",
            "release_hour": 5,
            "duration_hours": 1,
            "power_kw": 3.0,
            "deadline_hour": 10,
        },
        {
            "task_id": "T04",
            "release_hour": 8,
            "duration_hours": 2,
            "power_kw": 5.0,
            "deadline_hour": 18,
        },
        {
            "task_id": "T05",
            "release_hour": 10,
            "duration_hours": 3,
            "power_kw": 4.0,
            "deadline_hour": 22,
        },
    ]

    return pd.DataFrame(tasks)


def main():
    carbon = generate_carbon_profile()
    workload = generate_workload()

    carbon.to_csv(DATA_DIR / "carbon_intensity.csv", index=False)
    workload.to_csv(DATA_DIR / "workload.csv", index=False)

    print("Carbon intensity profile:")
    print(carbon.head())

    print("\nWorkload:")
    print(workload)

    plt.figure(figsize=(10, 5))
    plt.plot(
        carbon["hour"],
        carbon["carbon_intensity_g_per_kwh"],
        marker="o",
    )
    plt.xlabel("Hour of day")
    plt.ylabel("Carbon intensity (gCO2/kWh)")
    plt.title("Synthetic electricity-grid carbon intensity")
    plt.xticks(range(0, 24, 2))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "carbon_profile.png")
    plt.show()


if __name__ == "__main__":
    main()

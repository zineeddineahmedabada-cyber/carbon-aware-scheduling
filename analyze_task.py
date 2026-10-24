# Example task: 5 kW for 3 hours
power_kw = 5
duration_hours = 3

results = []

# Evaluate every feasible start time
for start_idx in range(len(carbon) - duration_hours + 1):
    window = carbon.iloc[start_idx:start_idx + duration_hours]

    emissions = sum(
        calculate_emissions(
            power_kw,
            1,
            float(row["carbon_intensity_g_per_kwh"]),
        )
        for _, row in window.iterrows()
    )

    results.append({
        "start_hour": int(window.iloc[0]["hour"]),
        "average_intensity": window[
            "carbon_intensity_g_per_kwh"
        ].mean(),
        "emissions_g": emissions,
    })

analysis = pd.DataFrame(results)

print(analysis.to_string(index=False))

best = analysis.loc[analysis["emissions_g"].idxmin()]

print("\nLowest-emission candidate:")
print(f"Start hour: {int(best['start_hour'])}:00")
print(f"Estimated emissions: {best['emissions_g']:.0f} gCO2")
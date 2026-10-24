
def calculate_emissions(power_kw, duration_hours, carbon_intensity):
    """
    Estimate task emissions in grams of CO2.

    power_kw: average power consumption in kilowatts
    duration_hours: execution duration in hours
    carbon_intensity: grams of CO2 per kWh
    """
    if power_kw < 0:
        raise ValueError("Power cannot be negative.")

    if duration_hours < 0:
        raise ValueError("Duration cannot be negative.")

    if carbon_intensity < 0:
        raise ValueError("Carbon intensity cannot be negative.")

    energy_kwh = power_kw * duration_hours
    emissions_g = energy_kwh * carbon_intensity

    return emissions_g

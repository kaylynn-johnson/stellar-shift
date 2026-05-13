import math as m


def calc_habitable_bound(teff, st_lum, bound):
    """calculates lower/upper bound using the Kopparapu model
        paper url: https://complexityexplorer.s3.amazonaws.com/supplemental_materials/6.3+Exoplanets/Kopparapu_2013_ApJ_765_131.pdf"""
    
    coeffs = {
        "lower": {
            "Seff0": 1.7763,
            "a": 1.4335e-4,
            "b": 3.3954e-9,
            "c": -7.6364e-12,
            "d": -1.1950e-15
        },
        "upper": {
            "Seff0": 0.3207,
            "a": 5.4417e-5,
            "b": 1.5275e-9,
            "c": -2.1709e-12,
            "d": -3.8282e-16
        }
    }

    T0 = teff - 5780 #[K]
    Seff = coeffs[bound]["Seff0"] + (coeffs[bound]["a"] * T0) + (coeffs[bound]["b"] * (T0 ** 2)) + (coeffs[bound]["c"] * (T0 ** 3)) + (coeffs[bound]["d"] * (T0 ** 4))

    d_hz = m.sqrt((10 ** st_lum) / Seff) #[AU]

    return d_hz


def calc_in_habitable_zone(planet_orbit_axis, stellar_eff_temp, stellar_lum):
    """determines if a planet is in the habitable zone"""

    # check for bounds of stellar temp that is valid for model
    if stellar_eff_temp <= 2600 or stellar_eff_temp >= 7200:
        # can't calculate habitable zone
        return None, None, None
    
    # run bound calculations for Kopparapu 2013 model
    lower_bound = calc_habitable_bound(stellar_eff_temp, stellar_lum, "lower")
    upper_bound = calc_habitable_bound(stellar_eff_temp, stellar_lum, "upper")

    if planet_orbit_axis >= lower_bound and planet_orbit_axis <= upper_bound:
        # in the habitable zone
        return 1, lower_bound, upper_bound
    
    # not in habitable zone
    return 0, lower_bound, upper_bound


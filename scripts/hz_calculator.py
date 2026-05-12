


def calc_in_habitable_zone(equil_temp):
    """determines if a planet is in the habitable zone"""

    # preliminary calculation is that equilibrium temp [K] is between (180, 310)
    if equil_temp > 180 and equil_temp < 310:
        # in HZ
        return 1
    # not in HZ
    return 0
import requests
import numpy as np
import re

# JPL Horizons API endpoint (correct URL)
BASE_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"

# System Configurations
SYSTEMS = {
    "Solar System": {
        "center": "500@0",  # Solar System Barycenter
        "bodies": [
            ("10", 1.98847e30, "Sun", (255, 204, 0)),
            ("199", 3.3011e23, "Mercury", (165, 165, 165)),
            ("299", 4.8675e24, "Venus", (227, 186, 142)),
            ("399", 5.97237e24, "Earth", (40, 122, 255)),
            ("499", 6.4171e23, "Mars", (255, 107, 60)),
            ("599", 1.8982e27, "Jupiter", (216, 178, 147)),
            ("699", 5.6834e26, "Saturn", (225, 198, 110)),
            ("799", 8.6810e25, "Uranus", (175, 238, 238)),
            ("899", 1.02413e26, "Neptune", (75, 112, 221)),
        ]
    },
    "Jovian System": {
        "center": "500@599",  # Jupiter Center
        "bodies": [
            ("599", 1.89822e27, "Jupiter", (216, 178, 147)),
            ("501", 8.9319e22, "Io", (249, 249, 131)),
            ("502", 4.800e22, "Europa", (191, 192, 192)),
            ("503", 1.4819e23, "Ganymede", (147, 125, 108)),
            ("504", 1.0759e23, "Callisto", (110, 103, 89)),
        ]
    },
    "Saturnian System": {
        "center": "500@699",  # Saturn Center
        "bodies": [
            ("699", 5.6834e26, "Saturn", (225, 198, 110)),
            ("606", 1.3452e23, "Titan", (238, 194, 70)),
            ("605", 2.306e21, "Rhea", (220, 220, 220)),
            ("608", 1.805e21, "Iapetus", (180, 180, 180)),
            ("604", 1.095e21, "Dione", (160, 160, 160)),
            ("603", 6.174e20, "Tethys", (140, 140, 140)),
        ]
    },
    "Earth-Moon": {
        "center": "500@399",  # Earth Center
        "bodies": [
            ("399", 5.97237e24, "Earth", (40, 122, 255)),
            ("301", 7.342e22, "Moon", (200, 200, 200)),
        ]
    },
    "Uranian System": {
        "center": "500@799",  # Uranus Center
        "bodies": [
            ("799", 8.6810e25, "Uranus", (175, 238, 238)),
            ("703", 3.527e21, "Titania", (210, 210, 210)),
            ("704", 3.014e21, "Oberon", (190, 190, 190)),
            ("702", 1.172e21, "Umbriel", (150, 150, 150)),
            ("701", 1.353e21, "Ariel", (230, 230, 230)),
        ]
    },
    "Neptunian System": {
        "center": "500@899",  # Neptune Center
        "bodies": [
            ("899", 1.02413e26, "Neptune", (75, 112, 221)),
            ("801", 2.14e22, "Triton", (210, 255, 210)),
        ]
    },
    "Extended Solar System": {
        "center": "500@0",
        "bodies": [
            ("10", 1.98847e30, "Sun", (255, 204, 0)),
            ("199", 3.3011e23, "Mercury", (165, 165, 165)),
            ("299", 4.8675e24, "Venus", (227, 186, 142)),
            ("399", 5.97237e24, "Earth", (40, 122, 255)),
            ("499", 6.4171e23, "Mars", (255, 107, 60)),
            ("1;", 9.393e20, "Ceres", (200, 200, 200)),
            ("4;", 2.59e20, "Vesta", (180, 180, 180)),
            ("599", 1.8982e27, "Jupiter", (216, 178, 147)),
            ("699", 5.6834e26, "Saturn", (225, 198, 110)),
            ("799", 8.6810e25, "Uranus", (175, 238, 238)),
            ("899", 1.02413e26, "Neptune", (75, 112, 221)),
            ("999", 1.303e22, "Pluto", (255, 230, 200)),
            ("920136199", 1.66e22, "Eris", (230, 230, 230)),
            ("920136108", 4.01e21, "Haumea", (240, 240, 240)),
            ("136472;", 3.1e21, "Makemake", (255, 180, 150)),
        ]
    },
    "Pluto System": {
        "center": "500@999",
        "bodies": [
            ("999", 1.303e22, "Pluto", (255, 230, 200)),
            ("901", 1.586e21, "Charon", (150, 150, 150)),
        ]
    },
    "Mars System": {
        "center": "500@499",
        "bodies": [
            ("499", 6.4171e23, "Mars", (255, 107, 60)),
            ("401", 1.066e16, "Phobos", (140, 130, 120)),
            ("402", 1.476e15, "Deimos", (160, 150, 140)),
        ]
    },
    "TRAPPIST-1": {
        "static": True,
        "G_real": 6.67430e-20,
        "bodies": [
            # [mass, [x, y, z], [vx, vy, vz], name, color]
            # Units: kg, km, km/s
            [1.78e29, [0, 0, 0], [0, 0, 0], "TRAPPIST-1", (255, 100, 50)],
            [8.18e24, [1.65e6, 0, 0], [0, 85, 0], "b", (200, 150, 100)],
            [7.82e24, [2.25e6, 0, 0], [0, 72, 0], "c", (210, 180, 150)],
            [2.33e24, [3.30e6, 0, 0], [0, 60, 0], "d", (180, 180, 180)],
            [4.12e24, [4.34e6, 0, 0], [0, 52, 0], "e", (100, 150, 255)],
            [6.21e24, [5.68e6, 0, 0], [0, 45, 0], "f", (150, 150, 200)],
            [7.88e24, [7.03e6, 0, 0], [0, 41, 0], "g", (120, 120, 180)],
            [1.97e24, [9.27e6, 0, 0], [0, 36, 0], "h", (160, 160, 160)],
        ]
    }
}

def fetch_state(body_id, center="'500@0'"):
    params = {
        "format": "json",
        "COMMAND": f"'{body_id}'",
        "EPHEM_TYPE": "VECTORS",
        "CENTER": center,
        "START_TIME": "2026-02-01",
        "STOP_TIME": "2026-02-02",
        "STEP_SIZE": "1d",
        "OUT_UNITS": "KM-S",
        "VEC_TABLE": "2",
        "VEC_LABELS": "NO"
    }

    r = requests.get(BASE_URL, params=params)
    r.raise_for_status()
    data = r.json()

    result_text = data["result"]
    match = re.search(r'\$\$SOE(.*?)\$\$EOE', result_text, re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse vector data for body {body_id}")
    
    data_block = match.group(1).strip()
    numbers = re.findall(r'[+-]?\d+\.\d+E[+-]\d+', data_block)
    
    x, y, z = float(numbers[0]), float(numbers[1]), float(numbers[2])
    vx, vy, vz = float(numbers[3]), float(numbers[4]), float(numbers[5])
    
    return np.array([x, y, z]), np.array([vx, vy, vz])

def get_system_data(system_name="Solar System"):
    """Fetch orbital data for a specific system and return formatted state vectors."""
    if system_name not in SYSTEMS:
        raise ValueError(f"Unknown system: {system_name}")
    
    config = SYSTEMS[system_name]
    
    positions = []
    velocities = []
    masses = []
    names = []
    colors = []
    G_real = 6.67430e-20  # km^3 kg^-1 s^-2

    if config.get("static"):
        print(f"Loading static system: {system_name}...")
        for b_data in config["bodies"]:
            masses.append(b_data[0])
            positions.append(np.array(b_data[1]))
            velocities.append(np.array(b_data[2]))
            names.append(b_data[3])
            colors.append(b_data[4])
        G_real = config.get("G_real", G_real)
    else:
        print(f"Fetching data for {system_name}...")
        center_id = f"'{config['center']}'"
        for body_id, mass, name, color in config["bodies"]:
            pos, vel = fetch_state(body_id, center=center_id)
            positions.append(pos)
            velocities.append(vel)
            masses.append(mass)
            names.append(name)
            colors.append(color)
        print("Data fetched successfully!")

    positions = np.array(positions)
    masses = np.array(masses)
    velocities = np.array(velocities)

    # --- Scaling Logic ---
    # Center on the primary body
    primary_pos = positions[0].copy()
    positions -= primary_pos

    # Scale positions for visualization
    max_dist = np.linalg.norm(positions, axis=1).max()
    if max_dist == 0: max_dist = 1
    scaled_positions = 1000 * (positions / max_dist)

    # Scale masses so the largest is 1,000,000
    max_mass = masses.max()
    scaled_masses = 1000000 * (masses / max_mass)

    # Calculate Physically Consistent G
    s_x = 1000 / max_dist
    s_m = 1000000 / max_mass
    sim_G = G_real * (s_x / s_m)

    system_data = []
    for i in range(len(masses)):
        system_data.append([
            float(scaled_masses[i]),
            [float(scaled_positions[i][0]), float(velocities[i][0])],
            [float(scaled_positions[i][1]), float(velocities[i][1])],
            [float(scaled_positions[i][2]), float(velocities[i][2])],
            [],  # Empty trail
            names[i],
            colors[i]
        ])

    return {"state": system_data, "G": sim_G}

if __name__ == "__main__":
    from pprint import pprint
    for sys_name in SYSTEMS.keys():
        data = get_system_data(sys_name)
        print(f"\nSystem: {sys_name}")
        print(f"Calculated G: {data['G']}")
        pprint(data['state'][0]) # Just print the primary body for brevity


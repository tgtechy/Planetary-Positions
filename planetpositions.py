import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import math
import numpy as np

# author - tgtechy

# Page configuration
st.set_page_config(page_title="Solar System Plotter", layout="wide")

# Keplerian elements for planetary positions (J2000.0 epoch)
PLANETS_DATA = {
    # Name: (a [AU], e, L [deg], w_bar [deg])
    'Mercury': (0.3871, 0.2056, 252.25, 77.46),
    'Venus': (0.7233, 0.0068, 181.98, 131.57),
    'Earth': (1.0000, 0.0167, 100.46, 102.93),
    'Mars': (1.5237, 0.0934, 355.43, 336.06),
    'Jupiter': (5.2026, 0.0485, 34.35, 14.33),
    'Saturn': (9.5549, 0.0555, 50.07, 92.43),
    'Uranus': (19.2184, 0.0463, 314.05, 173.00),
    'Neptune': (30.1104, 0.0095, 304.34, 48.12),
    'Pluto': (39.4817, 0.2488, 238.93, 224.07),
}

def compute_planetary_positions(target_datetime):
    """
    Calculates approximate heliocentric coordinates (x, y) in AU for planets.
    Uses Keplerian elements for J2000.0.
    """
    # Elements: a (AU), e, L (Mean Longitude deg), w_bar (Longitude of Perihelion deg)
    j2000 = datetime.datetime(2000, 1, 1, 12, 0, 0)
    d = (target_datetime - j2000).total_seconds() / 86400.0  # Convert to days with decimal for time
    positions = {}

    for name, (a, e, L_deg, w_bar_deg) in PLANETS_DATA.items():
        n = 0.9856076686 / (a ** 1.5)  # Daily motion
        L = L_deg + n * d              # Mean Longitude
        M = np.radians(L - w_bar_deg)  # Mean Anomaly
        
        # Solve Kepler Equation: M = E - e*sin(E) using Newton-Raphson
        E = M
        for _ in range(10):
            dE = (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
            E -= dE
            if abs(dE) < 1e-6:
                break
        
        # Coordinates in orbital plane -> Rotate to Ecliptic
        x_prime = a * (np.cos(E) - e)
        y_prime = a * np.sqrt(1 - e**2) * np.sin(E)
        w_rad = np.radians(w_bar_deg)
        
        x = x_prime * np.cos(w_rad) - y_prime * np.sin(w_rad)
        y = x_prime * np.sin(w_rad) + y_prime * np.cos(w_rad)
        positions[name] = (x, y)
        
    return positions

def orbital_elements_to_cartesian(a, e, i, Omega, omega, nu):
    """
    Convert orbital elements to Cartesian coordinates.
    a: semi-major axis (AU)
    e: eccentricity
    i: inclination (radians)
    Omega: longitude of ascending node (radians)
    omega: argument of perihelion (radians)
    nu: true anomaly (radians)
    Returns (x, y, z) in AU
    """
    r = a * (1 - e**2) / (1 + e * math.cos(nu))
    
    x_orb = r * math.cos(nu)
    y_orb = r * math.sin(nu)
    z_orb = 0
    
    # Rotation 1: argument of perihelion
    x1 = x_orb * math.cos(omega) - y_orb * math.sin(omega)
    y1 = x_orb * math.sin(omega) + y_orb * math.cos(omega)
    z1 = z_orb
    
    # Rotation 2: inclination
    x2 = x1
    y2 = y1 * math.cos(i) - z1 * math.sin(i)
    z2 = y1 * math.sin(i) + z1 * math.cos(i)
    
    # Rotation 3: longitude of ascending node
    x = x2 * math.cos(Omega) - y2 * math.sin(Omega)
    y = x2 * math.sin(Omega) + y2 * math.cos(Omega)
    z = z2
    
    return x, y, z

def get_planet_positions(date_obj):
    """
    Calculates the heliocentric (Sun-centered) coordinates of planets
    for a specific date using simplified Keplerian elements.
    """
    data = []
    
    # Add the Sun
    data.append({
        'Planet': 'Sun',
        'x': 0, 'y': 0, 'z': 0,
        'r': 0, 'theta': 0,
        'Diameter': 1391000,
        'Color': 'gold'
    })
    
    # Calculate positions for each planet using simplified method
    positions = compute_planetary_positions(date_obj)
    
    for name, (x, y) in positions.items():
        r = math.sqrt(x**2 + y**2)
        theta = math.degrees(math.atan2(y, x))
        
        data.append({
            'Planet': name,
            'x': x,
            'y': y,
            'z': 0,
            'r': r,
            'theta': theta,
            'Diameter': planet_diameters[name],
            'Color': name
        })
    
    return pd.DataFrame(data)

# Planetary diameters in kilometers
planet_diameters = {
    'Sun': 1391000,
    'Mercury': 3871,
    'Venus': 12104,
    'Earth': 12742,
    'Mars': 6779,
    'Jupiter': 139820,
    'Saturn': 116460,
    'Uranus': 50724,
    'Neptune': 49244,
    'Pluto': 2376
}



def compute_radial_tick_step(max_radius):
    """Choose a radial tick step that keeps grid lines sparse."""
    if max_radius <= 0:
        return 1
    rough_step = max_radius / 6
    magnitude = 10 ** math.floor(math.log10(rough_step))
    for factor in (1, 2, 5, 10):
        step = factor * magnitude
        if step >= rough_step:
            return step
    return magnitude * 10

def calculate_birthday_facts(birth_datetime):
    """Calculate various birthday-related facts and statistics."""
    today_datetime = datetime.datetime.now()
    today_date = today_datetime.date()
    birth_date = birth_datetime.date()
    
    facts = {}
    
    # Day of week born
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    facts['Day of Week Born'] = day_names[birth_date.weekday()]
    
    # Age calculations
    age_timedelta = today_datetime - birth_datetime
    age_days = age_timedelta.days
    age_weeks = age_days // 7
    age_seconds = int(age_timedelta.total_seconds())
    
    # Calculate years and months properly
    years = today_date.year - birth_date.year
    months = today_date.month - birth_date.month
    if today_date.day < birth_date.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    
    facts['Age (Years)'] = f"{years} years, {months} months"
    facts['Age (Days)'] = f"{age_days:,}"
    facts['Age (Weeks)'] = f"{age_weeks:,}"
    facts['Age (Seconds)'] = f"{age_seconds:,}"
    
    # Zodiac sign
    zodiac_signs = [
        ('Capricorn', (12, 22), (1, 19)),
        ('Aquarius', (1, 20), (2, 18)),
        ('Pisces', (2, 19), (3, 20)),
        ('Aries', (3, 21), (4, 19)),
        ('Taurus', (4, 20), (5, 20)),
        ('Gemini', (5, 21), (6, 20)),
        ('Cancer', (6, 21), (7, 22)),
        ('Leo', (7, 23), (8, 22)),
        ('Virgo', (8, 23), (9, 22)),
        ('Libra', (9, 23), (10, 22)),
        ('Scorpio', (10, 23), (11, 21)),
        ('Sagittarius', (11, 22), (12, 21)),
    ]
    
    birth_zodiac = None
    for sign, start, end in zodiac_signs:
        start_month, start_day = start
        end_month, end_day = end
        if start_month == end_month:
            if birth_date.month == start_month and start_day <= birth_date.day <= end_day:
                birth_zodiac = sign
                break
        else:
            if (birth_date.month == start_month and birth_date.day >= start_day) or \
               (birth_date.month == end_month and birth_date.day <= end_day):
                birth_zodiac = sign
                break
    
    facts['Zodiac Sign'] = birth_zodiac or 'Unknown'
    leap_days = 0
    for year in range(birth_date.year, today_date.year + 1):
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            leap_date = datetime.date(year, 2, 29)
            if birth_date <= leap_date <= today_date:
                leap_days += 1
    facts['Leap Days Lived'] = str(leap_days)
    
    # Half-birthday
    try:
        half_bday = birth_date.replace(month=birth_date.month + 6 if birth_date.month <= 6 else birth_date.month - 6)
    except ValueError:
        half_bday = birth_date.replace(month=birth_date.month + 6 if birth_date.month <= 6 else birth_date.month - 6, day=28)
    if half_bday < datetime.date.today():
        half_bday = half_bday.replace(year=half_bday.year + 1)
    facts['Next Half-Birthday'] = str(half_bday)
    
    # Golden birthday (age matches day of birth)
    golden_date = birth_date.replace(year=birth_date.year + birth_date.day)
    if golden_date < datetime.date.today():
        golden_date = golden_date.replace(year=golden_date.year + 1)
    if golden_date.month == birth_date.month and golden_date.day == birth_date.day:
        facts['Golden Birthday (Age=Day)'] = str(golden_date)
    else:
        facts['Golden Birthday (Age=Day)'] = f"Age {birth_date.day} on {birth_date.strftime('%B %d, %Y').split(',')[0]}"
    
    # Birth season
    month = birth_date.month
    if month in [12, 1, 2]:
        season_nh = "Winter"
        season_sh = "Summer"
    elif month in [3, 4, 5]:
        season_nh = "Spring"
        season_sh = "Autumn"
    elif month in [6, 7, 8]:
        season_nh = "Summer"
        season_sh = "Winter"
    else:
        season_nh = "Autumn"
        season_sh = "Spring"
    facts['Birth Season (Northern)'] = season_nh
    facts['Birth Season (Southern)'] = season_sh
    
    # Chinese zodiac
    chinese_animals = ['Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake', 'Horse', 'Goat', 'Monkey', 'Rooster', 'Dog', 'Pig']
    chinese_elements = ['Wood', 'Fire', 'Earth', 'Metal', 'Water']
    zodiac_index = (birth_date.year - 1900) % 12
    element_index = ((birth_date.year - 1900) // 12) % 5
    facts['Chinese Zodiac'] = f"{chinese_animals[zodiac_index]} ({chinese_elements[element_index]})"
    
    # Life elapsed as percentage of century
    pct_century = (age_days / 36525) * 100
    facts['Life Elapsed (% of Century)'] = f"{pct_century:.2f}%"
    
    # Birthstone and birth flower
    birthstones = {
        1: 'Garnet', 2: 'Amethyst', 3: 'Aquamarine', 4: 'Diamond',
        5: 'Emerald', 6: 'Pearl', 7: 'Ruby', 8: 'Peridot',
        9: 'Sapphire', 10: 'Opal', 11: 'Topaz', 12: 'Turquoise'
    }
    birth_flowers = {
        1: 'Carnation', 2: 'Violet', 3: 'Daffodil', 4: 'Daisy',
        5: 'Lily of the Valley', 6: 'Rose', 7: 'Larkspur', 8: 'Gladiolus',
        9: 'Aster', 10: 'Calendula', 11: 'Chrysanthemum', 12: 'Poinsettia'
    }
    facts['Birthstone'] = birthstones.get(birth_date.month, 'Unknown')
    facts['Birth Flower'] = birth_flowers.get(birth_date.month, 'Unknown')
    
    # Life path number (numerology)
    date_sum = sum(int(d) for d in birth_date.strftime('%Y%m%d'))
    while date_sum >= 10:
        date_sum = sum(int(d) for d in str(date_sum))
    facts['Life Path Number'] = str(date_sum)
    
    # Julian date (approximate)
    a = (14 - birth_date.month) // 12
    y = birth_date.year + 4800 - a
    m = birth_date.month + 12 * a - 3
    jdn = birth_date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    facts['Julian Day Number'] = str(jdn)
    
    # Age in different bases
    facts['Age in Binary'] = bin(years)[2:]
    facts['Age in Hexadecimal'] = hex(years)[2:].upper()
    facts['Age in Roman Numerals'] = int_to_roman(years)
    facts['Age in Base-12'] = int_to_base12(years)
    
    # Upcoming milestones
    days_to_10k = 10000 - age_days
    days_to_20k = 20000 - age_days
    if days_to_10k > 0:
        date_10k = datetime.date.today() + datetime.timedelta(days=days_to_10k)
        facts['10,000 Days Old On'] = str(date_10k)
    if days_to_20k > 0:
        date_20k = datetime.date.today() + datetime.timedelta(days=days_to_20k)
        facts['20,000 Days Old On'] = str(date_20k)
    
    # Seconds to 1 billion
    seconds_needed = 1000000000 - age_seconds
    if seconds_needed > 0:
        date_1b_sec = datetime.datetime.now() + datetime.timedelta(seconds=seconds_needed)
        facts['1 Billion Seconds Old On'] = date_1b_sec.strftime('%Y-%m-%d %H:%M:%S')
    
    # Next palindrome age
    for test_age in range(years + 1, 100):
        if str(test_age) == str(test_age)[::-1]:
            next_palindrome_year = birth_date.year + test_age
            facts['Next Palindrome Age'] = f"{test_age} (in year {next_palindrome_year})"
            break
    
    # Next square age
    sqrt_age = int(math.sqrt(years))
    for test_age in range(sqrt_age, 20):
        if test_age * test_age > years:
            next_square = test_age * test_age
            next_square_year = birth_date.year + next_square
            facts['Next Square Age'] = f"{next_square} ({test_age}², in year {next_square_year})"
            break
    
    # Next prime age
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    for test_age in range(years + 1, years + 50):
        if is_prime(test_age):
            next_prime_year = birth_date.year + test_age
            facts['Next Prime Age'] = f"{test_age} (in year {next_prime_year})"
            break
    
    # Saturn return (approximately age 29.5, 59, 88)
    saturn_returns = []
    for return_num, age_approx in enumerate([29.5, 59, 88.5], 1):
        return_year = birth_date.year + int(age_approx)
        if return_year <= today_date.year:
            continue
        saturn_returns.append(f"Return {return_num}: ~age {age_approx} (year {return_year})")
    if saturn_returns:
        facts['Saturn Return'] = ' | '.join(saturn_returns)
    
    # Birthday paradox probability
    group_size = 23
    prob = 1 - math.factorial(365) / (math.factorial(365 - group_size) * (365 ** group_size))
    facts['Birthday Paradox (23 people)'] = f"{prob*100:.1f}% chance of match"
    
    return facts

def int_to_roman(num):
    """Convert integer to Roman numerals."""
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syms[i]
            num -= val[i]
        i += 1
    return roman_num if roman_num else '0'

def int_to_base12(num):
    """Convert integer to base-12 (duodecimal)."""
    if num == 0:
        return '0'
    digits = '0123456789AB'
    result = ''
    while num > 0:
        result = digits[num % 12] + result
        num //= 12
    return result

def load_planet_image(planet_name):
    """Load a planet image file from the planet_images folder if it exists."""
    import os
    # Try PNG first, then GIF as fallback (use lowercase filenames)
    planet_name_lower = planet_name.lower()
    for ext in ['.png', '.gif']:
        image_path = f"planet_images/{planet_name_lower}{ext}"
        if os.path.exists(image_path):
            return image_path
    return None

def image_to_base64(image_path):
    """Convert image to base64 for embedding in Plotly."""
    import base64
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def polar_to_cartesian(r, theta_deg):
    """Convert polar coordinates to Cartesian coordinates."""
    import math
    theta_rad = math.radians(theta_deg)
    x = r * math.cos(theta_rad)
    y = r * math.sin(theta_rad)
    return x, y

def main():
    st.title("🪐 Planetary Positions")
    st.markdown("""
    Select a date below to see the heliocentric (Sun-centered) positions of the planets.
    The distances are measured in [**Astronomical Units (AU)**](https://en.wikipedia.org/wiki/Astronomical_unit).""")

    # 1. User Input
    col1, col2 = st.columns([1, 3])
    with col1:
        # Initialize default date value
        if "selected_date_value" not in st.session_state:
            st.session_state.selected_date_value = datetime.date(2000, 1, 1)
        
        selected_date = st.date_input(
            "Select Date (YYYY/MM/DD)",
            value=st.session_state.selected_date_value,
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date(2100, 12, 31)
        )
        
        # Update session state when date changes
        if selected_date != st.session_state.selected_date_value:
            st.session_state.selected_date_value = selected_date
        
        # Today button
        if st.button("Today", width='stretch'):
            st.session_state.selected_date_value = datetime.date.today()
            st.rerun()
        
        # Time input
        st.markdown("**Select Time**")
        time_col1, time_col2, time_col3 = st.columns(3)
        with time_col1:
            hour = st.number_input("Hour", min_value=0, max_value=23, value=12, step=1)
        with time_col2:
            minute = st.number_input("Minute", min_value=0, max_value=59, value=0, step=1)
        with time_col3:
            second = st.number_input("Second", min_value=0, max_value=59, value=0, step=1)
        
        selected_datetime = datetime.datetime(selected_date.year, selected_date.month, selected_date.day, hour, minute, second)
        
        show_perimeter = st.checkbox("Project to Perimeter (Angular Position Only)", key="show_perimeter")
        show_orbits = st.checkbox("Show Orbit Lines", value=True, key="show_orbits")
        show_zodiac_radials = st.checkbox("Show Zodiac Sector Lines", value=False, key="show_zodiac_radials")
        show_radial_scale = st.checkbox("Show Radial Scale", value=True, key="show_radial_scale")
        
        # Disable logarithmic scale when projecting to perimeter
        if show_perimeter:
            # Force off if previously enabled
            if "use_log_radius" in st.session_state and st.session_state.get("use_log_radius"):
                st.session_state["use_log_radius"] = False
            use_log_radius = st.checkbox(
                "Logarithmic Radial Scale",
                value=False,
                disabled=True,
                help="Disabled when 'Project to Perimeter' is selected",
                key="use_log_radius",
            )
        else:
            use_log_radius = st.checkbox(
                "Logarithmic Radial Scale",
                value=True,
                key="use_log_radius",
            )
        
        # Initialize planet mode in session state
        if "planet_mode" not in st.session_state:
            st.session_state.planet_mode = "Markers"
        
        # Planet visualization mode (mutually exclusive)
        planet_mode = st.radio(
            "Planet Display Mode",
            ["Markers", "Glyphs", "Letters", "Images"],
            horizontal=True,
            key="planet_mode"
        )
        use_glyphs = (planet_mode == "Glyphs")
        use_letters = (planet_mode == "Letters")
        use_planet_images = (planet_mode == "Images")
        
    # 2. Calculate Data
    with st.spinner("Calculating planetary orbits..."):
        df = get_planet_positions(selected_datetime)

    # Radial scaling (linear vs log); keep original AU values for hover
    df['r_linear'] = df['r']
    
    # Calculate maximum and minimum orbital radius from orbital paths (needed before perimeter projection)
    max_orbital_radius = 0
    min_orbital_radius = float('inf')
    for planet_name in df[df['Planet'] != 'Sun']['Planet'].unique():
        planet_data = PLANETS_DATA.get(planet_name)
        if planet_data:
            a, e, L_deg, w_bar_deg = planet_data
            # Maximum distance at aphelion
            max_r_orbit = a * (1 + e)
            max_orbital_radius = max(max_orbital_radius, max_r_orbit)
            # Minimum distance at perihelion
            min_r_orbit = a * (1 - e)
            min_orbital_radius = min(min_orbital_radius, min_r_orbit)
    
    if min_orbital_radius == float('inf'):
        min_orbital_radius = 0.1
    
    # Apply radial scaling before perimeter projection
    log_offset = 0  # Store offset for consistent use across log scaling
    if use_log_radius:
        # Create r_plot with log scale for planets, but keep Sun at 0
        # Calculate offset based on minimum orbital radius to ensure all orbit points are positive after log transform
        min_log = math.log10(min_orbital_radius)
        log_offset = abs(min_log) if min_log < 0 else 0
        df['r_plot'] = df.apply(lambda row: 0 if row['Planet'] == 'Sun' else math.log10(max(row['r'], 1e-6)) + log_offset, axis=1)
    else:
        df['r_plot'] = df['r']
    
    # Precompute max radius for arc sizing
    max_radius = df[df['Planet'] != 'Sun']['r_plot'].max()
    
    # Calculate arc_radius based on scale mode
    if use_log_radius:
        min_radius = df[df['Planet'] != 'Sun']['r_plot'].min()
        span = max_radius - min_radius if max_radius != min_radius else max_radius or 1
        arc_radius = max_radius + 0.3 * span
    else:
        # For linear scale, use the maximum orbital radius to position zodiac bands at perimeter
        arc_radius = max_orbital_radius * 1.15

    # Now apply perimeter projection after calculating arc_radius
    if show_perimeter:
        # Position planets closer to the perimeter when projecting to perimeter
        perimeter_radius = arc_radius * 0.80  # Move planets to 80% of arc_radius distance from center
        df.loc[df['Planet'] != 'Sun', 'r_plot'] = perimeter_radius

    # Build AU-based tick labels for log scale
    if use_log_radius:
        planet_r_values_linear = df[df['Planet'] != 'Sun']['r_linear']
        if len(planet_r_values_linear) > 0:
            min_val = planet_r_values_linear.min()
            max_val = planet_r_values_linear.max()
            start_decade = int(math.floor(math.log10(max(min_val, 1e-6))))
            end_decade = int(math.ceil(math.log10(max_val)))
            candidates = []
            for dec in range(start_decade, end_decade + 1):
                for factor in (1, 2, 5):
                    val = factor * (10 ** dec)
                    if min_val * 0.9 <= val <= max_val * 1.1:
                        candidates.append(val)
            candidates = sorted(set(candidates))
            radial_tickvals = [math.log10(v) + log_offset for v in candidates]
            radial_ticktext = [f"{v:g}" for v in candidates]
        else:
            radial_tickvals = []
            radial_ticktext = []
        radial_tick_step = None
    else:
        radial_tickvals = None
        radial_ticktext = None
        radial_tick_step = compute_radial_tick_step(max_orbital_radius)

    # Planet glyphs (astronomical symbols)
    planet_glyphs = {
        'Sun': '☉',
        'Mercury': '☿',
        'Venus': '♀',
        'Earth': '⊕',
        'Mars': '♂',
        'Jupiter': '♃',
        'Saturn': '♄',
        'Uranus': '♅',
        'Neptune': '♆',
        'Pluto': '♇'
    }

    # Planet letters (single-letter abbreviations)
    planet_letters = {
        'Sun': '*',
        'Mercury': 'M',
        'Venus': 'V',
        'Earth': 'E',
        'Mars': 'R',
        'Jupiter': 'J',
        'Saturn': 'S',
        'Uranus': 'U',
        'Neptune': 'N',
        'Pluto': 'P'
    }

    # Planet colors
    planet_colors = {
        'Sun': 'gold',
        'Mercury': 'gray',
        'Venus': '#FFC649',
        'Earth': '#4169E1',
        'Mars': '#E27B58',
        'Jupiter': '#C88B3A',
        'Saturn': '#FAD5A5',
        'Uranus': '#4FD0E7',
        'Neptune': '#4166F5',
        'Pluto': '#B0B0B0'
    }

    # Visualization
    with col2:
        # Create Polar Scatter Plot
        if use_planet_images:
            # Use Cartesian plot for better image placement
            fig = go.Figure(layout=go.Layout(template='plotly_dark'))
            
            # Convert all polar data to Cartesian
            df['x_cart'] = df.apply(lambda row: polar_to_cartesian(row['r_plot'], row['theta'])[0], axis=1)
            df['y_cart'] = df.apply(lambda row: polar_to_cartesian(row['r_plot'], row['theta'])[1], axis=1)
            
            # Draw zodiac boundary circles and labels in Cartesian
            zodiac_signs = [
                "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
            ]
            zodiac_glyphs = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
            colors = [
                'rgba(255, 80, 80, 0.7)', 'rgba(255, 140, 60, 0.7)', 'rgba(255, 200, 50, 0.7)',
                'rgba(100, 220, 100, 0.7)', 'rgba(80, 200, 200, 0.7)', 'rgba(100, 150, 255, 0.7)',
                'rgba(180, 100, 220, 0.7)', 'rgba(220, 100, 180, 0.7)', 'rgba(255, 120, 100, 0.7)',
                'rgba(255, 180, 80, 0.7)', 'rgba(150, 220, 150, 0.7)', 'rgba(120, 180, 255, 0.7)'
            ]
            
            # Draw zodiac arcs as filled wedges in Cartesian coordinates
            arc_width = max_radius * 0.08 if max_radius > 0 else 0.5
            arc_inner = arc_radius - arc_width
            
            # Add large black background circle first
            circle_angles = np.linspace(0, 360, 100)
            bg_radius = arc_radius * 1.5
            x_bg = [bg_radius * np.cos(np.radians(a)) for a in circle_angles]
            y_bg = [bg_radius * np.sin(np.radians(a)) for a in circle_angles]
            fig.add_trace(
                go.Scatter(
                    x=x_bg,
                    y=y_bg,
                    fill='toself',
                    fillcolor='black',
                    line=dict(width=0),
                    hoverinfo='skip',
                    showlegend=False,
                    mode='lines'
                )
            )
            
            # Draw zodiac wedge bands in images mode (single band),
            # polar arcs are disabled elsewhere to avoid duplicates
            for i in range(12):
                angle_start = i * 30
                angle_end = (i + 1) * 30
                
                # Create arc points in Cartesian
                num_points = 50
                angles = np.linspace(angle_start, angle_end, num_points)
                
                # Outer arc
                x_outer = [arc_radius * np.cos(np.radians(a)) for a in angles]
                y_outer = [arc_radius * np.sin(np.radians(a)) for a in angles]
                
                # Inner arc (reversed)
                x_inner = [arc_inner * np.cos(np.radians(a)) for a in reversed(angles)]
                y_inner = [arc_inner * np.sin(np.radians(a)) for a in reversed(angles)]
                
                # Combine for closed shape
                x_all = x_outer + x_inner
                y_all = y_outer + y_inner
                
                fig.add_trace(
                    go.Scatter(
                        x=x_all,
                        y=y_all,
                        fill='toself',
                        fillcolor=colors[i],
                        line=dict(color='black', width=2),
                        hoverinfo='skip',
                        showlegend=False,
                        mode='lines'
                    )
                )
            
            # Add radial lines for zodiac sector boundaries (Cartesian mode)
            if show_zodiac_radials:
                for i in range(12):
                    angle = i * 30  # Zodiac sector boundaries at 0°, 30°, 60°, etc.
                    x_line = [0, arc_radius * np.cos(np.radians(angle))]
                    y_line = [0, arc_radius * np.sin(np.radians(angle))]
                    fig.add_trace(
                        go.Scatter(
                            x=x_line,
                            y=y_line,
                            mode='lines',
                            line=dict(color='rgba(200, 200, 200, 0.5)', width=1),
                            hoverinfo='skip',
                            showlegend=False
                        )
                    )
            
            # Add planets with images
            layout_images = []
            for _, row in df.iterrows():
                planet_name = row['Planet']
                image_path = load_planet_image(planet_name)
                
                if image_path:
                    # Determine image size based on planet (larger sizes for better visibility)
                    if planet_name == 'Sun':
                        sizex = sizey = arc_radius * 0.15
                    elif planet_name in ['Jupiter', 'Saturn']:
                        sizex = sizey = arc_radius * 0.24
                    elif planet_name in ['Uranus', 'Neptune']:
                        sizex = sizey = arc_radius * 0.20
                    elif planet_name == 'Pluto':
                        sizex = sizey = arc_radius * 0.12
                    else:  # Mercury, Venus, Earth, Mars
                        sizex = sizey = arc_radius * 0.16
                    
                    # Convert image to base64
                    img_b64 = image_to_base64(image_path)
                    
                    layout_images.append(
                        dict(
                            source=f"data:image/png;base64,{img_b64}",
                            xref="x",
                            yref="y",
                            x=row['x_cart'],
                            y=row['y_cart'],
                            sizex=sizex,
                            sizey=sizey,
                            sizing="contain",
                            xanchor="center",
                            yanchor="middle",
                            layer="above"
                        )
                    )
                    
                    # Add invisible marker for hover and legend
                    fig.add_trace(
                        go.Scatter(
                            x=[row['x_cart']],
                            y=[row['y_cart']],
                            mode='markers',
                            marker=dict(size=0.1, color='rgba(0,0,0,0)'),
                            name=planet_name,
                            hovertemplate=f"<b>{planet_name}</b><br>r: {row['r_linear']:.3f} AU<br>Diameter: {row['Diameter']:,} km<extra></extra>",
                            showlegend=True
                        )
                    )
            
            # Add zodiac sign labels outside the colored bands
            label_radius = arc_radius * 1.35
            for i, sign in enumerate(zodiac_signs):
                angle = i * 30 + 15
                x_label = label_radius * np.cos(np.radians(angle))
                y_label = label_radius * np.sin(np.radians(angle))
                
                fig.add_annotation(
                    x=x_label,
                    y=y_label,
                    text=f"{zodiac_glyphs[i]} {sign}",
                    showarrow=False,
                    font=dict(color='white', size=14, family='Arial'),
                    xanchor='center',
                    yanchor='middle'
                )
            
            # Update layout for Cartesian plot
            max_extent_layout = arc_radius * 1.45
            fig.update_layout(
                template='plotly_dark',  # Dark theme
                xaxis=dict(
                    range=[-max_extent_layout, max_extent_layout],
                    showgrid=False,
                    showticklabels=False,
                    zeroline=False,
                    visible=False,
                    scaleanchor="y",
                    scaleratio=1,
                    fixedrange=True,
                    showline=False,
                    ticks='',
                    showspikes=False
                ),
                yaxis=dict(
                    range=[-max_extent_layout, max_extent_layout],
                    showgrid=False,
                    showticklabels=False,
                    zeroline=False,
                    visible=False,
                    fixedrange=True,
                    showline=False,
                    ticks='',
                    showspikes=False
                ),
                # CRITICAL: Override polar configuration to prevent any polar axes from appearing
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=False, showline=False, showgrid=False),
                    angularaxis=dict(visible=False, showline=False, showgrid=False)
                ),
                paper_bgcolor="black",
                plot_bgcolor="black",
                font=dict(color="white"),
                margin=dict(l=10, r=10, b=30, t=30),
                images=layout_images,
                showlegend=False,  # Always hide legend in Images mode
                hovermode='closest',
                dragmode=False
            )
            
            # Force all axes to be completely hidden
            fig.update_xaxes(
                showgrid=False, 
                zeroline=False, 
                visible=False, 
                showline=False,
                showticklabels=False,
                ticks='',
                showspikes=False,
                mirror=False
            )
            fig.update_yaxes(
                showgrid=False, 
                zeroline=False, 
                visible=False, 
                showline=False,
                showticklabels=False,
                ticks='',
                showspikes=False,
                mirror=False
            )
        elif use_glyphs:
            # Add custom text labels for planet glyphs
            fig = go.Figure()
            
            # Add zodiac arcs first (background)
            zodiac_signs = [
                "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
            ]
            colors = [
                'rgba(255, 80, 80, 0.7)', 'rgba(255, 140, 60, 0.7)', 'rgba(255, 200, 50, 0.7)',
                'rgba(100, 220, 100, 0.7)', 'rgba(80, 200, 200, 0.7)', 'rgba(100, 150, 255, 0.7)',
                'rgba(180, 100, 220, 0.7)', 'rgba(220, 100, 180, 0.7)', 'rgba(255, 120, 100, 0.7)',
                'rgba(255, 180, 80, 0.7)', 'rgba(150, 220, 150, 0.7)', 'rgba(120, 180, 255, 0.7)'
            ]
            
            # Create uniform-width zodiac arcs with inner and outer boundaries
            arc_width = max_radius * 0.08 if max_radius > 0 else 0.5
            arc_inner = arc_radius - arc_width
            
            for i in range(12):
                angle_start = i * 30
                angle_end = (i + 1) * 30
                
                # Create arc as a filled region between inner and outer radius
                num_points = 20
                # Outer arc
                angles_outer = [angle_start + (angle_end - angle_start) * j / (num_points - 1) for j in range(num_points)]
                radii_outer = [arc_radius] * num_points
                # Inner arc (reversed for proper fill)
                angles_inner = angles_outer[::-1]
                radii_inner = [arc_inner] * num_points
                
                # Combine outer and inner for closed shape
                all_angles = angles_outer + angles_inner
                all_radii = radii_outer + radii_inner
                
                fig.add_trace(
                    go.Scatterpolar(
                        r=all_radii,
                        theta=all_angles,
                        fill='toself',
                        fillcolor=colors[i],
                        line=dict(color='black', width=2),
                        hoverinfo='skip',
                        showlegend=False,
                        name=''
                    )
                )
            
            # Add planets as text glyphs
            color_map = {planet: planet_colors.get(planet, 'gray') for planet in df['Planet'].unique()}
            
            for _, row in df.iterrows():
                # Make Sun smaller than other planets
                text_size = 12 if row['Planet'] == 'Sun' else 24
                glyph_symbol = planet_glyphs.get(row['Planet'], '●')
                fig.add_trace(
                    go.Scatterpolar(
                        r=[row['r_plot']],
                        theta=[row['theta']],
                        mode='text',
                        text=[glyph_symbol],
                        textposition='middle center',
                        textfont=dict(size=text_size, color=color_map[row['Planet']]),
                        meta=[row['Planet'], row['r_linear']],
                        hovertemplate='<b>%{meta[0]}</b><br>r: %{meta[1]:.3f} AU<extra></extra>',
                        showlegend=False,
                        name=f"{glyph_symbol} - {row['Planet']}",
                        legendgroup=row['Planet']
                    )
                )

            # Legend-only traces to display glyph + planet without the default text icon
            # Use classical planetary order
            planet_order = ['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
            legend_planets = [p for p in planet_order if p in df['Planet'].values]
            for planet_name in legend_planets:
                glyph_symbol = planet_glyphs.get(planet_name, '●')
                glyph_color = planet_colors.get(planet_name, 'white')
                fig.add_trace(
                    go.Scatterpolar(
                        r=[None],
                        theta=[None],
                        mode='markers',
                        marker=dict(size=0, color='rgba(0,0,0,0)'),
                        showlegend=True,
                        # Color the glyph text via HTML span to match plot colors
                        name=f"<span style='color:{glyph_color}'>{glyph_symbol}</span> - {planet_name}",
                        legendgroup=planet_name,
                        hoverinfo='skip',
                        visible=True
                    )
                )

        elif use_letters:
            # Add text labels for planet letters
            fig = go.Figure()
            
            # Add zodiac arcs first (background)
            zodiac_signs = [
                "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
            ]
            colors = [
                'rgba(255, 80, 80, 0.7)', 'rgba(255, 140, 60, 0.7)', 'rgba(255, 200, 50, 0.7)',
                'rgba(100, 220, 100, 0.7)', 'rgba(80, 200, 200, 0.7)', 'rgba(100, 150, 255, 0.7)',
                'rgba(180, 100, 220, 0.7)', 'rgba(220, 100, 180, 0.7)', 'rgba(255, 120, 100, 0.7)',
                'rgba(255, 180, 80, 0.7)', 'rgba(150, 220, 150, 0.7)', 'rgba(120, 180, 255, 0.7)'
            ]
            
            # Create uniform-width zodiac arcs with inner and outer boundaries
            arc_width = max_radius * 0.08 if max_radius > 0 else 0.5
            arc_inner = arc_radius - arc_width
            
            for i in range(12):
                angle_start = i * 30
                angle_end = (i + 1) * 30
                
                # Create arc as a filled region between inner and outer radius
                num_points = 20
                # Outer arc
                angles_outer = [angle_start + (angle_end - angle_start) * j / (num_points - 1) for j in range(num_points)]
                radii_outer = [arc_radius] * num_points
                # Inner arc (reversed for proper fill)
                angles_inner = angles_outer[::-1]
                radii_inner = [arc_inner] * num_points
                
                # Combine outer and inner for closed shape
                all_angles = angles_outer + angles_inner
                all_radii = radii_outer + radii_inner
                
                fig.add_trace(
                    go.Scatterpolar(
                        r=all_radii,
                        theta=all_angles,
                        fill='toself',
                        fillcolor=colors[i],
                        line=dict(color='black', width=2),
                        hoverinfo='skip',
                        showlegend=False,
                        name=''
                    )
                )
            
            # Add planets as text letters
            color_map = {planet: planet_colors.get(planet, 'gray') for planet in df['Planet'].unique()}
            
            for _, row in df.iterrows():
                # Make Sun smaller than other planets
                text_size = 14 if row['Planet'] == 'Sun' else 20
                letter_symbol = planet_letters.get(row['Planet'], '●')
                fig.add_trace(
                    go.Scatterpolar(
                        r=[row['r_plot']],
                        theta=[row['theta']],
                        mode='text',
                        text=[letter_symbol],
                        textposition='middle center',
                        textfont=dict(size=text_size, color=color_map[row['Planet']], family='Arial, sans-serif', weight='bold'),
                        meta=[row['Planet'], row['r_linear']],
                        hovertemplate='<b>%{meta[0]}</b><br>r: %{meta[1]:.3f} AU<extra></extra>',
                        showlegend=False,
                        name=f"{letter_symbol} - {row['Planet']}",
                        legendgroup=row['Planet']
                    )
                )

            # Legend-only traces to display letter + planet
            # Use classical planetary order
            planet_order = ['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
            legend_planets = [p for p in planet_order if p in df['Planet'].values]
            for planet_name in legend_planets:
                letter_symbol = planet_letters.get(planet_name, '●')
                letter_color = planet_colors.get(planet_name, 'white')
                fig.add_trace(
                    go.Scatterpolar(
                        r=[None],
                        theta=[None],
                        mode='markers',
                        marker=dict(size=0, color='rgba(0,0,0,0)'),
                        showlegend=True,
                        # Color the letter text via HTML span to match plot colors
                        name=f"<span style='color:{letter_color}'>{letter_symbol}</span> - {planet_name}",
                        legendgroup=planet_name,
                        hoverinfo='skip',
                        visible=True
                    )
                )

        else:
            # Create figure with uniform marker sizes for simple colored dots
            fig = go.Figure()
            
            # Add each planet individually with a uniform marker size so planets render as colored dots
            for _, row in df.iterrows():
                # Make Sun smaller than other planets
                marker_size = 14 if row['Planet'] == 'Sun' else 18
                
                fig.add_trace(
                    go.Scatterpolar(
                        r=[row['r_plot']],
                        theta=[row['theta']],
                        mode='markers',
                        marker=dict(
                            size=marker_size,
                            color=planet_colors.get(row['Planet'], 'gray'),
                            line=dict(color='black', width=2)
                        ),
                        name=row['Planet'],
                        hovertemplate=f"<b>{row['Planet']}</b><br>r: {row['r_linear']:.3f} AU<br>Diameter: {row['Diameter']:,} km<extra></extra>",
                        showlegend=True
                    )
                )

        # Define zodiac signs (starting at 0 degrees = Aries, 30 degrees each)
        zodiac_signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        zodiac_glyphs = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
        zodiac_labels = [f"{zodiac_glyphs[i]} {zodiac_signs[i]}" for i in range(12)]
        
        # Only add polar zodiac arcs for markers mode (not images, glyphs, or letters)
        if not use_glyphs and not use_letters and not use_planet_images:
            # Use the shared arc radius to keep visuals aligned with glyph mode
            # Add zodiac sign arc regions and boundary lines with vibrant colors
            colors = [
                'rgba(255, 80, 80, 0.7)', 'rgba(255, 140, 60, 0.7)', 'rgba(255, 200, 50, 0.7)',
                'rgba(100, 220, 100, 0.7)', 'rgba(80, 200, 200, 0.7)', 'rgba(100, 150, 255, 0.7)',
                'rgba(180, 100, 220, 0.7)', 'rgba(220, 100, 180, 0.7)', 'rgba(255, 120, 100, 0.7)',
                'rgba(255, 180, 80, 0.7)', 'rgba(150, 220, 150, 0.7)', 'rgba(120, 180, 255, 0.7)'
            ]
            
            # Create uniform-width zodiac arcs with inner and outer boundaries
            arc_width = max_radius * 0.08 if max_radius > 0 else 0.5
            arc_inner = arc_radius - arc_width
            
            # Add arcs for each zodiac sign
            for i in range(12):
                angle_start = i * 30
                angle_end = (i + 1) * 30
                
                # Create arc as a filled region between inner and outer radius
                num_points = 20
                # Outer arc
                angles_outer = [angle_start + (angle_end - angle_start) * j / (num_points - 1) for j in range(num_points)]
                radii_outer = [arc_radius] * num_points
                # Inner arc (reversed for proper fill)
                angles_inner = angles_outer[::-1]
                radii_inner = [arc_inner] * num_points
                
                # Combine outer and inner for closed shape
                all_angles = angles_outer + angles_inner
                all_radii = radii_outer + radii_inner
                
                fig.add_trace(
                    go.Scatterpolar(
                        r=all_radii,
                        theta=all_angles,
                        fill='toself',
                        fillcolor=colors[i],
                        line=dict(color='black', width=2),
                        hoverinfo='skip',
                        showlegend=False,
                        name=''
                    )
                )
        
        # Add radial lines for zodiac sector boundaries (Polar mode)
        if show_zodiac_radials and not use_planet_images:
            for i in range(12):
                angle = i * 30  # Zodiac sector boundaries at 0°, 30°, 60°, etc.
                fig.add_trace(
                    go.Scatterpolar(
                        r=[0, arc_radius],
                        theta=[angle, angle],
                        mode='lines',
                        line=dict(color='rgba(200, 200, 200, 0.5)', width=1),
                        hoverinfo='skip',
                        showlegend=False
                    )
                )
        
        # Add orbital paths for each planet (skip if projecting to perimeter or using images)
        if not show_perimeter and not use_planet_images and show_orbits:
            for planet_name in sorted(PLANETS_DATA.keys()):
                # Only draw orbits for planets that are in the dataframe
                if planet_name not in df['Planet'].values:
                    continue
                    
                planet_data = PLANETS_DATA[planet_name]
                a, e, L_deg, w_bar_deg = planet_data
                # Generate points along the orbit with high accuracy
                num_orbit_points = 1000
                nu_angles = np.linspace(0, 360, num_orbit_points)  # True anomaly angles
                orbit_radii = []
                orbit_theta = []  # Ecliptic longitude angles
                
                for nu_deg in nu_angles:
                    nu = np.radians(nu_deg)  # true anomaly
                    r = a * (1 - e**2) / (1 + e * np.cos(nu))
                    orbit_radii.append(r)
                    # The ecliptic longitude is the true anomaly rotated by w_bar (argument of perihelion)
                    theta = nu_deg + w_bar_deg
                    orbit_theta.append(theta)
                
                # Validate orbit data (check for NaN or invalid values)
                if not all(np.isfinite(orbit_radii)):
                    continue
                
                # Apply log scaling if enabled to match planet visualization scale
                if use_log_radius:
                    orbit_radii_plot = [math.log10(max(r, 1e-6)) + log_offset for r in orbit_radii]
                else:
                    orbit_radii_plot = orbit_radii
                
                fig.add_trace(
                    go.Scatterpolar(
                        r=orbit_radii_plot,
                        theta=orbit_theta,
                        mode='lines',
                        line=dict(color=planet_colors.get(planet_name, 'gray'), width=1, dash='dot'),
                        hoverinfo='skip',
                        showlegend=False,
                        name=f'{planet_name} Orbit'
                    )
                )

        # Prepare radial axis config based on scale mode (only for polar plots)
        if not use_planet_images:
            if show_perimeter or not show_radial_scale:
                # Hide radial axis when projecting to perimeter or when radial scale is disabled
                radialaxis_config = dict(
                    visible=False,
                    showticklabels=False,
                )
            elif use_log_radius:
                radialaxis_config = dict(
                    visible=True,
                    showticklabels=True,
                    showgrid=False,
                    type='linear',
                    range=[0, None],
                    tickmode='array',
                    tickvals=radial_tickvals,
                    ticktext=radial_ticktext,
                )
            else:
                radialaxis_config = dict(
                    visible=True,
                    showticklabels=True,
                    showgrid=False,
                    type='linear',
                    range=[0, None],
                    dtick=radial_tick_step,
                )

            # Update layout for a dark space theme with zodiac labels (polar plot)
            # Position zodiac labels at the middle of each arc (15, 45, 75, etc.)
            fig.update_layout(
                polar=dict(
                    bgcolor="black",
                    radialaxis=radialaxis_config,
                    angularaxis=dict(
                        showgrid=False,
                        tickvals=[i * 30 + 15 for i in range(12)],
                        ticktext=zodiac_labels,
                        rotation=0,
                        direction='counterclockwise',
                        tickfont=dict(size=14)
                    )
                ),
                paper_bgcolor="black",
                plot_bgcolor="black",
                font=dict(color="white", size=14),
                margin=dict(l=0, r=0, b=80, t=40),
                legend=dict(font=dict(size=14), yanchor="top", y=-0.30, xanchor="left", x=0, orientation="h", tracegroupgap=12)
            )
            # Add a line above the legend
            fig.add_shape(
                type="line",
                xref="paper", yref="paper",
                x0=0, y0=-0.25, x1=1, y1=-0.25,
                line=dict(color="rgba(200, 200, 200, 0.5)", width=1)
            )

        # Add date annotation to lower right corner
        date_text = selected_datetime.strftime("%Y-%m-%d %H:%M:%S")
        if use_planet_images:
            # For Cartesian plots, add annotation with xref/yref to data coordinates
            fig.add_annotation(
                x=max_extent_layout * 1.45,
                y=-max_extent_layout * 0.95,
                text=date_text,
                showarrow=False,
                font=dict(color='white', size=12, family='Arial'),
                xanchor='right',
                yanchor='bottom'
            )
        else:
            # For polar plots, add annotation with xref/yref to paper coordinates
            fig.add_annotation(
                xref='paper',
                yref='paper',
                x=0.98,
                y=-0.23,
                text=date_text,
                showarrow=False,
                font=dict(color='white', size=12),
                xanchor='right',
                yanchor='bottom'
            )

        # Use theme=None when using planet images to prevent Streamlit from overriding Plotly's dark theme
        if use_planet_images:
            st.plotly_chart(fig, width='stretch', theme=None)
        else:
            st.plotly_chart(fig, width='stretch')
        
        # Export controls and download button for high-resolution PNG
        # These settings only affect the downloaded image, not the on-screen plot
        with st.expander("📥 PNG Export Settings", expanded=False):
            exp_col1, exp_col2, exp_col3 = st.columns(3)
            with exp_col1:
                export_scale = st.slider("PNG export scale", min_value=1, max_value=4, value=3, help="Higher scale increases resolution.")
                export_font_size = st.slider("PNG export font size", min_value=12, max_value=36, value=20, help="Larger values make text more readable in the PNG.")
            with exp_col2:
                export_width = st.number_input("PNG export width (px)", min_value=800, max_value=4000, value=1400, step=100, help="Width of the exported PNG.")
                export_height = st.number_input("PNG export height (px)", min_value=600, max_value=3000, value=1000, step=100, help="Height of the exported PNG.")
            with exp_col3:
                export_bg = st.selectbox(
                    "PNG background",
                    ["Match app (black)", "Transparent", "White"],
                    index=0,
                    help="Choose background for the exported image."
                )

            try:
                # Create an export-only copy of the figure and enlarge fonts
                fig_export = go.Figure(fig)

                # Apply background choice to export only
                if export_bg == "Transparent":
                    bg_color = "rgba(0,0,0,0)"
                elif export_bg == "White":
                    bg_color = "white"
                else:
                    bg_color = "black"

                fig_export.update_layout(
                    paper_bgcolor=bg_color,
                    plot_bgcolor=bg_color,
                )
                if getattr(fig_export.layout, "polar", None):
                    fig_export.update_layout(polar=dict(bgcolor=bg_color))

                # Base font and legend
                fig_export.update_layout(font=dict(size=export_font_size))
                fig_export.update_layout(legend=dict(font=dict(size=export_font_size)))

                # Title font (if present)
                if fig_export.layout.title and fig_export.layout.title.font:
                    current = fig_export.layout.title.font.size or 0
                    fig_export.layout.title.font.size = max(current, export_font_size)

                # Polar axis tick fonts (if polar is used)
                if getattr(fig_export.layout, "polar", None):
                    fig_export.update_layout(
                        polar=dict(
                            angularaxis=dict(tickfont=dict(size=export_font_size)),
                            radialaxis=dict(tickfont=dict(size=export_font_size))
                        )
                    )

                # Cartesian axes fonts (safe even if axes are hidden)
                fig_export.update_xaxes(tickfont=dict(size=export_font_size), title_font=dict(size=export_font_size))
                fig_export.update_yaxes(tickfont=dict(size=export_font_size), title_font=dict(size=export_font_size))

                # Annotation fonts (e.g., zodiac labels in images mode)
                if fig_export.layout.annotations:
                    for ann in fig_export.layout.annotations:
                        if getattr(ann, "font", None) is None:
                            ann.font = dict(size=export_font_size)
                        else:
                            ann.font.size = export_font_size

                # Generate PNG using export settings
                png_data = fig_export.to_image(
                    format="png",
                    width=int(export_width),
                    height=int(export_height),
                    scale=export_scale
                )
                st.download_button(
                    label="📥 Download Plot as PNG",
                    data=png_data,
                    file_name=f"planetary_positions_{selected_datetime.strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    key="download_plot"
                )
            except Exception as e:
                st.warning(f"PNG download unavailable: {str(e)}", icon="⚠️")
        
        # Display planet images if using images mode
        if use_planet_images:
            st.markdown("### Planet Image Gallery")
            image_cols = st.columns(3)
            col_idx = 0
            for _, row in df.iterrows():
                planet_name = row['Planet']
                image_path = load_planet_image(planet_name)
                if image_path:
                    with image_cols[col_idx % 3]:
                        st.markdown(f"**{planet_name}**")
                        st.image(image_path)
                        col_idx += 1

    # Birthday Facts Section
    st.markdown("---")
    st.subheader(f"🎂 If {selected_datetime.strftime('%Y/%m/%d %H:%M:%S')} is your birthday...")
    
    with st.expander("View Birthday Facts & Statistics", expanded=False):
        birthday_facts = calculate_birthday_facts(selected_datetime)
        
        # Create table from facts with date at the top
        facts_df = pd.DataFrame(list(birthday_facts.items()), columns=['Fact', 'Value'])
        date_row = pd.DataFrame([{'Fact': 'Date', 'Value': selected_datetime.strftime('%Y/%m/%d %H:%M:%S')}])
        facts_df = pd.concat([date_row, facts_df], ignore_index=True)
        st.dataframe(facts_df, width='stretch', hide_index=True)
        
        # Additional notes
        st.markdown("""
        **Notes:**
        - **Chinese Zodiac**: Based on lunar calendar, cycles every 12 years with 5 elements
        - **Life Path Number**: Numerology calculation (single digit reduction)
        - **Birthstone/Flower**: Traditional Western associations
        - **Saturn Return**: Astrological milestone when Saturn returns to natal position
        - **Julian Day Number**: Used by astronomers for precise date calculations
        - **Birthday Paradox**: Probability that someone in a random group of 23 shares your birthday
        """)

if __name__ == "__main__":
    main()

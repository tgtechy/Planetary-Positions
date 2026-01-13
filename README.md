# 🪐 Solar System Plotter

An interactive Streamlit web application for visualizing planetary positions in the solar system at any date and time.

## Overview

This application calculates and displays the heliocentric (Sun-centered) positions of planets using Keplerian orbital elements. It provides an interactive polar plot showing the positions of all planets from Mercury to Pluto (yes, we consider pluto a proto-planet), along with zodiac sign overlays and customizable visualization options.

## Features

### Planetary Visualization
- **Three Display Modes:**
  - **Markers**: Simple colored dots for each planet
  - **Glyphs**: Astronomical symbols (☿ ♀ ⊕ ♂ ♃ ♄ ♅ ♆ ♇)
  - **Images**: Planet images for realistic visualization

### Date and Time Selection
- Select any date from 1900 to 2100

### Visualization Options
- **Logarithmic Radial Scale**: Toggle between linear and logarithmic distance scaling for better visualization of inner planets
- **Show Orbit Lines**: Display orbital paths for each planet
- **Show Zodiac Sector Lines**: Draw radial lines dividing the 12 zodiac sectors
- **Show Radial Scale**: Toggle distance scale visibility
- **Project to Perimeter**: Project all planets to the perimeter circle, showing only angular positions

### Zodiac Integration
- 12 zodiac signs displayed as colored bands around the perimeter
- Each zodiac sign labeled with both name and astrological glyph (♈ Aries, ♉ Taurus, etc.)
- Zodiac bands color-coded for easy identification

### Birthday Facts & Statistics
An extensive collection of birthday-related calculations including:
- Age in various formats (years, days, weeks, seconds)
- Zodiac sign (Western and Chinese)
- Birthstone and birth flower
- Life path number (numerology)
- Upcoming milestones (10,000 days, 1 billion seconds, etc.)
- Next palindrome, square, and prime ages
- Saturn returns
- And many more interesting facts!

### Export Options
- Download high-resolution PNG images of visualizations
- Customizable export settings:
  - Resolution scale (1x to 4x)
  - Font size
  - Image dimensions
  - Background color (black, white, or transparent)

## Technical Details

### Orbital Mechanics
The application uses simplified Keplerian orbital elements referenced to the J2000.0 epoch:
- **Semi-major axis (a)**: Average distance from the Sun in Astronomical Units
- **Eccentricity (e)**: Orbital shape (0 = circular, <1 = elliptical)
- **Mean longitude (L)**: Initial position at epoch
- **Longitude of perihelion (ω̄)**: Orientation of the orbit

The positions are calculated by:
1. Computing mean anomaly from the date offset
2. Solving Kepler's equation using Newton-Raphson iteration
3. Converting to heliocentric Cartesian coordinates
4. Transforming to ecliptic plane coordinates

### Visualization
- Built with **Plotly** for interactive polar and Cartesian plots
- **Streamlit** provides the web interface and controls
- Dark space theme with vibrant zodiac colors
- Responsive layout that adapts to different screen sizes

## Installation

### Requirements
Install the required Python packages:

```bash
pip install -r requirements.txt
```

Required packages:
- streamlit
- pandas
- plotly
- numpy
- Pillow (for image handling)

### Optional: Planet Images
Place planet images in a `planet_images/` folder for the Images display mode. Supported formats:
- PNG files named: `mercury.png`, `venus.png`, `earth.png`, etc.
- GIF files as fallback: `mercury.gif`, `venus.gif`, etc.

## Usage

### Running the Application

```bash
streamlit run planetpositions.py
```

The application will open in your default web browser.

### Controls

1. **Select Date**: Choose any date from the date picker or click "Today"
2. **Set Time**: Enter specific hour, minute, and second
3. **Choose Display Mode**: Select Markers, Glyphs, or Images
4. **Adjust Options**: Toggle various checkboxes for orbit lines, zodiac sectors, radial scale, etc.
5. **Scale Type**: Switch between linear and logarithmic radial scaling
6. **Export**: Configure export settings and download high-resolution images

### Navigation Modes

- **Default View**: All planets shown with their actual distances
- **Logarithmic Scale**: Compresses outer planets to make inner planets more visible
- **Perimeter Projection**: All planets at same radius, showing only angular positions
- **With Orbits**: Display complete orbital paths as dotted lines

## Data Sources

- Planetary orbital elements: Simplified Keplerian elements for J2000.0 epoch
- Zodiac divisions: Traditional 30° sectors starting at 0° (Aries)
- Planet data: Semi-major axes, eccentricities, and diameters

## Accuracy

This application uses simplified two-body orbital mechanics and does not account for:
- Gravitational perturbations between planets
- Precession and nutation
- Relativistic effects
- Orbital plane inclinations (all planets shown in ecliptic plane)

For casual observation and educational purposes, the positions are sufficiently accurate. For precise astronomical calculations, use specialized astronomy software.

## License

This project is provided as-is for educational and entertainment purposes.

## Author

Created as an interactive tool for exploring solar system dynamics and astrological charts.

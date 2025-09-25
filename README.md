# Sun Movement Data Visualization

A real-time, generative Pygame visualization that morphs a mystical "sun totem" through multiple organic shapes (sun → moon → cloud → flower) while reacting to the (mock) sun position across the day. It overlays live textual data (time, sunrise/sunset, computed sun position fraction) and renders thousands of smoothly animated particles with layered rotation, ripples, pulses, and palette shifts tied to the diurnal cycle.

---
## ✨ Features
- 4,000+ animated radial particles forming a morphing energy totem
- Shape cycling: sun → moon → cloud → flower (smooth blended transitions)
- Time-based color modulation using a generated HSV gradient palette
- Dynamic background with layered ripple effects & subtle parallax particles
- Real-time overlay: clock, sunrise, sunset, sun position fraction, frame counter
- Modular structure for future expansion (data providers, astronomy API, theming)
- Clean separation between:
  - Visual core (`Sun Movement Data.py`)
  - Mock astronomical time helpers (`sun_times.py`)
  - Mock positional/elevation dataset (`data_fetcher.py`)

---
## 🗂 Project Structure
```
Sun Movement Data.py    # Main executable visualization (Pygame loop)
data_fetcher.py         # Mock sun elevation/azimuth/intensity time series (Pandas)
sun_times.py            # Mock sunrise/sunset + fractional position helper
__pycache__/            # Python bytecode cache (ignored in Git typically)
README.md               # This file
requirements.txt        # Python dependencies
```

---
## 🐍 Requirements
- Python 3.11+ (tested against 3.13 bytecode – adjust if needed)
- pip (for dependency installation)
- A display environment (runs natively on Windows; works on macOS/Linux with a normal desktop session)

### Python Dependencies
Declared in `requirements.txt`:
- `pygame` – real-time rendering
- `pandas` – structured mock dataset generation

Install them (Windows PowerShell):
```powershell
pip install -r requirements.txt
```

If you use a virtual environment (recommended):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---
## ▶️ Running the Visualization
From the project root:
```powershell
python "Sun Movement Data.py"
```
A window titled "Mystical Sun Totem Visualization" should appear. If it does not come to the foreground automatically, check:
- Another window may have focus
- GPU driver overlay conflicts
- Remote desktop session (sometimes Pygame window layering is delayed)

Exit via the window close button (standard Pygame quit event).

---
## 🔢 Data & Computation Overview
| Aspect | Source | Notes |
|--------|--------|-------|
| Sunrise/Sunset | `fetch_sun_times()` in `sun_times.py` | Currently hard-coded daily mock values (6:30 / 18:45) |
| Sun Position Fraction | `get_sun_position_fraction()` | Fraction of total day + sinusoidal variation to keep visuals lively |
| Particle Field | `SunTotem` + `Particle` classes | Procedural radial system with breathing + bloom modifiers |
| Background Particles | `BackgroundParticle` | Slow-floating ambient field (400 instances) |
| Elevation/Azimuth Table | `DataFetcher._generate_mock_data()` | 24h grid with randomized perturbations every 15 min |

---
## 🧪 Extending with Real Astronomy Data
You can replace mock logic with real calculations from libraries/APIs:
- `astral` (Python package) for solar times & elevation
- USNO / NOAA sunrise-sunset APIs
- `pyephem` / `skyfield` for precise ephemerides

Suggested integration path:
1. Replace `fetch_sun_times()` to return real `(sunrise_str, sunset_str)`.
2. Replace `get_sun_position_fraction()` with a normalized mapping of current time between astronomical dawn & dusk.
3. (Optional) Enhance `DataFetcher` to cache a day’s elevation + azimuth and smoothly interpolate.
4. Tie particle rotation speed or bloom parameters to sun elevation for more dynamic responsiveness.

---
## 🎨 Tuning & Customization
Modify constants near the top of `Sun Movement Data.py`:
| Constant | Purpose | Example Adjustment |
|----------|---------|-------------------|
| `PARTICLE_COUNT` | Density & fill detail | Lower to 2000 for performance |
| `RADIUS` | Core radius of totem | Increase for a larger inner hub |
| `BREATH_SPEED` | Pulsation speed | Slow to 0.3 for calmer visuals |
| `REPEAT_COUNT` | Layer multiplicity | 2–6 for less/more layering |
| `REPEAT_ROTATION_STEP` | Angular offset per layer | Try `2 * math.pi / 5` |
| `REPEAT_OFFSET` | Pixel offset per repeated layer | 10–30 for variety |

To experiment with palette generation, edit `get_gradient_palette()` and shift `base_hue` or saturation.

---
## 🖥 Performance Notes
- 4k particles × 4 repeated layers → many draws per frame; a mid-range GPU/CPU handles 60 FPS.
- If FPS dips:
  - Reduce `PARTIC

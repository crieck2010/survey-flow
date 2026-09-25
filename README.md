# survey-flow

Flow-field rendering engine for surveying and remote sensing — the second module of the earthwatch-suite **flow-field animation program** (the pipeline that produces mapped.earth-style animated current/temperature reels).

`survey-flow` takes a surface-current vector field plus a scalar field (water temperature) — as provided by [survey-currents](https://github.com/crieck2010/survey-currents) — advects particles through the flow, and renders map frames: a temperature colormap base with fading particle streaks, landmask, scale bar, timestamp, and colorbar legend. It emits a versioned **frame manifest** (JSON) that [survey-animate](https://github.com/crieck2010/survey-animate) (module 3) consumes to encode video.

## Install

```bash
pip install survey-flow                              # engine core (stdlib + numpy)
pip install "survey-flow[render]"                     # frame rendering (matplotlib)
pip install "survey-flow[raster]"                     # 4-band COG input (rasterio)
pip install "survey-flow[full]"                       # rendering + COG input
```

`survey-currents` is intentionally **not** a hard dependency: `survey-flow`
consumes its `CurrentField` via duck typing (any object with
`u, v, temperature, times, lats, lons`) and its per-timestep 4-band COGs
(`speed, u, v, temperature`) via rasterio. Either package installs standalone.

## Quickstart

```python
from currents.models import CurrentField          # survey-currents
from flow.fields import TimeVaryingField
from flow.pipeline import render_animation

cf = CurrentField.from_json("lmhofs_2026-09-16.json")  # or fetch via survey-currents
tvf = TimeVaryingField.from_current_field(cf, scalar="temperature")

manifest = render_animation(
    tvf, "reel_out/",
    style="reel-dark",     # or "reel-light", "print"
    n_frames=48,
    n_particles=1500,
    size="reel",           # 1080x1920 vertical; also "wide", "square", or (w, h)
    fps=30.0,
)
print(f"{len(manifest)} frames -> reel_out/manifest.json")
```

## CLI

```bash
# Render from a survey-currents CurrentField JSON export
survey-flow render --field lmhofs.json --style reel-dark --frames 48 \
    --particles 1500 --size reel --out reel_out/

# Render from per-timestep 4-band COGs (speed, u, v, temperature)
survey-flow render --cog t00.tif --cog t01.tif \
    --times 2026-09-16T00:00:00+00:00 --times 2026-09-16T01:00:00+00:00 \
    --out reel_out/

# Offline synthetic demo (no downloads, no survey-currents needed)
survey-flow demo --out demo_out/ --frames 12 --particles 400

# List style presets and output sizes
survey-flow styles
survey-flow sizes

# Rebuild manifest.json from an existing frames/ directory
survey-flow manifest --dir reel_out/frames --fps 30
```

## How it works

1. **Fields** (`flow.fields`) — `VectorField` wraps one timestep: bilinear
   u/v sampling at arbitrary points (NaN-aware, so ragged coastlines work),
   land masking (NaN velocity = land), and scalar overlays (temperature or
   speed). `TimeVaryingField` blends consecutive timesteps so frames sample
   a smooth flow at any fractional time.
2. **Advection** (`flow.advect`) — `ParticleSet` seeds tracers over water
   (deterministic), integrates them with RK2 (default) or RK4 in a
   spherical-earth degree conversion, keeps fading trail histories, and
   respawns particles that beach, exit, or age out.
3. **Rendering** (`flow.render`) — matplotlib (Agg, lazy import) draws the
   scalar colormap, land, particle streaks as alpha-graded line collections,
   colorbar, scale bar, and timestamp. `particles=None` gives a static
   scalar snapshot — the shape a future survey-qgis Processing algorithm
   would produce.
4. **Manifest** (`flow.frames`) — every run writes `manifest.json`
   (schema `survey-flow.frame-manifest/1.0`): frame order, timestamps, PNG
   paths, scalar range, colormap, style, and render params. This is the
   stable contract survey-animate consumes; see `docs/FRAME_MANIFEST.md`.

## Styles

| Preset | Look | Use |
|---|---|---|
| `reel-dark` | Dark-navy base, white streaks, cividis | Vertical social reels |
| `reel-light` | Light base, dark streaks, viridis | Light-themed reels |
| `print` | White base, thin black streaks | Reports and papers |

All colormaps are colorblind-safe. Fixed scalar ranges are computed across
all timesteps so the colormap never flickers between frames.

## Interoperability

- **Consumes** survey-currents (`CurrentField` JSON / 4-band COGs). Never
  forks or modifies it.
- **Feeds** survey-animate via the frame manifest (`docs/FRAME_MANIFEST.md`).
- **survey-qgis**: `docs/INTEROP.md` documents how a static snapshot plugs
  in as a future Processing algorithm (that repo untouched).
- Interchange formats: PNG frames, JSON manifest, GeoTIFF/COG inputs.

See `docs/ARCHITECTURE.md`, `docs/INTEROP.md`, `docs/FRAME_MANIFEST.md`.

## Project

Part of the [earthwatch-suite](https://github.com/crieck2010/earthwatch-suite)
remote-sensing program. Flow-field animation program: **survey-currents**
(1/4, data) → **survey-flow** (2/4, rendering, this repo) → survey-animate
(3/4, video) → survey-reels (4/4, orchestration).

## License

MIT — see [LICENSE](LICENSE).

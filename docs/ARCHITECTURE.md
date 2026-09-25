# Architecture

`survey-flow` is an **engine-first** package: pure logic in `src/flow/`,
zero UI-framework imports, importable and testable standalone. The CLI
(`flow.cli`) is a thin adapter. Heavy dependencies are lazy and optional:

| Layer | Imports | Notes |
|---|---|---|
| `fields`, `advect`, `frames`, `styles` | stdlib + numpy | Always available; fully unit-tested |
| `render`, `pipeline` | + matplotlib (Agg) | Lazy; informative `ImportError` without it |
| `fields.from_cog` | + rasterio | Lazy; informative `ImportError` without it |
| CLI demo | stdlib + numpy | Self-contained synthetic field |

## Data flow

```
CurrentField (survey-currents, duck-typed) or 4-band COGs
        |
        v
TimeVaryingField  -- fractional-time blending of u/v/scalar grids
        |
        v
ParticleSet  -- seeded tracers, RK2/RK4 advection, trails, respawn
        |
        v
render_frame  -- scalar colormap + streaks + decorations -> PNG
        |
        v
FrameManifest -- manifest.json (contract for survey-animate)
```

## Module responsibilities

- **`fields.py`** — spatial sampling. `VectorField` owns one timestep:
  NaN-aware bilinear interpolation (`_bilinear` renormalizes over valid
  corners, so ragged coastlines don't bleed land values into water),
  landmask (`is_land`, nearest-neighbor), bounds checks. `TimeVaryingField`
  linearly blends bracketing timesteps for fractional-time queries.
  Construction paths: `from_current_field` (duck-typed — any object with
  the `CurrentField` attributes, so survey-currents is not a hard
  dependency) and `from_cog` (survey-currents 4-band COG layout
  `speed, u, v, temperature`, geotransform-derived coordinates).
- **`advect.py`** — time integration. Positions are lon/lat degrees;
  `velocity_to_deg` converts m/s with a spherical earth. `ParticleSet`
  rejection-samples seeds over water (deterministic via seed), integrates
  with midpoint RK2 (default) or classical RK4, keeps a `(n, trail, 2)`
  ring buffer, and respawns beached/exited/aged particles to hold density
  constant. `trail_segments()` yields line segments plus a validity mask
  for streak rendering.
- **`styles.py`** — frozen `Style` presets (`reel-dark`, `reel-light`,
  `print`); colorblind-safe colormaps (cividis/viridis).
- **`render.py`** — one frame. matplotlib is imported lazily with the Agg
  backend. Scalar base via bilinear `imshow` (no cell-edge hairlines);
  land as an RGBA overlay; particle trails as a per-segment-alpha
  `LineCollection`; horizontal colorbar; scale bar with 1/2/5-nice
  kilometre lengths; pretty timestamps (`16 Sep 2026 01:20 UTC`).
  `fit_aspect` crops the view to the target aspect in kilometre space so
  nothing stretches. `particles=None` renders a static scalar snapshot.
- **`frames.py`** — `FrameManifest` (schema
  `survey-flow.frame-manifest/1.0`): ordered `FrameEntry` records,
  sequential-index enforcement, relative-path portability, `read`
  validation rejecting unknown schemas/major versions.
  `interpolate_times` spreads ISO labels across frames.
- **`pipeline.py`** — `render_animation`: the one-call path. Computes a
  global scalar range (no colormap flicker), defaults `dt_seconds` to
  model-span/frames, steps one shared particle set through fractional
  times, renders, and writes the manifest.
- **`cli.py`** — `render` / `demo` / `styles` / `sizes` / `manifest`.

## Scaling notes

- All per-particle and per-pixel work is vectorized numpy; no Python
  loops over particles or grid cells.
- Memory per frame is dominated by the figure raster (`w*h` RGBA) and the
  trail buffer (`n * trail_length * 2` float64) — e.g. 1500 particles ×
  12 trail points ≈ 0.3 MB.
- Frames render independently and could be parallelized by partitioning
  the frame index range (particle state would need per-worker seeding;
  not implemented in v0.1.0 — see CHANGELOG "Deferred").
- For very large grids, downsample before constructing `VectorField`
  (or render at lower dpi); bilinear sampling cost scales with particle
  count, not grid size.

## Conventions

- Units: u/v in m/s, temperature in °C, positions in degrees lon/lat,
  timestamps ISO-8601. NaN means land/missing everywhere.
- Determinism: every stochastic path takes a seed; identical inputs +
  seed reproduce identical frames.
- interchange formats: PNG frames, JSON manifest, GeoTIFF/COG inputs.

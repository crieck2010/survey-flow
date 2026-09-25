# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-25

### Added
- `VectorField`: one-timestep surface-current field on a regular lat/lon
  grid — NaN-aware bilinear u/v sampling, landmask (`is_land`), bounds
  checks, scalar overlays (`temperature` default, `speed` fallback).
  Constructed from a survey-currents `CurrentField` (duck-typed, no hard
  dependency) or a 4-band COG (`speed, u, v, temperature`) via lazy
  rasterio.
- `TimeVaryingField`: fractional-time blending across timesteps for
  smooth animation between model output times.
- `ParticleSet` / `AdvectionConfig`: deterministic seeded tracers, RK2
  (default) and RK4 integration with spherical-earth degree conversion,
  fading trail ring buffers, respawn rules (beached / exited / aged),
  `trail_segments()` for streak rendering.
- `render_frame` (matplotlib Agg, lazy): scalar colormap base (bilinear,
  no cell hairlines), RGBA land overlay, alpha-graded particle streaks
  (`LineCollection`) with head dots, horizontal colorbar, 1/2/5-nice
  kilometre scale bar, pretty timestamps (`16 Sep 2026 01:20 UTC`),
  aspect-correct view cropping. `particles=None` gives a static snapshot.
- `Style` presets: `reel-dark`, `reel-light`, `print` — colorblind-safe
  colormaps (cividis/viridis), frozen dataclasses.
- `FrameManifest` (`survey-flow.frame-manifest/1.0`): ordered frame
  entries, sequential-index enforcement, relative-path portability,
  schema/major-version validation — the stable contract for
  survey-animate (module 3/4). Full spec in `docs/FRAME_MANIFEST.md`.
- `render_animation` pipeline: fixed global scalar range (no colormap
  flicker), model-span-derived `dt_seconds`, shared particle set,
  progress callback, PNG frames + `manifest.json`.
- Thin CLI: `render` (CurrentField JSON or COGs), `demo` (fully offline
  synthetic), `styles`, `sizes`, `manifest` (rebuild from frames/).
- Docs: README, `docs/ARCHITECTURE.md`, `docs/INTEROP.md`,
  `docs/FRAME_MANIFEST.md`; `examples/run_demo.sh` (offline, verified).
- 68 tests passing, fully offline (matplotlib-dependent tests skip
  cleanly when it is not installed; no network anywhere).

### Deferred
- Frame-range parallelism (partition frame indices across workers).
- Streamline rendering mode (in addition to particle streaks).
- survey-qgis `flow_snapshot` Processing algorithm (landing zone
  documented in `docs/INTEROP.md`; that repo untouched).

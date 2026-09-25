# Interoperability

`survey-flow` sits between **survey-currents** (data, module 1/4) and
**survey-animate** (video, module 3/4) in the earthwatch-suite flow-field
animation program. It also offers hooks for the survey-suite cartography
layer. This document records every contract in both directions.

## Upstream: survey-currents (consumed, never modified)

Two input paths, both read-only:

1. **CurrentField (duck-typed).** `VectorField.from_current_field` /
   `TimeVaryingField.from_current_field` accept any object with the
   survey-currents `CurrentField` attributes (`u`, `v`, `temperature`,
   `times`, `lats`, `lons`, `crs`, `source`). `survey-currents` is **not**
   a declared dependency, so either package installs and versions
   independently. A `CurrentField` JSON export (`to_json`) loads through
   the CLI's `--field` flag.
2. **4-band COGs.** `VectorField.from_cog` reads survey-currents'
   per-timestep COG layout (`speed, u, v, temperature`, band descriptions
   in that order) via rasterio (lazy). The CLI accepts repeated
   `--cog` + `--times` for a time series.

Scalar selection: `temperature` (default; falls back to `speed` when the
field has no temperature grid) or `speed`.

## Downstream: survey-animate (the frame manifest contract)

`render_animation` writes `manifest.json` per `docs/FRAME_MANIFEST.md`
(schema `survey-flow.frame-manifest/1.0`). survey-animate must:

- read `manifest.json` with schema validation (reject unknown majors);
- resolve `frames[].png_path` relative to the manifest directory;
- honor `fps` as the default playback rate (overridable);
- use `size_px` to size the video canvas.

`FrameManifest` in `flow.frames` is the reference implementation both
sides can vendor or depend on.

## survey-qgis: static snapshot hook (future, that repo untouched)

`render_frame(field, particles=None, ...)` produces a static scalar map
with decorations but no streaks — exactly the output shape a QGIS
Processing algorithm needs. Proposed algorithm (for a future
survey-qgis release, to be spec'ed with that repo's maintainer):

- **id**: `flow_snapshot`
- **inputs**: vector field source (CurrentField JSON or COG), timestep
  index, scalar (`temperature`/`speed`), style preset, output PNG path,
  optional DPI/size
- **outputs**: PNG map + a one-row manifest fragment
- **group**: Imagery (alongside `spectral_index`)

No changes to survey-qgis were made for v0.1.0; this is a documented
landing zone only.

## survey-reels (module 4/4, future consumer)

`flow.pipeline.render_animation` is the orchestration seam: it takes a
`TimeVaryingField`, an output directory, and a `progress` callback, and
returns the manifest. survey-reels will call it per site-config
`animation:` block and pass the manifest directory to survey-animate.

## survey-monitor / survey-thermal

No direct dependency in v0.1.0. The natural future wiring, documented
here for the program:

- `survey-monitor`: a reel run becomes a run artifact — the manifest
  directory path recorded alongside `RunSummary`; `CurrentsPassProvider`
  (from survey-currents) supplies the field, survey-flow renders it.
- `survey-thermal`: `align_to_thermal_zone()` (survey-currents) clips
  model fields to a thermal zone; survey-flow can render the model
  temperature against the Landsat LST field for comparison frames.

## Format stability promise

- PNG frames: 8-bit RGBA, named `frame_%04d.png`.
- `manifest.json`: schema versioned; v1 readers reject major > 1.
- COG input band order `(speed, u, v, temperature)` follows
  survey-currents and will not change without a manifest major bump.

# Frame Manifest schema v1.0

The frame manifest is the **stable handoff contract** from survey-flow to
survey-animate. A manifest is a JSON document; frame PNG paths are stored
relative to the manifest file's directory so the whole output directory
is portable.

## Document

| Field | Type | Meaning |
|---|---|---|
| `schema` | string | `"survey-flow.frame-manifest/1.0"` — readers must reject unknown major versions |
| `generator` | string | e.g. `"survey-flow 0.1.0"` |
| `created` | string | ISO-8601 creation time (UTC) |
| `fps` | number | Intended playback rate (hint; the encoder may override) |
| `size_px` | `[w, h]` | Frame size in pixels, e.g. `[1080, 1920]` |
| `field_source` | string | Provenance of the vector field, e.g. `"noaa-ofs/LMHOFS"` |
| `n_frames` | integer | `len(frames)`; must match |
| `frames` | array | Ordered frame entries, `frame_index` 0..n-1 sequential |

## Frame entry

| Field | Type | Meaning |
|---|---|---|
| `frame_index` | integer | 0-based, sequential |
| `timestamp_iso` | string | ISO-8601 label for this frame (model time) |
| `png_path` | string | Path to the PNG, relative to the manifest dir when possible |
| `scalar` | string | Scalar rendered, `"temperature"` or `"speed"` |
| `scalar_range` | `[vmin, vmax]` | Colormap range used (fixed across frames) |
| `colormap` | string | Matplotlib colormap name, e.g. `"cividis"` |
| `style` | string | Style preset name, e.g. `"reel-dark"` |
| `render_params` | object | Free-form: `dpi`, `size_px`, `n_particles`, `dt_seconds`, `seed`, `title` |

## Example

```json
{
  "schema": "survey-flow.frame-manifest/1.0",
  "generator": "survey-flow 0.1.0",
  "created": "2026-09-25T22:40:00+00:00",
  "fps": 30.0,
  "size_px": [1080, 1920],
  "field_source": "noaa-ofs/LMHOFS",
  "n_frames": 48,
  "frames": [
    {
      "frame_index": 0,
      "timestamp_iso": "2026-09-16T00:00:00+00:00",
      "png_path": "frames/frame_0000.png",
      "scalar": "temperature",
      "scalar_range": [12.4, 21.8],
      "colormap": "cividis",
      "style": "reel-dark",
      "render_params": {
        "dpi": 100, "size_px": [1080, 1920],
        "n_particles": 1500, "dt_seconds": 3600.0,
        "seed": 7, "title": ""
      }
    }
  ]
}
```

## Reference implementation

`flow.frames.FrameManifest` / `flow.frames.FrameEntry`:

- `FrameManifest.write(path)` — writes with relative PNG paths;
  `FrameManifest.read(path)` — validates schema and sequential indices.
- `FrameManifest.png_paths(base_dir)` — resolved absolute PNG paths.
- `flow.frames.interpolate_times(times_iso, n_frames)` — even ISO labels.

## Versioning

- Minor additions (new optional `render_params` keys) do not bump the
  schema.
- Any breaking change (renamed/removed fields, new required fields)
  bumps to `survey-flow.frame-manifest/2.0`, and v1 readers must refuse
  it with a clear error (implemented in `FrameManifest.read`).

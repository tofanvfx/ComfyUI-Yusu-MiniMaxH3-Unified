[English](README.md) | [中文](README_CN.md)

Online Workflow (CN): http://runninghub.cn/post/2086063010979864577/?inviteCode=rh-v1525  
Online Workflow (Global): https://www.runninghub.ai/zh-cn/post/2086007179703197697/?inviteCode=rh-v1525  
Tutorials on Bilibili / YouTube: @在下鱼酥

# ComfyUI-Yusu-MiniMaxH3-Unified

Unified workflow for MiniMax H3 Text-to-Video, First/Last Frame to Video, and Omni-Modal Reference Video, featuring in-node image, video, and audio uploading with precise trimming.

> This extension is a wrapper around the official ComfyUI `MiniMaxH3ImageToVideo` and `MiniMaxH3ReferenceToVideo` nodes. It organizes inputs, handles media processing, and maps interfaces without modifying the underlying MiniMax H3 inference engine.

## 2026-10-09 Update

- Removed the 15-second cap on single reference audio clips. Uploaded audio and external AUDIO sockets now retain full selections; minimum requirement remains 2 seconds. Reference video limits remain unchanged.

## 2026-09-08 Update

- Aligned with the latest ComfyUI official MiniMax H3 node interfaces: keyword arguments are now uniformly used across Text-to-Video, First/Last Frame, and Omni Reference modes to prevent parameter misplacement if official order changes.
- Fixed an issue in Omni Reference mode where string width/height triggered `unsupported operand type(s) for //: 'str' and 'int'`.
- Normalized width, height, and dynamic duration inputs to numeric values, with clear error messages for invalid dimensions.
- Added regression tests for interface signatures, numeric dimension types, frame counts, and first/last frame passing across all three modes.

## 2026-08-10 Update

- Uploads now use the standard local ComfyUI `/upload/image` asset endpoint.
- The waveform canvas no longer passes click events down to the trimming timeline, resolving an issue where clicking "Load Waveform" shifted the trim playhead.
- When the host has not expanded official Autogrow media groups, only the first child socket is restored as a connectable `IMAGE` / `AUDIO` socket; existing expanded local sockets remain unchanged.
- Media panel width syncs with node width, preventing contents from being compressed to the left after host mounting.
- Each reference audio clip is independently bounded to 2–15 seconds; total multi-track audio duration is no longer merged into a 15-second limit.
- After updating the extension, a full ComfyUI restart is required. A clear notice will appear if frontend and backend versions mismatch during upload.

## 2026-08-09 Update

- Uses local official ComfyUI media path resolution.
- Automatic audio duration mode preserves a fallback manual `duration`.
- Added canvas event isolation and pointer capture to the trimming timeline.
- Cleaned up unused backend functions, single-call wrappers, and legacy trim styles while preserving all existing functionality.

## Features Overview

- Single node supporting 3 operating modes:
  - `text_to_video`: Text-to-Video
  - `first_last_frame`: First/Last Frame to Video
  - `omni_reference`: Omni-Modal Reference (Images, Videos, Audio)
- `clip`, `vae`, and `audio_vae` inputs are always displayed.
- First/last frame and reference media sockets dynamically display according to the selected mode.
- In-node upload, preview, replacement, and trimming of media; Omni Reference panel supports `Ctrl+V` pasting of images, videos, and audio directly into the first available slot.
- Maximum capacity:
  - 9 reference images
  - 3 reference videos
  - 3 paired video audio tracks
  - 3 standalone reference audio tracks
- External ComfyUI `IMAGE` / `AUDIO` sockets take priority over in-node files.
- Automatically calculates video generation duration based on reference audio.
- `duration` input in seconds, automatically converted and aligned to the H3 temporal grid.
- Provides a standard `AUDIO` output for easy downstream preview or saving of the trimmed reference audio.
- Media cards use unified header, preview, and button heights for neat horizontal and vertical alignment.
- Zero telemetry, no external APIs, no background polling, no idle GPU usage.

## Requirements

- A working installation of ComfyUI.
- ComfyUI must include the official MiniMax H3 nodes:
  - `MiniMaxH3ImageToVideo`
  - `MiniMaxH3ReferenceToVideo`
- MiniMax H3 model weights, CLIP, and VAE; an Audio VAE is also required when reference audio is used.
- No separate `requirements.txt` needed; uses standard ComfyUI environment dependencies: PyTorch, Pillow, PyAV, NumPy, and aiohttp.
- System `ffprobe` will be prioritized for media probing if installed, falling back to PyAV if absent.

## Installation

### Method 1: Git Clone

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/yusu-02/ComfyUI-Yusu-MiniMaxH3-Unified.git
```

### Method 2: Manual Installation

1. Download repository ZIP.
2. Extract and ensure the directory structure is:

```text
ComfyUI/
└── custom_nodes/
    └── ComfyUI-Yusu-MiniMaxH3-Unified/
        ├── __init__.py
        ├── nodes.py
        ├── media.py
        └── web/
```

3. Restart ComfyUI.
4. Press `Ctrl+F5` in the browser to refresh frontend cache.
5. Search in the node menu:

```text
Yusu / MiniMax / H3 / Yusu MiniMax H3 Unified
```

When upgrading from an older version, it is recommended to completely remove the old folder before copying the new one to prevent stale JavaScript or Python files.

## Important: Model Connection Guidelines

This node **does not have a `MODEL` input or output**.

The model loader should connect directly to downstream official sampling components (such as Guider, Scheduler, or Sampler); this node only outputs conditioning and the combined AV latent.

```text
Model Loader ───────────────→ Guider / Scheduler / Sampler
CLIP ────────→ Unified.clip
VAE ─────────→ Unified.vae
Unified.positive ───────────→ Guider.conditioning
Unified.av_latent ──────────→ Sampler.latent_image
```

Match the mode with the appropriate model family:

- `text_to_video`, `first_last_frame`: Use the corresponding FL2VA model.
- `omni_reference`: Use the corresponding Ref2VA model.

## Node Interfaces

### Sockets Always Displayed

| Socket | Type | Description |
|---|---|---|
| `clip` | `CLIP` | Used for prompt text encoding |
| `vae` | `VAE` | Used for image/video latent processing |
| `audio_vae` | `VAE` | Always shown; only required when reference audio is present |
| `prompt` | `STRING` | Supports external text nodes and dynamic prompts |
| `width` | `INT` | Output width, must be a multiple of 32 |
| `height` | `INT` | Output height, must be a multiple of 32 |
| `duration` | `FLOAT` | Target duration in seconds (allows 0, no upper limit) |
| `Auto Length From Audio` | `BOOLEAN` | In reference mode, auto-computes duration from longest audio |

### Sockets Displayed by Mode

#### `text_to_video`

No media sockets; only uses prompt, dimensions, and `duration`.

#### `first_last_frame`

| Socket | Type | Description |
|---|---|---|
| `first_frame` | `IMAGE` | Optional first frame (external input takes priority over in-node upload) |
| `last_frame` | `IMAGE` | Optional last frame (external input takes priority over in-node upload) |

At least one frame (first or last) must be provided.

#### `omni_reference`

| Socket | Type | Max Slots | Description |
|---|---|---:|---|
| `ref_image_0...` | `IMAGE` | 9 | Reference images |
| `ref_video_0...` | `IMAGE` batch | 3 | 24 FPS reference video frame batch |
| `ref_video_audio_0...` | `AUDIO` | 3 | Paired audio track for matching reference video |
| `ref_audio_0...` | `AUDIO` | 3 | Standalone reference audio |
| `ref_image_size` | `COMBO` | 1 | `match` or `max` |

### Outputs

| Socket | Type | Description |
|---|---|---|
| `positive` | `CONDITIONING` | Connects to conditioning input of Guider nodes |
| `av_latent` | `LATENT` | Combined video/audio latent, connects to sampler chain |
| `audio` | `AUDIO` | Longest trimmed audio actually used as reference (None if no audio) |

`audio` outputs the reference audio, NOT the final generated video soundtrack.

## The Three Modes

### 1. Text to Video

Select:

```text
mode = text_to_video
```

Requires only:

- `clip`
- `vae`
- prompt
- width, height
- `duration`

Any media uploaded inside the node is ignored.

### 2. First / Last Frame to Video

Select:

```text
mode = first_last_frame
```

Provide first frame, last frame, or both:

- Connect an external `IMAGE`;
- Or upload images directly in the node panel.

If both an external connection and an in-node file exist for the same slot, the external connection takes priority.

### 3. Omni-Modal Reference Video

Select:

```text
mode = omni_reference
```

Combine freely:

- Reference images
- Reference videos
- Embedded video soundtracks
- Video paired audio tracks
- Standalone reference audio

Whenever any reference audio is used, `audio_vae` must be connected.

## In-Node Media & External Socket Mapping

In-node slots start at 1, while ComfyUI external sockets are 0-indexed:

```text
In-node Ref Image 1        ↔ ref_image_0
In-node Ref Video 1        ↔ ref_video_0
Video 1 Paired Audio       ↔ ref_video_audio_0
In-node Standalone Audio 1 ↔ ref_audio_0
```

External connections override corresponding in-node slots without duplicating references.

Video soundtrack priority:

```text
External ref_video_audio_N
        ↓
In-node "Video N Paired Audio"
        ↓
Embedded soundtrack in Reference Video
```

`ref_video_audio_N` must be paired with matching `ref_video_N`. Orphan paired audio sockets are rejected before decoding to avoid wasting CPU and memory.

## Prompt Tags

In Omni Reference mode, the node panel displays the active tag mapping:

```text
<Picture 1> ← ref_image_0
<Audio 1>   ← ref_audio_0
<Video 1>   ← ref_video_0
```

The prompt must explicitly use the desired reference tags, for example:

```text
Using the voice and cadence of <Audio 1>,
have the character in <Picture 1> speak naturally.
```

Notes:

- External sockets start at index 0; prompt tags start at index 1.
- Video paired audio participates in tag ordering.
- Do not guess `<Audio n>` based on socket suffixes; refer to the mapping shown in the panel.
- When prompts originate from external text nodes, the plugin attempts to read the upstream text; for dynamically generated text that cannot be read in the frontend, the backend validates against the final runtime prompt without false warnings.
- Both English tags (`@Picture 1`, `@Video 1`, `@Audio 1`) and original Chinese tags (`@图片 1`, `@视频 1`, `@音频 1`) are supported.

## Duration Calculation

### Manual Duration

`duration` is specified in seconds:

```text
FLOAT (duration)
```

Calculation process:

```text
Target seconds
→ round(seconds × 24 FPS)
→ Aligned to H3's 17k+5 frame grid
→ Creates AV latent
```

Example:

```text
5.000s
→ 120 frames
→ Aligned to 124 frames
→ Actual ~5.167s
```

Entering `0` seconds will not produce a zero-frame latent, but rather the minimum 5 frames (~`0.208`s) permitted by H3's temporal architecture.

The plugin does not cap maximum output duration. Extra-long generations linearly increase RAM, VRAM, sampling time, and file size. Excessively large values may lead to out-of-memory errors or driver resets.

### Auto Length From Audio

Applies only to `omni_reference` mode.

When "Auto Length From Audio" is enabled:

- The `duration` widget is disabled and greyed out;
- The longest effective trimmed reference audio track is selected;
- Duration is automatically converted at 24 FPS and aligned to H3's frame grid;
- Falls back to the saved manual seconds if no valid reference audio is present.

Text-to-Video, First/Last Frame, and silent reference workflows do not require extra audio duration calculation nodes.

## Reference Media Limits

The plugin enforces the following reference media validation:

- Each reference video: 2–15 seconds.
- Total reference video duration: max 15 seconds.
- Each reference audio track: at least 2 seconds, no upper limit.
- Multiple reference audio tracks are validated individually; combined duration is not limited.
- Trimming sliders allow arbitrary selection; validation occurs during execution against the trimmed range.
- Dimensions must be multiples of 32.
- Maximum upload size per file: 512 MiB.
- Maximum image resolution: 100,000,000 pixels.
- Maximum audio sample rate: 384 kHz.

Note that these are limits for *reference media*, distinct from the unrestricted output generation `duration`.

## Audio Processing

- Trimming interval uses half-open range `[In, Out)`.
- Mono audio is automatically duplicated to stereo.
- Multi-channel audio retains the first two channels.
- Waveform values are clamped to `[-1, 1]`.
- Empty audio, pure silence, NaN, or infinite values raise immediate validation errors.
- Long in-node audio decodes only the trimmed range without loading the entire file into memory first.
- Audio/video timing offsets are synchronized to the video timeline, padding silence when necessary.
- Waveform previews do not auto-decode by default; click the waveform area to decode on-demand.

## Video Processing

- Video decoding standardizes to packed RGB24.
- Handles rotation metadata and non-square pixel aspect ratios (SAR).
- Resamples to 24 FPS online.
- Decoding adapts directly to the H3 reference canvas.
- Only materializes the frame prefix actually needed for conditioning, reducing memory pressure from high-framerate or long videos.

## Uploaded Files Location

Local ComfyUI stores files uploaded in the node at:

```text
ComfyUI/input/minimax_h3_unified/
```

Clicking "Delete" in the node removes only the slot reference, leaving the file on disk to avoid breaking other workflows that might reference the same asset. Unused files can be cleaned up manually.

Upload validation checks:

- File extension
- MIME type
- Authentic image format verification
- Video / audio streams
- File size
- Path security (preventing directory traversal)

Files failing validation will not be assigned to slot states.

## Performance Design

- Prompt modifications refresh only audio tag status without rebuilding the entire media panel.
- Trimming slider updates coalesce onto requestAnimationFrame.
- Images use lazy loading and async decoding.
- Video and audio previews preload metadata only.
- Waveform cache stores only downsampled peaks, never full `AudioBuffer` objects.
- Waveform cache is capped at 12 entries.
- Audio exceeding 64 MiB or 5 minutes disables browser waveform decoding to conserve RAM.
- Media probing executes in a thread pool, never blocking the main ComfyUI web server.
- Zero background polling, persistent worker threads, or idle GPU operations.

## Mode Switching Notes

`clip`, `vae`, and `audio_vae` are always retained.

The following sockets are dynamically created or removed based on mode:

- `first_frame`
- `last_frame`
- `ref_image_*`
- `ref_video_*`
- `ref_video_audio_*`
- `ref_audio_*`

When ComfyUI removes dynamic sockets, existing external connections to those sockets may disconnect. When switching modes, reconnect dynamic media sockets as needed; in-node media states remain safely preserved in the workflow.

## FAQ

### Audio is connected, why does the panel say it is not referenced?

Verify the following:

1. Mode is set to `omni_reference`;
2. `audio_vae` is connected;
3. At least one reference image or video is present;
4. The prompt includes the `<Audio n>` tag shown in the panel;
5. The trimmed audio is not silent and meets duration requirements (>= 2s).

### Why doesn't the output duration exactly match input seconds?

H3's temporal architecture requires frame counts of `17k + 5`. The node rounds up to the nearest valid frame grid value. The panel previews target seconds, effective frames, and actual seconds.

### Why is there no `MODEL` socket?

The model does not need to pass through this node. Connect the model loader directly to your Guider, Scheduler, or Sampler. This node only provides `positive` and `av_latent`.

### Why doesn't "Delete" delete the file from disk?

The same file might be referenced by other workflows. To prevent accidental asset loss, only the slot reference is removed. Physical files can be deleted manually from `ComfyUI/input/minimax_h3_unified/`.

### Why isn't the `audio` output the generated video soundtrack?

The `audio` output provides the trimmed reference audio that was passed into the reference encoder. The final generated video soundtrack must be obtained from sampling and decoding the AV latent.

### What if the UI looks outdated after upgrading?

1. Ensure the old plugin directory was completely removed;
2. Restart the ComfyUI backend;
3. Press `Ctrl+F5` in your browser;
4. Clear browser site cache if necessary.

## Repository Structure

```text
ComfyUI-Yusu-MiniMaxH3-Unified/
├── __init__.py
├── media.py
├── nodes.py
├── web/
│   ├── minimax_h3_unified.js
│   └── minimax_h3_unified.css
├── workflows/
│   ├── H3_Unified_Workflow.json
│   └── H3全能工作流.json
└── tests/
    ├── test_plugin.py
    └── test_frontend.mjs
```

- `__init__.py`: Plugin entry point and upload inspection route.
- `media.py`: Path security, media probing, trimming, decoding, and validation.
- `nodes.py`: Node schema, mode routing, slot mapping, and official node calls.
- `web/`: Node panel UI, upload interactions, dynamic sockets, and styles.
- `workflows/`: Ready-to-use ComfyUI workflow JSON files.
- `tests/`: Backend and frontend regression test suites (not run during ComfyUI startup).

## Development & Testing

Backend tests:

```bash
python -m unittest discover \
  -s custom_nodes/ComfyUI-Yusu-MiniMaxH3-Unified/tests \
  -v
```

Frontend tests:

```bash
node custom_nodes/ComfyUI-Yusu-MiniMaxH3-Unified/tests/test_frontend.mjs
```

Syntax checking:

```bash
python -m py_compile \
  custom_nodes/ComfyUI-Yusu-MiniMaxH3-Unified/__init__.py \
  custom_nodes/ComfyUI-Yusu-MiniMaxH3-Unified/media.py \
  custom_nodes/ComfyUI-Yusu-MiniMaxH3-Unified/nodes.py

node --check \
  custom_nodes/ComfyUI-Yusu-MiniMaxH3-Unified/web/minimax_h3_unified.js
```

## Known Limitations

- Relies on current official ComfyUI MiniMax H3 node interfaces; breaking upstream changes may require updates.
- Dynamic sockets may disconnect external links when toggling modes.
- High-resolution, long reference videos form large `IMAGE` batches, consuming system RAM.
- Uncapped duration does not guarantee model quality across all lengths beyond official training regimes.
- Reference audio conditioning does not guarantee verbatim content reproduction or perfect voice replication.
- Corrupted, missing-timestamp, or non-standard media streams may fail PyAV/FFmpeg decoding.

## Security & Privacy

- No telemetry collection.
- No media, prompts, or workflows sent to external servers.
- Frontend network requests only access standard local ComfyUI upload, plugin inspect, and `/view` endpoints.
- No mining, background tracking, daemon polling, or automated test execution on startup.

---

Feel free to submit reproducible issues on GitHub. Please include:

- ComfyUI version or commit hash
- Operating System
- Python, PyTorch, PyAV versions
- Mode used
- Full console error log
- Minimal reproducible workflow

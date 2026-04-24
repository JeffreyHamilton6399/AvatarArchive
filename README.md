# AvatarArchive

> A fan-made personal media hub for the entire Avatar universe.

Built by [Jeffrey Creates](https://www.youtube.com/@Jeffrey_Creates) — vanilla web tech, no frameworks, no servers.

---

## Pages

| File | Description |
|------|-------------|
| `index.html` | Home — all series, films, and features in one place |
| `atla.html` | Avatar: The Last Airbender (2005–2008) · Books 1–3 · 61 episodes |
| `kora.html` | The Legend of Korra (2012–2014) · Books 1–4 · 52 episodes |
| `liveshow.html` | Netflix Live Action Series (2024) · Seasons 1–2 |
| `movie2026.html` | Aang, The Last Airbender · 2026 animated film |
| `movie2010.html` | The Last Airbender · 2010 live action film |
| `books.html` | Avatar graphic novels & comics (Dark Horse) |
| `games.html` | ATLA games collection |
| `merch.html` | Official merchandise — Paramount, Netflix, Nick, Funko, and more |

---

## Features

**Video Player**
Custom-built player with skip-intro detection, next-episode auto-advance, and per-episode progress memory via `localStorage`. Full keyboard shortcut support for playback, volume, fullscreen, and captions.

**AI Captions**
The **AI CC** button runs Whisper Tiny (via Transformers.js + WebAssembly) entirely in the browser — no server, no upload. Audio is captured through the Web Audio API at the browser's native sample rate and software-downsampled to 16 kHz before model inference.

- ~39 MB of model weights downloaded on first use, then permanently cached in IndexedDB
- Audio processed in 30-second chunks with captions appearing progressively
- Completed caption sets cached in `localStorage` per episode for instant replay
- Cache keys are episode-scoped, so switching episodes never serves stale captions

**SRT Subtitles**
Standard SRT files fetched automatically at load time. The CC button toggles them; AI CC operates independently.

**Cross-Series Search**
Debounced search across all 113+ episodes, films, games, and merchandise — results appear inline with per-series color coding.

**Themes**
Four built-in themes — Dark, Parchment, Water, Earth — driven by CSS custom properties and persisted in `localStorage`.

**Ambient Sound**
Optional looping ambient audio with fade-in/out, triggered on user gesture to respect browser autoplay policies. Toggled from the settings panel.

**PWA**
Fully installable on mobile and desktop via Web App Manifest and inline service worker. Offline shell caching covers all HTML pages.

---

## AI Captions — Technical Notes

The caption engine lives in `whisper-captions.js`.

- **Native-rate AudioContext** — Created at the browser's default sample rate (44.1 or 48 kHz). Forcing 16 kHz here would degrade or silence video playback entirely.
- **Software downsampling** — PCM is resampled from the native rate to 16 kHz via a linear averaging function (`_downsample`) before being passed to Whisper. Playback quality is never affected.
- **Lazy episode keys** — The episode identifier is resolved via a getter passed to `injectButton`, so the cache key always reflects the currently loaded episode — even after switching without a page refresh.
- **Clean capture lifecycle** — `loadEpisode()` calls `WhisperCaptions._stopCapture()` before changing the video source, preventing the `ScriptProcessorNode` from processing stale audio after a track change.

---

## Stack

- Vanilla HTML, CSS, JavaScript — zero frameworks
- Transformers.js + Whisper Tiny — in-browser AI captions
- Web Audio API — real-time audio capture and processing
- `localStorage` — progress, caption cache, and user preferences
- PWA — service worker offline shell caching

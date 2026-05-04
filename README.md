# AvatarArchive

> The entire Avatar universe — one fan-made media hub.

Built by [Jeffrey Creates](https://www.youtube.com/@Jeffrey_Creates) &nbsp;·&nbsp; Vanilla HTML, CSS & JavaScript &nbsp;·&nbsp; No frameworks &nbsp;·&nbsp; No servers

---

## Overview

AvatarArchive is a fully self-contained fan site bringing together every corner of the Avatar universe — the original animated series, The Legend of Korra, the Netflix live action adaptation, both films, the Dark Horse graphic novel library, games, and merchandise — all under one roof with a custom-built video player, comic reader, and a suite of quality-of-life features built from scratch in plain HTML, CSS, and JavaScript.

---

## Pages

| File | Description |
|------|-------------|
| `index.html` | Home — world map splash, cross-series search, and hub card navigation |
| `atla.html` | Avatar: The Last Airbender (2005–2008) · Books 1–3 · 61 Episodes |
| `kora.html` | The Legend of Korra (2012–2014) · Books 1–4 · 52 Episodes |
| `liveshow.html` | Netflix Live Action Series (2024) · Seasons 1–2 |
| `movie2026.html` | Aang, The Last Airbender · 2026 animated film · with live countdown timer |
| `movie2010.html` | The Last Airbender · 2010 live action film |
| `books.html` | Avatar graphic novels & comics (Dark Horse) |
| `games.html` | ATLA games collection |
| `merch.html` | Official merchandise — Paramount, Netflix, Nick, Funko, and more |
| `timeline.html` | Full in-universe chronological timeline — all eras, accordion layout, element PNG spine markers |
| `familytrees.html` | Interactive pan-and-zoom family tree canvas — all major lineages with bridges |

---

## Features

### Password Gate
Every page is protected before anything renders. Authentication state is stored in `localStorage` so users only need to enter the password once across all pages.

### Custom Video Player
A fully custom-built player with skip-intro detection, next-episode auto-advance with a fill-bar countdown, per-episode progress memory, and resume-on-load. The floating pill UI includes a seek bar, volume control, playback speed, brightness and contrast adjustment, fullscreen, and SRT caption support.

### SRT Captions
Each episode and film automatically fetches its `.srt` caption file on load. The CC button toggles captions on and off with a smooth fade transition.

### Episode Browser
A Netflix-style series selector — a pill dropdown that switches between Books or Seasons — with an episode grid displaying per-episode progress bars and a watched checkmark that appears at 90%+ completion.

### PDF Comic Reader
PDF.js renders graphic novels as two-page spreads. Pages turn via buttons, keyboard arrows, mouse drag, or touch swipe. Includes zoom, page-jump input, fullscreen with an iOS fallback, and a download progress indicator.

### Cross-Series Search
A debounced search bar on the home page queries all 113+ episodes across ATLA, Korra, the films, games, and merchandise simultaneously — with per-series color coding on results.

### World Map Splash
The home page opens with a full-screen animated world map before transitioning into the hub card layout.

### Ambient Sound
Optional looping background audio powered by the Web Audio API. Plays a short intro cue first, then crossfades into the ambient loop, starting at a random position each session. Volume and mute state persist in `localStorage`.

### Themes
Four built-in visual themes — Dark, Parchment, Water, and Earth — applied via CSS custom properties and persisted in `localStorage`. Accessible at any time via the gear icon present on every page.

### Ambient Particles
Floating bending element symbols — air, water, earth, and fire — drift across the background using Canvas 2D with orbit, wave, and drift movement modes. The canvas pauses automatically when the browser tab is hidden.

### Continue Watching
Hub cards on the home page display a color-coded progress strip and update their call-to-action to "Resume" whenever an episode has been started but not finished.

### Star Rating
Film pages include a 5-star interactive rating widget. Ratings are stored per title in `localStorage` and persist across visits.

### Countdown Timer
The 2026 film page features a live countdown displaying days, hours, minutes, and seconds remaining until the October 9, 2026 Paramount+ premiere.

### Interactive Family Trees
A pan-and-zoom canvas displaying all major lineages across the Avatar universe — Fire Nation Royal Line, Avatar Cycle, Water Tribes, Beifong family, and more. Each node is a tappable card with element colour-coding and a bottom-sheet detail panel. Shared characters are linked by dashed SVG bridges. Includes live search with match highlighting and collapsible subtrees.

### Full Chronological Timeline
An accordion timeline spanning from Avatar Wan's era (~10,000 BG) through Korra's era. Each Avatar's age has nested subfolders of events. Spine markers use real element PNG images instead of plain dots. Every event opens a detail panel with full description.

### Progressive Web App
Fully installable on mobile and desktop via an inline Web App Manifest and a service worker registered from a Blob URL. Offline shell caching covers all HTML pages so the site loads without a network connection after the first visit.

---

## Atmosphere & Performance Modules (`shared.js` + `shared.css`)

All atmosphere effects are bundled in `shared.js` and `shared.css` and run on every page. They respect `prefers-reduced-motion` and are deferred via `requestIdleCallback` so they never compete with first paint.

| # | Feature | How it works |
|---|---------|-------------|
| 9 | **Cursor Ripple** | On every click, a coloured radial bloom appears at the cursor position. Colour is inherited from the nearest element accent (`--ec`, `--accent`). Uses `mix-blend-mode: screen` so it never looks jarring. |
| 10 | **Page Transition** | Internal link clicks trigger a 220 ms `opacity: 0` fade before navigation. The fade-in on arrival is handled by `@keyframes _avatarPageIn` in `shared.css`. |
| 11 | **Shooting Stars** | Every 18–45 seconds a slow golden streak crosses the existing `#particleCanvas` diagonally. Pauses when tab is hidden. Zero extra DOM cost. |
| 12 | **Dynamic Vignette** | A `radial-gradient` div lerps toward the mouse position at 4% per frame — the glow lags far behind the cursor, giving a soft ambient depth shift. `mix-blend-mode: screen`. |
| 13 | **Scroll Parallax** | The `.bg-layer` translates upward at 18% of scroll offset, giving an illusion of depth behind content. One `transform` per scroll frame. |
| 14 | **Time-of-Day Tint** | Checks `new Date().getHours()` on load and places a single tint over the page — amber at dawn, near-neutral by day, golden-orange at dusk, deep blue in the evening, indigo late at night. |
| 15 | **Card Shimmer** | A `::after` pseudo-element sweeps a 4% opacity highlight stripe across `.hub-card` on hover via `background-position` transition. Zero JS per-frame cost. |
| 16 | **Focus Glow** | `:focus-visible` shows a `box-shadow`-based ring matching the element colour of the focused item. Only appears for keyboard users, never on click. |

### `shared.css` Enhancements
- **Richer `bg-layer::after`** — five-stop gradient for a more atmospheric fade (darker top and bottom, lighter mid)
- **Particle canvas edge fade** — `mask-image` radial gradient makes symbols fade at screen edges
- **Page fade-in** — `body { animation: _avatarPageIn .28s }` on every page arrival
- **Custom scrollbar** — thin gold-tinted 4px scrollbar replacing browser default
- **Text selection** — `::selection` uses water blue at 28% opacity

---

## Keyboard Shortcuts

Available on all video pages. Press `?` at any time to display the shortcuts overlay.

| Key | Action |
|-----|--------|
| `Space` / `K` | Play / Pause |
| `←` / `→` | Seek ±5 seconds |
| `↑` / `↓` | Volume ±10% |
| `M` | Mute / Unmute |
| `F` | Toggle Fullscreen |
| `C` | Toggle Captions |
| `N` | Next Episode |
| `?` | Show Shortcuts Overlay |

---

## Tech Stack

| Technology | Usage |
|------------|-------|
| HTML / CSS / JavaScript | Everything — zero frameworks |
| PDF.js | Graphic novel two-page spread rendering |
| Web Audio API | Ambient music with intro cue and crossfade; UI SFX |
| Canvas 2D | Animated background particles + shooting stars |
| `localStorage` | Progress, preferences, auth, ratings |
| PWA / Service Worker | Installability and offline shell caching |
| `requestIdleCallback` | Defer atmosphere modules to after first paint |
| `mix-blend-mode: screen` | Ripple, vignette, and ToD tint without washing out content |

---

## Video Files

All video files are stored as `.mp4` (H.264 + AAC) and hosted via GitHub Releases. This format ensures native playback in all modern browsers without any plugins or additional libraries.

---

*Fan-made &nbsp;·&nbsp; Built with care by [Jeffrey Creates](https://www.youtube.com/@Jeffrey_Creates)*

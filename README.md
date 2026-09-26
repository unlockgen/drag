# Churchracersja Drag Tree

An installable drag racing reaction trainer built with HTML, CSS, JavaScript, and the Web Audio API.

## Play

Hold LAUNCH to stage, keep holding through the amber lights, and release on green. Early launches show a red light. Choose Sportsman (.500-second intervals) or Pro (.400-second interval) timing.

## Features

- Churchracersja branding and a track-style LED starting tree
- Reaction times, red-light detection, and recent-run history
- Best scores stored in the current browser using localStorage
- Synthesized engine, countdown, launch, and foul sounds with a saved mute setting
- App manifest, home-screen icons, and an offline service worker

## Run locally

No build tools or dependencies are required. From this folder run:

```sh
python3 -m http.server 8080
```

Open http://localhost:8080. For installation and offline support on a phone, deploy these files through an HTTPS static host.

## Files

- `index.html`: game interface, styles, timing, controls, and synthesized audio
- `sw.js`: offline asset caching; bump the cache version when changing releases
- `manifest.webmanifest`: installable app metadata
- `icon.svg` and PNG files: app icons

## Hosting and development

This repository is a portable source copy. The current Sites deployment is separate; GitHub commits do not automatically update it. To deploy elsewhere, publish this repository's root directory with an HTTPS static host.

## Notes

Scores and preferences stay in each browser and are not synced between devices. Browser scheduling, display refresh rate, and touch latency affect measured reaction times; this is a practice game, not certified racing timing equipment. Sound effects are synthesized, not recordings. Test sound and installation on physical iPhones before an App Store release.


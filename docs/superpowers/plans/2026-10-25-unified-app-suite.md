# Songdo AI Academy All-in-One Unified App Suite Implementation Plan

**Date**: 2026-10-25
**Feature**: Unified Single-Page Application Platform (`index.html` & `app.html`)

## Goal
Integrate all fragmented project pages (`landing.html`, `presentation.html`, `creator.html`, `courseware/index.html`, `process.html`) into a single, cohesive, modern Web Application Portal. Visiting `http://127.0.0.1:3000/` immediately launches the unified suite with tab navigation, responsive viewport controls (Desktop/Tablet/Mobile), Zen mode, and PWA desktop installation support.

---

## Tasks & Steps

### Task 1: Backup & Preserve Legacy Assets
- Rename existing `index.html` (old Devil's Advocate demo) to `devils_advocate_legacy.html`.

### Task 2: Build Web App Manifest & App Icons
- Create `manifest.json` for PWA desktop installation (`display: standalone`, `theme_color: #0f172a`).

### Task 3: Build the Unified App Shell (`index.html` & `app.html`)
- Header: Brand logo, status ping, navigation tabs (`#/landing`, `#/presentation`, `#/studio`, `#/courseware`, `#/process`).
- Multi-viewport container: State-preserved iframes with instant tab switching.
- Device emulator toolbar: Desktop (100%), Tablet (768px), Mobile (375px).
- Zen/Fullscreen mode toggle (`F`), External tab launcher (`↗`), PDF Print trigger (`🖨️`).
- Keyboard shortcuts (`1`~`5`, `F`, `O`, `?`).

### Task 4: Server Update & Verification
- Verify `server.py` routing for root `/`, `manifest.json`, and all sub-iframes.
- Test endpoint health (200 OK) and UI navigation via automated HTTP testing.
- Test responsive resizing and tab state retention.

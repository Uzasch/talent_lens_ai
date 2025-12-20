# Story 1.1: Frontend Project Setup

Status: review

## Story

As a **developer**,
I want **the React frontend project initialized with all dependencies and proper configuration**,
so that **I can start building UI components for TalentLens AI**.

## Acceptance Criteria

1. **AC1.1.1:** Vite + React project created in `frontend/` directory
2. **AC1.1.2:** Tailwind CSS configured with dark theme CSS variables matching UX specification
3. **AC1.1.3:** shadcn/ui initialized with dark theme configuration
4. **AC1.1.4:** All npm dependencies installed: react-router-dom, axios, recharts, react-dropzone, lucide-react
5. **AC1.1.5:** Project runs successfully on localhost:5173
6. **AC1.1.6:** Folder structure matches architecture.md: `components/`, `pages/`, `services/`, `lib/`

## Tasks / Subtasks

- [x] **Task 1: Create Vite + React project** (AC: 1.1.1)
  - [x] Run `npm create vite@latest frontend -- --template react`
  - [x] Navigate to frontend directory
  - [x] Verify initial project runs with `npm run dev`

- [x] **Task 2: Install and configure Tailwind CSS** (AC: 1.1.2)
  - [x] Install tailwindcss, postcss, autoprefixer
  - [x] Initialize Tailwind with `npx tailwindcss init -p`
  - [x] Configure `tailwind.config.js` with content paths
  - [x] Add Tailwind directives to `src/index.css`
  - [x] Add Spotify Dark theme CSS variables to `:root` in `index.css`:
    ```css
    :root {
      --background: 0 0% 7%;
      --foreground: 0 0% 100%;
      --card: 0 0% 16%;
      --card-foreground: 0 0% 100%;
      --primary: 141 76% 48%;
      --primary-foreground: 0 0% 100%;
      --secondary: 0 0% 16%;
      --secondary-foreground: 0 0% 70%;
      --muted: 0 0% 25%;
      --muted-foreground: 0 0% 70%;
      --accent: 141 76% 48%;
      --accent-foreground: 0 0% 100%;
      --destructive: 350 89% 49%;
      --destructive-foreground: 0 0% 100%;
      --border: 0 0% 25%;
      --input: 0 0% 25%;
      --ring: 141 76% 48%;
      --radius: 0.5rem;
    }
    ```

- [x] **Task 3: Initialize shadcn/ui** (AC: 1.1.3)
  - [x] Run `npx shadcn@latest init`
  - [x] Select dark theme during initialization
  - [x] Verify `components.json` is created
  - [x] Verify `lib/utils.js` is created with `cn` helper

- [x] **Task 4: Install project dependencies** (AC: 1.1.4)
  - [x] Run `npm install react-router-dom axios recharts react-dropzone lucide-react`
  - [x] Verify all packages in `package.json`

- [x] **Task 5: Create folder structure** (AC: 1.1.6)
  - [x] Create `src/components/` directory
  - [x] Create `src/pages/` directory
  - [x] Create `src/services/` directory
  - [x] Verify `src/lib/` exists (created by shadcn)

- [x] **Task 6: Create placeholder files**
  - [x] Create `src/services/api.js` with axios instance:
    ```javascript
    import axios from 'axios';

    const api = axios.create({
      baseURL: 'http://localhost:5000/api',
    });

    export default api;
    ```
  - [x] Create placeholder page components in `src/pages/`:
    - `HomePage.jsx`
    - `DashboardPage.jsx`
    - `HistoryPage.jsx`

- [x] **Task 7: Verify project runs** (AC: 1.1.5)
  - [x] Run `npm run dev`
  - [x] Confirm app loads at http://localhost:5173
  - [x] Verify no console errors
  - [x] Verify dark theme background is applied

## Dev Notes

### Architecture Alignment

This story implements the frontend foundation per architecture.md:
- **Framework:** React 18 with Vite (fast HMR, modern tooling)
- **Styling:** Tailwind CSS with shadcn/ui components
- **Theme:** Spotify Dark (#121212 background, #1DB954 primary)
- **Routing:** React Router v6 (configured in Story 1.5)

### Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Route-level components
│   ├── services/       # API service layer
│   ├── lib/            # Utilities (shadcn cn helper)
│   ├── App.jsx         # Root component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles + CSS variables
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── components.json     # shadcn configuration
```

### CSS Variables (from UX Specification)

The Spotify Dark theme uses HSL format for shadcn/ui compatibility:
- Primary green: `141 76% 48%` (#1DB954)
- Background: `0 0% 7%` (#121212)
- Card: `0 0% 16%` (#282828)
- Border: `0 0% 25%` (#404040)

[Source: docs/ux-design-specification.md#Section-9.1]

### Dependencies Purpose

| Package | Purpose | Used In |
|---------|---------|---------|
| react-router-dom | Client-side routing | Story 1.5 |
| axios | HTTP client for API calls | All API stories |
| recharts | Charts for dashboard | Epic 5 |
| react-dropzone | File upload component | Epic 2 |
| lucide-react | Icon library | All UI stories |

### Testing Notes

- **Manual verification:** Run `npm run dev` and check localhost:5173
- **Automated tests:** Deferred to Epic 5 (Playwright for E2E)
- **Coverage:** No unit tests required for setup story

[Source: docs/sprint-artifacts/tech-spec-epic-1.md#Test-Strategy-Summary]

### References

- [Source: docs/architecture.md#Frontend-Stack]
- [Source: docs/ux-design-specification.md#Section-9.1]
- [Source: docs/sprint-artifacts/tech-spec-epic-1.md#Story-1.1]
- [Source: docs/epics.md#Story-1.1]

## Dev Agent Record

### Context Reference

None (proceeded without story context file)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Used Tailwind v3 instead of v4 for shadcn/ui compatibility
- Added jsconfig.json and vite alias config for @ import paths
- Restored Spotify Dark theme CSS variables after shadcn init overwrote them

### Completion Notes List

- All 7 tasks completed successfully
- All 6 acceptance criteria satisfied
- Project builds without errors (`npm run build` passes)
- Dev server runs on localhost:5173
- Spotify Dark theme applied with primary green (#1DB954)

### File List

**Created:**
- frontend/ (entire directory)
- frontend/package.json
- frontend/vite.config.js
- frontend/tailwind.config.js
- frontend/postcss.config.js
- frontend/jsconfig.json
- frontend/components.json
- frontend/src/index.css
- frontend/src/App.jsx
- frontend/src/main.jsx
- frontend/src/lib/utils.js
- frontend/src/services/api.js
- frontend/src/pages/HomePage.jsx
- frontend/src/pages/DashboardPage.jsx
- frontend/src/pages/HistoryPage.jsx
- frontend/src/components/ (directory)

**Deleted:**
- frontend/src/App.css (unused Vite boilerplate)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |

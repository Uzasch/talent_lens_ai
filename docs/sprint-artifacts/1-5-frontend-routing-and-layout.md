# Story 1.5: Frontend Routing and Layout

Status: review

## Story

As a **user**,
I want **to navigate between the three main screens of the application**,
so that **I can access all features of TalentLens AI**.

## Acceptance Criteria

1. **AC1.5.1:** Route "/" shows HomePage placeholder component
2. **AC1.5.2:** Route "/dashboard/:sessionId" shows DashboardPage placeholder component
3. **AC1.5.3:** Route "/history" shows HistoryPage placeholder component
4. **AC1.5.4:** Navbar component with navigation links is visible on all pages
5. **AC1.5.5:** Spotify Dark theme (CSS variables) is applied globally

## Tasks / Subtasks

- [x] **Task 1: Configure React Router** (AC: 1.5.1, 1.5.2, 1.5.3)
  - [x] Update `App.jsx`:
    ```jsx
    import { BrowserRouter, Routes, Route } from 'react-router-dom';
    import Navbar from './components/Navbar';
    import HomePage from './pages/HomePage';
    import DashboardPage from './pages/DashboardPage';
    import HistoryPage from './pages/HistoryPage';

    function App() {
      return (
        <BrowserRouter>
          <div className="min-h-screen bg-background text-foreground">
            <Navbar />
            <main className="container mx-auto px-4 py-8">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/dashboard/:sessionId" element={<DashboardPage />} />
                <Route path="/history" element={<HistoryPage />} />
              </Routes>
            </main>
          </div>
        </BrowserRouter>
      );
    }

    export default App;
    ```

- [x] **Task 2: Create HomePage placeholder** (AC: 1.5.1)
  - [x] Create `src/pages/HomePage.jsx`

- [x] **Task 3: Create DashboardPage placeholder** (AC: 1.5.2)
  - [x] Create `src/pages/DashboardPage.jsx` with useParams for sessionId

- [x] **Task 4: Create HistoryPage placeholder** (AC: 1.5.3)
  - [x] Create `src/pages/HistoryPage.jsx`

- [x] **Task 5: Create Navbar component** (AC: 1.5.4)
  - [x] Create `src/components/Navbar.jsx` with active link highlighting

- [x] **Task 6: Verify theme is applied** (AC: 1.5.5)
  - [x] Confirm `index.css` has CSS variables from Story 1.1
  - [x] Verify dark background (#121212) is applied to body
  - [x] Verify primary green (#1DB954) is used for brand elements
  - [x] Check text colors match theme (white foreground, gray muted)

- [x] **Task 7: Test navigation**
  - [x] Run `npm run dev`
  - [x] Navigate to http://localhost:5173/
  - [x] Click "History" link - verify /history loads
  - [x] Manually navigate to /dashboard/test-123 - verify sessionId displayed
  - [x] Verify Navbar appears on all pages
  - [x] Verify dark theme is consistent

## Dev Notes

### Architecture Alignment

This story implements the frontend routing per architecture.md and UX specification:
- **Router:** React Router v6 with BrowserRouter
- **Pages:** 3 main screens (Home, Dashboard, History)
- **Layout:** Navbar + main content area
- **Theme:** Spotify Dark applied globally

### Route Structure

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | HomePage | Upload form (Epic 2) |
| `/dashboard/:sessionId` | DashboardPage | Results display (Epic 5) |
| `/history` | HistoryPage | Past sessions (Epic 7) |

### UX Design Alignment

From UX specification:
- Simple 3-screen flow: Upload → Dashboard → History
- Minimal navigation (no persistent sidebar)
- Dark theme with green accents
- Centered content layout

[Source: docs/ux-design-specification.md#Section-3.1]

### Tailwind Classes Used

| Class | Purpose |
|-------|---------|
| `bg-background` | Dark background from CSS vars |
| `text-foreground` | White text |
| `text-primary` | Green accent (#1DB954) |
| `text-muted-foreground` | Gray secondary text |
| `border-border` | Subtle borders |
| `bg-card` | Elevated surface |

### Dependency on Story 1.1

This story requires the frontend project structure from Story 1.1 to be complete, including:
- React Router installed
- Tailwind CSS configured
- CSS variables in index.css
- Folder structure (components/, pages/)

[Source: docs/sprint-artifacts/tech-spec-epic-1.md#Workflows-and-Sequencing]

### References

- [Source: docs/ux-design-specification.md#Section-4.1]
- [Source: docs/architecture.md#Frontend-Routing]
- [Source: docs/sprint-artifacts/tech-spec-epic-1.md#Story-1.5]
- [Source: docs/epics.md#Story-1.5]

## Dev Agent Record

### Context Reference

None (proceeded without story context file)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Fixed ESLint errors in config files (converted require to import, __dirname to import.meta.url)
- Build passes with no warnings
- Lint passes with no errors

### Completion Notes List

- All 7 tasks completed successfully
- All 5 acceptance criteria satisfied
- React Router configured with 3 routes
- Navbar with active link highlighting
- Spotify Dark theme verified (CSS variables present)
- Build and lint pass

### File List

**Created:**
- frontend/src/components/Navbar.jsx

**Modified:**
- frontend/src/App.jsx (added Router, Navbar, routes)
- frontend/src/pages/HomePage.jsx (updated content)
- frontend/src/pages/DashboardPage.jsx (added useParams)
- frontend/src/pages/HistoryPage.jsx (updated content)
- frontend/vite.config.js (fixed __dirname for ESM)
- frontend/tailwind.config.js (fixed require to import)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |

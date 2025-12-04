# Resume Shortlister - UX Design Specification

**Created:** 2025-11-30
**Author:** Uzasch
**Generated using BMad Method - Create UX Design Workflow**

---

## Executive Summary

An AI-powered resume shortlisting tool with **transparent reasoning**. The UX is designed to reduce HR decision fatigue through a clean, minimal interface that guides users through a simple 3-step flow: Upload → Dashboard → History.

**Design Philosophy:** Centered Minimal - one thing at a time, low cognitive load, generous spacing.

**Inspiration Sources:** Spotify (dark mode, cards), Fable (generous spacing, data viz), Myntra (clear hierarchy, large buttons)

---

## 1. Design System Foundation

### 1.1 Design System Choice

**Selected:** shadcn/ui (already specified in PRD)

**Why shadcn/ui:**
- Pre-built accessible components (Button, Card, Dialog, Input, Toast, etc.)
- Built on Radix UI primitives - excellent accessibility
- Tailwind CSS integration - matches our stack
- Copy-paste into project - you own the code
- CSS variables for easy theming
- Looks professional out of the box

**Components We'll Use:**
- `Button` - primary, secondary, destructive variants
- `Card` - candidate cards, stat cards
- `Input` / `Textarea` - job title, job description
- `Dialog` - email confirmation modal
- `Toast` - success/error notifications
- `Progress` - score breakdown bars
- `Badge` - rank indicators
- `Skeleton` - loading states

---

## 2. Visual Foundation

### 2.1 Color System (Spotify Dark Theme)

```css
:root {
  /* Primary */
  --primary: #1DB954;           /* Spotify green - main actions */
  --primary-hover: #1ed760;     /* Hover state */

  /* Backgrounds */
  --background: #121212;        /* Main background */
  --background-elevated: #181818; /* Slightly raised surfaces */
  --card: #282828;              /* Card backgrounds */
  --card-hover: #333333;        /* Card hover state */

  /* Borders */
  --border: #404040;            /* Subtle borders */

  /* Text */
  --foreground: #ffffff;        /* Primary text */
  --muted-foreground: #b3b3b3;  /* Secondary text */
  --dim: #727272;               /* Tertiary text */

  /* Semantic */
  --success: #1DB954;           /* Success states */
  --warning: #f59e0b;           /* Warning states */
  --error: #e91429;             /* Error states */
  --info: #509bf5;              /* Info states */
}
```

### 2.2 Typography

**Font Family:** Inter (shadcn default)

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 (Page title) | 2rem (32px) | 700 | 1.2 |
| H2 (Section) | 1.5rem (24px) | 600 | 1.3 |
| H3 (Card title) | 1.125rem (18px) | 600 | 1.4 |
| Body | 1rem (16px) | 400 | 1.5 |
| Small | 0.875rem (14px) | 400 | 1.5 |
| Tiny | 0.75rem (12px) | 400 | 1.4 |

### 2.3 Spacing System

**Base Unit:** 4px

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Tight spacing, inline elements |
| sm | 8px | Between related elements |
| md | 16px | Standard component padding |
| lg | 24px | Section spacing |
| xl | 32px | Major section gaps |
| 2xl | 48px | Page-level spacing |

### 2.4 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| sm | 4px | Small elements (badges) |
| md | 8px | Buttons, inputs |
| lg | 12px | Cards |
| xl | 16px | Large cards, modals |
| full | 9999px | Pills, circular buttons |

---

## 3. Design Direction

### 3.1 Chosen Approach: Centered Minimal

**Layout Characteristics:**
- Single-column centered layout (max-width: 600px for forms, 1200px for dashboard)
- Card grid for candidates (3 columns on desktop)
- Generous whitespace
- One primary action per screen

**Visual Hierarchy:**
- Stats prominently displayed at top of dashboard
- Candidate #1 visually emphasized
- WHY sections expandable to reduce initial density

**Information Density:** Low (spacious)
- Reduces cognitive load for fatigued HR users
- Progressive disclosure - details on demand

**Navigation Pattern:** Minimal
- No persistent sidebar (only 3 screens)
- Simple flow: Upload → Dashboard → History
- Back navigation via browser or explicit button

---

## 4. User Journey Flows

### 4.1 Primary Flow: Upload → Analyze → Results

```
┌─────────────────────────────────────────────────────────────┐
│                    SCREEN 1: UPLOAD                          │
│                                                              │
│                   "Find Your Top 6"                          │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Job Title: [________________________]               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Job Description:                                    │    │
│  │  [                                                 ] │    │
│  │  [                                                 ] │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐    │
│  │           📄 Drop resumes here                     │    │
│  │         or click to browse • PDF only              │    │
│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘    │
│                                                              │
│              [======= Analyze Resumes →=======]              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    LOADING STATE                             │
│                                                              │
│                 Analyzing batch 2/5...                       │
│                 ████████████░░░░░░░░ 40%                     │
│                                                              │
│              Extracting skills from resumes                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    SCREEN 2: DASHBOARD                       │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │    47    │ │    6     │ │   78%    │ │  3-7 yrs │       │
│  │ Analyzed │ │   Top    │ │ Avg Match│ │   Exp    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                              │
│  🏆 Top 6 Candidates                                        │
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ #1 Rahul   │ │ #2 Priya   │ │ #3 Amit    │           │
│  │    92%     │ │    89%     │ │    86%     │           │
│  │ ████████░░ │ │ ███████░░░ │ │ ██████░░░░ │           │
│  │ [WHY ▼]    │ │ [WHY ▼]    │ │ [WHY ▼]    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ #4 Sara    │ │ #5 Vikram  │ │ #6 Neha    │           │
│  │    84%     │ │    82%     │ │    80%     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                              │
│        [✉️ Email All Top 6]    [📊 View Report]             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    SCREEN 3: HISTORY                         │
│                                                              │
│  Past Sessions                                               │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  React Developer          Nov 30, 2025    47 resumes │    │
│  │  [View Dashboard]                                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Python Engineer          Nov 28, 2025    32 resumes │    │
│  │  [View Dashboard]                                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Email Flow

```
User clicks "Email All Top 6"
        │
        ▼
┌─────────────────────────────────────┐
│         CONFIRMATION MODAL           │
│                                      │
│  Send interview invitations to:      │
│  • Rahul Sharma (rahul@email.com)    │
│  • Priya Patel (priya@email.com)     │
│  • ... 4 more                        │
│                                      │
│  Message preview:                    │
│  ┌─────────────────────────────┐    │
│  │ Dear {name},                │    │
│  │ We'd like to invite you... │    │
│  └─────────────────────────────┘    │
│                                      │
│     [Cancel]    [Send Emails]        │
└─────────────────────────────────────┘
        │
        ▼
   Toast: "✓ 6 emails sent successfully"
```

---

## 5. Component Library

### 5.1 shadcn/ui Components Used

| Component | Variant | Usage |
|-----------|---------|-------|
| `Button` | default (green) | Primary actions |
| `Button` | outline | Secondary actions |
| `Button` | ghost | Tertiary/icon buttons |
| `Card` | default | Candidate cards, stat cards |
| `Input` | default | Text inputs |
| `Textarea` | default | Job description |
| `Dialog` | default | Email confirmation |
| `Toast` | success/error | Notifications |
| `Progress` | default | Score bars, upload progress |
| `Badge` | default | Rank badges |
| `Skeleton` | default | Loading states |

### 5.2 Custom Components

#### CandidateCard
- Rank badge (positioned top-left)
- Name, match percentage
- Score breakdown bars (Education/Experience/Projects)
- Expandable "WHY" section
- Hover state with slight elevation

#### DropZone
- Dashed border
- Icon + text
- Drag-over state (green border, light green bg)
- File list when files added

#### StatCard
- Large number (primary color)
- Label below
- Subtle background

---

## 6. UX Pattern Decisions

### 6.1 Buttons

| Type | Style | Usage |
|------|-------|-------|
| Primary | Green bg, white text, rounded-full | Main CTA (Analyze, Send Emails) |
| Secondary | Transparent, border, white text | Secondary actions (View Report) |
| Ghost | No border, text only | Tertiary actions, icon buttons |
| Destructive | Red | Cancel, remove file |

### 6.2 Feedback Patterns

| Scenario | Pattern |
|----------|---------|
| Success | Toast (bottom-right), auto-dismiss 4s |
| Error | Toast (bottom-right), manual dismiss |
| Loading (short) | Button shows spinner |
| Loading (long) | Full-screen with progress bar + message |
| Empty state | Centered message + CTA |

### 6.3 Form Patterns

| Element | Behavior |
|---------|----------|
| Labels | Above input, muted color |
| Placeholder | Hint text inside input |
| Validation | On submit, inline error below field |
| Required | No asterisk (all visible fields are required) |

### 6.4 Modal Patterns

| Aspect | Decision |
|--------|----------|
| Dismiss | Click outside OR close button |
| Focus | Auto-focus first interactive element |
| Size | Medium (max-width: 500px) |

### 6.5 Navigation

| Aspect | Decision |
|--------|----------|
| Style | Simple header with nav links |
| Active state | Green underline or text color |
| Back button | Use browser back (SPA handles routing) |

---

## 7. Responsive Design & Accessibility

### 7.1 Breakpoints

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile | < 640px | Single column, stacked cards |
| Tablet | 640px - 1024px | 2-column card grid |
| Desktop | > 1024px | 3-column card grid, full layout |

### 7.2 Mobile Adaptations

- Cards stack vertically
- Dropzone full width
- Stats row: 2x2 grid instead of 4-column
- Navigation: Hamburger menu (if needed) or simple header

### 7.3 Accessibility (WCAG 2.1 Level AA)

| Requirement | Implementation |
|-------------|----------------|
| Color contrast | 4.5:1 minimum (our theme passes) |
| Focus indicators | Visible focus ring (Tailwind default) |
| Keyboard navigation | All interactive elements focusable |
| Screen reader | Semantic HTML, ARIA labels where needed |
| Touch targets | Minimum 44x44px on mobile |
| Reduced motion | Respect `prefers-reduced-motion` |

---

## 8. Interactive Deliverables

### 8.1 Color Theme Visualizer
**File:** `docs/ux-color-themes.html`

Interactive HTML showing:
- 4 color theme options explored
- Live UI component examples
- Side-by-side comparison
- **Selected:** Theme 2 (Spotify Dark)

### 8.2 Design Direction Mockups
**File:** `docs/ux-design-directions.html`

Interactive HTML showing:
- 3 complete layout approaches
- Upload and Dashboard screens for each
- Comparison grid
- **Selected:** Direction 1 (Centered Minimal)

---

## 9. Implementation Guidance

### 9.1 CSS Variables Setup (index.css)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
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
}
```

### 9.2 Key Implementation Notes

1. **shadcn/ui setup:** Run `npx shadcn@latest init` and select dark theme
2. **Font:** Inter is loaded by default with shadcn/ui
3. **Icons:** Use Lucide React (included with shadcn/ui)
4. **Charts:** Recharts for score visualizations
5. **File upload:** Use react-dropzone for drag-and-drop

---

## Summary

| Aspect | Decision |
|--------|----------|
| **Design System** | shadcn/ui + Tailwind CSS |
| **Color Theme** | Spotify Dark (#1DB954 primary, #121212 bg) |
| **Layout Direction** | Centered Minimal (card grid) |
| **Screens** | 3 (Upload → Dashboard → History) |
| **Typography** | Inter font |
| **Accessibility** | WCAG 2.1 Level AA |

---

## Related Documents

- **PRD:** `docs/prd.md`
- **Brainstorming:** `docs/brainstorming-session-results-2025-11-30.md`
- **Research:** `docs/research-technical-2025-11-30.md`

---

_This UX Design Specification was created through collaborative design facilitation. All decisions were made with user input and are documented with rationale._

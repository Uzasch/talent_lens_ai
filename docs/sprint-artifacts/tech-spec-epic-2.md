# Epic Technical Specification: Upload & Role Management

Date: 2025-12-20
Author: Uzasch
Epic ID: 2
Status: Draft

---

## Overview

Epic 2 implements the primary user interface for TalentLens AI - the Home/Upload page where HR professionals input job details and upload resumes for analysis. This epic establishes the role-based candidate pooling system and the resume upload workflow.

This is the first user-facing epic after the foundation is complete. Users will be able to create/select job roles, enter job descriptions, optionally configure scoring weights, and upload PDF resumes through a drag-and-drop interface.

## Objectives and Scope

### In Scope

- Role title input with autocomplete from existing roles
- Role normalization (e.g., "Python Dev" → "Python Developer")
- Job description textarea input
- Optional weight configuration sliders (5 dimensions, default 20% each)
- Drag-and-drop file upload zone (PDF only)
- File list display with remove functionality
- Roles API endpoint for CRUD operations
- Form validation and error handling

### Out of Scope

- Resume parsing/extraction (Epic 3)
- AI analysis and ranking (Epic 4)
- Results display (Epic 5)
- File storage beyond upload handling
- Batch processing logic

## System Architecture Alignment

This epic implements the input layer of the two-tier architecture:

| Architecture Component | Story | Notes |
|------------------------|-------|-------|
| Role Management UI | 2.1 | Autocomplete combobox for roles |
| Job Description Input | 2.2 | Textarea component |
| Weight Configuration | 2.3 | Collapsible sliders |
| File Upload UI | 2.4, 2.5 | react-dropzone integration |
| Roles API | 2.6 | GET/POST /api/roles |

**Constraints from Architecture:**
- Use shadcn/ui components (Combobox, Textarea, Slider, Collapsible)
- PDF files only (application/pdf MIME type)
- Role titles must be normalized before storage
- Weights must sum to 100%

## Detailed Design

### Services and Modules

| Module | Location | Responsibility | Dependencies |
|--------|----------|----------------|--------------|
| **HomePage** | frontend/src/pages/HomePage.jsx | Main upload form container | React, shadcn/ui |
| **RoleInput** | frontend/src/components/RoleInput.jsx | Role autocomplete combobox | shadcn/ui Combobox |
| **WeightConfig** | frontend/src/components/WeightConfig.jsx | Weight sliders (collapsible) | shadcn/ui Slider, Collapsible |
| **DropZone** | frontend/src/components/DropZone.jsx | Drag-drop file upload | react-dropzone |
| **FileList** | frontend/src/components/FileList.jsx | Uploaded files display | lucide-react icons |
| **Roles API** | backend/app.py | Role CRUD endpoints | Flask, models.py |

### Data Models and Contracts

**Role Normalization Logic:**
```python
def normalize_role_title(title):
    """Normalize role title for matching."""
    title = title.lower().strip()
    # Expand common abbreviations
    abbreviations = {
        'dev': 'developer',
        'sr': 'senior',
        'jr': 'junior',
        'mgr': 'manager',
        'eng': 'engineer',
    }
    words = title.split()
    normalized = [abbreviations.get(w, w) for w in words]
    return ' '.join(normalized)
```

**Weight Configuration Schema:**
```javascript
{
  experience: 20,    // 0-100, default 20
  projects: 20,      // 0-100, default 20
  positions: 20,     // 0-100, default 20
  skills: 20,        // 0-100, default 20
  education: 20      // 0-100, default 20
  // Must sum to 100
}
```

**File Upload State:**
```javascript
{
  files: [
    { name: "resume1.pdf", size: 102400, file: File },
    { name: "resume2.pdf", size: 98304, file: File }
  ],
  count: 2
}
```

### APIs and Interfaces

**GET /api/roles**
```json
// Response
{
  "success": true,
  "data": {
    "roles": [
      {
        "id": "uuid-1",
        "title": "Python Developer",
        "normalized_title": "python developer",
        "candidate_count": 15,
        "created_at": "2025-12-20T10:00:00Z"
      }
    ]
  }
}
```

**POST /api/roles**
```json
// Request
{
  "title": "Python Dev",
  "weights": {
    "experience": 25,
    "projects": 20,
    "positions": 15,
    "skills": 25,
    "education": 15
  }
}

// Response (new role)
{
  "success": true,
  "data": {
    "id": "uuid-new",
    "title": "Python Dev",
    "normalized_title": "python developer",
    "is_new": true
  }
}

// Response (existing role matched)
{
  "success": true,
  "data": {
    "id": "uuid-existing",
    "title": "Python Developer",
    "normalized_title": "python developer",
    "is_new": false,
    "candidate_count": 15
  }
}
```

### Workflows and Sequencing

**Story Dependency Flow:**

```
Story 2.6 (Roles API) ──────► Story 2.1 (Role Input)
                                     │
                                     ▼
                              Story 2.2 (Job Desc)
                                     │
                                     ▼
                              Story 2.3 (Weights)
                                     │
Story 2.4 (DropZone) ──────► Story 2.5 (File List)
```

**Development Sequence:**
1. Story 2.6 (Roles API) - backend first
2. Story 2.1 (Role Input) - depends on 2.6
3. Story 2.2 (Job Description) - depends on 2.1
4. Story 2.3 (Weight Config) - depends on 2.2
5. Story 2.4 (DropZone) - can parallel with 2.1-2.3
6. Story 2.5 (File List) - depends on 2.4

**User Flow:**
```
1. User lands on HomePage
2. Types/selects role title → autocomplete shows existing roles
3. Enters job description in textarea
4. (Optional) Expands weight config, adjusts sliders
5. Drags PDFs onto dropzone OR clicks to browse
6. Reviews file list, removes unwanted files
7. Clicks "Analyze Resumes" button → triggers Epic 3
```

## Non-Functional Requirements

### Performance

| Metric | Target | Source |
|--------|--------|--------|
| Role autocomplete response | < 200ms | Best practice |
| File list update | Instant (client-side) | UX requirement |
| Dropzone feedback | < 100ms | UX requirement |

**Implementation Notes:**
- Role search is client-side filtering (small dataset)
- File handling is entirely client-side until submission
- No server calls during file selection

### Security

| Requirement | Implementation | Source |
|-------------|----------------|--------|
| PDF only validation | MIME type + extension check | PRD FR8 |
| File size limit | 10MB per file (configurable) | Best practice |
| XSS prevention | React's built-in escaping | Framework default |

**File Validation:**
```javascript
const acceptedTypes = {
  'application/pdf': ['.pdf']
};

// Reject non-PDF with toast error
if (!file.type === 'application/pdf') {
  toast.error('Only PDF files are accepted');
  return;
}
```

### Reliability/Availability

| Scenario | Handling |
|----------|----------|
| Roles API fails | Show error toast, allow retry |
| Invalid file type | Reject with clear error message |
| Empty form submission | Validate and show inline errors |

### Observability

| Signal | Implementation |
|--------|----------------|
| File upload count | Console log in development |
| Role creation | Server-side logging |
| Validation errors | Toast notifications |

## Dependencies and Integrations

### Frontend Components (from shadcn/ui)

| Component | Usage | Install Command |
|-----------|-------|-----------------|
| `Command` | Role autocomplete | `npx shadcn@latest add command` |
| `Popover` | Dropdown container | `npx shadcn@latest add popover` |
| `Textarea` | Job description | `npx shadcn@latest add textarea` |
| `Slider` | Weight config | `npx shadcn@latest add slider` |
| `Collapsible` | Weight section | `npx shadcn@latest add collapsible` |
| `Button` | Actions | `npx shadcn@latest add button` |
| `Toast` | Notifications | `npx shadcn@latest add toast` |

### External Libraries

| Package | Version | Purpose |
|---------|---------|---------|
| react-dropzone | ^14.x | File drag-drop | Already installed in Epic 1 |
| lucide-react | latest | Icons (X, Upload, FileText) | Already installed in Epic 1 |

### Backend Dependencies

No new backend dependencies required. Uses:
- Flask (from Epic 1)
- SQLite via models.py (from Epic 1)

## Acceptance Criteria (Authoritative)

### Story 2.1: Role Selection/Creation
1. AC2.1.1: Autocomplete input shows "Role Title" placeholder
2. AC2.1.2: Existing roles appear as suggestions while typing
3. AC2.1.3: New role can be created by typing a new title
4. AC2.1.4: Role titles are normalized (e.g., "Python Dev" → "Python Developer")
5. AC2.1.5: Selected role_id or new title is stored in form state

### Story 2.2: Job Description Input
1. AC2.2.1: Textarea with placeholder "Paste the full job description here..."
2. AC2.2.2: Textarea is required (validation on submit)
3. AC2.2.3: Styling matches Spotify Dark theme
4. AC2.2.4: Value stored in React state

### Story 2.3: Weight Configuration
1. AC2.3.1: "Customize Weights" section is collapsed by default
2. AC2.3.2: 5 sliders visible when expanded (Experience, Projects, Positions, Skills, Education)
3. AC2.3.3: Each slider ranges from 0-100
4. AC2.3.4: Total automatically redistributes to equal 100%
5. AC2.3.5: Default is 20% each dimension

### Story 2.4: File Dropzone Component
1. AC2.4.1: Dropzone border turns green (#1DB954) on drag-over
2. AC2.4.2: Background shows subtle green tint on drag-over
3. AC2.4.3: Files added to list on drop
4. AC2.4.4: Click opens file picker filtered to PDF
5. AC2.4.5: Non-PDF files show error toast

### Story 2.5: File List with Remove
1. AC2.5.1: Each filename displayed in list
2. AC2.5.2: Total count shows "X files selected"
3. AC2.5.3: Each file has X button to remove
4. AC2.5.4: Removing file updates count
5. AC2.5.5: Empty list shows default dropzone state

### Story 2.6: Roles API
1. AC2.6.1: GET /api/roles returns list of existing roles with candidate counts
2. AC2.6.2: POST /api/roles creates new role or returns existing if normalized title matches
3. AC2.6.3: Role includes weights if specified
4. AC2.6.4: Response includes is_new flag

## Traceability Mapping

| AC | FR | Spec Section | Component | Test Approach |
|----|-------|--------------|-----------|---------------|
| AC2.1.1-5 | FR1-FR3 | APIs > Roles | RoleInput.jsx | E2E: type and select |
| AC2.2.1-4 | FR4 | Detailed Design | HomePage.jsx | E2E: enter text |
| AC2.3.1-5 | FR5-FR6 | Data Models > Weights | WeightConfig.jsx | Unit: slider math |
| AC2.4.1-5 | FR7-FR8 | Security > File Validation | DropZone.jsx | E2E: drag files |
| AC2.5.1-5 | FR9-FR11 | Detailed Design | FileList.jsx | E2E: add/remove |
| AC2.6.1-4 | FR1-FR3 | APIs > Roles | backend/app.py | Integration: pytest |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Weight redistribution UX confusion | Medium | Low | Add tooltip explaining behavior |
| Large file uploads slow browser | Low | Medium | Add file size limit (10MB) |
| Role normalization mismatches | Low | Low | Keep abbreviation list minimal |

### Assumptions

1. Users upload 10-50 resumes per session (per PRD)
2. Role list will remain small (< 100 roles)
3. All resumes are text-based PDFs (not scanned images)
4. Weights feature is optional - most users will use defaults

### Open Questions

1. **Q1:** Should we show candidate count next to each role in autocomplete?
   - **Recommendation:** Yes, helps users understand pool size

2. **Q2:** Maximum file size limit?
   - **Recommendation:** 10MB per file, 100MB total

## Test Strategy Summary

### Unit Tests (Vitest)
- Weight redistribution logic (sum to 100%)
- Role normalization function
- File validation (PDF only)

### Integration Tests (pytest)
- GET /api/roles returns proper format
- POST /api/roles creates/matches roles correctly
- Role normalization works as expected

### E2E Tests (Playwright)
- Complete upload flow: role → description → weights → files
- File drag-and-drop works
- Remove file from list works
- Error toast on invalid file

**Test Priority:**
1. Roles API (critical for Epic 3)
2. File upload/validation
3. Weight configuration

---

_Generated by BMAD BMM Epic Tech Context Workflow_
_Epic: 2 - Upload & Role Management_
_Date: 2025-12-20_

# Story 2.5: File List with Remove

Status: review

## Story

As a **HR professional**,
I want **to see uploaded files and remove unwanted ones**,
so that **I can control which resumes are analyzed**.

## Acceptance Criteria

1. **AC2.5.1:** Each filename is displayed in a list below the dropzone
2. **AC2.5.2:** Total count shows "X files selected"
3. **AC2.5.3:** Each file has an X button to remove it
4. **AC2.5.4:** Removing a file updates the count immediately
5. **AC2.5.5:** When all files are removed, the dropzone returns to default state

## Tasks / Subtasks

- [x] **Task 1: Create FileList component** (AC: 2.5.1, 2.5.2, 2.5.3)
  - [x] Create `src/components/FileList.jsx`:
    ```jsx
    import { X, FileText } from 'lucide-react';
    import { Button } from '@/components/ui/button';

    function FileList({ files, onRemove }) {
      if (files.length === 0) return null;

      return (
        <div className="mt-4 space-y-2">
          <p className="text-sm text-muted-foreground">
            {files.length} file{files.length !== 1 ? 's' : ''} selected
          </p>
          <ul className="space-y-2">
            {files.map((file, index) => (
              <li
                key={`${file.name}-${index}`}
                className="flex items-center justify-between p-2 bg-card rounded-md"
              >
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm truncate max-w-[300px]">
                    {file.name}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    ({formatFileSize(file.size)})
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onRemove(index)}
                  className="h-8 w-8 p-0 hover:bg-destructive/10 hover:text-destructive"
                >
                  <X className="h-4 w-4" />
                </Button>
              </li>
            ))}
          </ul>
        </div>
      );
    }

    function formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    export default FileList;
    ```

- [x] **Task 2: Add remove handler to HomePage** (AC: 2.5.3, 2.5.4)
  - [x] Add remove function:
    ```jsx
    const handleRemoveFile = (indexToRemove) => {
      setFiles(prev => prev.filter((_, index) => index !== indexToRemove));
    };
    ```
  - [x] Pass to FileList:
    ```jsx
    <FileList files={files} onRemove={handleRemoveFile} />
    ```

- [x] **Task 3: Integrate with DropZone** (AC: 2.5.5)
  - [x] Place FileList below DropZone:
    ```jsx
    <div className="space-y-2">
      <label className="text-sm font-medium">Resumes</label>
      <DropZone onFilesAdded={handleFilesAdded} />
      <FileList files={files} onRemove={handleRemoveFile} />
    </div>
    ```
  - [x] When files.length === 0, FileList returns null (dropzone visible)

- [x] **Task 4: Install Button component if needed**
  - [x] Run `npx shadcn@latest add button` (if not already installed) - Already installed from Epic 1

- [x] **Task 5: Style file list for dark theme**
  - [x] Verify bg-card for file items
  - [x] Verify muted text colors
  - [x] Verify destructive hover on remove button

- [x] **Task 6: Test file list functionality**
  - [x] Add files → list appears with count
  - [x] Verify filenames are truncated if too long
  - [x] Click X → file removed, count updates
  - [x] Remove all files → list disappears
  - [x] Add more files → appended to existing list

## Dev Notes

### Architecture Alignment

This story implements the file list display per UX specification:
- **Component:** Custom FileList with shadcn/ui Button
- **Icons:** lucide-react (FileText, X)
- **Behavior:** Immediate state updates on remove

### Component Layout

```
┌──────────────────────────────────────┐
│         [DropZone]                   │
│     Drop resumes here...             │
└──────────────────────────────────────┘

3 files selected

┌──────────────────────────────────────┐
│ 📄 resume_john_doe.pdf    (245 KB) [X]│
├──────────────────────────────────────┤
│ 📄 resume_jane_smith.pdf  (198 KB) [X]│
├──────────────────────────────────────┤
│ 📄 cv_developer.pdf       (312 KB) [X]│
└──────────────────────────────────────┘
```

### File Size Formatting

- Bytes → "X B"
- KB → "X.X KB"
- MB → "X.X MB"

### State Management

Files stored in HomePage state as array of File objects:
```javascript
[
  File { name: "resume1.pdf", size: 102400, ... },
  File { name: "resume2.pdf", size: 98304, ... }
]
```

### Dependency on Story 2.4

This story requires the DropZone component from Story 2.4. The FileList displays files collected by DropZone.

### References

- [Source: docs/sprint-artifacts/tech-spec-epic-2.md#Story-2.5]
- [Source: docs/epics.md#Story-2.5]
- [Source: docs/prd.md#FR9-FR11]

## Dev Agent Record

### Context Reference

None (proceeded without story context file)

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Build and lint pass without errors

### Completion Notes List

- All 6 tasks completed successfully
- All 5 acceptance criteria satisfied:
  - AC2.5.1: Each filename displayed with FileText icon
  - AC2.5.2: Total count shows "X files selected"
  - AC2.5.3: Each file has X button to remove it
  - AC2.5.4: Removing a file updates count immediately
  - AC2.5.5: When all files removed, FileList returns null (dropzone visible)
- File size displayed in human-readable format (B/KB/MB)
- Filenames truncated at 300px with ellipsis
- Remove button has destructive hover state

### File List

**Created:**
- frontend/src/components/FileList.jsx

**Modified:**
- frontend/src/pages/HomePage.jsx (added FileList import, handleRemoveFile function)

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-12-20 | SM Agent (Bob) | Initial draft created |
| 2025-12-20 | Dev Agent (Amelia) | Implementation complete - all ACs satisfied |

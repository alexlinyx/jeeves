# Feature Spec: Gradio Dashboard

**Phase:** 3.1  
**Branch:** `feature/3.1-gradio-dashboard`  
**Priority:** P0  
**Est. Time:** 12 hours

---

## Objective

Build the Gradio web dashboard for reviewing and approving AI-generated email drafts.

---

## Acceptance Criteria

- [ ] `src/dashboard.py` implements Gradio app
- [ ] Shows pending drafts table with subject, sender, preview
- [ ] Draft text editor for editing drafts
- [ ] Approve / Edit / Delete buttons work
- [ ] Tone selector dropdown
- [ ] Real-time refresh every 30 seconds
- [ ] Tests verify UI components exist
- [ ] Unit tests pass

---

## Deliverable

### `src/dashboard.py`

```python
"""Gradio dashboard for email draft review."""
import gradio as gr
from typing import List, Dict, Optional
import time


class Dashboard:
    """Gradio dashboard for Jeeves email drafts."""
    
    def __init__(
        self,
        db=None,
        response_generator=None,
        refresh_interval: int = 30
    ):
        """Initialize dashboard."""
        self.db = db
        self.response_generator = response_generator
        self.refresh_interval = refresh_interval
    
    def get_pending_drafts(self) -> List[Dict]:
        """Get pending drafts from database."""
        return []
    
    def approve_draft(self, draft_id: int) -> str:
        """Approve and send a draft."""
        pass
    
    def delete_draft(self, draft_id: int) -> str:
        """Delete a draft."""
        pass
    
    def edit_draft(self, draft_id: int, new_text: str) -> str:
        """Edit a draft's text."""
        pass
    
    def generate_draft_from_email(self, email_id: int, tone: str) -> str:
        """Generate a draft for an email."""
        pass
    
    def build_interface(self) -> gr.Blocks:
        """Build the Gradio interface."""
        pass
    
    def run(self, share: bool = False, port: int = 7860):
        """Run the dashboard."""
        pass


# Demo data for testing without DB
DEMO_DRAFTS = [
    {"id": 1, "subject": "Re: Project Update", "from": "bob@company.com", "preview": "update on the project...", "tone": "match_style", "generated_text": "Thanks for the update!", "created_at": "2024-01-15T10:30:00"},
    {"id": 2, "subject": "Meeting Tomorrow", "from": "alice@startup.io", "preview": "Are we still meeting?", "tone": "formal", "generated_text": "Yes, I confirm our meeting.", "created_at": "2024-01-15T11:00:00"},
]


def get_demo_drafts() -> List[Dict]:
    """Get demo drafts for testing."""
    return DEMO_DRAFTS.copy()
```

---

## Testing Requirements

### Unit Tests (tests/test_dashboard.py)

The tests must verify:

1. **File & Import Tests**
   - `test_file_exists` - src/dashboard.py exists
   - `test_import` - Dashboard can be imported

2. **Class Tests**
   - `test_class_has_required_methods` - get_pending_drafts, approve_draft, delete_draft, edit_draft, generate_draft_from_email, build_interface, run
   - `test_dashboard_class_exists` - Dashboard class exists

3. **Demo Data Tests**
   - `test_demo_drafts_exists` - DEMO_DRAFTS constant exists
   - `test_get_demo_drafts_function` - get_demo_drafts() function exists
   - `test_demo_drafts_structure` - Each demo draft has required fields (id, subject, from, preview, tone, generated_text)

4. **Gradio Integration Tests**
   - `test_gradio_import` - Gradio can be imported
   - `test_build_interface_returns_blocks` - build_interface returns gr.Blocks

5. **Tone Options Tests**
   - `test_tone_options_defined` - Standard tone options available

6. **Configuration Tests**
   - `test_default_refresh_interval` - Default refresh is 30 seconds
   - `test_default_port` - Default port is 7860

---

## UI Components

The dashboard must have:

1. **Draft Table** - DataFrame or table showing pending drafts
2. **Draft Editor** - TextArea for viewing/editing draft content
3. **Tone Dropdown** - Dropdown with options: casual, formal, concise, match_style
4. **Action Buttons** - Approve, Edit/Save, Delete buttons
5. **Refresh Toggle** - Enable/disable auto-refresh
6. **Status Display** - Show status messages

---

## Tasks

### 3.1.1 Scaffold Gradio App (2 hrs)
- [ ] Set up basic Gradio Blocks interface
- [ ] Configure theme and layout
- [ ] Test basic rendering

### 3.1.2 Build Drafts Table (4 hrs)
- [ ] Create data table component
- [ ] Load drafts from DB (or demo data)
- [ ] Add row selection

### 3.1.3 Add Draft Editor (2 hrs)
- [ ] TextArea for draft content
- [ ] Pre-populate when draft selected
- [ ] Handle edits

### 3.1.4 Add Action Buttons (2 hrs)
- [ ] Approve & Send button
- [ ] Save Edit button
- [ ] Delete button

### 3.1.5 Add Tone Selector (1 hr)
- [ ] Dropdown with 4 tone options
- [ ] Connect to draft generation

### 3.1.6 Add Auto-Refresh (1 hr)
- [ ] Implement refresh mechanism
- [ ] Add toggle to enable/disable

---

## Dependencies

| Dependency | Purpose |
|------------|---------|
| gradio>=4.0.0 | UI framework |
| src.db | Database layer (3.2) |
| src.response_generator | Generate drafts (2.3) |

---

## Running the Dashboard

```bash
# Run with demo data
python src/dashboard.py

# Run on custom port
python src/dashboard.py --port 8080

# Run with public link
python src/dashboard.py --share

# Run tests
pytest tests/test_dashboard.py -v
```

---

## Notes

- Dashboard works with demo data if DB not ready
- Can use `get_demo_drafts()` for testing without database
- Default port 7860 is Gradio standard

---

## Definition of Done

1. `src/dashboard.py` implements working Gradio app
2. Shows pending drafts in table
3. Draft editor allows editing
4. All 3 action buttons work (Approve, Edit, Delete)
5. Tone selector has 4 options
6. Auto-refresh works
7. All unit tests pass (minimum 12 tests)
8. Branch pushed to GitHub
9. PR created

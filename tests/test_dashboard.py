"""Tests for the Gradio Dashboard."""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestFileAndImport:
    """Test file existence and imports."""
    
    def test_file_exists(self):
        """src/dashboard.py exists."""
        dashboard_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'dashboard.py')
        assert os.path.exists(dashboard_path), "src/dashboard.py must exist"
    
    def test_import(self):
        """Dashboard can be imported."""
        from dashboard import Dashboard
        assert Dashboard is not None


class TestDashboardClass:
    """Test Dashboard class."""
    
    def test_dashboard_class_exists(self):
        """Dashboard class exists."""
        from dashboard import Dashboard
        assert Dashboard is not None
    
    def test_class_has_required_methods(self):
        """Dashboard has all required methods."""
        from dashboard import Dashboard
        dashboard = Dashboard()
        
        required_methods = [
            'get_pending_drafts',
            'approve_draft',
            'delete_draft',
            'edit_draft',
            'generate_draft_from_email',
            'build_interface',
            'run'
        ]
        
        for method in required_methods:
            assert hasattr(dashboard, method), f"Dashboard must have {method} method"
            assert callable(getattr(dashboard, method)), f"{method} must be callable"


class TestDemoData:
    """Test demo data."""
    
    def test_demo_drafts_exists(self):
        """DEMO_DRAFTS constant exists."""
        from dashboard import DEMO_DRAFTS
        assert DEMO_DRAFTS is not None
    
    def test_get_demo_drafts_function(self):
        """get_demo_drafts() function exists."""
        from dashboard import get_demo_drafts
        assert callable(get_demo_drafts)
    
    def test_demo_drafts_structure(self):
        """Demo drafts have required fields."""
        from dashboard import DEMO_DRAFTS
        
        required_fields = ['id', 'subject', 'from', 'preview', 'tone', 'generated_text']
        
        for draft in DEMO_DRAFTS:
            for field in required_fields:
                assert field in draft, f"Draft must have '{field}' field"


class TestGradioIntegration:
    """Test Gradio integration."""
    
    def test_gradio_import(self):
        """Gradio can be imported."""
        import gradio as gr
        assert gr is not None
    
    def test_build_interface_returns_blocks(self):
        """build_interface returns gr.Blocks."""
        import gradio as gr
        from dashboard import Dashboard
        
        dashboard = Dashboard()
        interface = dashboard.build_interface()
        
        assert isinstance(interface, gr.Blocks), "build_interface must return gr.Blocks"


class TestToneOptions:
    """Test tone options."""
    
    def test_tone_options_defined(self):
        """Standard tone options available."""
        from dashboard import TONE_OPTIONS
        
        expected_tones = ["casual", "formal", "concise", "match_style"]
        
        for tone in expected_tones:
            assert tone in TONE_OPTIONS, f"Tone '{tone}' must be in TONE_OPTIONS"


class TestConfiguration:
    """Test configuration defaults."""
    
    def test_default_refresh_interval(self):
        """Default refresh is 30 seconds."""
        from dashboard import Dashboard
        
        dashboard = Dashboard()
        assert dashboard.refresh_interval == 30, "Default refresh interval should be 30"
    
    def test_default_port(self):
        """Default port is 7860."""
        from dashboard import Dashboard
        
        dashboard = Dashboard()
        assert dashboard.default_port == 7860, "Default port should be 7860"
    
    def test_custom_refresh_interval(self):
        """Custom refresh interval can be set."""
        from dashboard import Dashboard
        
        dashboard = Dashboard(refresh_interval=60)
        assert dashboard.refresh_interval == 60
    
    def test_custom_port(self):
        """Custom port can be set via parameter."""
        from dashboard import Dashboard
        
        dashboard = Dashboard()
        assert dashboard.default_port == 7860


class TestDashboardFunctionality:
    """Test dashboard functionality."""
    
    def test_get_pending_drafts_returns_list(self):
        """get_pending_drafts returns a list."""
        from dashboard import Dashboard
        
        dashboard = Dashboard()
        drafts = dashboard.get_pending_drafts()
        
        assert isinstance(drafts, list), "get_pending_drafts must return a list"
    
    def test_get_demo_drafts_returns_list(self):
        """get_demo_drafts returns list of dicts."""
        from dashboard import get_demo_drafts
        
        drafts = get_demo_drafts()
        
        assert isinstance(drafts, list)
        assert len(drafts) > 0
        assert isinstance(drafts[0], dict)
    
    def test_format_drafts_for_table(self):
        """format_drafts_for_table formats correctly."""
        from dashboard import Dashboard
        
        dashboard = Dashboard()
        drafts = [{"id": 1, "subject": "Test", "from": "a@b.com", "preview": "hi", "tone": "casual"}]
        
        table_data = dashboard.format_drafts_for_table(drafts)
        
        assert len(table_data) == 1
        assert table_data[0][0] == "1"  # id
        assert table_data[0][1] == "Test"  # subject
    
    def test_approve_draft_returns_message(self):
        """approve_draft returns a message."""
        from dashboard import Dashboard
        
        dashboard = Dashboard()
        result = dashboard.approve_draft(1)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_delete_draft_returns_message(self):
        """delete_draft returns a message."""
        from dashboard import Dashboard
        
        dashboard = Dashboard()
        result = dashboard.delete_draft(1)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_edit_draft_returns_message(self):
        """edit_draft returns a message."""
        from dashboard import Dashboard
        
        dashboard = Dashboard()
        result = dashboard.edit_draft(1, "New text")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_get_draft_by_id(self):
        """get_draft_by_id returns correct draft."""
        from dashboard import Dashboard
        
        dashboard = Dashboard()
        draft = dashboard.get_draft_by_id(1)
        
        assert draft is not None
        assert draft['id'] == 1
    
    def test_get_draft_by_id_not_found(self):
        """get_draft_by_id returns None for non-existent draft."""
        from dashboard import Dashboard
        
        dashboard = Dashboard()
        draft = dashboard.get_draft_by_id(999)
        
        assert draft is None
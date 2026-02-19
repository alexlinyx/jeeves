"""Gradio dashboard for email draft review."""
import gradio as gr
from typing import List, Dict, Optional
import time
import threading


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
        self.default_port = 7860
        self.selected_draft_id = None
    
    def get_pending_drafts(self) -> List[Dict]:
        """Get pending drafts from database."""
        if self.db is None:
            return get_demo_drafts()
        # TODO: Implement DB integration when feature 3.2 is done
        return get_demo_drafts()
    
    def approve_draft(self, draft_id: int) -> str:
        """Approve and send a draft."""
        if draft_id is None:
            return "Error: No draft selected"
        # TODO: Integrate with email sender when ready
        return f"Draft {draft_id} approved and sent!"
    
    def delete_draft(self, draft_id: int) -> str:
        """Delete a draft."""
        if draft_id is None:
            return "Error: No draft selected"
        # TODO: Implement DB deletion when feature 3.2 is done
        return f"Draft {draft_id} deleted!"
    
    def edit_draft(self, draft_id: int, new_text: str) -> str:
        """Edit a draft's text."""
        if draft_id is None:
            return "Error: No draft selected"
        # TODO: Implement DB update when feature 3.2 is done
        return f"Draft {draft_id} updated!"
    
    def generate_draft_from_email(self, email_id: int, tone: str) -> str:
        """Generate a draft for an email."""
        if self.response_generator is None:
            return "Error: Response generator not configured"
        # TODO: Implement with response generator when ready
        return f"Generated draft for email {email_id} with tone: {tone}"
    
    def get_draft_by_id(self, draft_id: int) -> Optional[Dict]:
        """Get a specific draft by ID."""
        drafts = self.get_pending_drafts()
        for draft in drafts:
            if draft.get("id") == draft_id:
                return draft
        return None
    
    def format_drafts_for_table(self, drafts: List[Dict]) -> List[List[str]]:
        """Format drafts for display in table."""
        table_data = []
        for draft in drafts:
            table_data.append([
                str(draft.get("id", "")),
                draft.get("subject", ""),
                draft.get("from", ""),
                draft.get("preview", ""),
                draft.get("tone", ""),
            ])
        return table_data
    
    def build_interface(self) -> gr.Blocks:
        """Build the Gradio interface."""
        
        # Tone options
        tone_options = ["casual", "formal", "concise", "match_style"]
        
        with gr.Blocks(title="Jeeves Email Dashboard") as demo:
            gr.Markdown("# 📧 Jeeves Email Assistant Dashboard")
            gr.Markdown("Review and manage AI-generated email drafts")
            
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("## Pending Drafts")
                    # Draft table
                    drafts = self.get_pending_drafts()
                    table_data = self.format_drafts_for_table(drafts)
                    
                    drafts_table = gr.Dataframe(
                        headers=["ID", "Subject", "From", "Preview", "Tone"],
                        value=table_data,
                        interactive=False,
                        max_height=300,
                        wrap=True,
                    )
                    
                    with gr.Row():
                        refresh_btn = gr.Button("🔄 Refresh", variant="secondary")
                        auto_refresh = gr.Checkbox(label="Auto-refresh (30s)", value=True)
                        
                with gr.Column(scale=1):
                    gr.Markdown("## Draft Details")
                    selected_id = gr.Number(label="Selected Draft ID", interactive=False, precision=0)
                    selected_subject = gr.Textbox(label="Subject", interactive=False)
                    selected_from = gr.Textbox(label="From", interactive=False)
                    selected_tone = gr.Dropdown(label="Tone", choices=tone_options, value="match_style")
                    draft_text = gr.Textbox(
                        label="Draft Content",
                        lines=10,
                        interactive=True,
                    )
            
            with gr.Row():
                approve_btn = gr.Button("✅ Approve & Send", variant="primary", size="lg")
                save_btn = gr.Button("💾 Save Edit", variant="secondary")
                delete_btn = gr.Button("🗑️ Delete", variant="stop")
            
            # Status message
            status_msg = gr.Textbox(label="Status", interactive=False, lines=2)
            
            # Event handlers
            def on_refresh():
                drafts = self.get_pending_drafts()
                return self.format_drafts_for_table(drafts), ""
            
            def on_table_select(evt: gr.SelectData):
                """Handle table row selection."""
                if evt.index and len(evt.index) > 0:
                    row_idx = evt.index[0]
                    if row_idx < len(drafts):
                        draft = drafts[row_idx]
                        return (
                            draft.get("id", 0),
                            draft.get("subject", ""),
                            draft.get("from", ""),
                            draft.get("tone", "match_style"),
                            draft.get("generated_text", "")
                        )
                return 0, "", "", "match_style", ""
            
            def on_approve(draft_id):
                if draft_id is None or draft_id == 0:
                    return "Please select a draft first"
                return self.approve_draft(int(draft_id))
            
            def on_save(draft_id, new_text):
                if draft_id is None or draft_id == 0:
                    return "Please select a draft first"
                return self.edit_draft(int(draft_id), new_text)
            
            def on_delete(draft_id):
                if draft_id is None or draft_id == 0:
                    return "Please select a draft first"
                return self.delete_draft(int(draft_id))
            
            # Bind events
            refresh_btn.click(
                on_refresh,
                outputs=[drafts_table, status_msg]
            )
            
            drafts_table.select(
                on_table_select,
                outputs=[selected_id, selected_subject, selected_from, selected_tone, draft_text]
            )
            
            approve_btn.click(
                on_approve,
                inputs=[selected_id],
                outputs=[status_msg]
            )
            
            save_btn.click(
                on_save,
                inputs=[selected_id, draft_text],
                outputs=[status_msg]
            )
            
            delete_btn.click(
                on_delete,
                inputs=[selected_id],
                outputs=[status_msg]
            )
            
            # Note: Auto-refresh every 30 seconds if enabled
            # (disabled for compatibility - can be enabled with Gradio 6.0+)
        
        return demo
    
    def run(self, share: bool = False, port: int = 7860):
        """Run the dashboard."""
        demo = self.build_interface()
        demo.launch(server_port=port, share=share)


# Demo data for testing without DB
DEMO_DRAFTS = [
    {
        "id": 1,
        "subject": "Re: Project Update",
        "from": "bob@company.com",
        "preview": "update on the project...",
        "tone": "match_style",
        "generated_text": "Thanks for the update! I appreciate you keeping me in the loop. Let me know if you need any help with the next steps.",
        "created_at": "2024-01-15T10:30:00"
    },
    {
        "id": 2,
        "subject": "Meeting Tomorrow",
        "from": "alice@startup.io",
        "preview": "Are we still meeting?",
        "tone": "formal",
        "generated_text": "Dear Alice,\n\nYes, I confirm our meeting scheduled for tomorrow. I look forward to discussing the project details.\n\nBest regards",
        "created_at": "2024-01-15T11:00:00"
    },
    {
        "id": 3,
        "subject": "Quick Question",
        "from": "charlie@tech.co",
        "preview": "关于我们的API集成",
        "tone": "concise",
        "generated_text": "Hi,\n\nJust wanted to quickly ask about the API integration status. When can we expect it to be ready?\n\nThanks!",
        "created_at": "2024-01-15T14:15:00"
    },
]


def get_demo_drafts() -> List[Dict]:
    """Get demo drafts for testing."""
    return DEMO_DRAFTS.copy()


# Standard tone options
TONE_OPTIONS = ["casual", "formal", "concise", "match_style"]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Jeeves Email Dashboard")
    parser.add_argument("--port", type=int, default=7860, help="Port to run dashboard on")
    parser.add_argument("--share", action="store_true", help="Create public link")
    args = parser.parse_args()
    
    dashboard = Dashboard()
    dashboard.run(share=args.share, port=args.port)

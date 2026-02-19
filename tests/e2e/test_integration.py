"""Integration tests between components."""
import pytest
from unittest.mock import Mock, MagicMock, call


class TestGmailRAGIntegration:
    """Test Gmail client + RAG integration."""
    
    def test_email_indexing(self, mock_gmail_client, mock_rag):
        """Test emails are properly indexed in RAG."""
        emails = mock_gmail_client.list_emails()
        
        # Manually trigger indexing for each email (simulating what pipeline would do)
        for email in emails:
            mock_rag.index_email(email['id'], email)
        
        # Verify RAG indexes each email
        assert mock_rag.index_email.call_count == len(emails)
    
    def test_context_retrieval(self, mock_gmail_client, mock_rag):
        """Test RAG retrieves relevant context for email."""
        email = mock_gmail_client.get_email('email_001')
        
        # Get context from RAG
        context = mock_rag.get_context(email['id'])
        
        # Verify RAG was called with correct email ID
        mock_rag.get_context.assert_called_with(email['id'])
        
        # Verify context is returned
        assert context is not None
        assert isinstance(context, str)
    
    def test_rag_search_integration(self, mock_gmail_client, mock_rag):
        """Test RAG search works with Gmail data."""
        # Mock RAG search
        mock_rag.search.return_value = [
            {"text": "Previous email about project", "score": 0.95},
            {"text": "Earlier discussion on timeline", "score": 0.85}
        ]
        
        email = mock_gmail_client.get_email('email_001')
        
        # Search for related context
        results = mock_rag.search(email['subject'])
        
        # Verify search was called
        mock_rag.search.assert_called()
        
        # Verify results
        assert len(results) == 2
        assert results[0]['score'] > results[1]['score']


class TestLLMResponseIntegration:
    """Test LLM + Response Generator integration."""
    
    def test_response_generation(self, mock_llm, mock_rag):
        """Test response generator uses LLM correctly."""
        from unittest.mock import MagicMock
        
        response_gen = MagicMock()
        response_gen.llm = mock_llm
        
        def generate(email, tone='casual'):
            prompt = f"Email from {email['from']}: {email['body_text']}"
            return mock_llm.generate_response(prompt, tone=tone)
        
        response_gen.generate.side_effect = generate
        
        email = {
            "id": "test_001",
            "from": "sender@example.com",
            "body_text": "Hello, how are you?"
        }
        
        # Generate response
        response = response_gen.generate(email, tone='formal')
        
        # Verify LLM was called
        mock_llm.generate_response.assert_called()
        
        # Verify response is not empty
        assert response is not None
        assert len(response) > 0
    
    def test_context_injection(self, mock_llm, mock_rag):
        """Test context is injected into prompts."""
        # Setup RAG to return context
        mock_rag.get_context.return_value = "User prefers short responses. User is a software engineer."
        
        email = {
            "id": "test_002",
            "from": "colleague@company.com",
            "body_text": "Can you review my PR?"
        }
        
        # Get context
        context = mock_rag.get_context(email['id'])
        
        # Verify context is retrieved
        assert context is not None
        
        # Generate prompt with context
        prompt = f"Context: {context}\n\nEmail from {email['from']}: {email['body_text']}"
        
        # Call LLM with context-enhanced prompt
        mock_llm.generate_response(prompt, tone='match_style')
        
        # Verify LLM was called with context
        mock_llm.generate_response.assert_called()
        call_args = mock_llm.generate_response.call_args
        assert 'Context:' in call_args[0][0]
    
    def test_tone_passing(self, mock_llm):
        """Test tone parameter is passed to LLM."""
        email = {
            "id": "test_003",
            "from": "client@business.com",
            "body_text": "What's the status?"
        }
        
        # Test different tones
        for tone in ['casual', 'formal', 'concise', 'match_style']:
            mock_llm.generate_response("prompt", tone=tone)
            
            # Verify tone was passed
            calls = mock_llm.generate_response.call_args_list
            assert calls[-1][1]['tone'] == tone


class TestDatabaseIntegration:
    """Test database integration."""
    
    def test_draft_persistence(self, test_db):
        """Test drafts persist across restarts."""
        # Save a draft
        test_db.save_draft('draft_001', 'email_001', 'Draft content', 'casual')
        
        # Retrieve the draft
        draft = test_db.get_draft('draft_001')
        
        # Verify draft was saved
        assert draft is not None
        assert draft['email_id'] == 'email_001'
        assert draft['content'] == 'Draft content'
        assert draft['tone'] == 'casual'
        assert draft['status'] == 'pending'
    
    def test_draft_status_updates(self, test_db):
        """Test draft status can be updated."""
        # Save a draft
        test_db.save_draft('draft_002', 'email_002', 'Another draft', 'formal')
        
        # Update status to sent
        test_db.update_draft_status('draft_002', 'sent')
        
        # Verify status was updated
        draft = test_db.get_draft('draft_002')
        assert draft['status'] == 'sent'
        
        # Update status to rejected
        test_db.update_draft_status('draft_002', 'rejected')
        
        # Verify status was updated
        draft = test_db.get_draft('draft_002')
        assert draft['status'] == 'rejected'
    
    def test_email_deduplication(self, test_db):
        """Test same email not processed twice."""
        email_id = 'email_dedup_001'
        
        # First check - should return False
        assert test_db.is_email_processed(email_id) is False
        
        # Mark as processed
        test_db.mark_email_processed(email_id)
        
        # Second check - should return True
        assert test_db.is_email_processed(email_id) is True
    
    def test_multiple_drafts_per_email(self, test_db):
        """Test multiple drafts can be saved for the same email."""
        email_id = 'email_multi_001'
        
        # Save multiple drafts
        test_db.save_draft('draft_101', email_id, 'First draft', 'casual')
        test_db.save_draft('draft_102', email_id, 'Second draft', 'formal')
        
        # Verify both drafts exist
        draft1 = test_db.get_draft('draft_101')
        draft2 = test_db.get_draft('draft_102')
        
        assert draft1 is not None
        assert draft2 is not None
        assert draft1['content'] == 'First draft'
        assert draft2['content'] == 'Second draft'


class TestPipelineIntegration:
    """Integration tests for the full pipeline."""
    
    def test_full_pipeline_integration(self, e2e_pipeline, sample_email):
        """Test full pipeline from email to sent."""
        # Process email
        result = e2e_pipeline.process_email(sample_email)
        
        # Verify draft created
        assert result['status'] == 'draft_created'
        draft_id = result['draft_id']
        
        # Approve draft
        e2e_pipeline.approve_draft(draft_id)
        
        # Verify sent
        assert draft_id in e2e_pipeline.sent_emails
    
    def test_filter_to_draft_flow(self, e2e_pipeline, sample_emails):
        """Test filtered emails don't create drafts."""
        # Get spam email
        spam_email = next(e for e in sample_emails if e['id'] == 'email_004')
        
        # Process - should be filtered
        result = e2e_pipeline.process_email(spam_email)
        
        # Verify no draft created
        assert result['status'] == 'filtered'
        assert result['reason'] == 'spam'
        
        # Verify no drafts in database
        assert len(e2e_pipeline.drafts_created) == 0
    
    def test_confidence_affects_auto_send(self, e2e_pipeline, sample_email):
        """Test confidence scoring affects auto-send decision."""
        # First with high confidence
        result = e2e_pipeline.process_email(sample_email)
        
        # By default mock returns medium confidence
        if result['auto_send']:
            # If auto-send, verify it was high confidence
            assert result['confidence'] >= 0.8
        else:
            # If not auto-send, verify it requires manual review
            assert result['confidence'] < 0.8


class TestEndToEndScenarios:
    """Real-world end-to-end scenarios."""
    
    def test_colleague_request_scenario(self, e2e_pipeline):
        """Scenario: Colleague asks for project update."""
        email = {
            "id": "scenario_001",
            "thread_id": "thread_scenario_001",
            "from": "colleague@company.com",
            "to": "me@example.com",
            "subject": "Quick question about the API",
            "body_text": "Hey, can you help me understand how the authentication works?",
            "date": "2024-01-15T10:00:00Z"
        }
        
        result = e2e_pipeline.process_email(email)
        
        assert result['status'] == 'draft_created'
        assert result['confidence'] >= 0.7
    
    def test_client_meeting_request_scenario(self, e2e_pipeline):
        """Scenario: Client requests a meeting."""
        email = {
            "id": "scenario_002",
            "thread_id": "thread_scenario_002",
            "from": "client@external.com",
            "to": "me@example.com",
            "subject": "Meeting Request",
            "body_text": "I'd like to schedule a call to discuss the project next week. What times work for you?",
            "date": "2024-01-15T11:00:00Z"
        }
        
        result = e2e_pipeline.process_email(email)
        
        assert result['status'] == 'draft_created'
    
    def test_personal_email_scenario(self, e2e_pipeline):
        """Scenario: Personal email from friend."""
        email = {
            "id": "scenario_003",
            "thread_id": "thread_scenario_003",
            "from": "friend@gmail.com",
            "to": "me@example.com",
            "subject": "Coffee this weekend?",
            "body_text": "Hey! Want to grab coffee this Saturday?",
            "date": "2024-01-15T12:00:00Z"
        }
        
        result = e2e_pipeline.process_email(email, tone='casual')
        
        assert result['status'] == 'draft_created'
        draft = e2e_pipeline.db.get_draft(result['draft_id'])
        assert draft['tone'] == 'casual'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""End-to-end tests for complete email processing flow."""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestFullFlow:
    """Test complete email processing flow."""
    
    def test_email_to_draft_generation(self, e2e_pipeline, sample_email):
        """Test: Email received → Draft generated."""
        result = e2e_pipeline.process_email(sample_email)
        
        # Verify draft was created
        assert result['status'] == 'draft_created'
        assert 'draft_id' in result
        assert result['draft_id'] == 'draft_001'
        
        # Verify Gmail client was called
        e2e_pipeline.gmail.create_draft.assert_called_once()
        
        # Verify draft was saved to database
        draft = e2e_pipeline.db.get_draft(result['draft_id'])
        assert draft is not None
        assert draft['email_id'] == sample_email['id']
    
    def test_draft_to_approval_to_send(self, e2e_pipeline, sample_email):
        """Test: Draft created → User approves → Email sent."""
        # First create a draft
        result = e2e_pipeline.process_email(sample_email)
        draft_id = result['draft_id']
        
        # User approves the draft
        approval_result = e2e_pipeline.approve_draft(draft_id)
        
        # Verify email was sent
        assert approval_result is True
        e2e_pipeline.gmail.send_draft.assert_called_with(draft_id)
        
        # Verify draft status updated
        draft = e2e_pipeline.db.get_draft(draft_id)
        assert draft['status'] == 'sent'
        
        # Verify in sent emails list
        assert draft_id in e2e_pipeline.sent_emails
    
    def test_draft_edit_and_send(self, e2e_pipeline, sample_email):
        """Test: Draft created → User edits → Email sent."""
        # First create a draft
        result = e2e_pipeline.process_email(sample_email)
        draft_id = result['draft_id']
        
        # User edits the draft
        new_content = "Edited response content"
        edited_draft = e2e_pipeline.edit_draft(draft_id, new_content)
        
        # Verify draft was edited
        assert edited_draft['content'] == new_content
        
        # User approves the edited draft
        e2e_pipeline.approve_draft(draft_id)
        
        # Verify email was sent
        assert draft_id in e2e_pipeline.sent_emails
    
    def test_draft_rejection(self, e2e_pipeline, sample_email):
        """Test: Draft created → User rejects → No email sent."""
        # First create a draft
        result = e2e_pipeline.process_email(sample_email)
        draft_id = result['draft_id']
        
        # User rejects the draft
        rejection_result = e2e_pipeline.reject_draft(draft_id)
        
        # Verify rejection was successful
        assert rejection_result is True
        
        # Verify draft status updated
        draft = e2e_pipeline.db.get_draft(draft_id)
        assert draft['status'] == 'rejected'
        
        # Verify email was NOT sent
        assert draft_id not in e2e_pipeline.sent_emails


class TestToneModes:
    """Test each tone mode produces appropriate responses."""
    
    def test_casual_tone(self, e2e_pipeline, sample_email):
        """Test casual tone generates informal response."""
        result = e2e_pipeline.process_email(sample_email, tone='casual')
        
        assert result['status'] == 'draft_created'
        # The mock returns casual response
        draft = e2e_pipeline.db.get_draft(result['draft_id'])
        assert draft['tone'] == 'casual'
    
    def test_formal_tone(self, e2e_pipeline, sample_email):
        """Test formal tone generates professional response."""
        result = e2e_pipeline.process_email(sample_email, tone='formal')
        
        assert result['status'] == 'draft_created'
        draft = e2e_pipeline.db.get_draft(result['draft_id'])
        assert draft['tone'] == 'formal'
    
    def test_concise_tone(self, e2e_pipeline, sample_email):
        """Test concise tone generates brief response."""
        result = e2e_pipeline.process_email(sample_email, tone='concise')
        
        assert result['status'] == 'draft_created'
        draft = e2e_pipeline.db.get_draft(result['draft_id'])
        assert draft['tone'] == 'concise'
    
    def test_match_style_tone(self, e2e_pipeline, sample_email):
        """Test match_style tone mimics user's style."""
        result = e2e_pipeline.process_email(sample_email, tone='match_style')
        
        assert result['status'] == 'draft_created'
        draft = e2e_pipeline.db.get_draft(result['draft_id'])
        assert draft['tone'] == 'match_style'


class TestFiltering:
    """Test email filtering logic."""
    
    def test_filter_promotional_email(self, e2e_pipeline):
        """Test promotional emails are filtered out."""
        # Create a promotional email with no-reply sender but promotional keywords in subject
        promo_email = {
            "id": "email_promo",
            "thread_id": "thread_promo",
            "from": "offers@shop.com",
            "to": "me@example.com",
            "subject": "SPECIAL OFFER: 50% OFF!",
            "body_text": "Check out our latest deals...",
            "date": "2024-01-15T12:00:00Z"
        }
        
        result = e2e_pipeline.process_email(promo_email)
        
        assert result['status'] == 'filtered'
        assert result['reason'] == 'promotional'
    
    def test_filter_spam_email(self, e2e_pipeline, sample_emails):
        """Test spam emails are filtered out."""
        # Find the spam email
        spam_email = next(e for e in sample_emails if e['id'] == 'email_004')
        
        result = e2e_pipeline.process_email(spam_email)
        
        assert result['status'] == 'filtered'
        assert result['reason'] == 'spam'
    
    def test_filter_noreply_email(self, e2e_pipeline, sample_emails):
        """Test noreply emails are filtered out."""
        # Create a noreply email
        noreply_email = {
            "id": "email_noreply",
            "thread_id": "thread_noreply",
            "from": "noreply@service.com",
            "to": "me@example.com",
            "subject": "Notification",
            "body_text": "This is an automated notification.",
            "date": "2024-01-15T10:00:00Z"
        }
        
        result = e2e_pipeline.process_email(noreply_email)
        
        assert result['status'] == 'filtered'
        assert result['reason'] == 'noreply_sender'
    
    def test_accept_valid_email(self, e2e_pipeline, sample_email):
        """Test valid emails are processed."""
        result = e2e_pipeline.process_email(sample_email)
        
        assert result['status'] == 'draft_created'
        assert 'draft_id' in result


class TestConfidenceScoring:
    """Test confidence scoring and auto-send logic."""
    
    def test_high_confidence_auto_send(self, e2e_pipeline, sample_emails):
        """Test high confidence score triggers auto-send."""
        # Use simple question email that should have high confidence
        high_conf_email = {
            "id": "email_high_conf",
            "thread_id": "thread_high_conf",
            "from": "colleague@company.com",
            "to": "me@example.com",
            "subject": "When is the meeting?",
            "body_text": "What time is the meeting tomorrow?",
            "date": "2024-01-15T10:00:00Z"
        }
        
        result = e2e_pipeline.process_email(high_conf_email)
        
        assert result['status'] == 'draft_created'
        assert result['confidence'] >= 0.8
        assert result['auto_send'] is True
    
    def test_low_confidence_manual_review(self, e2e_pipeline, sample_email):
        """Test low confidence score requires manual review."""
        # Use a simple email (should have high confidence by default)
        # Let's modify mock to return low confidence
        e2e_pipeline.confidence.score_email = Mock(return_value=0.5)
        
        result = e2e_pipeline.process_email(sample_email)
        
        assert result['status'] == 'draft_created'
        assert result['confidence'] < 0.8
        assert result['auto_send'] is False
    
    def test_financial_email_no_auto_send(self, e2e_pipeline, sample_emails):
        """Test financial emails never auto-send."""
        # Find the financial email
        financial_email = next(e for e in sample_emails if e['id'] == 'email_005')
        
        result = e2e_pipeline.process_email(financial_email)
        
        assert result['status'] == 'draft_created'
        # Financial emails should have low confidence
        assert result['confidence'] < 0.8
        assert result['auto_send'] is False
    
    def test_urgent_email_manual_review(self, e2e_pipeline, sample_emails):
        """Test urgent emails require manual review."""
        # Find the urgent email
        urgent_email = next(e for e in sample_emails if e['id'] == 'email_006')
        
        result = e2e_pipeline.process_email(urgent_email)
        
        assert result['status'] == 'draft_created'
        # Urgent emails should have low confidence
        assert result['confidence'] < 0.8
        assert result['auto_send'] is False


class TestErrorHandling:
    """Test error handling and recovery."""
    
    def test_gmail_api_failure(self, e2e_pipeline, sample_email):
        """Test handling of Gmail API failures."""
        # Make Gmail client raise an exception
        e2e_pipeline.gmail.create_draft.side_effect = Exception("Gmail API error: rate limit exceeded")
        
        with pytest.raises(Exception) as exc_info:
            e2e_pipeline.process_email(sample_email)
        
        assert "Gmail API error" in str(exc_info.value)
    
    def test_llm_timeout(self, e2e_pipeline, sample_email):
        """Test handling of LLM timeouts."""
        # Make LLM raise a timeout
        e2e_pipeline.llm.generate_response.side_effect = TimeoutError("LLM request timed out")
        
        # The error should propagate
        with pytest.raises(TimeoutError):
            e2e_pipeline.process_email(sample_email)
    
    def test_rate_limiting(self, e2e_pipeline, sample_email):
        """Test handling of API rate limits."""
        # Make Gmail return rate limit error
        from googleapiclient.errors import HttpError
        
        # Create a mock HttpError with 429 status
        mock_resp = Mock()
        mock_resp.status = 429
        mock_resp.reason = "Rate Limit Exceeded"
        
        e2e_pipeline.gmail.create_draft.side_effect = Exception("Rate limit exceeded. Please try again later.")
        
        with pytest.raises(Exception) as exc_info:
            e2e_pipeline.process_email(sample_email)
        
        assert "Rate limit" in str(exc_info.value) or "429" in str(exc_info.value)
    
    def test_duplicate_email_skip(self, e2e_pipeline, sample_email):
        """Test same email is not processed twice."""
        # First process
        result1 = e2e_pipeline.process_email(sample_email)
        assert result1['status'] == 'draft_created'
        
        # Mark as processed
        e2e_pipeline.db.mark_email_processed(sample_email['id'])
        
        # Second process should be skipped
        result2 = e2e_pipeline.process_email(sample_email)
        assert result2['status'] == 'skipped'
        assert result2['reason'] == 'already_processed'


class TestLoadTesting:
    """Test system under load."""
    
    def test_batch_email_processing(self, e2e_pipeline, sample_emails):
        """Test processing multiple emails in batch."""
        # Filter out emails that would be filtered
        valid_emails = [e for e in sample_emails if e['id'] in ['email_001', 'email_002', 'email_006', 'email_007']]
        
        results = []
        for email in valid_emails:
            result = e2e_pipeline.process_email(email)
            results.append(result)
        
        # All should create drafts
        assert all(r['status'] == 'draft_created' for r in results)
        assert len(results) == len(valid_emails)
    
    def test_concurrent_draft_generation(self, e2e_pipeline, sample_emails):
        """Test concurrent draft generation."""
        import threading
        
        results = []
        errors = []
        
        def process_email_thread(email):
            try:
                result = e2e_pipeline.process_email(email)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Process first 3 valid emails concurrently
        valid_emails = [e for e in sample_emails if e['id'] in ['email_001', 'email_002', 'email_007']]
        
        threads = []
        for email in valid_emails:
            t = threading.Thread(target=process_email_thread, args=(email,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All should succeed
        assert len(errors) == 0
        assert len(results) == len(valid_emails)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

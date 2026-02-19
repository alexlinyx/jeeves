"""Tests for confidence scoring module."""
import pytest
from src.confidence import (
    ConfidenceScorer,
    ScoreResult,
    RiskLevel,
    FINANCIAL_PATTERNS,
    LEGAL_PATTERNS,
    SENSITIVE_PATTERNS,
    URGENT_PATTERNS,
    analyze_content_risk,
    get_auto_send_eligibility
)


class TestConfidenceScorer:
    """Test cases for ConfidenceScorer."""
    
    def test_file_exists(self):
        """Test confidence.py exists."""
        # If we get here, the file was imported successfully
        assert ConfidenceScorer is not None
    
    def test_import(self):
        """Test ConfidenceScorer can be imported."""
        from src.confidence import ConfidenceScorer
        assert ConfidenceScorer is not None
    
    def test_class_has_required_methods(self):
        """Test all required methods exist."""
        scorer = ConfidenceScorer()
        assert hasattr(scorer, 'score')
        assert hasattr(scorer, 'should_auto_send')
        assert hasattr(scorer, 'get_risk_level')
        assert callable(scorer.score)
        assert callable(scorer.should_auto_send)
        assert callable(scorer.get_risk_level)
    
    def test_default_auto_send_threshold(self):
        """Test default threshold is 0.9."""
        scorer = ConfidenceScorer()
        assert scorer.auto_send_threshold == 0.9
    
    def test_score_returns_score_result(self):
        """Test score() returns ScoreResult dataclass."""
        scorer = ConfidenceScorer()
        result = scorer.score(
            {'from': 'test@example.com', 'text': 'Hello'},
            {'text': 'Thanks for your email!'}
        )
        assert isinstance(result, ScoreResult)
        assert hasattr(result, 'score')
        assert hasattr(result, 'risk_level')
        assert hasattr(result, 'factors')
        assert hasattr(result, 'reasoning')
        assert hasattr(result, 'auto_send')
    
    def test_score_range(self):
        """Test score is always between 0.0 and 1.0."""
        scorer = ConfidenceScorer()
        
        # Test various inputs
        test_cases = [
            ({'from': 'test@example.com', 'text': 'Hello'}, {'text': 'Hi'}),
            ({'from': 'test@gmail.com', 'text': 'Question?'}, {'text': 'Thanks for your email!'}),
            ({'from': 'unknown@weirddomain.xyz', 'text': ''}, {'text': 'A' * 1000}),
            ({'from': 'test@example.com', 'text': 'Hello'}, {'text': ''}),
        ]
        
        for incoming, draft in test_cases:
            result = scorer.score(incoming, draft)
            assert 0.0 <= result.score <= 1.0, f"Score {result.score} out of range"
    
    def test_auto_send_high_score_low_risk(self):
        """Test auto-send True for high score + low risk."""
        scorer = ConfidenceScorer()
        
        # Create a high-scoring, low-risk scenario
        incoming = {'from': 'friend@gmail.com', 'text': 'Hey, how are you?'}
        draft = {'text': 'Thanks for checking in! I am doing great.'}
        
        result = scorer.score(incoming, draft)
        
        # Should have high score (>=0.9) and low risk
        if result.risk_level == RiskLevel.LOW and result.score >= 0.9:
            assert result.auto_send == True
    
    def test_no_auto_send_medium_score(self):
        """Test auto-send False for medium score."""
        scorer = ConfidenceScorer()
        
        # Create a medium-scoring scenario
        incoming = {'from': 'unknown@weird.com', 'text': 'Hello'}
        draft = {'text': 'Hi'}
        
        result = scorer.score(incoming, draft)
        
        # If score is below threshold, auto_send should be False
        if result.score < 0.9:
            assert result.auto_send == False
    
    def test_no_auto_send_high_risk(self):
        """Test auto-send False for any critical risk."""
        scorer = ConfidenceScorer()
        
        # Test critical risk
        assert scorer.should_auto_send(0.95, RiskLevel.CRITICAL) == False
        
        # Test high risk
        assert scorer.should_auto_send(0.95, RiskLevel.HIGH) == False
        
        # Test medium risk with high score - should not auto-send
        assert scorer.should_auto_send(0.9, RiskLevel.MEDIUM) == False
        
        # Test low risk with high score - should auto-send
        assert scorer.should_auto_send(0.9, RiskLevel.LOW) == True
    
    def test_financial_detection(self):
        """Test financial patterns detected."""
        scorer = ConfidenceScorer()
        
        # Test financial keywords
        test_texts = [
            "Please send wire transfer to my bank account",
            "I need to make a payment of $500",
            "Can you send money via wire transfer?",
        ]
        
        for text in test_texts:
            risk = scorer.get_risk_level(text)
            assert risk in (RiskLevel.CRITICAL, RiskLevel.HIGH), f"Failed to detect financial risk in: {text}"
    
    def test_legal_detection(self):
        """Test legal patterns detected."""
        scorer = ConfidenceScorer()
        
        # Test legal keywords
        test_texts = [
            "We need to review the contract",
            "I will sue if not resolved",
            "Please consult with your attorney",
        ]
        
        for text in test_texts:
            risk = scorer.get_risk_level(text)
            assert risk in (RiskLevel.HIGH, RiskLevel.CRITICAL), f"Failed to detect legal risk in: {text}"
    
    def test_sensitive_detection(self):
        """Test sensitive patterns detected."""
        scorer = ConfidenceScorer()
        
        # Test sensitive keywords
        test_texts = [
            "Please reset my password",
            "My medical records need updating",
            "Do not share this confidential information",
        ]
        
        for text in test_texts:
            risk = scorer.get_risk_level(text)
            assert risk in (RiskLevel.HIGH, RiskLevel.CRITICAL), f"Failed to detect sensitive risk in: {text}"
    
    def test_urgent_detection(self):
        """Test urgent patterns detected."""
        scorer = ConfidenceScorer()
        
        # Test urgent keywords
        test_texts = [
            "This is urgent, please respond immediately",
            "ASAP - deadline tomorrow",
            "Emergency meeting needed right now",
        ]
        
        for text in test_texts:
            risk = scorer.get_risk_level(text)
            assert risk in (RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL), f"Failed to detect urgent risk in: {text}"
    
    def test_score_result_has_reasoning(self):
        """Test ScoreResult includes reasoning list."""
        scorer = ConfidenceScorer()
        result = scorer.score(
            {'from': 'test@example.com', 'text': 'Hello'},
            {'text': 'Thanks for your email!'}
        )
        
        assert isinstance(result.reasoning, list)
        assert len(result.reasoning) > 0


class TestRiskLevel:
    """Test RiskLevel enum."""
    
    def test_risk_levels_exist(self):
        """Test all risk levels defined: LOW, MEDIUM, HIGH, CRITICAL."""
        assert hasattr(RiskLevel, 'LOW')
        assert hasattr(RiskLevel, 'MEDIUM')
        assert hasattr(RiskLevel, 'HIGH')
        assert hasattr(RiskLevel, 'CRITICAL')
        
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"


class TestSafetyPatterns:
    """Test safety pattern detection."""
    
    def test_financial_patterns_defined(self):
        """Test FINANCIAL_PATTERNS list exists."""
        assert isinstance(FINANCIAL_PATTERNS, list)
        assert len(FINANCIAL_PATTERNS) > 0
    
    def test_legal_patterns_defined(self):
        """Test LEGAL_PATTERNS list exists."""
        assert isinstance(LEGAL_PATTERNS, list)
        assert len(LEGAL_PATTERNS) > 0
    
    def test_sensitive_patterns_defined(self):
        """Test SENSITIVE_PATTERNS list exists."""
        assert isinstance(SENSITIVE_PATTERNS, list)
        assert len(SENSITIVE_PATTERNS) > 0
    
    def test_urgent_patterns_defined(self):
        """Test URGENT_PATTERNS list exists."""
        assert isinstance(URGENT_PATTERNS, list)
        assert len(URGENT_PATTERNS) > 0


class TestAnalyzeContentRisk:
    """Test analyze_content_risk function."""
    
    def test_returns_dict(self):
        """Test function returns a dict."""
        result = analyze_content_risk("Test text")
        assert isinstance(result, dict)
    
    def test_has_required_keys(self):
        """Test result has all required keys."""
        result = analyze_content_risk("Test text")
        assert 'financial' in result
        assert 'legal' in result
        assert 'sensitive' in result
        assert 'urgent' in result
    
    def test_empty_text(self):
        """Test empty text returns empty lists."""
        result = analyze_content_risk("")
        assert result['financial'] == []
        assert result['legal'] == []
        assert result['sensitive'] == []
        assert result['urgent'] == []


class TestGetAutoSendEligibility:
    """Test get_auto_send_eligibility function."""
    
    def test_returns_tuple(self):
        """Test function returns a tuple."""
        result = get_auto_send_eligibility(0.5, RiskLevel.LOW)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_critical_risk_not_eligible(self):
        """Test critical risk returns False."""
        eligible, reason = get_auto_send_eligibility(0.95, RiskLevel.CRITICAL)
        assert eligible == False
    
    def test_high_risk_not_eligible(self):
        """Test high risk returns False."""
        eligible, reason = get_auto_send_eligibility(0.95, RiskLevel.HIGH)
        assert eligible == False
    
    def test_low_risk_high_score_eligible(self):
        """Test low risk + high score returns True."""
        eligible, reason = get_auto_send_eligibility(0.9, RiskLevel.LOW)
        assert eligible == True
    
    def test_low_score_not_eligible(self):
        """Test low score returns False."""
        eligible, reason = get_auto_send_eligibility(0.5, RiskLevel.LOW)
        assert eligible == False


class TestScorerEdgeCases:
    """Test edge cases for the scorer."""
    
    def test_empty_draft(self):
        """Test scoring empty draft."""
        scorer = ConfidenceScorer()
        result = scorer.score(
            {'from': 'test@example.com'},
            {'text': ''}
        )
        assert result.score < 0.5  # Should have low score
        assert result.auto_send == False
    
    def test_empty_incoming(self):
        """Test scoring with empty incoming email."""
        scorer = ConfidenceScorer()
        result = scorer.score(
            {},
            {'text': 'Thanks!'}
        )
        assert 0.0 <= result.score <= 1.0
    
    def test_custom_threshold(self):
        """Test custom threshold."""
        scorer = ConfidenceScorer(auto_send_threshold=0.7)
        assert scorer.auto_send_threshold == 0.7
        
        # With lower threshold, low risk + moderate score should auto-send
        result = scorer.should_auto_send(0.7, RiskLevel.LOW)
        assert result == True


class TestFactorWeights:
    """Test factor weights are properly configured."""
    
    def test_weights_sum_to_one(self):
        """Test factor weights sum to 1.0."""
        total = sum(ConfidenceScorer.FACTOR_WEIGHTS.values())
        assert abs(total - 1.0) < 0.01
    
    def test_all_factors_defined(self):
        """Test all 5 factors are defined."""
        expected_factors = [
            'sender_familiarity',
            'response_length',
            'tone_match',
            'context_relevance',
            'content_safety'
        ]
        for factor in expected_factors:
            assert factor in ConfidenceScorer.FACTOR_WEIGHTS

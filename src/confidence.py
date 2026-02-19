"""Confidence scoring for draft quality and auto-send decisions."""
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    """Risk levels for email content."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ScoreResult:
    """Result of confidence scoring."""
    score: float
    risk_level: RiskLevel
    factors: Dict[str, float]
    reasoning: List[str]
    auto_send: bool


class ConfidenceScorer:
    """Score draft quality and determine auto-send eligibility."""
    
    # Default thresholds
    AUTO_SEND_THRESHOLD = 0.9
    MANUAL_REVIEW_THRESHOLD = 0.5
    
    # Factor weights
    FACTOR_WEIGHTS = {
        'sender_familiarity': 0.25,
        'response_length': 0.15,
        'tone_match': 0.15,
        'context_relevance': 0.20,
        'content_safety': 0.25
    }
    
    def __init__(
        self,
        auto_send_threshold: float = None,
        rag_pipeline=None,
        db=None
    ):
        """Initialize confidence scorer.
        
        Args:
            auto_send_threshold: Minimum score for auto-send (default: 0.9)
            rag_pipeline: RAGPipeline for context matching
            db: Database for sender history
        """
        self.auto_send_threshold = auto_send_threshold or self.AUTO_SEND_THRESHOLD
        self.rag_pipeline = rag_pipeline
        self.db = db
    
    def score(self, incoming_email: Dict, draft: Dict) -> ScoreResult:
        """Calculate confidence score for a draft.
        
        Args:
            incoming_email: Original email dict
            draft: Generated draft dict
            
        Returns:
            ScoreResult with score, risk level, factors, and reasoning
        """
        reasoning = []
        
        # Score each factor
        sender_score, sender_reason = self._score_sender_familiarity(incoming_email)
        reasoning.append(sender_reason)
        
        length_score, length_reason = self._score_response_length(draft)
        reasoning.append(length_reason)
        
        tone_score, tone_reason = self._score_tone_match(incoming_email, draft)
        reasoning.append(tone_reason)
        
        context_score, context_reason = self._score_context_relevance(incoming_email, draft)
        reasoning.append(context_reason)
        
        safety_score, risk_level, safety_reason = self._score_content_safety(draft)
        reasoning.append(safety_reason)
        
        # Calculate weighted total score
        factors = {
            'sender_familiarity': sender_score,
            'response_length': length_score,
            'tone_match': tone_score,
            'context_relevance': context_score,
            'content_safety': safety_score
        }
        
        total_score = sum(
            factors[key] * self.FACTOR_WEIGHTS[key]
            for key in self.FACTOR_WEIGHTS
        )
        
        # Ensure score is in valid range
        total_score = max(0.0, min(1.0, total_score))
        
        # Determine auto-send
        auto_send = self.should_auto_send(total_score, risk_level)
        
        return ScoreResult(
            score=total_score,
            risk_level=risk_level,
            factors=factors,
            reasoning=[r for r in reasoning if r],
            auto_send=auto_send
        )
    
    def should_auto_send(self, score: float, risk_level: RiskLevel) -> bool:
        """Determine if draft should be auto-sent.
        
        Args:
            score: Confidence score (0.0-1.0)
            risk_level: Risk level of content
            
        Returns:
            True if should auto-send
        """
        # Never auto-send critical, high, or medium risk content
        if risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM):
            return False
        
        # Auto-send if score meets threshold and risk is low
        return score >= self.auto_send_threshold and risk_level == RiskLevel.LOW
    
    def _score_sender_familiarity(self, email: Dict) -> Tuple[float, str]:
        """Score based on sender familiarity.
        
        Higher score for known senders we've emailed before.
        """
        sender = email.get('from', '').lower()
        
        # Check if we have database access and sender history
        if self.db:
            try:
                # Check sender in database
                if hasattr(self.db, 'get_sender_history'):
                    history = self.db.get_sender_history(sender)
                    if history and len(history) > 5:
                        return 1.0, "Sender has extensive email history"
                    elif history and len(history) > 0:
                        return 0.7, "Sender has some email history"
            except Exception:
                pass
        
        # Default: moderate familiarity based on email domain
        if '@' in sender:
            domain = sender.split('@')[1] if '@' in sender else ''
            # Known domains get higher score
            common_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
            if any(common in domain for common in common_domains):
                return 0.6, "Sender uses common email provider"
        
        return 0.4, "Unknown sender - default familiarity score"
    
    def _score_response_length(self, draft: Dict) -> Tuple[float, str]:
        """Score based on response length appropriateness.
        
        Penalize too short or too long responses.
        """
        text = draft.get('text', '')
        text = text.strip() if text else ''
        length = len(text)
        
        # Optimal range: 50-300 characters
        optimal_min = 50
        optimal_max = 300
        
        if length == 0:
            return 0.0, "Empty draft - no content"
        elif length < optimal_min:
            # Linear scale from 0 to optimal_min
            score = length / optimal_min
            return score, f"Response too short ({length} chars)"
        elif length <= optimal_max:
            return 1.0, f"Response length optimal ({length} chars)"
        else:
            # Penalize overly long responses
            # Linear decrease from optimal_max to 1000, then floor at 0.3
            if length <= 1000:
                score = 1.0 - ((length - optimal_max) / (1000 - optimal_max)) * 0.7
            else:
                score = 0.3
            return max(0.3, score), f"Response longer than optimal ({length} chars)"
    
    def _score_tone_match(self, incoming_email: Dict, draft: Dict) -> Tuple[float, str]:
        """Score based on tone matching.
        
        Check if draft tone matches incoming email tone.
        """
        incoming_text = incoming_email.get('text', '') or incoming_email.get('subject', '')
        draft_text = draft.get('text', '')
        
        if not incoming_text or not draft_text:
            return 0.5, "No text to compare for tone matching"
        
        # Simple heuristic: check for question marks in incoming
        # If incoming has questions, draft should be more substantive
        has_questions = '?' in incoming_text
        
        # Check for exclamation marks - indicates enthusiastic tone
        has_exclamation = '!' in draft_text
        
        # Check for formal language
        formal_words = ['please', 'thank you', 'regards', 'sincerely', 'best']
        informal_words = ['hey', 'cool', 'awesome', 'thanks', 'cheers']
        
        incoming_lower = incoming_text.lower()
        draft_lower = draft_text.lower()
        
        formal_count = sum(1 for word in formal_words if word in incoming_lower)
        informal_count = sum(1 for word in informal_words if word in incoming_lower)
        
        if formal_count > informal_count:
            return 0.8, "Formal tone matched"
        elif informal_count > formal_count:
            return 0.8, "Informal tone matched"
        else:
            return 0.7, "Neutral tone - default match"
    
    def _score_context_relevance(self, incoming_email: Dict, draft: Dict) -> Tuple[float, str]:
        """Score based on context relevance from RAG.
        
        Higher score when draft references relevant past context.
        """
        # Check if RAG pipeline is available
        if self.rag_pipeline:
            try:
                incoming_text = incoming_email.get('text', '') or incoming_email.get('subject', '')
                draft_text = draft.get('text', '')
                
                # Query RAG for relevant context
                if hasattr(self.rag_pipeline, 'query'):
                    context = self.rag_pipeline.query(incoming_text, top_k=3)
                    if context and len(context) > 0:
                        # Check if draft references context keywords
                        context_text = ' '.join(str(c) for c in context)
                        # Simple keyword overlap check
                        draft_words = set(draft_text.lower().split())
                        context_words = set(context_text.lower().split())
                        overlap = len(draft_words & context_words)
                        if overlap > 5:
                            return 0.9, "Draft references relevant context"
                        elif overlap > 0:
                            return 0.7, "Some context relevance detected"
            except Exception:
                pass
        
        # Default: moderate context relevance
        return 0.6, "No RAG context available - default score"
    
    def _score_content_safety(self, draft: Dict) -> Tuple[float, RiskLevel, str]:
        """Score based on content safety analysis.
        
        Returns risk level and score.
        """
        text = draft.get('text', '')
        
        if not text:
            return 0.0, RiskLevel.LOW, "Empty draft - no content risk"
        
        # Get risk level
        risk_level = self.get_risk_level(text)
        
        # Map risk level to safety score
        risk_to_score = {
            RiskLevel.LOW: 1.0,
            RiskLevel.MEDIUM: 0.7,
            RiskLevel.HIGH: 0.4,
            RiskLevel.CRITICAL: 0.0
        }
        
        score = risk_to_score.get(risk_level, 0.5)
        
        reason = f"Content safety: {risk_level.value} risk"
        
        return score, risk_level, reason
    
    def get_risk_level(self, text: str) -> RiskLevel:
        """Analyze text for risk level.
        
        Checks for:
        - Financial keywords (bank, transfer, payment, wire)
        - Legal keywords (contract, sue, legal, attorney)
        - Sensitive topics (password, ssn, medical, health)
        - Urgent language (immediately, urgent, asap, emergency)
        """
        if not text:
            return RiskLevel.LOW
        
        text_lower = text.lower()
        
        # Check for critical risk patterns
        critical_matches = []
        for pattern in FINANCIAL_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                critical_matches.append('financial')
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                critical_matches.append('sensitive')
        
        if critical_matches:
            return RiskLevel.CRITICAL
        
        # Check for high risk patterns
        high_matches = []
        for pattern in LEGAL_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                high_matches.append('legal')
        
        if high_matches:
            return RiskLevel.HIGH
        
        # Check for medium risk (urgent patterns)
        urgent_matches = []
        for pattern in URGENT_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                urgent_matches.append('urgent')
        
        if urgent_matches:
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW


# Safety patterns
FINANCIAL_PATTERNS = [
    r'\bbank\s*(account|transfer)\b',
    r'\bwire\s*transfer\b',
    r'\bpayment\b',
    r'\bcredit\s*card\b',
    r'\bssn\b',
    r'\bsocial\s*security\b',
    r'\bwire\s*money\b',
    r'\bsend\s*money\b',
    r'\bbitcoin\b',
    r'\bcrypto\b',
]

LEGAL_PATTERNS = [
    r'\bcontract\b',
    r'\blawsuit\b',
    r'\bsue\b',
    r'\battorney\b',
    r'\blawyer\b',
    r'\blegal\s*action\b',
    r'\bn\s*d\s*a\b',  # NDA variations
    r'\bsettlement\b',
    r'\bliability\b',
]

SENSITIVE_PATTERNS = [
    r'\bpassword\b',
    r'\bpasscode\b',
    r'\bpin\b',
    r'\bsecret\b',
    r'\bconfidential\b',
    r'\bmedical\b',
    r'\bhealth\b',
    r'\bdiagnosis\b',
    r'\bpatient\b',
]

URGENT_PATTERNS = [
    r'\bimmediately\b',
    r'\burgent\b',
    r'\basap\b',
    r'\bemergency\b',
    r'\bright\s*now\b',
    r'\bdeadline\b',
    r'\btime\s*sensitive\b',
]


def analyze_content_risk(text: str) -> Dict[str, List[str]]:
    """Analyze text for risk patterns.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dict with 'financial', 'legal', 'sensitive', 'urgent' lists of matches
    """
    if not text:
        return {'financial': [], 'legal': [], 'sensitive': [], 'urgent': []}
    
    text_lower = text.lower()
    
    def find_matches(patterns: List[str]) -> List[str]:
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text_lower, re.IGNORECASE)
            if found:
                matches.extend(found if isinstance(found[0], str) else [pattern])
        return matches
    
    return {
        'financial': find_matches(FINANCIAL_PATTERNS),
        'legal': find_matches(LEGAL_PATTERNS),
        'sensitive': find_matches(SENSITIVE_PATTERNS),
        'urgent': find_matches(URGENT_PATTERNS)
    }


def get_auto_send_eligibility(score: float, risk_level: RiskLevel) -> Tuple[bool, str]:
    """Determine if draft is eligible for auto-send.
    
    Args:
        score: Confidence score
        risk_level: Content risk level
        
    Returns:
        Tuple of (eligible, reason)
    """
    # Check risk level first - only LOW risk can auto-send
    if risk_level == RiskLevel.CRITICAL:
        return False, "Critical risk content - manual review required"
    if risk_level == RiskLevel.HIGH:
        return False, "High risk content - manual review required"
    if risk_level == RiskLevel.MEDIUM:
        return False, "Medium risk content - manual review required"
    
    # Check score threshold
    threshold = ConfidenceScorer.AUTO_SEND_THRESHOLD
    if score >= threshold:
        return True, f"Score {score:.2f} meets threshold {threshold}"
    elif score >= ConfidenceScorer.MANUAL_REVIEW_THRESHOLD:
        return False, f"Score {score:.2f} below auto-send threshold - queue for review"
    else:
        return False, f"Low score {score:.2f} - flag for manual review"

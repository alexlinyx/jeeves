# Feature Spec: Confidence Scoring & Auto-Send

**Phase:** 4.2  
**Branch:** `feature/4.2-confidence-scoring`  
**Priority:** P1  
**Est. Time:** 6 hours

---

## Objective

Implement confidence scoring system to evaluate draft quality and enable automatic sending for high-confidence, low-risk emails.

---

## Acceptance Criteria

- [ ] `src/confidence.py` implements confidence scoring
- [ ] Score range: 0.0-1.0 (float)
- [ ] Considers: sender familiarity, email complexity, response length
- [ ] Safety rules: never auto-send financial, legal, sensitive topics
- [ ] Configurable thresholds (default: auto-send >= 0.9)
- [ ] Logs all scoring decisions with reasoning
- [ ] Tests verify scoring logic and safety rules
- [ ] Unit tests pass

---

## Deliverable

### `src/confidence.py`

```python
"""Confidence scoring for draft quality and auto-send decisions."""
import re
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
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
        pass
    
    def should_auto_send(self, score: float, risk_level: RiskLevel) -> bool:
        """Determine if draft should be auto-sent.
        
        Args:
            score: Confidence score (0.0-1.0)
            risk_level: Risk level of content
            
        Returns:
            True if should auto-send
        """
        pass
    
    def _score_sender_familiarity(self, email: Dict) -> Tuple[float, str]:
        """Score based on sender familiarity.
        
        Higher score for known senders we've emailed before.
        """
        pass
    
    def _score_response_length(self, draft: Dict) -> Tuple[float, str]:
        """Score based on response length appropriateness.
        
        Penalize too short or too long responses.
        """
        pass
    
    def _score_tone_match(self, incoming_email: Dict, draft: Dict) -> Tuple[float, str]:
        """Score based on tone matching.
        
        Check if draft tone matches incoming email tone.
        """
        pass
    
    def _score_context_relevance(self, incoming_email: Dict, draft: Dict) -> Tuple[float, str]:
        """Score based on context relevance from RAG.
        
        Higher score when draft references relevant past context.
        """
        pass
    
    def _score_content_safety(self, draft: Dict) -> Tuple[float, RiskLevel, str]:
        """Score based on content safety analysis.
        
        Returns risk level and score.
        """
        pass
    
    def get_risk_level(self, text: str) -> RiskLevel:
        """Analyze text for risk level.
        
        Checks for:
        - Financial keywords (bank, transfer, payment, wire)
        - Legal keywords (contract, sue, legal, attorney)
        - Sensitive topics (password, ssn, medical, health)
        - Urgent language (immediately, urgent, asap, emergency)
        """
        pass


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
    r'\bn ? ?d\s*a\b',  # NDA variations
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
    pass


def get_auto_send_eligibility(score: float, risk_level: RiskLevel) -> Tuple[bool, str]:
    """Determine if draft is eligible for auto-send.
    
    Args:
        score: Confidence score
        risk_level: Content risk level
        
    Returns:
        Tuple of (eligible, reason)
    """
    pass
```

---

## Testing Requirements

### Unit Tests (tests/test_confidence.py)

```python
class TestConfidenceScorer:
    """Test cases for ConfidenceScorer."""
    
    def test_file_exists(self):
        """Test confidence.py exists."""
    
    def test_import(self):
        """Test ConfidenceScorer can be imported."""
    
    def test_class_has_required_methods(self):
        """Test all required methods exist:
        - score, should_auto_send, get_risk_level
        """
    
    def test_default_auto_send_threshold(self):
        """Test default threshold is 0.9."""
    
    def test_score_returns_score_result(self):
        """Test score() returns ScoreResult dataclass."""
    
    def test_score_range(self):
        """Test score is always between 0.0 and 1.0."""
    
    def test_auto_send_high_score(self):
        """Test auto-send True for high score + low risk."""
    
    def test_no_auto_send_medium_score(self):
        """Test auto-send False for medium score."""
    
    def test_no_auto_send_high_risk(self):
        """Test auto-send False for any critical risk."""
    
    def test_financial_detection(self):
        """Test financial patterns detected."""
    
    def test_legal_detection(self):
        """Test legal patterns detected."""
    
    def test_sensitive_detection(self):
        """Test sensitive patterns detected."""
    
    def test_urgent_detection(self):
        """Test urgent patterns detected."""
    
    def test_score_result_has_reasoning(self):
        """Test ScoreResult includes reasoning list."""


class TestRiskLevel:
    """Test RiskLevel enum."""
    
    def test_risk_levels_exist(self):
        """Test all risk levels defined: LOW, MEDIUM, HIGH, CRITICAL."""


class TestSafetyPatterns:
    """Test safety pattern detection."""
    
    def test_financial_patterns_defined(self):
        """Test FINANCIAL_PATTERNS list exists."""
    
    def test_legal_patterns_defined(self):
        """Test LEGAL_PATTERNS list exists."""
    
    def test_sensitive_patterns_defined(self):
        """Test SENSITIVE_PATTERNS list exists."""
    
    def test_urgent_patterns_defined(self):
        """Test URGENT_PATTERNS list exists."""
```

---

## Tasks

### 4.2.1 Define Scoring Factors (1.5 hrs)
- [ ] Define factor weights
- [ ] Define ScoreResult dataclass
- [ ] Define RiskLevel enum

### 4.2.2 Implement Scoring Logic (2 hrs)
- [ ] Implement score() method
- [ ] Implement factor scoring methods
- [ ] Combine factors with weights

### 4.2.3 Implement Safety Rules (1.5 hrs)
- [ ] Define pattern lists
- [ ] Implement get_risk_level()
- [ ] Implement auto-send eligibility

### 4.2.4 Write Tests (1 hr)
- [ ] Write unit tests
- [ ] Test edge cases
- [ ] Test safety rules

---

## Scoring Algorithm

```
Total Score = Σ (Factor Score × Factor Weight)

Factors:
├── Sender Familiarity (25%)
│   └── Higher if we've exchanged emails with sender before
├── Response Length (15%)
│   └── Optimal range: 50-300 characters
├── Tone Match (15%)
│   └── Higher if draft tone matches incoming email
├── Context Relevance (20%)
│   └── Higher when RAG finds relevant context
└── Content Safety (25%)
    └── Lower if risk patterns detected

Auto-Send Decision:
├── Score >= 0.9 AND RiskLevel == LOW → AUTO-SEND
├── Score >= 0.5 AND RiskLevel != CRITICAL → QUEUE FOR REVIEW
└── Score < 0.5 OR RiskLevel == CRITICAL → FLAG FOR MANUAL REVIEW
```

---

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| src.rag | ✅ Done | For context relevance scoring |
| src.db | 🔲 3.2 | For sender familiarity |

---

## Configuration

```bash
# Environment variables
AUTO_SEND_THRESHOLD=0.9     # Minimum score for auto-send
CONFIDENCE_MIN_LENGTH=50    # Minimum response length
CONFIDENCE_MAX_LENGTH=500   # Maximum response length
```

---

## Running Tests

```bash
pytest tests/test_confidence.py -v

# Test scoring manually
python -c "
from src.confidence import ConfidenceScorer
scorer = ConfidenceScorer()
result = scorer.score({'from': 'test@example.com'}, {'text': 'Thanks!'})
print(f'Score: {result.score}, Auto-send: {result.auto_send}')
"
```

---

## Definition of Done

1. `src/confidence.py` implements ConfidenceScorer
2. Score range 0.0-1.0
3. Five scoring factors implemented
4. Safety rules prevent auto-send for risky content
5. All unit tests pass (minimum 15 tests)
6. Branch pushed to GitHub
7. PR created (not merged until dependencies ready)

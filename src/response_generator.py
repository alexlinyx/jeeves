"""Response generator using LLM + RAG for email drafting."""
from typing import List, Dict, Optional


class ResponseGenerator:
    """Generate email responses using LLM and RAG context."""
    
    # Tone configurations
    TONES = {
        "casual": {
            "system_prompt": "You are writing a casual, friendly email. Use contractions, be warm, keep it conversational.",
            "max_length": 200,
        },
        "formal": {
            "system_prompt": "You are writing a formal professional email. Use proper grammar, be polite, maintain a professional tone.",
            "max_length": 300,
        },
        "concise": {
            "system_prompt": "You are writing a brief, to-the-point email. Get straight to the answer, minimize fluff.",
            "max_length": 100,
        },
        "match_style": {
            "system_prompt": "You are writing an email that matches the user's personal writing style from their past emails.",
            "max_length": 250,
        },
    }
    
    def __init__(
        self,
        llm=None,
        rag=None,
        default_tone: str = "match_style",
        include_context: bool = True,
        context_top_k: int = 5
    ):
        """Initialize response generator."""
        # Import LLM and RAG if not provided
        if llm is None:
            try:
                from src.llm import LLM
                self.llm = LLM()
            except ImportError:
                self.llm = None
        else:
            self.llm = llm
        
        if rag is None:
            try:
                from src.rag import RAGPipeline
                self.rag = RAGPipeline()
            except ImportError:
                self.rag = None
        else:
            self.rag = rag
        
        self.default_tone = default_tone if default_tone in self.TONES else "match_style"
        self.include_context = include_context
        self.context_top_k = context_top_k
    
    def generate_reply(
        self,
        incoming_email: Dict,
        tone: str = None,
        custom_prompt: str = None
    ) -> str:
        """Generate a reply to an incoming email."""
        tone = tone or self.default_tone
        tone_config = self.TONES.get(tone, self.TONES["match_style"])
        
        # Get context from RAG if enabled
        context = []
        if self.include_context and self.rag and self.llm:
            try:
                context_results = self.rag.search(
                    incoming_email.get('body_text', ''),
                    top_k=self.context_top_k
                )
                context = [r.get('text', '') for r in context_results]
            except:
                pass
        
        # Build prompt
        system_prompt, user_prompt = self._build_prompt(
            incoming_email, context, tone, custom_prompt
        )
        
        # Generate using LLM
        if self.llm:
            return self.llm.generate_with_context(user_prompt, context) if context else self.llm.generate(user_prompt)
        
        # Fallback: return prompt for debugging
        return f"[Generated response would go here based on: {tone} tone]"
    
    def generate_with_context(
        self,
        incoming_email: Dict,
        context_emails: List[Dict]
    ) -> str:
        """Generate response with explicit context emails."""
        context = [e.get('body_text', '') for e in context_emails]
        
        tone = self.default_tone
        system_prompt, user_prompt = self._build_prompt(incoming_email, context, tone, None)
        
        if self.llm:
            return self.llm.generate_with_context(user_prompt, context)
        
        return f"[Generated response with {len(context)} context emails]"
    
    def set_tone(self, tone: str):
        """Set default tone for responses."""
        if tone in self.TONES:
            self.default_tone = tone
    
    def get_available_tones(self) -> List[str]:
        """Get list of available tone modes."""
        return list(self.TONES.keys())
    
    def _build_prompt(
        self,
        incoming_email: Dict,
        context: List[str] = None,
        tone: str = None,
        custom: str = None
    ) -> tuple:
        """Build prompt for LLM."""
        tone = tone or self.default_tone
        tone_config = self.TONES.get(tone, self.TONES["match_style"])
        
        system_prompt = custom or tone_config["system_prompt"]
        
        # Build user prompt with email content
        subject = incoming_email.get('subject', '(No Subject)')
        from_addr = incoming_email.get('from', 'Unknown')
        body = incoming_email.get('body_text', incoming_email.get('snippet', ''))
        
        user_prompt = f"The following email was received:\n\nFrom: {from_addr}\nSubject: {subject}\n\n{body}\n\n"
        
        if context:
            user_prompt += "Relevant context from past emails:\n"
            for i, ctx in enumerate(context[:3], 1):
                user_prompt += f"\n{i}. {ctx[:200]}...\n"
            user_prompt += "\n\n"
        
        user_prompt += "Write a reply to this email."
        
        return system_prompt, user_prompt
    
    def _get_style_from_past_emails(self, from_email: str) -> str:
        """Analyze user's past emails to determine writing style."""
        if not self.rag:
            return "Your typical writing style"
        
        try:
            # Get user's sent emails
            sent_emails = self.rag.get_sent_emails(top_k=10)
            if not sent_emails:
                return "Your typical writing style"
            
            # Extract characteristics (simple heuristic)
            avg_length = sum(len(e.get('text', '')) for e in sent_emails) / len(sent_emails)
            
            if avg_length < 100:
                return "Your writing style tends to be brief and direct"
            elif avg_length < 200:
                return "Your writing style is moderate, conversational"
            else:
                return "Your writing style tends to be detailed and elaborate"
        except:
            return "Your typical writing style"


# Convenience functions

def generate_reply(incoming_email: Dict, tone: str = None, **kwargs) -> str:
    """Quick function to generate a reply."""
    gen = ResponseGenerator(**kwargs)
    return gen.generate_reply(incoming_email, tone)
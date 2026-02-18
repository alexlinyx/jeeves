# AutoResponder Agent — Design Document

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CORE ENGINE (Shared)                     │
├─────────────────────────────────────────────────────────────┤
│  Intent Parser → RAG → State Machine → Response Generator   │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
   ┌─────────┐         ┌──────────┐         ┌──────────┐
   │ OpenClaw│         │  Mobile  │         │ Desktop  │
   │  Skill  │         │   App    │         │   App    │
   └─────────┘         └──────────┘         └──────────┘
```

## Tier 1: OpenClaw Skill (`clawhub install auto-responder`)

### What It Does
- Hooks into your existing channels (Gmail, Telegram, etc.)
- Reads messages, suggests responses
- You approve → it sends
- Learns from your edits

### Integration Points
```yaml
channels:
  - gmail: "auto-respond to newsletters, receipts"
  - telegram: "auto-respond to group mentions"
  - sms: "auto-respond to unknown numbers"

triggers:
  - "message contains 'invoice' → draft payment confirmation"
  - "unknown sender + 'quote' → generate estimate response"
  - "newsletter → summarize + ask if unsubscribe"
```

### Why Start Here
- ✅ Uses your existing OpenClaw setup
- ✅ Immediate utility (you're already in chats/email)
- ✅ No new UI to build
- ✅ Validates core engine with real data

---

## Tier 2: Standalone Mobile App

### Core Value Prop
"Your AI agent that lives on your phone, handles your messages"

### Key Features
1. **Universal Inbox** — Gmail, SMS, WhatsApp, Slack in one place
2. **Smart Suggestions** — "Draft reply?" / "Auto-send?" / "Ignore?"
3. **Voice Mode** — "Tell my mom I'll be late" → generates text
4. **Rules Engine** — "Always auto-respond to DoorDash"
5. **Escalation** — Confident responses auto-send, edge cases notify you

### Platform Strategy
- **iOS/Android**: React Native or Flutter
- **Backend**: Same core engine, deployed as API
- **On-device**: Local LLM for privacy (optional)

---

## Shared Core Engine

### Components

```python
# 1. INTENT PARSER
class IntentParser:
    """Understand what the user wants"""
    
    def parse(self, user_input: str) -> Task:
        # "Dispute the $450 Starbucks charge"
        # → Task(type="dispute", merchant="Starbucks", amount=450)
        pass

# 2. RAG RETRIEVER
class PersonalRAG:
    """Access your data securely"""
    
    def query(self, task: Task) -> Context:
        # Find: account numbers, previous disputes, policies
        pass

# 3. STATE MACHINE
class ConversationState:
    """Track progress through multi-step tasks"""
    
    def next_action(self, context: Context) -> Action:
        # AUTH → GATHER_INFO → DRAFT → REVIEW → SEND
        pass

# 4. RESPONSE GENERATOR
class ResponseGenerator:
    """Draft the actual message"""
    
    def generate(self, state: State, tone: str) -> str:
        # Compose email/SMS based on your style
        pass
```

### Data Model

```yaml
# User Profile
user:
  voice_sample: "/data/voice_cloning/sample.mp3"
  writing_style: "concise, professional"
  auto_approve_rules:
    - "sender: known contact + intent: simple_qa"
    - "category: receipt + action: acknowledge"
  escalate_rules:
    - "amount: > $1000"
    - "sentiment: angry"

# Task State
task:
  id: "uuid"
  goal: "dispute_transaction"
  context:
    merchant: "Starbucks"
    amount: 450
    date: "2026-01-10"
  state: "drafting"  # pending | drafting | review | sent | failed
  messages: [...]
```

---

## ClawHub Skill Structure

```
auto-responder/
├── SKILL.md
├── manifest.yaml
├── scripts/
│   ├── intent_parser.py
│   ├── rag_retriever.py
│   ├── state_machine.py
│   └── response_generator.py
├── references/
│   ├── prompts/
│   │   ├── dispute_email.txt
│   │   ├── customer_support.txt
│   │   └── personal_style.txt
│   └── workflows/
│       ├── dispute_transaction.yaml
│       └── appointment_scheduling.yaml
└── assets/
    └── voice_samples/
        └── default_tone.mp3
```

---

## Development Phases

### Phase 1: OpenClaw Skill (Weeks 1-2)
- [ ] Intent parser for 3 tasks (dispute, schedule, unsubscribe)
- [ ] Gmail integration (read → draft → approve → send)
- [ ] Personal style learning (analyze your sent emails)

### Phase 2: Core Engine Hardening (Weeks 3-4)
- [ ] State machine for multi-step flows
- [ ] RAG integration (Plaid, 1Password, Notion)
- [ ] Recovery/escalation logic

### Phase 3: Mobile App MVP (Weeks 5-8)
- [ ] React Native scaffold
- [ ] Universal inbox (Gmail + SMS initially)
- [ ] Suggestion UI (swipe to approve/send/edit)

### Phase 4: Voice Layer (Weeks 9-10)
- [ ] Integrate Bland/Vapi
- [ ] Voice cloning pipeline
- [ ] Real-time call handling

---

## Open Questions

1. **Privacy**: What runs locally vs cloud? (Financial data = local)
2. **Auth**: How does mobile app auth to your services? (OAuth, device keys)
3. **Revenue**: Skill = free? App = subscription? (Standard SaaS model)
4. **Safety**: Prevent social engineering / fraud (rate limits, confirmation for sensitive actions)

---

## Next Steps

1. **Design doc review** — You validate approach
2. **Single task MVP** — Just "dispute transaction" end-to-end
3. **ClawHub skill scaffold** — Get it installable
4. **Test with your data** — Learn what breaks

Want to proceed with the skill scaffold? Or dive deeper on any component?
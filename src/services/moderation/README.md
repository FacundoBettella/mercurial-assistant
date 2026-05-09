# Moderation Middleware

Content moderation service that evaluates user text for policy violations.

## What It Does

- Analyzes text for explicit risky keywords (hate speech, violence, cyber abuse, self-harm)
- Detects jailbreak attempts using adversarial context patterns
- Returns moderation action: `allow`, `flag`, or `block`
- Logs all events with privacy-first hashing (no raw PII stored)

## How It Works

1. **Keyword Detection**: Scans text for explicit risky terms (SQL injection, phishing, violence, hate speech)
   - If found → BLOCK immediately

2. **Jailbreak Detection**: Checks for adversarial framing + sensitive payload
   - Pattern: disguise phrases ("for educational purposes", "pretend") + sensitive tokens ("credentials", "bypass")
   - If found → FLAG for manual review

3. **Logging**: All events stored in `logs/moderation_events.jsonl` with:
   - Hashed user ID (SHA-256)
   - Hashed input text
   - Detected risks
   - Moderation action
   - Retention tag (clean_30d, flagged_event_90d, incident_365d)

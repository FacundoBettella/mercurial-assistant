# Safety Checklist for Moderation Middleware

## Base Security Compliance

1. **Flagged event traceability**
   Verify every flagged or blocked moderation event is logged with `request_id` and UTC `timestamp`.

2. **Decision and response consistency**
   Verify API status and response body align with moderation decisions (`allow`, `flag`, `block`, `escalate`).

3. **PII protection in telemetry**
   Verify user identifiers and user input are not stored in clear text; only hashed/anonymized values are logged.

4. **Retention policy enforcement**
   Verify all logs include `retention_tag` and retention lifecycle is applied (`clean_30d`, `flagged_event_90d`, `incident_365d`).

5. **Dependency integrity and pinning**
   Verify dependencies are pinned and scanned regularly for known vulnerabilities.

6. **Change management controls**
   Verify moderation policy/model changes require staging validation before production release.

## Operational and Quality Controls

1. **Adversarial prompt testing cadence**
   Run regular tests against updated adversarial prompt datasets and track pass/fail trends.

2. **False positive review loop**
   Review false positives monthly, document patterns, and tune thresholds/rules to reduce user friction.

3. **False negative review loop**
   Review false negatives monthly, prioritize high-severity misses, and patch rules or model prompts.

4. **Upstream/downstream fault safety**
    Validate fail-safe behavior during external service errors, timeouts, and malformed responses.

5. **Injection and evasion hardening**
    Test for prompt injection, obfuscation, and role-play bypass tactics; confirm guardrails still trigger.

6. **Logging integrity assurance**
    Ensure logs are append-only, tamper-evident where possible, and parseable as valid JSON lines.

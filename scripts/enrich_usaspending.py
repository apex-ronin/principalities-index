"""
STUB — USASpending enrichment (roadmap 2B.3, never executed).

Intent: for each entity (after 2B.2 attaches UEI), query the USASpending
API (https://api.usaspending.gov/) to attach:
  - federal award history (count, total, recent awards)
  - top awarding agencies
  - active IDV/contract vehicles

Notes for implementation:
  - No API key required; rate-limit courteously.
  - Recipient lookup by UEI is exact — run AFTER enrich_sam.py.
  - Award history feeds opportunity scoring: an entity that has never
    held a federal award is a different outreach conversation than a
    serial awardee.
  - Write to a NEW enriched file; master JSONL stays untouched.
"""

raise NotImplementedError("Roadmap 2B.3 — not yet executed. See module docstring.")

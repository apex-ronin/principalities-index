"""
STUB — SAM.gov /entities enrichment (roadmap 2B.2, never executed).

Intent: for each entity in data/master_gov_units_2022.jsonl, query the
SAM.gov Entity Management API (https://open.gsa.gov/api/entity-api/) by
legal business name + state to attach:
  - UEI (Unique Entity ID) and CAGE code
  - registration status + expiration
  - NAICS codes
  - points of contact (fills contact_skeleton.caio_email targets)

Notes for implementation:
  - SAM_API_KEY in .env (same key the GovTech Hunter scanner uses;
    rotates ~every 90 days — see STATE for the current expiry).
  - Name matching is fuzzy: Census names ("County Of Autauga") vs SAM
    legal names ("AUTAUGA, COUNTY OF") — normalize before matching, and
    record match confidence in the output.
  - Write enriched records to a NEW file (master is append-only source
    of truth); never mutate data/master_gov_units_2022.jsonl in place.
"""

raise NotImplementedError("Roadmap 2B.2 — not yet executed. See module docstring.")

# principalities-index (public sample)

Core infrastructure for [`primordial-galaxy`](https://github.com/apex-ronin/primordial-galaxy)
— the U.S. government-entity index that feeds its opportunity-scoring and
entity-verification pipeline. Also consumed by `ronin`'s Prism
entity-retrieval agent.

**This is a fixed, real 50-record sample spread across all 52 states and
territories — not synthetic data, and not meant to grow.** It exists so the
full retrieval pipeline can be built and run end to end as a working demo.
The full private dataset is 78,291 U.S. government units (counties, cities,
townships, special districts, school districts) from the 2022 Census of
Governments.

## Data

`data/master_gov_units_2022.jsonl` — one JSON object per line:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Census GIDID (14-char government unit identifier). Unique. |
| `name` | string | Entity name, e.g. `"County Of Autauga"`. |
| `content` | string | Prose description used as the embedding text. |
| `metadata.state_code` | string | Two-letter state, e.g. `"CA"`. |
| `metadata.government_type` | string | Census type code + label, e.g. `"1 - COUNTY"`. |
| `metadata.county` | string | County name. |
| `metadata.population` | int | Documented population. |
| `metadata.fips_state` | int | FIPS state code. |
| `contact_skeleton.web_address` | string\|null | Entity website if documented. |
| `contact_skeleton.caio_email` | string\|null | Contact email — enrichment target, always null in this sample and mostly null in the full dataset. No personal names or phone numbers appear anywhere in this schema. |

## Scripts

- `scripts/build_master_jsonl.py` — provenance: builds the master JSONL
  from the Census PUF workbook.
- `scripts/build_index.py` — embeds records into a local FAISS index.

## Provenance

2022 Census of Governments, Government Units Survey public-use file
(https://www.census.gov/programs-surveys/cog.html).

## License

[PolyForm Shield 1.0.0](LICENSE) — free to use, may not be used to build a
competing product.

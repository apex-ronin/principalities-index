r"""
Build principalities.faiss from data/master_gov_units_2022.jsonl via local
LM Studio embedder.

Standalone equivalent of data-arsenal/pipeline/build_local_indexes.py
(--only princ), reading from THIS repo's data/ directory. Output goes to
G:\AI-Models\indexes (override with INDEX_DIR env var) — index artifacts
stay out of git.

Chunked + checkpointed: ~78K records is an hours-scale CPU job; rerun
resumes from the last complete part.

Requires: faiss-cpu, numpy, requests; LM Studio serving
text-embedding-nomic-embed-text-v1.5 on localhost:1234.
"""

import datetime
import json
import os
import sys
import time
from pathlib import Path

import faiss
import numpy as np
import requests

EMBED_URL = os.environ.get("LOCAL_LLM_BASE_URL", "http://localhost:1234/v1").rstrip("/") + "/embeddings"
EMBED_MODEL = "text-embedding-nomic-embed-text-v1.5"
EMBED_DIMS = 768
DOC_PREFIX = "search_document: "    # nomic v1.5 task prefixes — required
QUERY_PREFIX = "search_query: "
BATCH_SIZE = 64
PART_SIZE = 1024

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "master_gov_units_2022.jsonl"
INDEX_DIR = Path(os.environ.get("INDEX_DIR", r"G:\AI-Models\indexes"))
CKPT_DIR = INDEX_DIR / ".checkpoints" / "principalities"


def load_records() -> list[dict]:
    records = []
    with open(DATA_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            records.append({
                "id": r["id"],
                "name": r.get("name", ""),
                "metadata": r.get("metadata", {}),
                "contact_skeleton": r.get("contact_skeleton", {}),
                "embed_text": r["content"],
            })
    return records


def embed(texts: list[str]) -> np.ndarray:
    resp = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "input": texts}, timeout=300)
    resp.raise_for_status()
    data = sorted(resp.json()["data"], key=lambda d: d["index"])
    return np.array([d["embedding"] for d in data], dtype=np.float32)


def main() -> int:
    records = load_records()
    print(f"Embedding {len(records)} entity records via {EMBED_MODEL}...")
    CKPT_DIR.mkdir(parents=True, exist_ok=True)

    n_parts = (len(records) + PART_SIZE - 1) // PART_SIZE
    parts = []
    t0 = time.time()
    for p in range(n_parts):
        part_file = CKPT_DIR / f"part_{p:05d}.npy"
        lo, hi = p * PART_SIZE, min((p + 1) * PART_SIZE, len(records))
        if part_file.exists():
            arr = np.load(part_file)
            if arr.shape == (hi - lo, EMBED_DIMS):
                parts.append(arr)
                continue
            part_file.unlink()
        chunks = []
        for b in range(lo, hi, BATCH_SIZE):
            chunks.append(embed([DOC_PREFIX + r["embed_text"]
                                 for r in records[b:min(b + BATCH_SIZE, hi)]]))
        arr = np.vstack(chunks)
        np.save(part_file, arr)
        parts.append(arr)
        rate = hi / max(time.time() - t0, 1e-9)
        print(f"  part {p + 1}/{n_parts} — {hi}/{len(records)} "
              f"({rate:.0f} rec/s, ~{(len(records) - hi) / max(rate, 1e-9) / 60:.0f} min left)")

    vectors = np.vstack(parts)
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(EMBED_DIMS)
    index.add(vectors)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_DIR / "principalities.faiss"))
    with open(INDEX_DIR / "principalities_meta.jsonl", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps({k: v for k, v in r.items() if k != "embed_text"},
                               ensure_ascii=False) + "\n")

    manifest_path = INDEX_DIR / "index_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    manifest["principalities"] = {
        "embedder": EMBED_MODEL,
        "embedder_serving": "LM Studio /v1/embeddings (localhost:1234)",
        "dimensions": EMBED_DIMS,
        "metric": "cosine (L2-normalized IndexFlatIP)",
        "doc_prefix": DOC_PREFIX,
        "query_prefix": QUERY_PREFIX,
        "record_count": len(records),
        "source": "jsnnlsn-prog/principalities-index data/master_gov_units_2022.jsonl "
                  "(2022 Census of Governments)",
        "index_file": "principalities.faiss",
        "metadata_sidecar": "principalities_meta.jsonl",
        "built_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"OK: {index.ntotal} vectors -> {INDEX_DIR / 'principalities.faiss'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

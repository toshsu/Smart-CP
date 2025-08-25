# nlp.py
"""
Lightweight NLP utilities for the Smart CP Generator.
This is intentionally rules-first to run offline without large models.
"""

import re
from typing import Dict, List, Tuple

PLACEHOLDER_KEYS = [
    "VESSEL", "OWNER", "CHARTERER", "CP_FORM", "LAYCAN_START", "LAYCAN_END",
    "FREIGHT", "CARGO", "QUANTITY", "LOADING_PORT", "DISCHARGE_PORT", "DEMURRAGE_RATE",
    "NOR", "GOVERNING_LAW", "ARBITRATION_SEAT"
]

def normalize(text: str) -> str:
    return re.sub(r'\r\n?', '\n', text or '').strip()

def parse_key_values(text: str) -> Dict[str, str]:
    """
    Parses simple key: value lines from fixture recap or negotiated inputs.
    Example lines:
      Charterer: ABC Shipping
      Laycan: 2025-09-01 to 2025-09-03
    Returns normalized keys aligned to placeholders when possible.
    """
    text = normalize(text)
    data = {}
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            k_clean = re.sub(r'[^A-Z_ ]+', '', k.upper()).strip()
            v_clean = v.strip()
            # Map common synonyms to placeholders
            mapping = {
                "CHARTERER": "CHARTERER",
                "OWNER": "OWNER",
                "OWNERS": "OWNER",
                "VESSEL": "VESSEL",
                "SHIP": "VESSEL",
                "FORM": "CP_FORM",
                "CP FORM": "CP_FORM",
                "LAYCAN": "LAYCAN",
                "LAYCAN START": "LAYCAN_START",
                "LAYCAN END": "LAYCAN_END",
                "FREIGHT": "FREIGHT",
                "CARGO": "CARGO",
                "QTY": "QUANTITY",
                "QUANTITY": "QUANTITY",
                "LOADING PORT": "LOADING_PORT",
                "LOAD PORT": "LOADING_PORT",
                "DISCHARGE PORT": "DISCHARGE_PORT",
                "DIS PORT": "DISCHARGE_PORT",
                "DEMURRAGE": "DEMURRAGE_RATE",
                "DEMURRAGE RATE": "DEMURRAGE_RATE",
                "NOR": "NOR",
                "LAW": "GOVERNING_LAW",
                "GOVERNING LAW": "GOVERNING_LAW",
                "ARBITRATION": "ARBITRATION_SEAT",
                "ARBITRATION SEAT": "ARBITRATION_SEAT",
            }
            key_std = mapping.get(k_clean, k_clean.replace(" ", "_"))
            if key_std == "LAYCAN" and "to" in v_clean:
                parts = [p.strip() for p in v_clean.split("to", 1)]
                if len(parts) == 2:
                    data["LAYCAN_START"] = parts[0]
                    data["LAYCAN_END"] = parts[1]
                    continue
            data[key_std] = v_clean
    return data

def parse_clauses(text: str) -> List[Tuple[str, str]]:
    """
    Parses numbered clauses like:
      1. This is clause one.
      1.1 Sub clause
    Returns list of (clause_id, text)
    """
    text = normalize(text)
    clauses = []
    for line in text.splitlines():
        m = re.match(r'\s*((?:\d+\.)+\d*|\d+)\s*[\)\.]?\s+(.*\S)', line)
        if m:
            cid, body = m.group(1).rstrip('.'), m.group(2).strip()
            clauses.append((cid, body))
    return clauses

def merge_clauses(base: List[Tuple[str, str]], negotiated: List[Tuple[str, str]]):
    """
    Merge negotiated clauses into base by clause_id, replacing body if conflict.
    Returns merged list and a list of detected conflicts.
    """
    idx = {cid: body for cid, body in base}
    conflicts = []
    for cid, body in negotiated:
        if cid in idx and idx[cid].strip() != body.strip():
            conflicts.append((cid, idx[cid], body))
        idx[cid] = body  # negotiated overrides / inserts
    # Rebuild and renumber sequentially (1, 2, 3...) while preserving original order keys where possible.
    ordered = sorted(idx.items(), key=lambda x: [int(p) for p in x[0].split('.')])
    # Renumber top-level to be 1..n; keep substructure if present
    renumbered = []
    top = 1
    for cid, body in ordered:
        parts = cid.split('.')
        if len(parts) == 1:
            new_id = str(top)
            top += 1
        else:
            # Keep sub numbering after first part
            new_id = f"{parts[0]}.{'.'.join(parts[1:])}"
        renumbered.append((new_id, body))
    return renumbered, conflicts

def detect_gaps(clauses: List[Tuple[str, str]]) -> List[str]:
    """
    Detect missing top-level numbers (e.g., jump from 1 to 3).
    """
    tops = sorted({int(c.split('.')[0]) for c, _ in clauses})
    gaps = []
    if tops:
        expected = list(range(tops[0], tops[-1] + 1))
        missing = [x for x in expected if x not in tops]
        if missing:
            gaps.append(f"Missing top-level clauses: {', '.join(map(str, missing))}")
    return gaps

def fill_placeholders(text: str, kv: Dict[str, str]) -> str:
    def repl(m):
        key = m.group(1).upper()
        return kv.get(key, m.group(0))
    return re.sub(r'\{\{\s*([A-Z_]+)\s*\}\}', repl, text)

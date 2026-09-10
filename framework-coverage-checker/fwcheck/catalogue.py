import re
from pathlib import Path
from .io import file_hash, digest, InputError


def index_framework(path):
    text = Path(path).read_text()
    lines = text.splitlines(keepends=True)
    starts = []
    for i, line in enumerate(lines):
        match = re.match(r"^(?:### (F\d{2})\. |## (P\d+)\s+)(.*)", line)
        if match:
            starts.append((i, match.group(1) or match.group(2), match.group(3).strip()))
    out = {"format": "fwcheck.framework-index.v1", "source_sha256": file_hash(path),
           "families": {}, "proofs": {}, "executable_profiles": [],
           "warning": "Full-text retrieval index. Referenced prose is not an admitted executable contract or execution evidence."}
    for n, (start, id_, title) in enumerate(starts):
        # Stop at the next section heading of the same or higher level. Family
        # blocks stop at the next ###; proof blocks retain their ### continuations.
        level = 3 if id_.startswith("F") else 2
        stop = next((j for j in range(start + 1, len(lines)) if re.match(r"^#{1," + str(level) + r"} ", lines[j])), len(lines))
        body = "".join(lines[start:stop])
        states = re.findall(r"^State:\s*(.*)$", body, re.M)
        primary = re.findall(r"^Primary family:\s*(.*)$", body, re.M)
        entry = {"id": id_, "title": title, "line_start": start + 1, "line_end": stop,
                 "text_sha256": digest(body), "text": body,
                 "proof_refs": sorted(set(re.findall(r"\bP\d+\b", body)), key=lambda x: int(x[1:])),
                 "family_refs": sorted(set(re.findall(r"\bF\d{2}\b", body))),
                 "declared_state": states[0] if states else "NO_MACHINE_QUALIFICATION_ESTABLISHED",
                 "primary_family": primary[0] if primary else None}
        dest = out["families"] if id_.startswith("F") else out["proofs"]
        if id_ in dest: raise InputError(f"Duplicate framework record {id_}")
        dest[id_] = entry
    if not out["families"] or not out["proofs"]:
        raise InputError("No family/proof catalogue found")
    return out

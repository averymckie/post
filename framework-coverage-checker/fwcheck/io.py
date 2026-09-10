import hashlib
import json
from pathlib import Path


class InputError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise InputError(f"Duplicate JSON key: {key}")
        out[key] = value
    return out


def read_json(path):
    def nonfinite(value):
        raise InputError(f"Nonfinite JSON number: {value}")
    return json.loads(Path(path).read_text(), object_pairs_hook=unique_object, parse_constant=nonfinite)


def write_json(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    tmp.replace(p)

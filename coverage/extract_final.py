#!/usr/bin/env python3
"""Extract a subagent's final message verbatim from its JSONL transcript.

The final message is the run of assistant text blocks after the last tool use.
Consecutive blocks are concatenated; a single space is inserted only when the
boundary has no whitespace on either side (a continuation split mid-sentence).

Usage: python3 coverage/extract_final.py <transcript.jsonl> <out.md>
Prints the number of blocks joined, the boundary snippets, and the output size.
"""
import json
import sys


def main():
    src, dst = sys.argv[1], sys.argv[2]
    entries = []
    with open(src, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            msg = obj.get("message") if isinstance(obj.get("message"), dict) else None
            role = (msg or {}).get("role") or obj.get("role")
            if role != "assistant":
                continue
            content = (msg or obj).get("content")
            if isinstance(content, str):
                entries.append(("text", content))
                continue
            has_tool = any(isinstance(c, dict) and c.get("type") == "tool_use" for c in (content or []))
            text = "\n".join(c["text"] for c in (content or []) if isinstance(c, dict) and c.get("type") == "text" and c.get("text"))
            entries.append(("tool" if has_tool else "text", text))
    tail = []
    for kind, text in reversed(entries):
        if kind == "tool":
            break
        if text:
            tail.append(text)
    tail.reverse()
    out = ""
    for i, t in enumerate(tail):
        if i and out and not out[-1].isspace() and not t[:1].isspace():
            print(f"boundary {i}: {out[-40:]!r} + {t[:40]!r} (space inserted)")
            out += " "
        elif i:
            print(f"boundary {i}: {out[-40:]!r} + {t[:40]!r}")
        out += t
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"blocks joined: {len(tail)}; chars: {len(out)}; lines: {out.count(chr(10)) + 1}")


if __name__ == "__main__":
    main()

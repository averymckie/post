"""Mechanically check the hardening assurance recorded at the top of ../Proofs.txt.

Exit status is nonzero on any violation. The four rules are checked as follows.

Rule 1 and 4 (no hand-written implementation, zero LLM reasoning intervention at runtime): a compliant guard
module declares no case functions of its own and types no expected values. Both are counted from the AST, not
from text, so a rename does not evade them: a case function is any function reached through a decorator whose
name is `case`, and a hand-typed expected value is any literal in the second argument position of `g.equal`.

Rule 3 (generated inputs, declarative cases): a compliant module imports hypothesis and reads its cases from a
spec file rather than defining them.

Integrity: every guard module and evidence file embedded in Proofs.txt must round-trip byte-exactly against its
copy in this directory, and every `frozen master lines` pointer must still select the section whose SHA256 the
record names.

Modules named in LEGACY are the ones the assurance already records as violating rules 1 and 4. They are reported
with their counts and do not fail the run; they are frozen history under HG07 and cannot be edited. Anything not
in LEGACY is checked strictly.
"""
from __future__ import annotations
import ast, hashlib, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROOFS = HERE.parent / 'Proofs.txt'
LEGACY = {'handoff_guards_v%d.py' % n for n in range(1, 22)}


def case_functions(tree: ast.AST) -> list[str]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                target = dec.func if isinstance(dec, ast.Call) else dec
                if isinstance(target, ast.Name) and target.id == 'case':
                    out.append(node.name)
    return out


def typed_expectations(tree: ast.AST) -> int:
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'equal':
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                count += 1
    return count


def imports(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name.split('.')[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split('.')[0])
    return names


def check_modules() -> list[str]:
    failures, notes = [], []
    for path in sorted(HERE.glob('handoff_guards_v*.py')) + sorted(HERE.glob('guard_runner*.py')):
        tree = ast.parse(path.read_text())
        cases, typed = case_functions(tree), typed_expectations(tree)
        legacy = path.name in LEGACY
        if legacy:
            notes.append('  legacy %-26s %2d case functions, %3d typed expectations (recorded violation)'
                         % (path.name, len(cases), typed))
            continue
        if cases:
            failures.append('%s defines %d case functions; rule 1 and 4 require them to be spec data'
                            % (path.name, len(cases)))
        if typed:
            failures.append('%s types %d expected values by hand; rule 3 requires an oracle or an invariant'
                            % (path.name, typed))
        if 'hypothesis' not in imports(tree):
            failures.append('%s does not import hypothesis; rule 3 requires generated inputs' % path.name)
    print('legacy modules (rules 1 and 4 already recorded as violated):')
    print('\n'.join(notes) if notes else '  none')
    return failures


def check_embedding() -> list[str]:
    raw = PROOFS.read_bytes()
    failures = []
    for name, fence in re.findall(rb'## (?:Embedded runnable local guard module|Fresh local guard evidence): '
                                  rb'([\w.\-]+)\n.*?```(python|json)\n', raw, re.S):
        pass
    for name in re.findall(r'## Embedded runnable local guard module: ([\w.\-]+)', raw.decode('utf-8')):
        block = raw.split(('## Embedded runnable local guard module: %s' % name).encode())[-1]
        embedded = block.split(b'```python\n', 1)[1].split(b'```\n', 1)[0]
        on_disk = HERE / name
        if not on_disk.exists():
            failures.append('%s is embedded in Proofs.txt but absent from hardening/' % name); continue
        if embedded != on_disk.read_bytes():
            failures.append('%s embedded bytes differ from hardening/%s' % (name, name))
    for name in re.findall(r'## Fresh local guard evidence: ([\w.\-]+)', raw.decode('utf-8')):
        block = raw.split(('## Fresh local guard evidence: %s' % name).encode())[-1]
        embedded = block.split(b'```json\n', 1)[1].split(b'```\n', 1)[0]
        on_disk = HERE / name
        if not on_disk.exists():
            failures.append('%s is embedded in Proofs.txt but absent from hardening/' % name); continue
        if embedded != on_disk.read_bytes():
            failures.append('%s embedded bytes differ from hardening/%s' % (name, name))
    return failures


def check_pointers() -> list[str]:
    text = PROOFS.read_text(encoding='utf-8'); lines = text.split('\n')
    failures = []
    for match in re.finditer(r'^Source location: frozen master lines (\d+)-(\d+); '
                             r'original section SHA256 ([0-9a-f]{64})', text, re.M):
        start, end, sha = int(match.group(1)), int(match.group(2)), match.group(3)
        if hashlib.sha256('\n'.join(lines[start + 6 - 1:end + 6]).encode()).hexdigest() != sha:
            failures.append('frozen pointer %d-%d no longer selects its recorded section' % (start, end))
    return failures


if __name__ == '__main__':
    problems = check_modules() + check_embedding() + check_pointers()
    print('\nembedded artifacts and frozen pointers checked against Proofs.txt')
    if problems:
        print('\nASSURANCE VIOLATIONS (%d):' % len(problems))
        print('\n'.join('  ' + p for p in problems))
        raise SystemExit(1)
    print('assurance holds')

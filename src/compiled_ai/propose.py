"""Step 3, propose: a typed statement per sentence, drafted by a model. Neural.

Two adapters behind one interface:

- ReplayProposer reads recorded fixtures keyed by the sentence digest. Every
  test and every build uses it. It opens no network connection.
- LiveProposer calls the model through the Anthropic SDK with the output
  forced into the Proposal schema. It is used only to create or refresh
  fixtures, and a refreshed fixture is kept only if the checker accepts it.

Model output is not deterministic and the API does not take sampling
controls, so determinism comes from the fixtures, not from the call.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from .model import Proposal, ProposalRecord, Provenance, Sentence


class Proposer(Protocol):
    def propose(self, sentence: Sentence) -> ProposalRecord | None: ...


def fixture_path(fixtures_dir: Path, digest: str) -> Path:
    return fixtures_dir / f"{digest[:16]}.json"


def write_fixture(fixtures_dir: Path, record: ProposalRecord) -> Path:
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    path = fixture_path(fixtures_dir, record.sentence_digest)
    path.write_text(record.model_dump_json(indent=2, exclude_none=True) + "\n", encoding="utf-8")
    return path


def load_fixtures(fixtures_dir: Path) -> dict[str, ProposalRecord]:
    out: dict[str, ProposalRecord] = {}
    if not fixtures_dir.exists():
        return out
    for path in sorted(fixtures_dir.glob("*.json")):
        rec = ProposalRecord.model_validate_json(path.read_text(encoding="utf-8"))
        out[rec.sentence_digest] = rec
    return out


class ReplayProposer:
    def __init__(self, fixtures_dir: Path) -> None:
        self._fixtures = load_fixtures(fixtures_dir)

    def propose(self, sentence: Sentence) -> ProposalRecord | None:
        rec = self._fixtures.get(sentence.digest)
        if rec is not None and rec.sentence_text != sentence.text:
            # The fixture was recorded against different bytes. Digest collisions
            # are not expected; treat as no fixture rather than trust it.
            return None
        return rec


class _ProposalSet(BaseModel):
    """The schema the model must fill. Mirrors Proposal; the API validates shape."""

    model_config = ConfigDict(extra="forbid")
    proposals: list[Proposal]


SYSTEM_PROMPT = """You read one sentence of a regulation and state, in a fixed schema, each statement the sentence makes.

Kinds: definition (a term and what it means), condition (when something applies), step (something an actor shall do), precedence (an ordering or a clock), reserved_decision (a decision the sentence gives to a named role, which a program must route to that role and never make), none (the sentence makes no compilable statement).

Rules you must follow:
- quote: copy the exact characters from the sentence that support the statement. Do not paraphrase, do not fix spelling, do not change punctuation.
- actor: name the actor with the exact term the regulation uses.
- clock: state a deadline only if the sentence states the number and the unit. Copy them as written.
- If the sentence gives a decision to a role (the head of the agency determines, the agency reasonably foresees), emit a reserved_decision statement for it.
- For step, condition and reserved_decision statements, give one short example the sentence allows and one it forbids.
- If the sentence depends on a lead-in from another sentence (such as 'Each agency shall—'), say so in the notes; you cannot quote other sentences.
"""


class LiveProposer:
    """Calls the model. Not exercised in this repository's tests.

    The request shape follows the SDK's documented structured-output call
    (`client.messages.parse(..., output_format=Model)`). A response that stops
    with a refusal is raised as an error rather than recorded.
    """

    def __init__(self, model: str = "claude-opus-5", max_tokens: int = 4000) -> None:
        import anthropic  # the only import of a model client in the compiler; never in the runtime

        self._client = anthropic.Anthropic()
        self._model = model
        self._max_tokens = max_tokens

    def propose(self, sentence: Sentence) -> ProposalRecord | None:
        response = self._client.messages.parse(
            model=self._model,
            max_tokens=self._max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"Sentence {sentence.path or sentence.id}:\n{sentence.text}"}],
            output_format=_ProposalSet,
        )
        if response.stop_reason == "refusal":
            raise RuntimeError(f"model refused to propose for sentence {sentence.id}")
        parsed = response.parsed_output
        if parsed is None:
            return None
        return ProposalRecord(
            sentence_digest=sentence.digest,
            sentence_text=sentence.text,
            proposals=tuple(parsed.proposals),
            provenance=Provenance(producer="model", channel="propose-adapter", model=self._model),
        )


def records_to_proposals(records: dict[str, ProposalRecord]) -> dict[str, tuple[Proposal, ...]]:
    return {d: r.proposals for d, r in sorted(records.items())}


def dump_record(record: ProposalRecord) -> str:
    return json.dumps(record.model_dump(exclude_none=True), indent=2, sort_keys=True)

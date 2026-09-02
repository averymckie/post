"""Step 11, run: a case in, a proof or a list of reasons out. No model.

The runtime is total. For any input it returns exactly one of two values:

- Proof: the rules that applied, each with its sentence, and the decisions
  routed to the people the source names;
- Reasons: the clauses the case tripped, each with its remedy.

There is no third outcome. A record that does not match the schema is a
Reasons with code MALFORMED_RECORD. A rule that raises is a Reasons with code
NOT_EVALUATED. The runtime fails closed: nothing that was not evaluated is
ever reported as a proof.

This module imports only pydantic, the standard library, and the registry.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from pydantic import BaseModel, ValidationError

from .model import Applied, Manifest, Proof, Reason, Reasons, Result, Route
from .registry import Fail, Ok, RouteTo, RuleDef, RuleFn, Skip


class Runtime:
    def __init__(self, manifest: Manifest, rules: Iterable[tuple[RuleDef, RuleFn]], record_type: type[BaseModel]) -> None:
        self.manifest = manifest
        self.record_type = record_type
        specs = {s.id: s for s in manifest.rules}
        self._rules: list[tuple[RuleDef, RuleFn]] = []
        for rdef, fn in sorted(rules, key=lambda t: t[0].id):
            if rdef.id in specs:
                self._rules.append((rdef, fn))
        # Every sealed rule with a function must be present, or the runtime is
        # running a different rule base than the manifest says.
        missing = sorted(s.id for s in manifest.rules if s.function and s.id not in {r.id for r, _ in self._rules})
        if missing:
            raise ValueError(f"manifest names rules the rules module does not provide: {missing}")

    def evaluate(self, raw: Any) -> Result:
        prov = self.manifest.provisional
        digest = self.manifest.digest
        try:
            record = raw if isinstance(raw, self.record_type) else self.record_type.model_validate(raw)
        except ValidationError as e:
            errs = tuple(
                Reason(
                    code="MALFORMED_RECORD",
                    message=f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}",
                    remedy="supply the field with the type the record requires",
                )
                for err in sorted(e.errors(), key=lambda err: (str(err["loc"]), err["msg"]))
            )
            return Reasons(reasons=errs, applied=(), routes=(), provisional=prov, manifest_digest=digest)
        except Exception as e:  # noqa: BLE001 - fail closed on anything
            return Reasons(
                reasons=(Reason(code="NOT_EVALUATED", message=f"record could not be read: {type(e).__name__}", remedy="report this case; it was not evaluated"),),
                applied=(),
                routes=(),
                provisional=prov,
                manifest_digest=digest,
            )

        specs = {s.id: s for s in self.manifest.rules}
        applied: list[Applied] = []
        reasons: list[Reason] = []
        routes: list[Route] = []
        for rdef, fn in self._rules:
            spec = specs[rdef.id]
            outcome: object
            try:
                outcome = cast(object, fn(record))
            except Exception as e:  # noqa: BLE001 - fail closed
                reasons.append(
                    Reason(
                        code="NOT_EVALUATED",
                        message=f"rule {rdef.id} raised {type(e).__name__}",
                        remedy="report this case; the rule did not evaluate",
                        rule_id=rdef.id,
                        sentence_id=spec.sentence_id,
                        path=spec.path,
                        quote=spec.quote,
                    )
                )
                continue
            if isinstance(outcome, Ok):
                applied.append(Applied(rule_id=rdef.id, sentence_id=spec.sentence_id, path=spec.path, quote=spec.quote))
            elif isinstance(outcome, Fail):
                reasons.append(
                    Reason(
                        code=outcome.code,
                        message=outcome.message,
                        remedy=outcome.remedy,
                        rule_id=rdef.id,
                        sentence_id=spec.sentence_id,
                        path=spec.path,
                        quote=spec.quote,
                    )
                )
            elif isinstance(outcome, RouteTo):
                routes.append(
                    Route(
                        decision=outcome.decision,
                        role=outcome.role,
                        rule_id=rdef.id,
                        sentence_id=spec.sentence_id,
                        path=spec.path,
                        quote=spec.quote,
                    )
                )
            elif isinstance(outcome, Skip):
                continue
            else:
                reasons.append(
                    Reason(
                        code="NOT_EVALUATED",
                        message=f"rule {rdef.id} returned an unknown outcome",
                        remedy="report this case; the rule did not evaluate",
                        rule_id=rdef.id,
                        sentence_id=spec.sentence_id,
                        path=spec.path,
                        quote=spec.quote,
                    )
                )
        if reasons:
            return Reasons(reasons=tuple(reasons), applied=tuple(applied), routes=tuple(routes), provisional=prov, manifest_digest=digest)
        return Proof(applied=tuple(applied), routes=tuple(routes), provisional=prov, manifest_digest=digest)

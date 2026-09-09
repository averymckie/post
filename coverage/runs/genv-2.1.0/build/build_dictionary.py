#!/usr/bin/env python3
"""Authoring program for dictionary.json (generation version genv-2.0.0).

Run:  python3 build_dictionary.py --out dictionary.json

No language model runs inside this program.  It expands compact authoring
tables into the full versioned vocabulary, derives the per-ingredient
prerequisite / result / constraint tokens from declared forms and kinds using
the recorded derivation rules, inverts the grounding table so that every
inventory item in assets/01.raw.md, assets/02.raw.md and assets/03.raw.md is
accounted for, and verifies the vocabulary floors before writing.
"""
import argparse, json, os, re, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))

DICTIONARY_VERSION = "2.1.0"
GENERATION_VERSION = "genv-2.1.0"

# --------------------------------------------------------------------------
# Regimes (the seven scales/regimes named in section 1 of the brief)
# --------------------------------------------------------------------------
REGIMES = {
    "R-PHYS": ("Physical and engineered systems",
               "Matter, machines, structures, energy and the engineered artefacts that carry them."),
    "R-BIO":  ("Cellular and organismal biology",
               "Cells, tissues, organisms and the clinical or veterinary settings that act on them."),
    "R-ECO":  ("Ecological and environmental systems",
               "Populations, habitats, catchments, climate and the flows between them."),
    "R-HOME": ("Households and everyday life",
               "Domestic settings, personal routines, care within families and the objects of daily use."),
    "R-ORG":  ("Organizations and markets",
               "Firms, cooperatives, supply chains, employment and exchange between parties."),
    "R-LAW":  ("Law and public administration",
               "Statute, regulation, entitlement, public record and the administration of both."),
    "R-COMP": ("Computation and networks",
               "Software, data, protocols and the networks of independent implementations that run them."),
}
RCODE = {"P": "R-PHYS", "B": "R-BIO", "E": "R-ECO", "H": "R-HOME",
         "O": "R-ORG", "L": "R-LAW", "C": "R-COMP"}

ISIC = {
    "A": "Agriculture, forestry and fishing",
    "B": "Mining and quarrying",
    "C": "Manufacturing",
    "D": "Electricity, gas, steam and air conditioning supply",
    "E": "Water supply; sewerage, waste management and remediation",
    "F": "Construction",
    "G": "Wholesale and retail trade; repair of motor vehicles",
    "H": "Transportation and storage",
    "I": "Accommodation and food service activities",
    "J": "Information and communication",
    "K": "Financial and insurance activities",
    "L": "Real estate activities",
    "M": "Professional, scientific and technical activities",
    "N": "Administrative and support service activities",
    "O": "Public administration and defence; compulsory social security",
    "P": "Education",
    "Q": "Human health and social work activities",
    "R": "Arts, entertainment and recreation",
    "S": "Other service activities",
    "T": "Activities of households as employers; own-use production",
    "U": "Activities of extraterritorial organizations and bodies",
}
FORD = {
    "1": "Natural sciences",
    "2": "Engineering and technology",
    "3": "Medical and health sciences",
    "4": "Agricultural and veterinary sciences",
    "5": "Social sciences",
    "6": "Humanities and the arts",
}

# --------------------------------------------------------------------------
# Situations (controlled tags; every ingredient declares a subset)
# --------------------------------------------------------------------------
SITUATIONS = {
    "S-ROUTINE": "Steady routine operation with known inputs.",
    "S-STARTUP": "A new arrangement with no operating history to learn from.",
    "S-PEAK": "Demand or contention at its seasonal or daily peak.",
    "S-CRISIS": "An emergency in which the normal process cannot be followed.",
    "S-INTERRUPTED": "The work is interrupted and must resume from a partial state.",
    "S-HANDOVER": "Custody, duty or knowledge passes between parties.",
    "S-DISPUTE": "Parties disagree about facts, entitlement or attribution.",
    "S-AUDIT": "An external party can compel evidence about what was done.",
    "S-SCARCITY": "A resource needed by several parts is genuinely short.",
    "S-REMOTE": "Work happens far from support, often without connectivity.",
    "S-MULTILINGUAL": "Several working languages must carry the same obligations.",
    "S-LOW-CAPACITY": "The party who must act lacks tooling, staff or expertise.",
    "S-DIVIDED-AUTHORITY": "Approval sits with one body and delivery with another.",
    "S-IRREVERSIBLE": "At least one step cannot be undone once taken.",
    "S-UNCERTAIN-EVIDENCE": "The evidence is noisy, missing, contested or assumed.",
    "S-VERSION-CHANGE": "A definition, schema or rule changes on a schedule.",
    "S-CONCURRENT": "Several actors act on one object at the same time.",
    "S-MAINTENANCE": "The purpose is keeping something already built working.",
    "S-LEARNING": "Someone must reach competence, not merely receive information.",
    "S-PUBLIC-FACING": "Members of the public encounter the result directly.",
    "S-SAFETY-CRITICAL": "A foreseeable failure injures people or destroys value.",
    "S-PRIVACY-SENSITIVE": "Disclosure could harm an identifiable person.",
    "S-SEASONAL": "A short window governs when the work is possible at all.",
    "S-LONG-HORIZON": "The horizon exceeds the organisation's own memory.",
    "S-COLLABORATIVE": "Independent parties must act together to get any result.",
    "S-SOLO": "One person or household acts alone, without an organisation.",
    "S-TIME-BOUNDED": "A bounded response time decides whether the result is useful at all.",
}
TAG2SIT = {
    "routine": "S-ROUTINE", "startup": "S-STARTUP", "peak": "S-PEAK", "crisis": "S-CRISIS",
    "interrupt": "S-INTERRUPTED", "handover": "S-HANDOVER", "dispute": "S-DISPUTE",
    "audit": "S-AUDIT", "scarce": "S-SCARCITY", "remote": "S-REMOTE",
    "multiling": "S-MULTILINGUAL", "lowcap": "S-LOW-CAPACITY", "divauth": "S-DIVIDED-AUTHORITY",
    "irrev": "S-IRREVERSIBLE", "uncert": "S-UNCERTAIN-EVIDENCE", "version": "S-VERSION-CHANGE",
    "concurrent": "S-CONCURRENT", "maint": "S-MAINTENANCE", "learn": "S-LEARNING",
    "public": "S-PUBLIC-FACING", "safety": "S-SAFETY-CRITICAL", "privacy": "S-PRIVACY-SENSITIVE",
    "seasonal": "S-SEASONAL", "long": "S-LONG-HORIZON", "collab": "S-COLLABORATIVE",
    "solo": "S-SOLO", "realtime": "S-TIME-BOUNDED",
}

# --------------------------------------------------------------------------
# Units and dimensions
# --------------------------------------------------------------------------
UNITS = {
    "U-COUNT":       ("count", 1.0, "items"),
    "U-RECORD":      ("records", 1.0, "records"),
    "U-SLOT":        ("slots", 1.0, "bookable slots"),
    "U-MINUTE":      ("time", 1.0 / 60.0, "minutes"),
    "U-HOUR":        ("time", 1.0, "hours"),
    "U-DAY":         ("time", 24.0, "days"),
    "U-WEEK":        ("time", 168.0, "weeks"),
    "U-PERSON-HOUR": ("labour", 1.0, "person-hours"),
    "U-PERSON-DAY":  ("labour", 8.0, "person-days"),
    "U-GRAM":        ("mass", 0.001, "g"),
    "U-KG":          ("mass", 1.0, "kg"),
    "U-TONNE":       ("mass", 1000.0, "t"),
    "U-ML":          ("volume", 0.001, "mL"),
    "U-LITRE":       ("volume", 1.0, "L"),
    "U-M3":          ("volume", 1000.0, "m3"),
    "U-MM":          ("length", 0.001, "mm"),
    "U-METRE":       ("length", 1.0, "m"),
    "U-KM":          ("length", 1000.0, "km"),
    "U-M2":          ("area", 1.0, "m2"),
    "U-HECTARE":     ("area", 10000.0, "ha"),
    "U-KWH":         ("energy", 1.0, "kWh"),
    "U-MWH":         ("energy", 1000.0, "MWh"),
    "U-KW":          ("power", 1.0, "kW"),
    "U-CU":          ("money", 1.0, "CU (hypothetical currency unit)"),
    "U-KCU":         ("money", 1000.0, "thousand CU"),
    "U-GB":          ("data", 1.0, "GB"),
    "U-TB":          ("data", 1000.0, "TB"),
    "U-PPM":         ("concentration", 1.0, "ppm"),
    "U-PCT":         ("ratio", 1.0, "%"),
    "U-DEGC":        ("temperature", 1.0, "degrees C"),
}

ENTITY_TYPES = {
    "PARTY": "A named party: person, household, team, firm or authority.",
    "SITE": "A located place at which work happens.",
    "ASSET": "A durable engineered or built asset.",
    "DEVICE": "An individually addressable device or instrument.",
    "LOT": "A batch or lot of material moving through a chain.",
    "SPECIMEN": "A collected biological or material specimen.",
    "PARCEL": "A land parcel or spatial unit.",
    "ROUTE": "A route or itinerary.",
    "CONSIGNMENT": "A consignment under transport.",
    "WORKORDER": "An instruction to carry out work.",
    "PERMIT": "A permission, licence or authorisation instrument.",
    "CASEFILE": "A case under administration or care.",
    "COHORT": "A defined group of people or organisms followed together.",
    "COLLECTION": "A held collection of objects or records.",
    "DATASET": "A published or held dataset.",
    "MODEL": "A model, schema or specification artefact.",
    "EVENT": "A scheduled or observed occurrence.",
    "ACCOUNT": "An account against which value is held or moved.",
    "VESSEL": "A vessel, vehicle or mobile unit.",
    "RECORDSET": "A delivered set of records.",
}

# --------------------------------------------------------------------------
# Composition relationship kinds
# --------------------------------------------------------------------------
RELATIONSHIP_KINDS = {
    "RK-INPUT": {
        "label": "provides an input needed by another part",
        "meaning": "The source part produces a quantity of something the target part cannot start without.",
        "transfers": "a quantity of material, data, signal, credential or funds, with a unit",
        "requires": ["source part yields a form the target part needs",
                     "quantity expressed in a unit of the target's expected dimension"],
        "changes": "the target's prerequisite set becomes satisfiable",
        "shares": None,
        "checks": ["REL_FORM_MATCH", "REL_UNIT_DIMENSION", "PRECEDENCE"],
        "directed": True,
    },
    "RK-COORD": {
        "label": "several parts produce a coordinated result",
        "meaning": "Two or more parts jointly deliver an outcome that none of them delivers alone.",
        "transfers": "commitments and status about a joint outcome",
        "requires": ["a named joint outcome", "at least two contributing parts"],
        "changes": "a joint deliverable becomes attributable to the set rather than to one part",
        "shares": "the joint outcome",
        "checks": ["REL_JOINT_OUTCOME", "REL_MIN_TWO"],
        "directed": False,
    },
    "RK-SHARE": {
        "label": "shares a resource or an identity",
        "meaning": "Parts draw on one bounded pool, or refer to one entity by one identifier.",
        "transfers": "nothing; it establishes that two parts are bound to the same pool or identifier",
        "requires": ["a declared resource pool or a declared entity identity"],
        "changes": "consumption by one part reduces what remains for the other, or a rename in one breaks the other",
        "shares": "a capacity pool or an entity identifier",
        "checks": ["REL_SHARED_OBJECT", "CAPACITY", "IDENTITY_CONSISTENT"],
        "directed": False,
    },
    "RK-COND": {
        "label": "conditional decision gate",
        "meaning": "The target part runs only when a stated predicate over the source's result holds.",
        "transfers": "a verdict and the values it was computed from",
        "requires": ["a predicate over a named observable of the source",
                     "a stated action when the predicate fails"],
        "changes": "the target becomes optional rather than unconditional",
        "shares": None,
        "checks": ["REL_PREDICATE", "REL_ELSE_BRANCH", "PRECEDENCE"],
        "directed": True,
    },
    "RK-TIME": {
        "label": "interaction repeated over time",
        "meaning": "Two parts exchange on a stated cadence rather than once.",
        "transfers": "a repeated exchange on a cadence, each instance dated",
        "requires": ["a cadence", "a stated staleness bound for the exchanged item"],
        "changes": "state becomes perishable and must be refreshed",
        "shares": "a clock",
        "checks": ["REL_CADENCE", "REL_STALENESS"],
        "directed": True,
    },
    "RK-FEEDBACK": {
        "label": "feedback, revision and recovery",
        "meaning": "An observation of the target's behaviour revises the source, within a bounded number of cycles.",
        "transfers": "a measured discrepancy and a revision instruction",
        "requires": ["a bounded cycle count", "a criterion for stopping"],
        "changes": "an earlier part is revised after it was thought finished",
        "shares": None,
        "checks": ["REL_CYCLE_BOUND", "REL_STOP_CRITERION"],
        "directed": True,
    },
    "RK-EMBED": {
        "label": "a product becomes a component of another product",
        "meaning": "A complete deliverable is carried inside a larger deliverable and keeps its own acceptance.",
        "transfers": "the whole embedded product together with its own acceptance conditions",
        "requires": ["the embedded part is itself a complete deliverable",
                     "its acceptance conditions are inherited, not replaced"],
        "changes": "the larger product inherits the smaller one's obligations",
        "shares": "the embedded product's identity",
        "checks": ["REL_EMBED_COMPLETE", "REL_INHERIT_ACCEPTANCE", "PRECEDENCE"],
        "directed": True,
    },
    "RK-EMIT": {
        "label": "a generator or configurator produces a further product",
        "meaning": "One part is a generator; the other is a concrete product it must actually emit.",
        "transfers": "a configuration and the emitted artefact",
        "requires": ["the source is a generator form", "the target is a concrete emitted product"],
        "changes": "the emitted product exists and must itself be acceptable",
        "shares": "the generator's rule set",
        "checks": ["REL_GENERATOR_FORM", "REL_EMITTED_CONCRETE", "PRECEDENCE"],
        "directed": True,
    },
    "RK-DELEGATE": {
        "label": "authority or custody passes to another part",
        "meaning": "A scoped, expiring authority (or custody of a thing and its obligations) moves between parts.",
        "transfers": "an authorisation with a scope and an expiry, or custody of an entity",
        "requires": ["a declared authority condition in the case", "a scope and an expiry"],
        "changes": "who may act, and who answers for the action",
        "shares": "the accountability for the delegated act",
        "checks": ["REL_AUTHORITY_PRESENT", "REL_SCOPE_EXPIRY", "PRECEDENCE"],
        "directed": True,
    },
    "RK-CONSTRAIN": {
        "label": "one part sets a limit the other must respect",
        "meaning": "The source publishes an operating envelope; the target must stay inside it and say what it does at the edge.",
        "transfers": "a limit value with a unit and a validity period",
        "requires": ["a limit quantity with a unit", "a stated behaviour at the limit"],
        "changes": "the target's admissible operating range narrows",
        "shares": "the limit value",
        "checks": ["REL_LIMIT_UNIT", "REL_EDGE_BEHAVIOUR"],
        "directed": True,
    },
}

# --------------------------------------------------------------------------
# Requirement, constraint and check templates
# --------------------------------------------------------------------------
CONSTRAINT_TEMPLATES = {
    "CT-CAPACITY_BOUND": {
        "text": "Total draw on shared pool {pool_id} ({resource}) across all parts must not exceed {capacity} {unit}.",
        "check": "CAPACITY", "severity": "hard", "machine_checkable": True},
    "CT-SCHEDULE_FEASIBLE": {
        "text": "Every part must finish by day {deadline_day} given its duration and the precedences declared.",
        "check": "SCHEDULE", "severity": "hard", "machine_checkable": True},
    "CT-IDENTITY_UNIQUE": {
        "text": "Each entity identifier in this case denotes exactly one entity of one declared type.",
        "check": "IDENTITY_CONSISTENT", "severity": "hard", "machine_checkable": True},
    "CT-UNIT_DECLARED": {
        "text": "Every transferred quantity carries a unit drawn from the dictionary unit table.",
        "check": "UNITS_DECLARED", "severity": "hard", "machine_checkable": True},
    "CT-DIMENSION_MATCH": {
        "text": "A quantity transferred between two parts must be expressed in the dimension the receiving part expects.",
        "check": "REL_UNIT_DIMENSION", "severity": "hard", "machine_checkable": True},
    "CT-PREREQ_CLOSED": {
        "text": "Every prerequisite declared by a part is met by a concrete input, an inbound relationship, or a recorded assumption.",
        "check": "PREREQ_CLOSURE", "severity": "hard", "machine_checkable": True},
    "CT-ACYCLIC": {
        "text": "Directed dependency relationships form no cycle; revision cycles are permitted only through RK-FEEDBACK with a bound.",
        "check": "ACYCLIC", "severity": "hard", "machine_checkable": True},
    "CT-DEPTH_BOUND": {
        "text": "Composition depth must not exceed {max_depth}, so recursive construction terminates.",
        "check": "DEPTH", "severity": "hard", "machine_checkable": True},
    "CT-REGIME_ADMISSIBLE": {
        "text": "Every ingredient used must declare the regime of the part that uses it.",
        "check": "REGIME_ADMISSIBLE", "severity": "hard", "machine_checkable": True},
    "CT-SITUATION_ADMISSIBLE": {
        "text": "Every ingredient used must declare at least one of the case's situation tags.",
        "check": "SITUATION_ADMISSIBLE", "severity": "hard", "machine_checkable": True},
    "CT-AUTHORITY_SCOPED": {
        "text": "Any delegated authority carries a named scope and an expiry day within the case window.",
        "check": "REL_SCOPE_EXPIRY", "severity": "hard", "machine_checkable": True},
    "CT-GENERATOR_EMITS": {
        "text": "A generator part must be paired with at least one concrete emitted product by an RK-EMIT relationship.",
        "check": "GENERATOR_EMITS", "severity": "hard", "machine_checkable": True},
    "CT-ACCEPTANCE_COVER": {
        "text": "Every required deliverable carries at least one acceptance condition.",
        "check": "ACCEPTANCE_COVER", "severity": "hard", "machine_checkable": True},
    "CT-VERSION_STAMPED": {
        "text": "Outputs derived from versioned rules carry the version of the rules that produced them.",
        "check": "VERSION_STAMP", "severity": "hard", "machine_checkable": True},
    "CT-HYPOTHETICAL_LABELLED": {
        "text": "Every synthetic fixture is labelled hypothetical and is never presented as an observed record.",
        "check": "FIXTURE_LABELLED", "severity": "hard", "machine_checkable": True},
    "CT-PII_MINIMISED": {
        "text": "Personal identifiers are excluded from any published artefact of this case.",
        "check": "PII_FLAG", "severity": "hard", "machine_checkable": True},
    "CT-REVERSIBILITY_DECLARED": {
        "text": "Each irreversible step names the compensating action available after it, or states that none exists.",
        "check": "REVERSIBILITY", "severity": "hard", "machine_checkable": True},
    "CT-STALENESS_BOUND": {
        "text": "Repeated exchanges declare a staleness bound and the rendering used once it is exceeded.",
        "check": "REL_STALENESS", "severity": "hard", "machine_checkable": True},
    "CT-LANGUAGE_PARITY": {
        "text": "Where several working languages apply, every language version carries the same obligations.",
        "check": "HUMAN", "severity": "soft", "machine_checkable": False},
    "CT-SAFETY_INTERLOCK": {
        "text": "The unsafe action is made impossible by construction rather than discouraged by instruction.",
        "check": "HUMAN", "severity": "soft", "machine_checkable": False},
    "CT-JUDGMENT_RECORDED": {
        "text": "Each judgment call is recorded with the criteria applied and the person who applied them.",
        "check": "HUMAN", "severity": "soft", "machine_checkable": False},
}

REQUIREMENT_TEMPLATES = {
    "RT-INPUT-PRESENT": "{part} shall not begin before {what} is present in the stated form and quantity.",
    "RT-METHOD-CITED": "Every value {part} reports shall cite the method and version that produced it.",
    "RT-UNIT-CARRIED": "Every quantity {part} emits shall carry a unit from the declared unit table.",
    "RT-IDENTITY-STABLE": "{part} shall refer to {entity} by the identifier minted for it and by no other.",
    "RT-CAPACITY-RESPECTED": "{part} shall draw no more than its allocated {amount} {unit} from pool {pool_id}.",
    "RT-DEADLINE": "{part} shall be complete by day {day} of the case window.",
    "RT-AUTHORITY": "{part} shall act only within the authority declared by {authority} and shall stop at its expiry.",
    "RT-REVOCATION": "{part} shall cease using {what} within the stated interval after the authorisation is withdrawn.",
    "RT-DEGRADE": "On loss of {what}, {part} shall enter the declared safe state rather than continue on stale values.",
    "RT-RECORD-DISAGREEMENT": "Where parties disagree, {part} shall retain both accounts rather than resolve them silently.",
    "RT-VERSION-STAMP": "{part} shall stamp its output with the version of the rules applied.",
    "RT-FIXTURE-LABEL": "{part} shall label every synthetic fixture as hypothetical wherever it is displayed.",
    "RT-COMPENSATE": "Where {part} performs an irreversible step, it shall name the compensating action or state that none exists.",
    "RT-RESUME": "{part} shall resume from its partial state without discarding completed work.",
    "RT-STALENESS": "{part} shall render the age of {what} and mark it stale beyond {bound} {unit}.",
    "RT-JOINT-OUTCOME": "{part} shall contribute the named share of the joint outcome {outcome}.",
    "RT-EMIT-CONCRETE": "{part} shall emit at least one concrete product, not only a description of what it could emit.",
    "RT-INHERIT": "{part} shall preserve the acceptance conditions of the product embedded within it.",
    "RT-PRIVACY": "{part} shall not publish an identifier that resolves to a named individual.",
    "RT-LIMIT-RESPECT": "{part} shall stay within the limit of {amount} {unit} published by {source} and shall declare its behaviour at the limit.",
    "RT-JUDGMENT": "{part} shall record who made each judgment call and against which written criterion.",
    "RT-TRACE": "Every figure {part} publishes shall be traceable to the source record it came from.",
}

DERIVATION_RULES = {
    "note": "Prerequisite, result and constraint tokens are derived from each ingredient's axis and declared "
            "form/kind, then extended by any tokens authored on the ingredient itself. The rules below are the "
            "whole derivation; generate.py and checker.py read only the expanded tokens.",
    "input_by_form": {
        "material": {"prereq": ["event:sourcing_or_collection"], "results": ["yields_form:material"],
                     "constraints": ["CT-IDENTITY_UNIQUE", "CT-UNIT_DECLARED"]},
        "artifact": {"prereq": ["event:authoring_or_capture"], "results": ["yields_form:artifact"],
                     "constraints": ["CT-VERSION_STAMPED"]},
        "data": {"prereq": ["event:recording"], "results": ["yields_form:data"],
                 "constraints": ["CT-UNIT_DECLARED", "CT-HYPOTHETICAL_LABELLED"]},
        "signal": {"prereq": ["device:emitting"], "results": ["yields_form:signal"],
                   "constraints": ["CT-STALENESS_BOUND"]},
        "credential": {"prereq": ["authority:issuing"], "results": ["yields_form:credential"],
                       "constraints": ["CT-AUTHORITY_SCOPED"]},
        "knowledge": {"prereq": ["party:expertise"], "results": ["yields_form:knowledge"],
                      "constraints": ["CT-VERSION_STAMPED"]},
        "organism": {"prereq": ["event:sourcing_or_collection", "condition:viability"],
                     "results": ["yields_form:organism"], "constraints": ["CT-IDENTITY_UNIQUE"]},
        "energy": {"prereq": ["supply:connection"], "results": ["yields_form:energy"],
                   "constraints": ["CT-UNIT_DECLARED"]},
        "space": {"prereq": ["access:permission"], "results": ["yields_form:space"],
                  "constraints": ["CT-CAPACITY_BOUND"]},
        "funding": {"prereq": ["authority:approval"], "results": ["yields_form:funding"],
                    "constraints": ["CT-CAPACITY_BOUND", "CT-UNIT_DECLARED"]},
        "person_time": {"prereq": ["party:availability"], "results": ["yields_form:person_time"],
                        "constraints": ["CT-CAPACITY_BOUND"]},
    },
    "product_by_form": {
        "physical_object": {"needs": ["needs_form:material"], "results": ["deliverable:physical_object"],
                            "constraints": ["CT-ACCEPTANCE_COVER", "CT-IDENTITY_UNIQUE"]},
        "procedure": {"needs": ["needs_form:knowledge"], "results": ["deliverable:procedure"],
                      "constraints": ["CT-ACCEPTANCE_COVER", "CT-JUDGMENT_RECORDED"]},
        "service": {"needs": ["needs_form:person_time"], "results": ["deliverable:service"],
                    "constraints": ["CT-ACCEPTANCE_COVER", "CT-CAPACITY_BOUND"]},
        "instrument": {"needs": ["needs_form:material", "needs_form:knowledge"],
                       "results": ["deliverable:instrument"],
                       "constraints": ["CT-ACCEPTANCE_COVER", "CT-UNIT_DECLARED"]},
        "creative_work": {"needs": ["needs_form:knowledge"], "results": ["deliverable:creative_work"],
                          "constraints": ["CT-ACCEPTANCE_COVER"]},
        "explanation": {"needs": ["needs_form:data"], "results": ["deliverable:explanation"],
                        "constraints": ["CT-ACCEPTANCE_COVER"]},
        "interactive_tool": {"needs": ["needs_form:data"], "results": ["deliverable:interactive_tool"],
                             "constraints": ["CT-ACCEPTANCE_COVER", "CT-VERSION_STAMPED"]},
        "coordinated_system": {"needs": ["needs_form:data", "needs_form:person_time"],
                               "results": ["deliverable:coordinated_system"],
                               "constraints": ["CT-ACCEPTANCE_COVER", "CT-IDENTITY_UNIQUE"]},
        "generator": {"needs": ["needs_form:knowledge"], "results": ["deliverable:generator", "emits_products"],
                      "constraints": ["CT-ACCEPTANCE_COVER", "CT-GENERATOR_EMITS"]},
        "dataset": {"needs": ["needs_form:data"], "results": ["deliverable:dataset"],
                    "constraints": ["CT-ACCEPTANCE_COVER", "CT-HYPOTHETICAL_LABELLED"]},
        "document": {"needs": ["needs_form:knowledge"], "results": ["deliverable:document"],
                     "constraints": ["CT-ACCEPTANCE_COVER", "CT-VERSION_STAMPED"]},
        "credential": {"needs": ["needs_form:credential"], "results": ["deliverable:credential"],
                       "constraints": ["CT-ACCEPTANCE_COVER", "CT-AUTHORITY_SCOPED"]},
        "training": {"needs": ["needs_form:person_time", "needs_form:knowledge"],
                     "results": ["deliverable:training"], "constraints": ["CT-ACCEPTANCE_COVER"]},
        "experience": {"needs": ["needs_form:space", "needs_form:person_time"],
                       "results": ["deliverable:experience"], "constraints": ["CT-ACCEPTANCE_COVER"]},
    },
    "condition_by_kind": {
        "resource": {"results": ["provides_pool"], "constraints": ["CT-CAPACITY_BOUND"]},
        "authority": {"results": ["provides_authority"], "constraints": ["CT-AUTHORITY_SCOPED"]},
        "environment": {"results": ["shapes_environment"], "constraints": []},
    },
    "dynamic_by_kind": {
        "time": {"constraints": ["CT-SCHEDULE_FEASIBLE"]},
        "uncertainty": {"constraints": ["CT-JUDGMENT_RECORDED"]},
        "state": {"constraints": ["CT-PREREQ_CLOSED"]},
        "change": {"constraints": ["CT-VERSION_STAMPED"]},
    },
    "acceptance_by_mode": {
        "machine": {"constraints": []},
        "mixed": {"constraints": ["CT-JUDGMENT_RECORDED"]},
        "human": {"constraints": ["CT-JUDGMENT_RECORDED"]},
    },
}

COMPATIBILITY_RULES = {
    "note": "These rules are what generate.py samples from and what checker.py re-derives. "
            "An ingredient's `domains` list records the domains in which it is characteristic; "
            "its `regimes` and `situations` lists record where it is admissible at all.",
    "regime_gated_axes": ["beneficiary", "need", "input", "product", "activity",
                          "condition", "dynamic", "acceptance", "scale"],
    "regime_rule": "The regime of the part using an ingredient must appear in that ingredient's `regimes`.",
    "situation_gated_axes": ["beneficiary", "need", "input", "product", "activity",
                             "condition", "dynamic", "acceptance", "scale"],
    "situation_rule": "At least one of the case's situation tags must appear in the ingredient's `situations`.",
    "domain_gated_axes": ["need", "product"],
    "domain_rule": "The case's primary_domain must appear in the `domains` of the root need and of every "
                   "product ingredient used as a component, because those two axes are what the domain "
                   "classification actually classifies.",
    "domain_preferred_axes": ["beneficiary", "input", "activity", "condition", "dynamic", "acceptance", "scale"],
    "domain_preference_rule": "On these axes the primary domain is a sampling preference only; a case records "
                              "`domain_matched_axes` so that the mix can be measured rather than assumed.",
    "beneficiary_rule": "The beneficiary's `scale_band` must appear in the need's `beneficiary_bands`.",
    "activity_rule": "Every prerequisite token of the activity of the form needs_form:X must be met by a "
                     "concrete input of form X, by an inbound relationship transferring form X, or by a "
                     "recorded assumption; every needs_capacity:K token must be met by a declared resource "
                     "pool of kind K carrying an allocation for that part.",
    "acceptance_rule": "Every required deliverable carries at least one acceptance condition whose ingredient "
                       "admits the case regime and situation.",
}

GENERATION_BOUNDS = {
    "max_depth": 3,
    "min_components": 2,
    "max_components": 6,
    "min_relationships": 1,
    "max_relationships": 8,
    "max_resource_pools": 4,
    "max_entities": 6,
    "max_backtracks_per_case": 12,
    "case_window_days": {"min": 21, "max": 400},
    "epoch": "day 0 of the case window; all dates are relative day numbers, never wall-clock",
    "max_feedback_cycles": 4,
    "max_parameter_variants_per_full_key": 1,
}

# --------------------------------------------------------------------------
# Ingredient authoring tables
#   row = (id, label, meaning, regimes, domains, tags, extra)
#   regimes: space-separated of P B E H O L C, or "*" for all seven
#   domains: space-separated ISIC letters / FORD digits, or "*" for all 27
#   tags:    space-separated situation tags (see TAG2SIT)
# --------------------------------------------------------------------------

BENEFICIARY = [
 ("BEN-SMALLHOLDER","smallholder farmers and growers","People farming small holdings who bear the cost of a wrong input decision themselves.","E O H","A 4","routine seasonal lowcap solo",{"scale_band":"household","capabilities":["field observation","local knowledge"],"vulnerabilities":["thin margins","no analytic staff"]}),
 ("BEN-AGRONOMIST","agronomists and farm advisors","Advisors who translate measurements into a recommendation a grower will act on.","E O","A 4","routine seasonal uncert collab",{"scale_band":"team","capabilities":["interpretation","sampling design"],"vulnerabilities":["liability for advice"]}),
 ("BEN-FISHER","small-scale fishers and cooperatives","Fishing households and their cooperatives working under a shared catch limit.","E O","A 1 4","scarce dispute seasonal collab",{"scale_band":"community","capabilities":["local stock knowledge"],"vulnerabilities":["quota disputes","weather"]}),
 ("BEN-VET","veterinarians and livestock keepers","Animal health workers and the keepers who call them.","B E","A 3 4","crisis routine remote",{"scale_band":"team","capabilities":["clinical examination","treatment"],"vulnerabilities":["distance","record gaps"]}),
 ("BEN-LAB-TECH","laboratory technicians","Staff running analytic methods to a throughput target.","P B","M 1 3 4","routine scarce peak audit",{"scale_band":"team","capabilities":["method execution","calibration"],"vulnerabilities":["turnaround pressure"]}),
 ("BEN-MINE-ENG","mine geologists and engineers","Engineers modelling an orebody and the ground around it.","P E","B 2 1","uncert dispute safety long",{"scale_band":"organization","capabilities":["modelling","survey"],"vulnerabilities":["model disagreement"]}),
 ("BEN-DOWNSTREAM-COMM","communities downstream of an industrial facility","People who bear the consequence of a failure they did not choose.","E H L","B E O","safety irrev public dispute",{"scale_band":"community","capabilities":["local witness"],"vulnerabilities":["no technical access","irreversible harm"]}),
 ("BEN-FACTORY-OP","machine operators and shop-floor supervisors","People running production equipment shift by shift.","P O","C 2","routine handover maint peak",{"scale_band":"team","capabilities":["machine setting","first-line diagnosis"],"vulnerabilities":["shift handover loss"]}),
 ("BEN-MAINT-TECH","maintenance technicians","People who keep installed equipment working, often at night and alone.","P","C D E F 2","maint remote solo safety",{"scale_band":"team","capabilities":["fault diagnosis","repair"],"vulnerabilities":["missing history","parts availability"]}),
 ("BEN-HW-ENGINEER","hardware and silicon engineers","Engineers whose mistakes are fixed in silicon and cannot be patched.","P C","C J 2","irrev safety version audit",{"scale_band":"team","capabilities":["specification","verification"],"vulnerabilities":["one-way lifecycle steps"]}),
 ("BEN-ROBOTICIST","robotics integrators","People integrating machines that move in shared space with humans.","P C","C H 2","safety concurrent startup",{"scale_band":"team","capabilities":["integration","simulation"],"vulnerabilities":["unmodelled human behaviour"]}),
 ("BEN-GRID-OP","distribution grid operators","Operators balancing an electrical network they do not fully observe.","P C","D 2","realtime peak safety concurrent",{"scale_band":"organization","capabilities":["switching","forecasting"],"vulnerabilities":["edge devices they do not control"]}),
 ("BEN-HOUSEHOLD-ENERGY","householders with on-site generation or an electric vehicle","Households whose appliances now negotiate with a grid on their behalf.","H P","D T","solo routine public uncert",{"scale_band":"household","capabilities":["choosing settings"],"vulnerabilities":["opaque controls","bill surprises"]}),
 ("BEN-WATER-UTILITY","water and sanitation utility staff","Staff responsible for water that people drink without checking it.","P E","E 2","safety routine crisis audit",{"scale_band":"organization","capabilities":["network operation","sampling"],"vulnerabilities":["invisible network state"]}),
 ("BEN-CATCHMENT-RESIDENT","residents of a flood-prone or contaminated catchment","People living with a risk produced upstream of them.","E H","E F O","crisis public uncert dispute",{"scale_band":"community","capabilities":["local observation"],"vulnerabilities":["no control over the source"]}),
 ("BEN-SITE-WORKER","construction site workers","People working at height, in trenches and around moving plant.","P","F 2","safety concurrent handover routine",{"scale_band":"team","capabilities":["trade skill"],"vulnerabilities":["duty attaches per person per surface"]}),
 ("BEN-BUILDING-OPERATOR","building operations managers","People who inherit a building and must run it on what the designers left them.","P O","F L 2","maint handover long routine",{"scale_band":"organization","capabilities":["operation","tuning"],"vulnerabilities":["as-built drift"]}),
 ("BEN-ARCHITECT","designers and architects","People making commitments at design stage that others must live with.","P O","F M 2 6","long collab version dispute",{"scale_band":"team","capabilities":["design","specification"],"vulnerabilities":["decisions taken before evidence exists"]}),
 ("BEN-RETAILER","small retailers and market traders","Traders handling goods, prices and receipts with no back office.","O H","G I","routine lowcap peak solo",{"scale_band":"organization","capabilities":["direct customer contact"],"vulnerabilities":["no systems staff"]}),
 ("BEN-SUPPLY-AUDITOR","supply chain auditors","People asked to confirm a claim about something they cannot see.","O L","G H 5","audit uncert dispute remote",{"scale_band":"organization","capabilities":["sampling","document review"],"vulnerabilities":["reliance on the audited party's records"]}),
 ("BEN-TRANSIT-RIDER","public transport riders","People planning a journey across operators who do not coordinate.","O C H","H","public routine peak lowcap",{"scale_band":"individual","capabilities":["choosing a route"],"vulnerabilities":["stale information"]}),
 ("BEN-FLEET-DISPATCH","fleet dispatchers","People assigning vehicles and drivers to work against the clock.","O P","H G","peak concurrent scarce routine",{"scale_band":"team","capabilities":["allocation","rerouting"],"vulnerabilities":["incomplete availability data"]}),
 ("BEN-PORT-CLERK","port and freight documentation clerks","People whose paperwork releases or holds physical cargo.","O L","H","handover irrev routine audit",{"scale_band":"team","capabilities":["document handling"],"vulnerabilities":["one wrong endorsement holds a container"]}),
 ("BEN-KITCHEN-OP","small kitchen and food-service operators","Operators who must apply a food-safety discipline built for larger organisations.","H O B","I","safety lowcap routine peak",{"scale_band":"organization","capabilities":["cooking","direct control of process"],"vulnerabilities":["no technical staff"]}),
 ("BEN-FOOD-INSPECTOR","food safety inspectors","Officers sampling premises against written criteria under time pressure.","L B","I O","audit routine dispute peak",{"scale_band":"team","capabilities":["inspection","enforcement"],"vulnerabilities":["inconsistent scoring"]}),
 ("BEN-SOFTWARE-TEAM","software engineering teams","People maintaining a running service other people depend on.","C","J 2","maint version concurrent routine",{"scale_band":"team","capabilities":["build and deploy"],"vulnerabilities":["silent failure modes"]}),
 ("BEN-DISABLED-USER","people using assistive technology","People for whom an interface is either usable or a closed door.","C H","J P S","public lowcap routine learn",{"scale_band":"individual","capabilities":["expert use of their own tools"],"vulnerabilities":["untested interfaces"]}),
 ("BEN-JOURNALIST","journalists and fact-checkers","People deciding whether a piece of media can be published as true.","C O","J R 5 6","uncert crisis public dispute",{"scale_band":"team","capabilities":["verification","sourcing"],"vulnerabilities":["fabricated provenance"]}),
 ("BEN-TRANSLATOR","translators and localisation teams","People carrying obligations, not only words, across languages.","O C","J N 6","multiling routine version collab",{"scale_band":"team","capabilities":["language","domain reading"],"vulnerabilities":["source drift after translation"]}),
 ("BEN-BANK-CUSTOMER","retail banking and payments customers","People whose money is moved by systems they cannot inspect.","O C","K","public irrev privacy routine",{"scale_band":"individual","capabilities":["consent and refusal"],"vulnerabilities":["irreversible transfers"]}),
 ("BEN-CLAIMS-ADJUSTER","insurance claims and underwriting staff","People deciding payouts on evidence assembled by others.","O L","K","uncert audit dispute routine",{"scale_band":"organization","capabilities":["assessment"],"vulnerabilities":["inconsistent data across insurers"]}),
 ("BEN-TENANT","tenants and prospective homebuyers","People committing to a home on information held by the other side.","H O L","L","public uncert dispute lowcap",{"scale_band":"household","capabilities":["viewing","questions"],"vulnerabilities":["asymmetric information"]}),
 ("BEN-LAND-CLAIMANT","customary and informal land claimants","People whose relationship to land is real but not written as ownership.","L H E","L A O","dispute divauth long lowcap",{"scale_band":"community","capabilities":["witness","occupation"],"vulnerabilities":["records that cannot express their claim"]}),
 ("BEN-SURVEY-ENUMERATOR","field survey enumerators","People collecting data door to door, often without connectivity.","O L H","M N 5","remote routine lowcap interrupt",{"scale_band":"team","capabilities":["interviewing","local access"],"vulnerabilities":["device and power failure"]}),
 ("BEN-STATISTICIAN","official statisticians","People publishing figures that other people will act on for years.","L O C","M O 5","audit long version uncert",{"scale_band":"organization","capabilities":["estimation","dissemination"],"vulnerabilities":["comparability breaks"]}),
 ("BEN-SOCIAL-RESEARCHER","social researchers","People whose claims depend on decisions made before data collection.","O L","M 5","uncert audit long collab",{"scale_band":"team","capabilities":["design","analysis"],"vulnerabilities":["undisclosed analytic choices"]}),
 ("BEN-RECRUITER","recruiters and hiring managers","People matching people to work under an obligation not to discriminate.","O L","N","routine privacy audit peak",{"scale_band":"organization","capabilities":["screening","interviewing"],"vulnerabilities":["opaque taxonomies"]}),
 ("BEN-JOBSEEKER","jobseekers and career changers","People trying to see what would actually close the gap to a job.","O H","N P","learn lowcap public routine",{"scale_band":"individual","capabilities":["effort","study"],"vulnerabilities":["unreadable requirements"]}),
 ("BEN-PROCUREMENT-OFFICER","public procurement officers","People spending public money against published criteria.","L O","O 5","audit divauth routine dispute",{"scale_band":"organization","capabilities":["tendering","contract management"],"vulnerabilities":["challenge and delay"]}),
 ("BEN-CITIZEN-PETITIONER","residents dealing with a public authority","People navigating a process designed by the body they are asking.","L H","O S","public lowcap dispute routine",{"scale_band":"individual","capabilities":["persistence"],"vulnerabilities":["no map of the process"]}),
 ("BEN-TEACHER","teachers and instructional designers","People turning a syllabus into something a class can actually do.","O H","P 5 6","learn routine lowcap collab",{"scale_band":"team","capabilities":["pedagogy","assessment"],"vulnerabilities":["mixed prior attainment"]}),
 ("BEN-LEARNER","learners and students","People whose progress depends on being able to resume after interruption.","H O","P","learn interrupt lowcap public",{"scale_band":"individual","capabilities":["study","practice"],"vulnerabilities":["interrupted schooling"]}),
 ("BEN-CLINICIAN","front-line clinicians","People making care decisions with incomplete records and no spare time.","B O","Q 3","crisis peak handover safety",{"scale_band":"team","capabilities":["examination","judgment"],"vulnerabilities":["record fragmentation"]}),
 ("BEN-PATIENT","patients and their carers","People who must carry their own history between services.","B H","Q 3","handover privacy lowcap interrupt",{"scale_band":"individual","capabilities":["consent","self-report"],"vulnerabilities":["records they cannot read"]}),
 ("BEN-CAREGIVER","unpaid family caregivers","Relatives providing care with no training and no relief.","H B","Q T","solo interrupt lowcap long",{"scale_band":"household","capabilities":["daily presence"],"vulnerabilities":["exhaustion","no formal standing"]}),
 ("BEN-PUBLIC-HEALTH","public health surveillance teams","People trying to see an outbreak before it is obvious.","B E L","Q 3","crisis uncert privacy peak",{"scale_band":"organization","capabilities":["surveillance","investigation"],"vulnerabilities":["signal buried in noise"]}),
 ("BEN-TRIALIST","clinical trial teams","People bound to an analysis plan written before the data existed.","B O","Q 3","audit irrev long handover",{"scale_band":"organization","capabilities":["protocol execution"],"vulnerabilities":["amendment drift"]}),
 ("BEN-CURATOR","museum and archive curators","People holding objects for people not yet born.","H O","R 6","long version public dispute",{"scale_band":"organization","capabilities":["description","conservation"],"vulnerabilities":["software that outlives nothing"]}),
 ("BEN-ARCHIVIST","archivists and records managers","People keeping the context of records, not only the records.","L O","R M 6","long audit handover version",{"scale_band":"organization","capabilities":["appraisal","arrangement"],"vulnerabilities":["custody breaks"]}),
 ("BEN-MUSICIAN","performing musicians and composers","People turning notation into a performance under rehearsal constraints.","H O","R 6","collab learn scarce public",{"scale_band":"team","capabilities":["performance","interpretation"],"vulnerabilities":["editorial ambiguity"]}),
 ("BEN-ATHLETE-CLUB","community sports clubs and participants","Volunteer-run clubs organising activity for people who just want to take part.","H O","R S","collab lowcap seasonal public",{"scale_band":"community","capabilities":["organising","coaching"],"vulnerabilities":["volunteer turnover"]}),
 ("BEN-REPAIR-VOLUNTEER","community repair volunteers","People fixing other people's things for free, and recording what happened.","H P O","S C","collab lowcap routine public",{"scale_band":"community","capabilities":["diagnosis","teaching by doing"],"vulnerabilities":["no parts","no data discipline"]}),
 ("BEN-GENEALOGIST","family historians","People reconstructing kinship from records that disagree.","H O","S R 6","uncert dispute long solo",{"scale_band":"individual","capabilities":["record search"],"vulnerabilities":["conflicting sources"]}),
 ("BEN-DOMESTIC-WORKER","domestic workers","People employed inside a private home, often without a written agreement.","H O L","T","solo lowcap dispute privacy",{"scale_band":"individual","capabilities":["skill","presence"],"vulnerabilities":["no HR function","stand-by hours disputed"]}),
 ("BEN-HOUSEHOLD-EMPLOYER","household employers","Families who become employers without becoming an organisation.","H L","T","solo lowcap routine audit",{"scale_band":"household","capabilities":["direct instruction"],"vulnerabilities":["obligations discovered late"]}),
 ("BEN-HUMANITARIAN","humanitarian field responders","People delivering assistance where systems and records have failed.","L O H","U 5","crisis remote lowcap collab",{"scale_band":"organization","capabilities":["rapid delivery"],"vulnerabilities":["no infrastructure","protection risks"]}),
 ("BEN-DONOR-PUBLIC","donors and the funding public","People who paid and want to know what happened.","O L","U K 5","public audit long uncert",{"scale_band":"community","capabilities":["withholding funds"],"vulnerabilities":["unreadable reporting"]}),
 ("BEN-ECOLOGIST","field ecologists and biodiversity recorders","People counting things that move, in places that change.","E B","M 1 4","seasonal remote uncert collab",{"scale_band":"team","capabilities":["identification","survey"],"vulnerabilities":["detection bias"]}),
 ("BEN-ASTRONOMER","observational astronomers","People sharing an instrument that cannot be duplicated.","P C","M 1","scarce collab long routine",{"scale_band":"organization","capabilities":["observation","reduction"],"vulnerabilities":["oversubscribed time"]}),
 ("BEN-CHEMIST","synthetic and analytical chemists","People whose results depend on an identifier generated by software.","P B","M C 1 2","version uncert routine audit",{"scale_band":"team","capabilities":["synthesis","characterisation"],"vulnerabilities":["silent identifier changes"]}),
 ("BEN-GENERALIST-ORG","small organisations without specialist staff","Small bodies that must satisfy requirements written for large ones.","O L H","*","lowcap routine audit collab",{"scale_band":"organization","capabilities":["direct decision-making"],"vulnerabilities":["no compliance function"]}),
 ("BEN-FRONTLINE-STAFF","front-line staff in any service","People applying a rule to a person in front of them, now.","O L H B","*","peak routine handover lowcap",{"scale_band":"team","capabilities":["direct contact","local judgment"],"vulnerabilities":["rules written elsewhere"]}),
 ("BEN-COMMUNITY-GROUP","voluntary community groups","Groups with commitment and no budget line.","H O","*","collab lowcap public seasonal",{"scale_band":"community","capabilities":["local trust","volunteer effort"],"vulnerabilities":["turnover","no funding"]}),
 ("BEN-REGULATED-FIRM","firms subject to an external requirement","Organisations that must prove, not merely assert, that they complied.","O L C P","*","audit version routine divauth",{"scale_band":"organization","capabilities":["record keeping"],"vulnerabilities":["moving requirements"]}),
 ("BEN-INDIVIDUAL-USER","an individual using a thing on their own","One person, unaided, at the moment of use.","H C P","*","solo lowcap public learn",{"scale_band":"individual","capabilities":["attention"],"vulnerabilities":["no support to call"]}),
]

NEED = [
 ("NED-IDENTIFY-THING","hold the identity of a thing across parties","Several parties must agree which thing they are talking about without one of them owning the answer.","*","*","collab dispute version routine",{"purpose_class":"coordination","beneficiary_bands":["organization","community","team"]}),
 ("NED-RECONCILE-CLAIMS","reconcile conflicting records of the same object","Two records that should agree do not, and someone must decide what to do about it.","*","*","dispute audit uncert routine",{"purpose_class":"accountability","beneficiary_bands":["team","organization","community"]}),
 ("NED-MEASURE-CONDITION","measure a condition that cannot be observed directly","The thing that matters is hidden, so it must be inferred from something measurable.","P B E C","*","uncert routine safety maint",{"purpose_class":"discovery","beneficiary_bands":["team","organization"]}),
 ("NED-EXPLAIN-DECISION","explain how a decision was reached to the people it affects","A decision is defensible only if the people bound by it can follow the reasoning.","O L H C","*","public dispute audit lowcap",{"purpose_class":"explanation","beneficiary_bands":["individual","community","household"]}),
 ("NED-TEACH-PROCEDURE","teach a procedure to someone who will perform it unsupervised","Instruction has to survive the absence of the instructor.","*","*","learn lowcap remote safety",{"purpose_class":"learning","beneficiary_bands":["individual","team","household"]}),
 ("NED-EXPRESS-EXPERIENCE","give an experience a form other people can encounter","Something felt or witnessed needs a made form to reach anyone else.","H O","R P S 6","public collab learn solo",{"purpose_class":"expression","beneficiary_bands":["individual","community","team"]}),
 ("NED-CARE-CONTINUITY","keep care continuous across handovers and interruptions","Care fails at the seams more often than in the middle.","B H O","Q T P 3","handover interrupt crisis privacy",{"purpose_class":"care","beneficiary_bands":["individual","household","team"]}),
 ("NED-COORDINATE-PARTIES","coordinate independent parties toward one outcome","No party can be instructed, so the arrangement must make cooperation the easy path.","*","*","collab divauth concurrent routine",{"purpose_class":"coordination","beneficiary_bands":["organization","community","team"]}),
 ("NED-PRODUCE-TO-SPEC","produce a physical item to a stated specification","Something must be made, and made to fit.","P","C F A B 2","routine scarce peak maint",{"purpose_class":"production","beneficiary_bands":["team","organization","individual"]}),
 ("NED-KEEP-WORKING","keep an installed thing working over its whole life","The thing exists; the problem is the next fifteen years.","P C E","*","maint long handover routine",{"purpose_class":"maintenance","beneficiary_bands":["team","organization","household"]}),
 ("NED-RUN-HOUSEHOLD","carry out a household task safely without professional support","A domestic task with a real failure mode and no professional in the room.","H B P","T I S","solo lowcap safety routine",{"purpose_class":"everyday_life","beneficiary_bands":["household","individual"]}),
 ("NED-PREVENT-HARM","prevent a foreseeable and serious harm","The harm is known, the mechanism is known, and it still happens.","*","*","safety irrev audit crisis",{"purpose_class":"safety","beneficiary_bands":["community","organization","team"]}),
 ("NED-ACCOUNT-FOR-MONEY","account for how money was spent and what it achieved","Spending is recorded; effect is not, and the two are rarely joined.","O L","*","audit public long uncert",{"purpose_class":"accountability","beneficiary_bands":["organization","community"]}),
 ("NED-REACH-SERVICE","reach a service one is entitled to","The entitlement exists; the path to it does not.","L H O B","*","public lowcap crisis privacy",{"purpose_class":"access","beneficiary_bands":["individual","household","community"]}),
 ("NED-DECIDE-UNDER-UNCERTAINTY","decide with incomplete and contested evidence","The decision cannot wait for better evidence, and pretending otherwise is the failure.","*","*","uncert crisis dispute audit",{"purpose_class":"decision","beneficiary_bands":["organization","team","community"]}),
 ("NED-PRESERVE-RECORD","keep a record usable after its software and its authors are gone","Preservation is a promise about a time when nobody is left to fix it.","C O L H","*","long version handover audit",{"purpose_class":"preservation","beneficiary_bands":["organization","community"]}),
 ("NED-RECOVER-AFTER-FAILURE","recover after a partial failure","Something stopped part-way and the state is neither before nor after.","*","*","interrupt crisis irrev maint",{"purpose_class":"recovery","beneficiary_bands":["team","organization","household"]}),
 ("NED-DETECT-EARLY","detect a change early enough to still act","By the time the signal is unambiguous the window has closed.","B E P C","*","uncert crisis routine peak",{"purpose_class":"discovery","beneficiary_bands":["organization","community","team"]}),
 ("NED-COMPARE-FAIRLY","compare options that were measured in different ways","Comparison is being made anyway; the question is whether it is honest.","*","*","uncert version public audit",{"purpose_class":"explanation","beneficiary_bands":["individual","organization","community"]}),
 ("NED-TRANSFER-CUSTODY","transfer custody of a thing together with its obligations","Handing over the object is easy; handing over the duties is where it breaks.","P O L H","*","handover irrev audit dispute",{"purpose_class":"coordination","beneficiary_bands":["organization","team","household"]}),
 ("NED-SET-SAFE-LIMIT","set and respect an operating limit shared by several actors","Several parties act on one physical limit that none of them owns.","P E C","*","safety concurrent divauth routine",{"purpose_class":"safety","beneficiary_bands":["organization","community","household"]}),
 ("NED-SHOW-PROVENANCE","show where something came from and who vouches for it","An assertion without a chain behind it cannot be checked or challenged.","*","*","audit dispute public version",{"purpose_class":"accountability","beneficiary_bands":["organization","individual","community"]}),
 ("NED-ADAPT-TO-LOCAL","adapt a general standard to one specific local setting","General guidance leaves exactly the judgment the local party cannot make.","*","*","lowcap learn multiling routine",{"purpose_class":"learning","beneficiary_bands":["organization","household","community"]}),
 ("NED-FIND-MATCH","find the right counterpart among many","The match exists somewhere in a set too large to read.","O C H L","*","routine public peak lowcap",{"purpose_class":"access","beneficiary_bands":["individual","organization","community"]}),
 ("NED-SCHEDULE-SCARCE","allocate a scarce shared facility fairly","Demand exceeds the facility, and the allocation itself must be defensible.","*","*","scarce concurrent dispute peak",{"purpose_class":"coordination","beneficiary_bands":["organization","team","community"]}),
 ("NED-DOCUMENT-DISAGREEMENT","record a disagreement rather than resolve it falsely","Forcing a single answer destroys information the parties will need later.","L O E H","*","dispute audit long collab",{"purpose_class":"accountability","beneficiary_bands":["community","organization","household"]}),
 ("NED-MAKE-LEGIBLE","make a technical artefact readable by the people it affects","The artefact is correct and unreadable, which for its audience is the same as wrong.","*","*","public lowcap learn multiling",{"purpose_class":"explanation","beneficiary_bands":["individual","household","community"]}),
 ("NED-REPAIR-OBJECT","repair rather than replace an object","Repair is possible in principle and blocked in practice.","P H O","*","maint lowcap collab routine",{"purpose_class":"maintenance","beneficiary_bands":["individual","community","household"]}),
 ("NED-REDUCE-WASTE","cut material or energy waste in a routine process","The waste is built into the routine, so only the routine can remove it.","P E O H","*","routine scarce long maint",{"purpose_class":"production","beneficiary_bands":["organization","household","team"]}),
 ("NED-ONBOARD-NEWCOMER","bring a newcomer to working competence quickly","Turnover means the knowledge has to be rebuilt regularly, not once.","O H C","*","learn handover lowcap routine",{"purpose_class":"learning","beneficiary_bands":["team","organization"]}),
 ("NED-PROVE-CONFORMANCE","prove conformance to an external requirement","Conforming is not enough; the proof has to be produceable on demand.","O L C P","*","audit version divauth routine",{"purpose_class":"accountability","beneficiary_bands":["organization","team"]}),
 ("NED-REVOKE-ACCESS","withdraw an access or a consent and have it actually take effect","Granting is well designed everywhere; withdrawal is usually vague.","C L O","*","privacy irrev divauth audit",{"purpose_class":"safety","beneficiary_bands":["individual","organization"]}),
 ("NED-SAMPLE-POPULATION","get a representative picture of a population","Everything downstream depends on who was and was not asked.","E B O L","*","uncert remote routine audit",{"purpose_class":"discovery","beneficiary_bands":["organization","community"]}),
 ("NED-ARCHIVE-COLLECTION","organise a collection so that things can be found again","A collection nobody can search is a store, not a collection.","O H C","*","long routine collab lowcap",{"purpose_class":"preservation","beneficiary_bands":["organization","community","individual"]}),
 ("NED-PERFORM-TOGETHER","rehearse and perform together","Several people must arrive at one moment ready.","H O","R P S 6","collab scarce learn public",{"purpose_class":"expression","beneficiary_bands":["team","community"]}),
 ("NED-TRACK-GROWTH","follow the development of a living thing over time","The interesting quantity is a trajectory, not a reading.","B E","A Q M 1 3 4","seasonal long uncert routine",{"purpose_class":"discovery","beneficiary_bands":["team","organization","household"]}),
 ("NED-SHARE-EQUIPMENT","share expensive equipment among many users","One instrument, many claims on it, and no obvious priority order.","P C O","*","scarce collab concurrent routine",{"purpose_class":"coordination","beneficiary_bands":["organization","team","community"]}),
 ("NED-INTERPRET-SIGNAL","turn a noisy signal into a statement someone can act on","The data arrives; the actionable statement does not.","P C E B","*","uncert routine peak maint",{"purpose_class":"explanation","beneficiary_bands":["team","organization"]}),
 ("NED-PLAN-UNDER-BUDGET","plan work inside a fixed budget and calendar","Everything is possible except all of it.","O L H","*","scarce routine dispute peak",{"purpose_class":"production","beneficiary_bands":["organization","community","household"]}),
 ("NED-PROTECT-PRIVACY","meet an obligation without exposing the person","The duty to disclose and the duty to protect point in opposite directions.","L O C H","*","privacy audit dispute public",{"purpose_class":"safety","beneficiary_bands":["individual","organization","community"]}),
 ("NED-HANDOVER-SHIFT","hand over work at a boundary without losing what is open","The next person needs the open items, not the finished ones.","*","*","handover interrupt routine peak",{"purpose_class":"coordination","beneficiary_bands":["team","organization"]}),
 ("NED-TEST-BEFORE-COMMIT","test a change before it becomes irreversible","Rehearsal is cheap and the alternative is not.","P C O L","*","irrev safety startup version",{"purpose_class":"safety","beneficiary_bands":["organization","team"]}),
 ("NED-COLLECT-FIELD-DATA","collect data in the field where connectivity and power fail","The method has to work where the assumptions do not.","E B O L","*","remote interrupt lowcap seasonal",{"purpose_class":"discovery","beneficiary_bands":["team","community","organization"]}),
 ("NED-NAVIGATE-RULES","find a way through an unfamiliar body of rules","The rules are public and still unusable by the people they bind.","L O H","*","lowcap public dispute version",{"purpose_class":"access","beneficiary_bands":["individual","household","organization"]}),
 ("NED-COMMEMORATE","mark an occasion or a loss in a way that holds","Ritual and record do different work, and both are needed.","H O","R S T 6","public solo long collab",{"purpose_class":"expression","beneficiary_bands":["household","community","individual"]}),
 ("NED-FEED-PEOPLE","feed people safely from a constrained kitchen","Volume, safety and cost pull against one another every service.","H B O","I T","peak safety lowcap routine",{"purpose_class":"everyday_life","beneficiary_bands":["organization","household","community"]}),
 ("NED-MOVE-PEOPLE","get people across operators in one journey","The journey is one thing; the operators are several.","O P C","H","public peak collab routine",{"purpose_class":"access","beneficiary_bands":["individual","community","organization"]}),
 ("NED-STEWARD-HABITAT","steward a habitat under competing uses","Every use is legitimate and together they exceed what the place can carry.","E B","A E R 1 4","scarce dispute long seasonal",{"purpose_class":"care","beneficiary_bands":["community","organization"]}),
 ("NED-CALIBRATE-INSTRUMENT","keep an instrument trustworthy over time","Instruments drift quietly and confidently.","P C B","*","maint routine uncert audit",{"purpose_class":"maintenance","beneficiary_bands":["team","organization"]}),
 ("NED-SETTLE-OBLIGATION","settle an obligation between parties who do not trust each other","Neither party will go first, and both need the exchange to happen.","O L C","*","irrev dispute concurrent routine",{"purpose_class":"coordination","beneficiary_bands":["organization","individual","community"]}),
 ("NED-REDUCE-EXPOSURE","reduce exposure of people to a known hazard","The hazard cannot be removed, so exposure is the variable.","P E B H","*","safety routine peak long",{"purpose_class":"safety","beneficiary_bands":["team","community","household"]}),
 ("NED-BUILD-SHARED-RECORD","build one record several parties will each rely on","Each party keeps its own version today and none of them agrees.","*","*","collab dispute version audit",{"purpose_class":"coordination","beneficiary_bands":["organization","community","team"]}),
]


INPUT = [
 ("INP-FIELD-POLYGON","field boundary geometry with its capture method","A parcel outline that is only usable if how it was obtained travels with it.","E O L","A L 4 5","routine dispute version audit",{"form":"data","unit":"U-HECTARE","identity_type":"PARCEL"}),
 ("INP-SOIL-SAMPLE","a physical soil sample with collection metadata","Material whose value dies the moment its label is separated from it.","E B","A 4","seasonal routine handover peak",{"form":"material","unit":"U-KG","identity_type":"SPECIMEN"}),
 ("INP-LAB-METHOD-LIST","a maintained list of analytic methods","The shared vocabulary without which a number is uninterpretable.","B P O","M A 1 4","version collab audit routine",{"form":"knowledge","unit":None,"identity_type":"MODEL"}),
 ("INP-ANIMAL-RECORD","a per-animal identity and event record","One animal, many events, recorded by several parties over years.","B E O","A 4","long routine handover version",{"form":"data","unit":"U-RECORD","identity_type":"SPECIMEN"}),
 ("INP-CROP-TRIAL","a multi-site crop trial dataset","Observations whose comparability rests on trait, method and scale travelling together.","B E","A 4 1","seasonal collab uncert version",{"form":"data","unit":"U-RECORD","identity_type":"DATASET"}),
 ("INP-PHENOTYPE-SET","a phenotype observation set","Measured characteristics of organisms, each needing its measurement method.","B","Q A 1 3 4","uncert routine collab version",{"form":"data","unit":"U-RECORD","identity_type":"DATASET"}),
 ("INP-SPECIMEN","a biological specimen with chain of custody","Perishable material whose provenance is as important as its content.","B E","Q M A 1 3 4","handover irrev scarce remote",{"form":"organism","unit":"U-COUNT","identity_type":"SPECIMEN"}),
 ("INP-GENOME-SEQUENCE","a genomic sequence with its sampling metadata","A sequence is a signal about a place and time as much as about an organism.","B E C","Q E 1 3","uncert privacy crisis version",{"form":"data","unit":"U-GB","identity_type":"DATASET"}),
 ("INP-WASTEWATER-SAMPLE","a wastewater catchment sample","A pooled sample that says something about a population and nobody in particular.","B E","E Q 3","crisis privacy routine uncert",{"form":"material","unit":"U-LITRE","identity_type":"SPECIMEN"}),
 ("INP-SPECIES-OBSERVATION","a species occurrence observation","A record of what was seen where, carrying the observer's detection ability with it.","E B","A M R 1 4","seasonal remote uncert collab",{"form":"data","unit":"U-RECORD","identity_type":"EVENT"}),
 ("INP-CORE-SAMPLE","drill core and assay results","Physical evidence of the subsurface, expensive and unrepeatable.","P E","B 1 2","scarce irrev audit long",{"form":"material","unit":"U-METRE","identity_type":"SPECIMEN"}),
 ("INP-BLOCK-MODEL","a three-dimensional block model of a deposit","A model that different software packages each read slightly differently.","P C","B 2 1","version dispute long routine",{"form":"data","unit":"U-M3","identity_type":"MODEL"}),
 ("INP-TAILINGS-CLASSIFICATION","a consequence classification for a facility","A rating whose validity expires as the population downstream changes.","P E L","B O 2","safety irrev long version",{"form":"knowledge","unit":None,"identity_type":"ASSET"}),
 ("INP-MACHINE-TELEMETRY","a machine tool telemetry stream","Present-tense data about a machine, with no memory of its own.","P C","C 2","routine maint peak version",{"form":"signal","unit":"U-RECORD","identity_type":"DEVICE"}),
 ("INP-CAD-MODEL","a three-dimensional geometry file for manufacture","Geometry plus the material and tolerance intent that must survive the file format.","P C","C F 2","version routine handover collab",{"form":"artifact","unit":"U-COUNT","identity_type":"MODEL"}),
 ("INP-BOM","a bill of materials with supplier references","The list that decides whether the thing can be built or repaired.","P O","C G 2","routine scarce maint version",{"form":"data","unit":"U-COUNT","identity_type":"MODEL"}),
 ("INP-TEST-VECTOR","a verification test vector set","Stimulus designed to make a design fail while failure is still cheap.","C P","J C 2","version audit routine startup",{"form":"data","unit":"U-COUNT","identity_type":"DATASET"}),
 ("INP-CHIP-SPEC","a processor or hardware interface specification","A frozen contract between people who will never meet.","C P","J C 2","version collab long irrev",{"form":"knowledge","unit":None,"identity_type":"MODEL"}),
 ("INP-METER-READING","interval meter readings","Consumption seen at intervals, from which behaviour is inferred.","P C H","D T K","routine privacy version peak",{"form":"data","unit":"U-KWH","identity_type":"DEVICE"}),
 ("INP-INVERTER-STATE","distributed generation capability and state","What a device can do right now, which is not what it was commissioned to do.","P C","D 2","realtime safety routine maint",{"form":"signal","unit":"U-KW","identity_type":"DEVICE"}),
 ("INP-TARIFF-SCHEDULE","a price or tariff schedule","A published set of prices that changes behaviour the moment it is announced.","O L C","D K G","version public routine peak",{"form":"data","unit":"U-CU","identity_type":"MODEL"}),
 ("INP-PIPE-NETWORK","a hydraulic network description","A model of pipes, valves and demands standing in for a network nobody can see.","P E","E F 2","uncert maint crisis routine",{"form":"data","unit":"U-KM","identity_type":"ASSET"}),
 ("INP-WATER-SAMPLE","a water sample with chain of custody","A litre of water that has to represent a whole system.","E B P","E A 1","routine audit crisis handover",{"form":"material","unit":"U-LITRE","identity_type":"SPECIMEN"}),
 ("INP-RAINFALL-SERIES","a rainfall or flow time series","A record whose meaning changes when the catchment beneath it changes.","E","E A 1","seasonal long uncert version",{"form":"data","unit":"U-RECORD","identity_type":"DATASET"}),
 ("INP-SENSOR-FEED","an environmental or building sensor feed","A stream that is only trustworthy while the sensor is calibrated and reachable.","P E C","E F D 2","routine maint remote uncert",{"form":"signal","unit":"U-RECORD","identity_type":"DEVICE"}),
 ("INP-BIM-MODEL","a building information model","A design description that must answer questions its authors did not anticipate.","P C","F 2","version handover collab long",{"form":"artifact","unit":"U-COUNT","identity_type":"MODEL"}),
 ("INP-SITE-PHOTO","dated site photographs","Evidence that is trivially produced and hard to place in time.","P H","F G S","dispute audit routine public",{"form":"artifact","unit":"U-COUNT","identity_type":"EVENT"}),
 ("INP-ENERGY-AUDIT","a building energy audit record","Findings whose comparability depends on the audit level being declared.","P O","F L D 2","version audit uncert routine",{"form":"data","unit":"U-RECORD","identity_type":"ASSET"}),
 ("INP-FLOOR-PLAN","a measured floor plan","Measured space, where the measurement convention decides the number.","P O H","L F","dispute version routine public",{"form":"artifact","unit":"U-M2","identity_type":"ASSET"}),
 ("INP-PRODUCT-CATALOGUE","a product catalogue with identifiers","A list of things for sale that other systems will join against.","O C","G I C","version routine collab public",{"form":"data","unit":"U-RECORD","identity_type":"DATASET"}),
 ("INP-INVOICE","a structured invoice document","A commercial claim that has to match a physical event.","O L C","G K","routine audit dispute version",{"form":"artifact","unit":"U-CU","identity_type":"ACCOUNT"}),
 ("INP-SHIPMENT-EVENT","a consignment event record","What happened to a lot, where, when and under whose control.","O P L","G H","handover routine audit version",{"form":"data","unit":"U-RECORD","identity_type":"CONSIGNMENT"}),
 ("INP-TIMETABLE","a published service timetable","A promise about the future published before the future is known.","O C P","H","public routine version peak",{"form":"data","unit":"U-RECORD","identity_type":"ROUTE"}),
 ("INP-VEHICLE-AVAILABILITY","a real-time vehicle or asset availability feed","Perishable truth about where things are.","C P O","H G","realtime peak routine public",{"form":"signal","unit":"U-COUNT","identity_type":"VESSEL"}),
 ("INP-MENU-RECIPE","a recipe with quantities, yields and allergens","A production instruction that is also a safety document.","H B O","I T","safety routine peak lowcap",{"form":"knowledge","unit":"U-GRAM","identity_type":"MODEL"}),
 ("INP-INSPECTION-REPORT","a premises or equipment inspection report","A snapshot judgment that will be read as a standing property.","L B P","I F O S","audit public dispute routine",{"form":"data","unit":"U-RECORD","identity_type":"SITE"}),
 ("INP-SOURCE-CODE","a source repository with its dependency graph","Working software that carries obligations nobody read.","C","J 2","version audit routine maint",{"form":"artifact","unit":"U-COUNT","identity_type":"MODEL"}),
 ("INP-MEDIA-ASSET","an image, audio or video asset","Content whose origin is the contested part.","C H O","J R 6","dispute public privacy version",{"form":"artifact","unit":"U-GB","identity_type":"COLLECTION"}),
 ("INP-ACCESSIBILITY-AUDIT","an accessibility audit result","A finding list that is only useful when it names who is excluded and how.","C O","J P O","audit public lowcap routine",{"form":"data","unit":"U-RECORD","identity_type":"DATASET"}),
 ("INP-TRANSACTION-LEDGER","a ledger of financial transactions","An ordered record whose order is the meaning.","O C L","K","irrev audit routine privacy",{"form":"data","unit":"U-CU","identity_type":"ACCOUNT"}),
 ("INP-CONSENT-RECORD","a consent or authorisation record","A permission with a scope, an expiry and a way to take it back.","*","*","privacy irrev audit version divauth routine handover",{"form":"credential","unit":"U-COUNT","identity_type":"PERMIT"}),
 ("INP-PROPERTY-TITLE","a title, tenure or occupancy record","A record of a relationship to land that may not be ownership.","L H E","L O A","dispute long divauth audit",{"form":"credential","unit":"U-HECTARE","identity_type":"PARCEL"}),
 ("INP-SURVEY-FORM","a questionnaire or form definition","The instrument that decides which answers are possible at all.","O L H","M N P 5","version multiling lowcap routine",{"form":"artifact","unit":"U-COUNT","identity_type":"MODEL"}),
 ("INP-CODEBOOK","a variable codebook or data dictionary","The bridge between a question as asked and a figure as published.","O C L","M O P 5","version audit collab long",{"form":"knowledge","unit":"U-RECORD","identity_type":"MODEL"}),
 ("INP-SATELLITE-IMAGE","a satellite or aerial image with acquisition metadata","A picture of a moment that is often used as a picture of now.","E C","A E L 1","version uncert seasonal routine",{"form":"data","unit":"U-GB","identity_type":"DATASET"}),
 ("INP-TELESCOPE-TABLE","a tabular astronomical catalogue","Columns whose units and null conventions decide what a query means.","P C","M 1","version collab routine long",{"form":"data","unit":"U-RECORD","identity_type":"DATASET"}),
 ("INP-MOLECULE-STRUCTURE","a chemical structure record","An identifier that is a function of the software that generated it.","B P C","M C 1 2","version uncert audit routine",{"form":"data","unit":"U-COUNT","identity_type":"MODEL"}),
 ("INP-OCCUPATION-TAXONOMY","an occupation and skills taxonomy","Concept identifiers that many downstream records embed and none control.","O L C","N P 5","version collab multiling routine",{"form":"knowledge","unit":"U-RECORD","identity_type":"MODEL"}),
 ("INP-STAFF-ROSTER","a staff roster with skills and availability","Who is available, qualified and not already committed.","O H","N Q O P","peak scarce concurrent routine",{"form":"data","unit":"U-PERSON-HOUR","identity_type":"PARTY"}),
 ("INP-TENDER-NOTICE","a tender or contract notice","A public statement of intent to spend that binds what follows.","L O","O 5","public audit version routine",{"form":"data","unit":"U-CU","identity_type":"WORKORDER"}),
 ("INP-STATUTE-TEXT","the text of a statute, regulation or published policy","Language that has legal effect and is rarely machine readable.","L","O 5 6","public version dispute long",{"form":"knowledge","unit":"U-COUNT","identity_type":"MODEL"}),
 ("INP-CURRICULUM","a curriculum, syllabus or learning outcome set","A statement of what someone should be able to do afterwards.","O H","P 5","learn version multiling routine",{"form":"knowledge","unit":"U-COUNT","identity_type":"MODEL"}),
 ("INP-BADGE-ASSERTION","a digital credential or badge assertion","A portable claim about a person that a third party must be able to check.","C L O","P N J","version audit privacy public",{"form":"credential","unit":"U-COUNT","identity_type":"PERMIT"}),
 ("INP-CLINICAL-RECORD","a de-identified clinical record extract","Care data reshaped for a purpose it was not collected for.","B C L","Q 3","privacy version uncert audit",{"form":"data","unit":"U-RECORD","identity_type":"COHORT"}),
 ("INP-CARE-PROTOCOL","a clinical guideline or care protocol","Guidance that must be executable at the bedside, not only correct.","B O","Q 3","safety lowcap routine version",{"form":"knowledge","unit":"U-COUNT","identity_type":"MODEL"}),
 ("INP-TRIAL-PROTOCOL","a clinical or field trial protocol","A plan that becomes evidence of good faith once it is frozen.","B O L","Q M 3 5","irrev audit long version",{"form":"knowledge","unit":"U-COUNT","identity_type":"MODEL"}),
 ("INP-COLLECTION-OBJECT","a held object with an accession record","A thing whose identity has to outlive every system that describes it.","H P O","R 6","long handover public dispute",{"form":"material","unit":"U-COUNT","identity_type":"COLLECTION"}),
 ("INP-SCORE-MANUSCRIPT","a musical score, part or manuscript source","Notation that encodes ambiguity a performer must resolve.","H O","R 6","collab learn dispute long",{"form":"artifact","unit":"U-COUNT","identity_type":"COLLECTION"}),
 ("INP-EVENT-LISTING","an activity, session or event listing","A statement that something will happen, which must distinguish cancelled from unknown.","O H C","R S P","public peak version routine",{"form":"data","unit":"U-RECORD","identity_type":"EVENT"}),
 ("INP-REPAIR-LOG","a repair attempt log","What was brought in, what was wrong, and whether it left working.","H P O","S C G","collab routine lowcap version",{"form":"data","unit":"U-RECORD","identity_type":"EVENT"}),
 ("INP-FAMILY-RECORD","a genealogical or kinship record","Sources that disagree about people who cannot be asked.","H O","S R 6","uncert dispute long solo",{"form":"data","unit":"U-RECORD","identity_type":"PARTY"}),
 ("INP-TIME-USE-DIARY","a time-use diary","Unpaid work made visible by asking people to write it down.","H O L","T 5","solo uncert routine lowcap",{"form":"data","unit":"U-HOUR","identity_type":"PARTY"}),
 ("INP-WORK-AGREEMENT","a written work agreement","A document whose absence is the usual cause of the dispute.","H O L","T N","solo dispute multiling lowcap",{"form":"artifact","unit":"U-COUNT","identity_type":"PARTY"}),
 ("INP-AID-ACTIVITY","an aid or grant activity record","A published account of intended spending that many parties join against.","L O","U 5","public audit version collab",{"form":"data","unit":"U-CU","identity_type":"WORKORDER"}),
 ("INP-ROBOT-LOG","a machine or vehicle run log with sensor traces","A recording detailed enough to replay a failure.","P C","H C 2","maint uncert version routine",{"form":"data","unit":"U-GB","identity_type":"DEVICE"}),
 ("INP-FOOD-ONTOLOGY","a food and ingredient vocabulary","Shared terms that let two parties agree what a product is.","B O C","I A G 4","collab version multiling routine",{"form":"knowledge","unit":"U-RECORD","identity_type":"MODEL"}),
 ("INP-BUDGET-ENVELOPE","an approved budget envelope","Money that exists on paper and constrains everything after it.","*","*","scarce audit routine divauth peak public solo",{"form":"funding","unit":"U-CU","identity_type":"ACCOUNT"}),
 ("INP-VOLUNTEER-HOURS","pledged volunteer hours","Effort promised by people with no obligation to appear.","H O","S R U T","collab lowcap uncert seasonal",{"form":"person_time","unit":"U-PERSON-HOUR","identity_type":"PARTY"}),
 ("INP-BENCH-SLOT","bookable bench, instrument or facility time","A slot that cannot be stored and is lost if unused.","P C B","M Q C 1 2","scarce concurrent peak routine",{"form":"space","unit":"U-SLOT","identity_type":"SITE"}),
 ("INP-COLD-CHAIN","cold-chain or controlled-storage capacity","Capacity whose failure is silent until the contents are already spoiled.","P B","Q I H A 3","scarce safety remote crisis",{"form":"space","unit":"U-SLOT","identity_type":"ASSET"}),
 ("INP-SPARE-PART","a spare part with a fitment reference","A component that either fits or does not, and rarely says which.","P H O","C G S","maint scarce lowcap routine",{"form":"material","unit":"U-COUNT","identity_type":"ASSET"}),
 ("INP-TRAINING-COHORT","a group of people to be brought to competence","People with different starting points and one end point.","O H","P N Q","learn peak lowcap collab",{"form":"person_time","unit":"U-PERSON-HOUR","identity_type":"COHORT"}),
 ("INP-LOCAL-KNOWLEDGE","undocumented local knowledge held by practitioners","Knowledge that leaves when the person does.","*","*","lowcap handover long remote learn solo crisis",{"form":"knowledge","unit":None,"identity_type":"PARTY"}),
 ("INP-POWER-SUPPLY","an electrical or fuel supply connection","Energy availability that is assumed until it is not there.","P H","D F E C 2","remote crisis routine scarce",{"form":"energy","unit":"U-KWH","identity_type":"ASSET"}),
 ("INP-WORKSPACE","a physical workspace with access conditions","Space with rules about who may be in it and when.","*","*","scarce concurrent routine safety remote public solo",{"form":"space","unit":"U-M2","identity_type":"SITE"}),
 ("INP-COMMITTED-STAFF-TIME","committed hours of named, qualified people","Time promised by specific people who are also promised elsewhere.","*","*","scarce peak concurrent routine handover lowcap",{"form":"person_time","unit":"U-PERSON-HOUR","identity_type":"PARTY"}),
 ("INP-ISSUED-PERMIT","a permission instrument issued by a named authority","A written permission with a scope, an issuer and an end date.","*","*","audit divauth privacy irrev routine public",{"form":"credential","unit":"U-COUNT","identity_type":"PERMIT"}),
 ("INP-WRITTEN-BRIEF","a written brief, drawing or specification of what is wanted","The statement of intent everything downstream is measured against.","*","*","collab routine version dispute learn startup",{"form":"artifact","unit":"U-COUNT","identity_type":"MODEL"}),
 ("INP-CONDITION-READING","a timestamped reading of a monitored condition","A value that is only meaningful with the moment it was taken.","*","*","routine peak uncert maint remote safety",{"form":"signal","unit":"U-RECORD","identity_type":"DEVICE"}),
 ("INP-CONSUMABLE-STOCK","consumable material held in stock with a shelf life","Material that is either there when needed or quietly expired.","*","*","scarce routine maint peak remote seasonal",{"form":"material","unit":"U-KG","identity_type":"LOT"}),
 ("INP-WORK-QUEUE","a queue of pending items with arrival times","Work that has arrived and not yet been done.","*","*","peak scarce routine interrupt concurrent crisis",{"form":"data","unit":"U-RECORD","identity_type":"RECORDSET"}),
]


PRODUCT = [
 ("PRD-REGISTRY-SERVICE","a registry service that mints and resolves identifiers","A service whose whole job is to hand out identifiers and answer questions about them.","O C L","*","collab version routine public",{"form":"service","generator":False}),
 ("PRD-CROSSWALK-LEDGER","a ledger of sameness assertions between identifier schemes","A record of claims that two identifiers denote one thing, each signed, dated and revocable.","C O L","*","dispute collab version audit",{"form":"coordinated_system","generator":False}),
 ("PRD-FIELD-PROCEDURE","a written field procedure with roles and steps","A procedure written for the person who will be alone when they use it.","*","*","safety lowcap remote routine",{"form":"procedure","generator":False}),
 ("PRD-WALL-CHART","a printed wall chart for one specific setting","A single sheet that removes a choice rather than presenting all of them.","H P B","T I S F A","solo lowcap safety public",{"form":"physical_object","generator":False}),
 ("PRD-POCKET-CARD","a pocket reference card","A card carried by the person doing the work, marked for the decisions that matter.","H P B O","Q F I T","safety peak lowcap routine",{"form":"physical_object","generator":False}),
 ("PRD-JIG-FIXTURE","a bench jig or fixture","A physical constraint that makes the correct action the easy one.","P","C F A 2","safety routine maint lowcap",{"form":"physical_object","generator":False}),
 ("PRD-TEST-RIG","a test rig that measures a stated property","Apparatus that turns a claim into a measurement with a stated tolerance.","P B C","C E D Q 1 2","audit uncert maint routine",{"form":"instrument","generator":False}),
 ("PRD-SENSOR-KIT","a low-cost sensing kit with its calibration procedure","Instrumentation cheap enough to deploy widely and honest about its error.","P E C","E A D 1 2","remote lowcap uncert routine",{"form":"instrument","generator":False}),
 ("PRD-VALIDATOR","a validator that reports per-record verdicts with reasons","A checker whose output explains the verdict rather than only stating it.","C O L","*","audit version routine lowcap",{"form":"interactive_tool","generator":False}),
 ("PRD-DASHBOARD","an operational view that renders staleness and gaps","A display that shows what it does not know as clearly as what it does.","C O P","*","peak uncert routine public",{"form":"interactive_tool","generator":False}),
 ("PRD-SIMULATOR","a simulator for rehearsing a decision before it is real","A place to be wrong cheaply.","P C E O","*","irrev learn safety startup",{"form":"interactive_tool","generator":False}),
 ("PRD-CONFORMANCE-PACK","a conformance pack with fixtures and a counterparty stand-in","A test kit that lets one party check itself without a willing partner.","C O P","*","audit collab version startup",{"form":"instrument","generator":False}),
 ("PRD-DATASET-PUBLICATION","a documented published dataset","Data released with the description that makes it re-usable rather than merely available.","C O L E","*","public version audit collab",{"form":"dataset","generator":False}),
 ("PRD-DATA-SCHEMA","a schema with worked examples and conditional rules","A structure definition that says when a field is required, not only that it exists.","C O","*","version collab audit routine",{"form":"document","generator":False}),
 ("PRD-API-SERVICE","an interface with a declared capability statement","A service that publishes what it actually supports, not what the standard permits.","C O","*","version collab routine audit",{"form":"service","generator":False}),
 ("PRD-DECISION-AID","an interactive decision aid","A tool that narrows a decision to the few facts that change the answer.","*","*","lowcap uncert public learn",{"form":"interactive_tool","generator":False}),
 ("PRD-EXPLAINER","a plain-language explanation of a technical result","A piece written for the person the result is about.","*","*","public lowcap multiling learn",{"form":"explanation","generator":False}),
 ("PRD-STATEMENT-GENERATOR","a generator that produces a per-case statement","A generator taking one case's records and emitting the statement that case needs.","C O L","*","routine lowcap version public",{"form":"generator","generator":True}),
 ("PRD-CONFIGURATOR","a configurator that emits a tailored product","A configurator whose value is only real when it has emitted a concrete product.","C O P","*","version collab lowcap startup",{"form":"generator","generator":True}),
 ("PRD-TEMPLATE-KIT","a template kit with one fully filled worked example","Templates plus the completed example that shows what belongs in the blanks.","O H L","*","lowcap learn routine multiling",{"form":"document","generator":False}),
 ("PRD-WORKED-EXAMPLE","a complete worked reference example","One real case, done properly, published so others can adapt it.","*","*","learn lowcap public routine",{"form":"document","generator":False}),
 ("PRD-TRAINING-COURSE","a short course with an assessment against criteria","Training that ends in a demonstration, not attendance.","O H B","*","learn peak collab lowcap",{"form":"training","generator":False}),
 ("PRD-DRILL-EXERCISE","a rehearsed exercise run with the real parties","A rehearsal that produces a corrected plan, not a report.","P E O L","*","crisis collab safety irrev",{"form":"experience","generator":False}),
 ("PRD-CLINIC-SERVICE","a periodic clinic where people bring problems","Recurring sessions where the problem arrives with the person who has it.","H O B","*","collab lowcap routine public",{"form":"service","generator":False}),
 ("PRD-HELPDESK","a triage and referral desk","A front door that routes rather than answers.","O L H","*","peak lowcap routine public",{"form":"service","generator":False}),
 ("PRD-AUDIT-PROCEDURE","an audit procedure with sampling and adjudication rules","A method that says what to look at and how to decide.","L O","*","audit dispute routine version",{"form":"procedure","generator":False}),
 ("PRD-CERTIFICATE","a machine-verifiable certificate or badge","A statement whose scope and version are part of the statement.","C L O","*","audit version public privacy",{"form":"credential","generator":False}),
 ("PRD-REGISTER","a public register with a revision history","A record designed so that alteration is visible rather than possible.","L O C","*","public irrev audit long",{"form":"dataset","generator":False}),
 ("PRD-MONITORING-PROGRAMME","a monitoring programme with a sampling design","A design that says in advance what will and will not be seen.","E B P L","*","long uncert scarce routine",{"form":"coordinated_system","generator":False}),
 ("PRD-EARLY-WARNING","an early-warning arrangement with escalation rules","A signal path with a named person at the end of it.","E B P C","*","crisis peak safety uncert",{"form":"coordinated_system","generator":False}),
 ("PRD-SCHEDULING-SYSTEM","a booking and allocation arrangement for shared capacity","An allocation whose rules are published before the demand arrives.","O C P","*","scarce concurrent dispute peak",{"form":"coordinated_system","generator":False}),
 ("PRD-HANDOVER-PROTOCOL","a handover protocol with a checklist artefact","A protocol built around what is still open, not what is finished.","*","*","handover interrupt safety routine",{"form":"procedure","generator":False}),
 ("PRD-CATALOGUE","a searchable catalogue with provenance on every entry","Findability plus the record of where each entry came from.","C O H","*","public collab version long",{"form":"interactive_tool","generator":False}),
 ("PRD-EXHIBITION","an exhibition or public installation","A made encounter in a physical place with an intended effect.","H P O","R P S 6","public collab seasonal scarce",{"form":"experience","generator":False}),
 ("PRD-PERFORMANCE-EDITION","a performing edition of a work","An edition that resolves what a performer must decide and records what it resolved.","H O","R 6","collab dispute learn long",{"form":"creative_work","generator":False}),
 ("PRD-DOCUMENTARY-PIECE","a documentary narrative piece","A told account built from records, with its sources visible.","H O L","R J U 6","public uncert long collab",{"form":"creative_work","generator":False}),
 ("PRD-GAME-ACTIVITY","a structured game or participatory activity","An activity whose rules produce the intended experience.","H O","R P S","learn collab public lowcap",{"form":"experience","generator":False}),
 ("PRD-SIGNAGE-SYSTEM","a wayfinding or signage system","Physical information placed where the decision is made.","P H O","H F I O R","public lowcap multiling routine",{"form":"physical_object","generator":False}),
 ("PRD-PACKAGING","protective packaging designed for one route","Packaging designed against the journey, not the shelf.","P O","C G H","routine irrev scarce peak",{"form":"physical_object","generator":False}),
 ("PRD-RETROFIT-KIT","a retrofit kit for equipment already installed","An upgrade that has to work on what is there, not on what should have been.","P H","C D F E S 2","maint lowcap long routine",{"form":"physical_object","generator":False}),
 ("PRD-SPARE-PARTS-PLAN","a spare-parts and availability plan","A commitment about the future obtainability of a part.","P O","C G S 2","maint long scarce audit",{"form":"document","generator":False}),
 ("PRD-MAINTENANCE-SCHEDULE","a condition-based maintenance schedule","Intervention timed by evidence rather than by calendar alone.","P E C","*","maint routine long uncert",{"form":"procedure","generator":False}),
 ("PRD-FIELD-MANUAL","an illustrated field manual","A manual that assumes no support and poor light.","P H B","*","remote lowcap learn safety",{"form":"document","generator":False}),
 ("PRD-COMMUNITY-AGREEMENT","a negotiated community agreement","Terms arrived at with the affected people, recorded so they can be held to.","H L O E","*","collab dispute public long",{"form":"document","generator":False}),
 ("PRD-GOVERNANCE-PROCESS","a governance process with named decision points","A process that says who decides what, and when it is too late to object.","O L","*","divauth collab dispute version",{"form":"procedure","generator":False}),
 ("PRD-BUDGET-PLAN","a costed delivery plan","A plan whose numbers add up to the money that exists.","O L H","*","scarce audit routine peak",{"form":"document","generator":False}),
 ("PRD-LINEAGE-MAP","a lineage map from source record to published figure","A map that makes an untraceable figure visible as untraceable.","C O L","*","audit version uncert long",{"form":"document","generator":False}),
 ("PRD-QUALITY-LABEL","a quality and limitation label carried with every figure","A caveat rendered as part of the headline rather than a footnote.","*","*","uncert public audit version",{"form":"document","generator":False}),
 ("PRD-RECOVERY-PLAN","a documented recovery plan with rehearsed steps","A plan written for the day the normal route is unavailable.","*","*","crisis interrupt irrev safety",{"form":"procedure","generator":False}),
 ("PRD-ACCESS-PATHWAY","a navigable pathway through an entitlement process","A route through a process, described from the applicant's side.","L H O","*","public lowcap crisis privacy",{"form":"service","generator":False}),
 ("PRD-MEAL-SYSTEM","a menu and production system for a constrained kitchen","Menus, quantities and controls designed together against one kitchen.","H B O","I T","peak safety lowcap routine",{"form":"coordinated_system","generator":False}),
 ("PRD-ROUTE-PLAN","a multi-operator journey or logistics plan","One plan that crosses parties who do not coordinate.","O P C","H","peak collab public routine",{"form":"service","generator":False}),
 ("PRD-HABITAT-PLAN","a habitat management plan with monitoring triggers","A plan that states in advance what evidence would change it.","E B","A E R 1 4","long seasonal dispute uncert",{"form":"document","generator":False}),
 ("PRD-CALIBRATION-SERVICE","a calibration and verification service","A service whose product is confidence in someone else's numbers.","P B C","*","maint audit routine scarce",{"form":"service","generator":False}),
 ("PRD-SETTLEMENT-MECHANISM","a settlement mechanism with compensating actions","An exchange arrangement in which mistakes are corrected forward, not undone.","O C L","K G H U","irrev dispute concurrent routine",{"form":"coordinated_system","generator":False}),
 ("PRD-REFERENCE-CORPUS","a reference corpus of deliberately hard cases","A shared set of the cases everybody gets wrong.","C O B","*","collab audit version learn",{"form":"dataset","generator":False}),
 ("PRD-ANNOTATION-GUIDE","an annotation guide with adjudication rules","Instructions that tell two people how to disagree productively.","C O H","*","collab dispute learn version",{"form":"document","generator":False}),
 ("PRD-OBSERVATORY","an observatory that samples and reports a recurring gap","A standing measurement of a problem that is otherwise anecdotal.","O L C E","*","long public uncert audit",{"form":"coordinated_system","generator":False}),
 ("PRD-EXCHANGE-FORMAT","an interchange format with round-trip guarantees","A format defined by what must survive a round trip.","C P O","*","version collab audit routine",{"form":"document","generator":False}),
 ("PRD-BENCH-PROTOCOL","a bench or field protocol with acceptance limits","A protocol that states the limits at which a result is rejected.","B P E","M Q A E 1 3 4","routine audit uncert safety",{"form":"procedure","generator":False}),
 ("PRD-KIT-OF-PARTS","a kit of parts with assembly instructions","Everything needed to build the thing, including the knowledge.","P H","C F A S 2","lowcap learn remote routine",{"form":"physical_object","generator":False}),
 ("PRD-REHEARSAL-SPACE","a controlled environment for practising a real task","A place where the real task can be attempted without the real consequence.","P O H B","*","learn safety irrev collab",{"form":"experience","generator":False}),
 ("PRD-ESCROW-ARRANGEMENT","a holding arrangement that releases on a condition","A third position that lets neither party go first.","O L C","K G L U","dispute irrev collab routine",{"form":"coordinated_system","generator":False}),
]

ACTIVITY = [
 ("ACT-SURVEY-SITE","survey a site and record what is there","Going to the place and writing down what is actually present.","P E L H","*","remote seasonal routine dispute",{"verb":"survey","duration_band":"days","consumes":["staff_hours"],"needs":["needs_form:space"],"yields":["yields_form:data"]}),
 ("ACT-COLLECT-SAMPLE","collect and label a physical sample","Taking material and binding a label to it that will not come off.","B E P","*","seasonal handover routine remote",{"verb":"collect","duration_band":"hours","consumes":["staff_hours"],"needs":["needs_form:space"],"yields":["yields_form:material"]}),
 ("ACT-ANALYSE-SAMPLE","analyse a sample by a named method","Running a method whose identity must travel with the number.","B P","*","peak scarce routine audit",{"verb":"analyse","duration_band":"days","consumes":["lab_capacity","staff_hours"],"needs":["needs_form:material","needs_form:knowledge"],"yields":["yields_form:data"]}),
 ("ACT-MEASURE-INSTRUMENT","take instrument measurements on a schedule","Repeated readings whose value depends on the schedule being kept.","P B E C","*","routine maint uncert long",{"verb":"measure","duration_band":"hours","consumes":["bench_time"],"needs":["needs_form:signal"],"yields":["yields_form:data"]}),
 ("ACT-CALIBRATE","calibrate against a reference","Comparing the instrument to something better and recording the offset.","P B C","*","maint audit routine scarce",{"verb":"calibrate","duration_band":"hours","consumes":["bench_time","staff_hours"],"needs":["needs_form:material"],"yields":["yields_form:data"]}),
 ("ACT-MODEL-SIMULATE","build and run a simulation","Reasoning about a system by running a description of it.","P E C B","*","uncert startup irrev long",{"verb":"simulate","duration_band":"weeks","consumes":["compute","staff_hours"],"needs":["needs_form:data"],"yields":["yields_form:data"]}),
 ("ACT-VALIDATE-RECORDS","validate records against a schema and its conditional rules","Deciding which records may pass and saying why the others did not.","C O L","*","routine version audit peak",{"verb":"validate","duration_band":"hours","consumes":["compute"],"needs":["needs_form:data"],"yields":["yields_form:data"]}),
 ("ACT-RECONCILE","reconcile two records that should agree","Finding the difference and deciding what it means.","O C L","*","dispute audit routine version",{"verb":"reconcile","duration_band":"days","consumes":["staff_hours"],"needs":["needs_form:data"],"yields":["yields_form:data"]}),
 ("ACT-TRANSFORM-DATA","transform data between representations","Moving content across a boundary where meaning is usually lost.","C O","*","version routine collab audit",{"verb":"transform","duration_band":"days","consumes":["compute"],"needs":["needs_form:data"],"yields":["yields_form:data"]}),
 ("ACT-PUBLISH","publish an artefact with a version stamp","Making something available in a way that can be cited later.","*","*","public version audit routine",{"verb":"publish","duration_band":"days","consumes":["staff_hours"],"needs":["needs_form:artifact"],"yields":["yields_form:artifact"]}),
 ("ACT-REVIEW-PEER","have the work reviewed by an independent second party","A second pair of eyes with the standing to say no.","*","*","audit dispute collab routine",{"verb":"review","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:artifact"],"yields":["yields_form:knowledge"]}),
 ("ACT-ADJUDICATE","adjudicate a disputed case against written criteria","Deciding between accounts and recording the reasoning.","L O","*","dispute audit divauth routine",{"verb":"adjudicate","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:data"],"yields":["yields_form:knowledge"]}),
 ("ACT-NEGOTIATE","negotiate terms between parties","Arriving at terms both sides will actually keep.","O L H","*","dispute collab divauth long",{"verb":"negotiate","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:knowledge"],"yields":["yields_form:artifact"]}),
 ("ACT-SCHEDULE-ALLOCATE","allocate scarce capacity to competing requests","Deciding who gets the slot and being able to defend it.","O C P","*","scarce concurrent peak dispute",{"verb":"allocate","duration_band":"days","consumes":["staff_hours"],"needs":["needs_form:data"],"yields":["yields_form:data"]}),
 ("ACT-DISPATCH","dispatch people or vehicles to tasks","Committing resources to work in real time.","O P","*","peak concurrent crisis routine",{"verb":"dispatch","duration_band":"hours","consumes":["vehicle_hours","staff_hours"],"needs":["needs_form:data"],"yields":["yields_form:person_time"]}),
 ("ACT-FABRICATE","fabricate a physical part","Cutting, forming or printing material to a dimension.","P","*","routine scarce maint peak",{"verb":"fabricate","duration_band":"days","consumes":["machine_time","staff_hours"],"needs":["needs_form:material","needs_form:artifact"],"yields":["yields_form:material"]}),
 ("ACT-ASSEMBLE","assemble components into a working whole","Putting parts together so that the whole does what none of them does.","P","*","routine learn lowcap collab",{"verb":"assemble","duration_band":"days","consumes":["staff_hours"],"needs":["needs_form:material"],"yields":["yields_form:material"]}),
 ("ACT-INSTALL-COMMISSION","install and commission on site","Getting the thing working where it will actually live.","P C","*","handover safety startup remote",{"verb":"commission","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:material","needs_form:space"],"yields":["yields_form:signal"]}),
 ("ACT-INSPECT","inspect against a checklist","Looking for specific things in a specific order.","P B L","*","audit routine safety peak",{"verb":"inspect","duration_band":"hours","consumes":["staff_hours"],"needs":["needs_form:space"],"yields":["yields_form:data"]}),
 ("ACT-REPAIR","diagnose and repair a fault","Finding out what is wrong and putting it right.","P H","*","maint lowcap scarce routine",{"verb":"repair","duration_band":"days","consumes":["staff_hours","spare_parts"],"needs":["needs_form:material"],"yields":["yields_form:material"]}),
 ("ACT-DISPOSE-RECYCLE","dispose of or recycle material lawfully","Ending the life of material in a way that can be evidenced.","P E L","*","audit irrev routine dispute",{"verb":"dispose","duration_band":"days","consumes":["staff_hours"],"needs":["needs_form:material"],"yields":["yields_form:data"]}),
 ("ACT-TRAIN-PEOPLE","train people to a stated competence","Bringing people to the point of doing the thing unsupervised.","O H B","*","learn peak collab lowcap",{"verb":"train","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:person_time","needs_form:knowledge"],"yields":["yields_form:person_time"]}),
 ("ACT-REHEARSE-DRILL","rehearse a scenario with the real parties","Practising the bad day with the people who will be there.","P O L E","*","crisis collab safety irrev",{"verb":"rehearse","duration_band":"days","consumes":["staff_hours"],"needs":["needs_form:person_time"],"yields":["yields_form:knowledge"]}),
 ("ACT-FACILITATE-SESSION","facilitate a structured session","Running a meeting whose output is a decision or a record.","H O L","*","collab dispute public lowcap",{"verb":"facilitate","duration_band":"days","consumes":["staff_hours"],"needs":["needs_form:space","needs_form:person_time"],"yields":["yields_form:knowledge"]}),
 ("ACT-INTERVIEW","conduct structured interviews","Asking the same things of different people in a comparable way.","O L H B","*","privacy routine multiling lowcap",{"verb":"interview","duration_band":"days","consumes":["staff_hours"],"needs":["needs_form:person_time"],"yields":["yields_form:data"]}),
 ("ACT-ENUMERATE-FIELD","enumerate a population in the field","Counting or listing in the places where people and things actually are.","E O L","*","remote seasonal lowcap interrupt",{"verb":"enumerate","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:space"],"yields":["yields_form:data"]}),
 ("ACT-CODE-CLASSIFY","code free text into a controlled vocabulary","Turning what people wrote into something that can be counted.","O C L","*","uncert routine multiling collab",{"verb":"classify","duration_band":"days","consumes":["staff_hours"],"needs":["needs_form:data","needs_form:knowledge"],"yields":["yields_form:data"]}),
 ("ACT-ANNOTATE","annotate material against an agreed guide","Adding structure to material without destroying what it says.","C H O","*","collab dispute learn version",{"verb":"annotate","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:artifact","needs_form:knowledge"],"yields":["yields_form:data"]}),
 ("ACT-TRANSCRIBE","transcribe source material","Making a text machine-readable while keeping what the original does.","H C O","*","long collab lowcap version",{"verb":"transcribe","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:artifact"],"yields":["yields_form:data"]}),
 ("ACT-TRANSLATE","translate and back-check","Carrying obligations across a language boundary and checking they arrived.","O H C","*","multiling audit collab routine",{"verb":"translate","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:artifact"],"yields":["yields_form:artifact"]}),
 ("ACT-DESIGN-DRAFT","draft a design against a brief","Committing to a shape before all the evidence exists.","P C H O","*","startup collab uncert long",{"verb":"design","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:knowledge"],"yields":["yields_form:artifact"]}),
 ("ACT-PROTOTYPE-TEST","build and test a prototype","Learning by making the cheap version first.","P C","*","startup learn irrev scarce",{"verb":"prototype","duration_band":"weeks","consumes":["staff_hours","machine_time"],"needs":["needs_form:material"],"yields":["yields_form:data"]}),
 ("ACT-COMPOSE-ARRANGE","compose, arrange or edit a creative work","Shaping material into a form an audience will meet.","H O","R P J 6","collab learn scarce long",{"verb":"compose","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:artifact"],"yields":["yields_form:artifact"]}),
 ("ACT-PERFORM","perform or present to an audience","One moment in which the preparation either holds or does not.","H O","R P S 6","peak collab public irrev",{"verb":"perform","duration_band":"hours","consumes":["staff_hours","venue"],"needs":["needs_form:space","needs_form:person_time"],"yields":["yields_form:person_time"]}),
 ("ACT-CURATE-SELECT","curate a selection against stated criteria","Choosing what is in and being able to say why.","H O C","*","dispute public collab long",{"verb":"curate","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:artifact"],"yields":["yields_form:knowledge"]}),
 ("ACT-CATALOGUE","catalogue items with persistent identifiers","Giving things names that will still resolve later.","C O H L","*","long version routine collab",{"verb":"catalogue","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:artifact"],"yields":["yields_form:data"]}),
 ("ACT-ARCHIVE-DEPOSIT","deposit into a preservation store","Placing something where it can be recovered without the depositing software.","C O H L","*","long irrev handover audit",{"verb":"deposit","duration_band":"days","consumes":["storage"],"needs":["needs_form:artifact"],"yields":["yields_form:artifact"]}),
 ("ACT-MONITOR-CONTINUOUS","monitor continuously and raise alerts","Watching for the thing that rarely happens without becoming noise.","P C E B","*","routine peak uncert crisis",{"verb":"monitor","duration_band":"months","consumes":["compute","staff_hours"],"needs":["needs_form:signal"],"yields":["yields_form:data"]}),
 ("ACT-ESCALATE","escalate according to a defined ladder","Passing a problem upward with the information it needs to be acted on.","O L B C","*","crisis peak safety handover",{"verb":"escalate","duration_band":"hours","consumes":["staff_hours"],"needs":["needs_form:data"],"yields":["yields_form:knowledge"]}),
 ("ACT-AUTHORISE","grant an authorisation with a scope and an expiry","Saying yes in a way that can later be bounded and withdrawn.","L O C","*","divauth privacy audit routine",{"verb":"authorise","duration_band":"days","consumes":["staff_hours"],"needs":["needs_form:credential"],"yields":["yields_form:credential"]}),
 ("ACT-REVOKE","revoke an authorisation and propagate the withdrawal","Making a withdrawal take effect everywhere it was relied on.","L O C","*","privacy irrev divauth crisis",{"verb":"revoke","duration_band":"days","consumes":["staff_hours"],"needs":["needs_form:credential"],"yields":["yields_form:credential"]}),
 ("ACT-VERIFY-CREDENTIAL","verify a presented credential","Checking a claim about a person or thing without collecting more than needed.","C L O","*","privacy public routine peak",{"verb":"verify","duration_band":"hours","consumes":["compute"],"needs":["needs_form:credential"],"yields":["yields_form:knowledge"]}),
 ("ACT-SETTLE-PAYMENT","settle a payment or a compensating transfer","Moving value in a way that either completes or is corrected forward.","O C L","*","irrev concurrent routine dispute",{"verb":"settle","duration_band":"days","consumes":["budget"],"needs":["needs_form:funding"],"yields":["yields_form:funding"]}),
 ("ACT-PROCURE","run a procurement against published criteria","Buying in a way that can withstand challenge.","L O","*","audit divauth dispute long",{"verb":"procure","duration_band":"months","consumes":["staff_hours","budget"],"needs":["needs_form:funding","needs_form:knowledge"],"yields":["yields_form:artifact"]}),
 ("ACT-REPORT-STATUTORY","file a statutory report by a deadline","A submission whose lateness is itself the failure.","L O","*","audit routine peak version",{"verb":"report","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:data"],"yields":["yields_form:artifact"]}),
 ("ACT-CONSULT-PUBLIC","consult affected people and record the input","Asking before deciding, and being able to show what was said.","L H O E","*","public dispute collab audit",{"verb":"consult","duration_band":"months","consumes":["staff_hours"],"needs":["needs_form:person_time"],"yields":["yields_form:data"]}),
 ("ACT-TRIAGE","triage incoming cases by severity","Deciding order when everything cannot be first.","B O L","*","peak crisis scarce routine",{"verb":"triage","duration_band":"hours","consumes":["staff_hours"],"needs":["needs_form:data"],"yields":["yields_form:knowledge"]}),
 ("ACT-CARE-VISIT","carry out a care or service visit and record it","Time with a person, and the record that lets the next person continue.","B H O","*","handover privacy routine remote",{"verb":"visit","duration_band":"hours","consumes":["staff_hours","vehicle_hours"],"needs":["needs_form:person_time"],"yields":["yields_form:data"]}),
 ("ACT-HANDOVER","hand over work and the items still open","Transferring not the finished work but the unfinished part.","*","*","handover interrupt peak safety",{"verb":"hand over","duration_band":"hours","consumes":["staff_hours"],"needs":["needs_form:knowledge"],"yields":["yields_form:knowledge"]}),
 ("ACT-BACKUP-RESTORE","take a backup and test that it restores","A backup nobody has restored is a belief, not a backup.","C P","*","maint irrev routine audit",{"verb":"restore","duration_band":"days","consumes":["storage","compute"],"needs":["needs_form:data"],"yields":["yields_form:data"]}),
 ("ACT-VERSION-MIGRATE","migrate content across a version boundary","Moving to the new definition without losing what the old one meant.","C O L","*","version irrev long audit",{"verb":"migrate","duration_band":"months","consumes":["staff_hours","compute"],"needs":["needs_form:data"],"yields":["yields_form:data"]}),
 ("ACT-BENCHMARK-COMPARE","benchmark alternatives on a common corpus","Comparing on the same problem rather than on each vendor's own.","C P O","*","audit uncert collab version",{"verb":"benchmark","duration_band":"weeks","consumes":["compute","staff_hours"],"needs":["needs_form:data"],"yields":["yields_form:data"]}),
 ("ACT-SAMPLE-AUDIT","audit a random sample against a rule","Checking a few properly rather than all badly.","L O C","*","audit scarce routine dispute",{"verb":"audit","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:data"],"yields":["yields_form:knowledge"]}),
 ("ACT-TAG-IDENTIFY","attach a durable identifier to a physical thing","Binding a name to an object so that it survives handling.","P E B O","*","handover routine irrev audit",{"verb":"tag","duration_band":"hours","consumes":["staff_hours"],"needs":["needs_form:material"],"yields":["yields_form:credential"]}),
 ("ACT-ROUTE-PLAN","plan a route or sequence under constraints","Choosing an order that respects what cannot be changed.","P O C","*","peak scarce routine crisis",{"verb":"plan","duration_band":"days","consumes":["staff_hours","compute"],"needs":["needs_form:data"],"yields":["yields_form:data"]}),
 ("ACT-OBSERVE-BEHAVIOUR","observe people or organisms behaving normally","Watching without changing what is being watched.","B E H O","*","uncert privacy long seasonal",{"verb":"observe","duration_band":"weeks","consumes":["staff_hours"],"needs":["needs_form:space"],"yields":["yields_form:data"]}),
 ("ACT-DECOMMISSION","take a thing out of service and close its record","Ending well, including the obligations that outlive the thing.","P C O L","*","irrev handover long audit",{"verb":"decommission","duration_band":"months","consumes":["staff_hours","budget"],"needs":["needs_form:material"],"yields":["yields_form:data"]}),
]

CONDITION = [
 ("CND-STAFF-HOURS","a fixed pool of qualified staff hours","People with the right qualification are the binding constraint, not the budget.","*","*","scarce peak routine concurrent",{"kind":"resource","resource_kind":"staff_hours","unit":"U-PERSON-HOUR","cap_range":[120,3200]}),
 ("CND-VOLUNTEER-HOURS","pledged volunteer hours that may not materialise","Capacity that is real on average and unreliable on the day.","H O","S R U T P","scarce lowcap collab uncert",{"kind":"resource","resource_kind":"volunteer_hours","unit":"U-PERSON-HOUR","cap_range":[40,600]}),
 ("CND-BUDGET-CAP","a capped budget with no contingency","Every overrun has to be found by not doing something else.","O L H","*","scarce audit divauth routine",{"kind":"resource","resource_kind":"budget","unit":"U-CU","cap_range":[8000,900000]}),
 ("CND-LAB-CAPACITY","laboratory throughput per week","A queue with a fixed service rate and a seasonal arrival spike.","B P","*","scarce peak seasonal routine",{"kind":"resource","resource_kind":"lab_capacity","unit":"U-COUNT","cap_range":[40,1200]}),
 ("CND-BENCH-TIME","bookable instrument or bench time","Time on the one machine everybody needs.","P B C","*","scarce concurrent peak collab",{"kind":"resource","resource_kind":"bench_time","unit":"U-SLOT","cap_range":[20,400]}),
 ("CND-COLD-CHAIN","limited cold-chain or controlled storage slots","Storage whose failure is discovered after the contents are lost.","P B","*","scarce safety remote crisis",{"kind":"resource","resource_kind":"cold_chain","unit":"U-SLOT","cap_range":[10,200]}),
 ("CND-VEHICLE-HOURS","limited vehicle or vessel hours","Movement capacity that also has to be somewhere else.","P O","*","scarce peak remote routine",{"kind":"resource","resource_kind":"vehicle_hours","unit":"U-HOUR","cap_range":[40,900]}),
 ("CND-STORAGE-VOLUME","limited storage volume","Space that runs out quietly and then all at once.","P C O","*","scarce peak routine long",{"kind":"resource","resource_kind":"storage","unit":"U-M3","cap_range":[20,4000]}),
 ("CND-POWER-LIMIT","a site electrical limit shared by everything on it","A ceiling several parties negotiate against without seeing each other.","P C H","*","safety concurrent peak scarce",{"kind":"resource","resource_kind":"power","unit":"U-KW","cap_range":[8,900]}),
 ("CND-WATER-ALLOCATION","an allocated water volume","A share of something that is genuinely finite this season.","E O L","*","scarce seasonal dispute long",{"kind":"resource","resource_kind":"water","unit":"U-M3","cap_range":[500,90000]}),
 ("CND-BANDWIDTH","constrained network bandwidth","A link that is fine until everyone uses it at once.","C P","*","remote peak scarce routine",{"kind":"resource","resource_kind":"bandwidth","unit":"U-GB","cap_range":[5,900]}),
 ("CND-COMPUTE-QUOTA","a compute quota","A budget of machine time that forces a choice of what not to compute.","C P","*","scarce peak routine collab",{"kind":"resource","resource_kind":"compute","unit":"U-HOUR","cap_range":[100,20000]}),
 ("CND-SEATS","a fixed number of seats or places","Places that cannot be created on the day.","H O","*","scarce peak public routine",{"kind":"resource","resource_kind":"seats","unit":"U-COUNT","cap_range":[12,900]}),
 ("CND-BED-CAPACITY","a fixed number of beds or care slots","Capacity whose overflow is a person with nowhere to go.","B O L","*","scarce crisis peak safety",{"kind":"resource","resource_kind":"beds","unit":"U-COUNT","cap_range":[6,400]}),
 ("CND-LICENCE-SEATS","a fixed number of tool or software licences","An artificial scarcity that behaves like a real one.","C O","*","scarce concurrent routine version",{"kind":"resource","resource_kind":"licences","unit":"U-COUNT","cap_range":[3,120]}),
 ("CND-MACHINE-TIME","shared machine, kiln or furnace time","A process step everything else queues behind.","P","*","scarce peak concurrent routine",{"kind":"resource","resource_kind":"machine_time","unit":"U-HOUR","cap_range":[20,800]}),
 ("CND-SPARE-PARTS-STOCK","a limited spare-parts stock","Parts that are either on the shelf or three weeks away.","P O H","*","maint scarce remote routine",{"kind":"resource","resource_kind":"spare_parts","unit":"U-COUNT","cap_range":[5,300]}),
 ("CND-VENUE-CAPACITY","a venue with a fixed capacity and licence","A room that legally holds a number of people.","P H O","*","scarce peak public safety",{"kind":"resource","resource_kind":"venue","unit":"U-COUNT","cap_range":[25,2000]}),
 ("CND-FIELD-WINDOW","a short seasonal field window","Work that is possible for weeks and impossible for months.","E B","*","seasonal scarce peak remote",{"kind":"resource","resource_kind":"field_days","unit":"U-DAY","cap_range":[5,60]}),
 ("CND-SINGLE-OWNER","one accountable owner with full authority","One person can decide, and one person can be asked why.","O H","*","routine solo audit handover",{"kind":"authority","authority_shape":"unitary"}),
 ("CND-DIVIDED-AUTHORITY","approval sits with one body and delivery with another","The party that must act cannot decide, and the party that decides does not act.","L O","*","divauth dispute audit collab",{"kind":"authority","authority_shape":"split"}),
 ("CND-DELEGATED-AUTHORITY","authority delegated with a scope and an expiry","Someone acts on another's behalf, within limits that must be checkable.","L O C","*","divauth privacy audit handover",{"kind":"authority","authority_shape":"delegated"}),
 ("CND-REGULATOR-OVERSIGHT","an external regulator can compel evidence","Records exist because someone outside can demand them.","L O","*","audit version public dispute",{"kind":"authority","authority_shape":"supervised"}),
 ("CND-CONSENT-BASED","the subject's consent is the authority and may be withdrawn","Permission that can end at any moment and must then take effect.","L C B H","*","privacy irrev routine dispute",{"kind":"authority","authority_shape":"consent"}),
 ("CND-COMMUNITY-CONSENT","collective consent by an affected community","A decision that belongs to a group with no single representative.","H L E O","*","collab dispute public long",{"kind":"authority","authority_shape":"collective"}),
 ("CND-COMMITTEE-CONSENSUS","a committee that must reach consensus","Progress stops when two members will not move.","O L C","*","collab divauth dispute version",{"kind":"authority","authority_shape":"consensus"}),
 ("CND-EMERGENCY-POWERS","temporary emergency authority with a sunset","Normal rules suspended, with a date on which they return.","L O","*","crisis irrev audit divauth",{"kind":"authority","authority_shape":"emergency"}),
 ("CND-CONTRACTUAL","authority derived from a contract with penalties","What may be required is exactly what was written down.","O L","*","audit dispute routine version",{"kind":"authority","authority_shape":"contractual"}),
 ("CND-VOLUNTARY-STANDARD","a voluntary standard with no enforcement","Compliance is real only while it is convenient.","O C","*","collab version lowcap audit",{"kind":"authority","authority_shape":"voluntary"}),
 ("CND-CUSTOMARY-AUTHORITY","customary authority not recorded in statute","Real authority that the formal record cannot express.","H L E","*","dispute divauth long collab",{"kind":"authority","authority_shape":"customary"}),
 ("CND-TWO-KEY","two independent approvals required before an action","One person cannot do this alone, by design.","P L O C","*","safety irrev divauth audit",{"kind":"authority","authority_shape":"dual_control"}),
 ("CND-SELF-DIRECTED","the person acts on their own authority","Nobody else approves, and nobody else is responsible.","H","*","solo lowcap routine learn",{"kind":"authority","authority_shape":"self"}),
 ("CND-NO-CONNECTIVITY","intermittent or absent connectivity","The method has to complete without the network.","P E H C","*","remote interrupt lowcap crisis",{"kind":"environment"}),
 ("CND-HAZARDOUS-SITE","a hazardous physical environment","The place itself can injure the people working in it.","P E","*","safety remote routine peak",{"kind":"environment"}),
 ("CND-COLD-CLIMATE","extreme cold affecting equipment and people","Materials, batteries and hands all behave differently.","P E H","*","seasonal remote safety routine",{"kind":"environment"}),
 ("CND-HEAT-HUMIDITY","heat and humidity affecting material and people","Conditions that spoil samples and shorten attention.","P E B H","*","seasonal safety remote peak",{"kind":"environment"}),
 ("CND-DUST-VIBRATION","dust, vibration and mechanical noise","An environment that destroys instruments and legibility.","P","*","routine maint safety peak",{"kind":"environment"}),
 ("CND-NIGHT-SHIFT","work at night with reduced supervision","Fewer people, slower help, and the same consequences.","P B O","*","safety handover solo peak",{"kind":"environment"}),
 ("CND-PUBLIC-SPACE","an uncontrolled public space","People who did not agree to be there are present.","P H L","*","public safety concurrent peak",{"kind":"environment"}),
 ("CND-STERILE-AREA","a controlled clean or sterile area","Entry conditions that constrain who and what can be present.","B P","*","safety routine scarce audit",{"kind":"environment"}),
 ("CND-REMOTE-LOCATION","long travel times to the site","Every mistake costs a return journey.","E P H","*","remote scarce seasonal lowcap",{"kind":"environment"}),
 ("CND-MULTILINGUAL","several working languages in one process","The same obligation has to hold in each language.","O L H","*","multiling public collab lowcap",{"kind":"environment"}),
 ("CND-LOW-LITERACY","low text literacy among the intended users","Text is not the medium available.","H L O","*","lowcap public learn multiling",{"kind":"environment"}),
 ("CND-HIGH-TURNOVER","high staff turnover","The people who know leave faster than documentation is written.","O H B","*","handover learn lowcap routine",{"kind":"environment"}),
 ("CND-LEGACY-EQUIPMENT","long-lived equipment that cannot be replaced","The new thing must work with what is already there.","P C","*","maint version long lowcap",{"kind":"environment"}),
 ("CND-SEASONAL-PEAK","a strong seasonal peak in demand","Capacity sized for the average fails at the peak.","O E B H","*","seasonal peak scarce routine",{"kind":"environment"}),
 ("CND-CONTESTED-SITE","a site with contested claims or access","Doing the work at all requires agreement about being there.","L E H","*","dispute divauth remote long",{"kind":"environment"}),
 ("CND-SUPERVISION-ABSENT","the person performing the work is unsupervised","Nobody will notice a shortcut until its consequence appears.","H P O","*","solo safety remote lowcap",{"kind":"environment"}),
 ("CND-DATA-SENSITIVE","data whose disclosure could harm an identifiable person","Publication is not neutral; it can be the harm.","L C B H","*","privacy audit dispute public",{"kind":"environment"}),
 ("CND-OPEN-PUBLICATION","an expectation that results are published openly","Whatever is produced will be read by people it was not written for.","L O C","*","public audit version collab",{"kind":"environment"}),
]

DYNAMIC = [
 ("DYN-HARD-DEADLINE","a statutory or contractual deadline","A date after which the work is late whatever its quality.","L O","*","audit peak routine irrev",{"kind":"time","effect":"schedule must be met, not merely planned"}),
 ("DYN-SEASONAL-WINDOW","the work is possible only in a season","Miss the window and the next attempt is a year away.","E B","*","seasonal scarce remote peak",{"kind":"time","effect":"all preparation must precede the window"}),
 ("DYN-SHIFT-BOUNDARY","work crosses a shift or team boundary","The work continues; the people do not.","P B O","*","handover interrupt routine peak",{"kind":"time","effect":"open items must survive the boundary"}),
 ("DYN-CADENCE-DAILY","a daily cadence","Something must happen every day, including the bad days.","*","*","routine peak maint solo",{"kind":"time","effect":"a missed day must be visible"}),
 ("DYN-CADENCE-WEEKLY","a weekly cadence","A rhythm slow enough to plan and fast enough to correct.","*","*","routine maint collab long",{"kind":"time","effect":"drift accumulates between cycles"}),
 ("DYN-CADENCE-ANNUAL","an annual cycle","One attempt per year to learn anything.","E O L H","*","seasonal long uncert routine",{"kind":"time","effect":"learning rate is bounded by the cycle"}),
 ("DYN-LEAD-TIME","a long procurement or fabrication lead time","The decision has to be taken long before its consequence is visible.","P O","*","scarce long irrev routine",{"kind":"time","effect":"commitment precedes information"}),
 ("DYN-PUBLICATION-LAG","a lag between the event and the published figure","Every published number is about a past that has already changed.","L O C","*","version uncert public long",{"kind":"time","effect":"the cut-off must be stated with the figure"}),
 ("DYN-REALTIME-BOUND","a bounded response time","Late is the same as wrong.","P C","*","peak safety crisis routine",{"kind":"time","effect":"a bound must be stated and measured"}),
 ("DYN-LONG-HORIZON","a horizon longer than the organisation's memory","Nobody who set this up will still be here.","P L O E","*","long handover audit version",{"kind":"time","effect":"the design must survive its designers"}),
 ("DYN-NOISY-MEASUREMENT","measurement noise larger than the effect of interest","The instrument cannot see what the decision needs.","P B E C","*","uncert routine safety audit",{"kind":"uncertainty","effect":"claims must be bounded by the noise"}),
 ("DYN-MISSING-DATA","systematically missing data","What is missing is not missing at random.","O L E B","*","uncert audit lowcap routine",{"kind":"uncertainty","effect":"coverage must be reported alongside the result"}),
 ("DYN-CONTESTED-EVIDENCE","the parties disagree about the evidence itself","There is no neutral record to appeal to.","L O E H","*","dispute uncert divauth public",{"kind":"uncertainty","effect":"both accounts must be retained"}),
 ("DYN-MODEL-UNCERTAINTY","the model structure itself is uncertain","Two defensible structures give different answers.","P E C B","*","uncert dispute long audit",{"kind":"uncertainty","effect":"structural choices must be disclosed"}),
 ("DYN-SELF-REPORTED","self-reported data with an incentive to misreport","The respondent has a reason to answer in a particular way.","H O L","*","uncert privacy lowcap routine",{"kind":"uncertainty","effect":"the incentive must be stated"}),
 ("DYN-PROXY-MEASURE","a proxy stands in for the thing of interest","The measurable thing is not the thing that matters.","*","*","uncert audit public routine",{"kind":"uncertainty","effect":"the gap between proxy and target must be named"}),
 ("DYN-SMALL-SAMPLE","too few observations for the confidence claimed","The honest interval is wider than the reported one.","B E O L","*","uncert scarce audit routine",{"kind":"uncertainty","effect":"the interval must be shown, not the point"}),
 ("DYN-UNVERIFIED-SOURCE","a source that could not be verified","The claim rests on something nobody has opened.","C O L","*","uncert audit dispute version",{"kind":"uncertainty","effect":"the unverified status must travel with the claim"}),
 ("DYN-ASSUMED-PARAMETER","a headline figure resting on an assumed parameter","One number that nobody measured carries the whole result.","*","*","uncert public audit long",{"kind":"uncertainty","effect":"the assumption must be rendered with the figure"}),
 ("DYN-PARTIAL-COMPLETION","the work is partially complete when conditions change","The state is neither before nor after.","*","*","interrupt crisis handover routine",{"kind":"state","effect":"partial state must be a first-class state"}),
 ("DYN-STALE-STATE","state that expires and must be refreshed","Old truth presented as current truth.","C P O E","*","routine peak uncert maint",{"kind":"state","effect":"age must be rendered, not hidden"}),
 ("DYN-DIVERGENT-COPIES","two copies of one record have diverged","Both are in use and neither knows about the other.","C O L","*","dispute version collab audit",{"kind":"state","effect":"divergence must be detectable"}),
 ("DYN-BACKLOG","an accumulated backlog","The queue is longer than the service rate can clear.","O B L","*","peak scarce routine crisis",{"kind":"state","effect":"the clearance plan is part of the design"}),
 ("DYN-IN-FLIGHT","transactions in flight when a change lands","Something started under the old rules must finish somehow.","C O L","*","version irrev concurrent routine",{"kind":"state","effect":"in-flight items need a stated treatment"}),
 ("DYN-DEGRADED-MODE","operating in a degraded but safe mode","Reduced function chosen deliberately over stopping.","P C B","*","crisis safety maint remote",{"kind":"state","effect":"the degraded state must be declared and visible"}),
 ("DYN-COLD-START","no history to learn from yet","The method needs data the situation has not produced.","*","*","startup uncert lowcap routine",{"kind":"state","effect":"the first period needs a different rule"}),
 ("DYN-QUEUE-PRIORITY","a queue whose order is itself contested","Who goes first is the decision, not a detail.","O B L","*","scarce dispute peak concurrent",{"kind":"state","effect":"the ordering rule must be published"}),
 ("DYN-VERSION-BOUNDARY","a definition changes on a schedule","Comparisons across the boundary are not comparisons.","C O L","*","version audit long routine",{"kind":"change","effect":"cross-boundary comparisons need a marker"}),
 ("DYN-REGULATION-CHANGE","a regulatory change with a transition window","New duties arrive with a date and a partial map.","L O","*","version audit divauth long",{"kind":"change","effect":"the transition itself needs a plan"}),
 ("DYN-STAFF-CHANGE","the people who hold the knowledge leave","The system worked because of someone who is now gone.","O H B","*","handover lowcap learn long",{"kind":"change","effect":"tacit knowledge must be externalised in advance"}),
 ("DYN-SUPPLIER-EXIT","a supplier or service is withdrawn","A dependency announces its own end.","O C P","*","irrev version handover long",{"kind":"change","effect":"a successor and a cutover are required"}),
 ("DYN-SCALE-UP","demand grows by an order of magnitude","What worked by hand no longer works at all.","O C P","*","peak startup scarce routine",{"kind":"change","effect":"manual steps become the failure point"}),
 ("DYN-SCOPE-CHANGE","the scope changes after commitment","The target moved after the plan was fixed.","O L","*","dispute divauth interrupt routine",{"kind":"change","effect":"inherited obligations must be re-derived"}),
 ("DYN-INTERRUPTION","the process is interrupted and must resume","Stopping is normal; restarting from zero is the defect.","*","*","interrupt crisis lowcap routine",{"kind":"change","effect":"resumption must not discard completed work"}),
 ("DYN-RECOVERY-COMPENSATE","errors can only be compensated, not reversed","There is no edit, only a further authorised action.","O L C P","*","irrev audit crisis routine",{"kind":"change","effect":"a compensating action must be defined in advance"}),
 ("DYN-IRREVERSIBLE-STEP","a step that cannot be undone once taken","After this point the options are gone.","P B L C","*","irrev safety audit collab",{"kind":"change","effect":"a rehearsal and a stop point are required"}),
 ("DYN-REVISION-CYCLE","a bounded revise-and-resubmit cycle","Work goes back and forth a limited number of times.","*","*","collab audit routine version",{"kind":"change","effect":"the cycle bound and stopping rule must be stated"}),
 ("DYN-ROLLBACK","a rollback to a known-good state","Going back is possible if the good state was actually kept.","C P","*","irrev maint crisis version",{"kind":"change","effect":"the known-good state must be verified, not assumed"}),
 ("DYN-MIGRATION-CUTOVER","a dated cutover between systems","One day the old thing stops answering.","C O L","*","version irrev peak handover",{"kind":"change","effect":"a rehearsal and a fallback are required"}),
 ("DYN-CONCURRENT-ACTORS","several actors act on one object at once","Duty and effect attach per actor per moment.","*","*","concurrent safety dispute peak",{"kind":"change","effect":"attribution must be per actor, not per object"}),
 ("DYN-CONTENTION-PEAK","contention for a shared resource peaks","Everything fits on average and nothing fits at the peak.","*","*","peak scarce concurrent routine",{"kind":"change","effect":"the peak, not the mean, sizes the design"}),
 ("DYN-DRIFT","slow drift away from the calibrated state","Nothing broke; it just stopped being right.","P B C E","*","maint uncert long routine",{"kind":"change","effect":"drift must be measured, not assumed absent"}),
 ("DYN-FEEDBACK-LOOP","the output changes the thing being measured","Publishing the measure changes the behaviour it measures.","O L E C","*","public long uncert dispute",{"kind":"change","effect":"the loop must be acknowledged in the design"}),
 ("DYN-ESCALATION","a condition escalates if left unattended","Waiting is itself a decision with a cost.","B P L O","*","crisis peak safety routine",{"kind":"change","effect":"a time-based escalation ladder is required"}),
 ("DYN-EXPIRY","an authorisation or certificate expires","A permission that quietly stops being true.","L O C","*","audit privacy version routine",{"kind":"change","effect":"expiry must be checked at use, not at issue"}),
 ("DYN-SUCCESSION","custody passes to a successor","Someone else will hold this, and must be able to.","L O H","*","handover long irrev audit",{"kind":"change","effect":"the successor must be named before the transfer"}),
 ("DYN-EMBARGO","a period during which a result may not be released","The result exists and may not yet be said.","L O C","*","audit privacy public irrev",{"kind":"change","effect":"the embargo must be enforced, not requested"}),
 ("DYN-RETRACTION","a published result must be corrected or withdrawn","The wrong number is already in other people's work.","L O C","*","public audit irrev version",{"kind":"change","effect":"downstream users must be reachable"}),
 ("DYN-QUIET-FAILURE","a failure that produces plausible output rather than an error","The worst failure is the one that looks like success.","C P B","*","safety uncert maint audit",{"kind":"change","effect":"failures must be made loud by construction"}),
 ("DYN-DEMAND-SURGE","an unplanned surge in demand","Everyone arrives at once for a reason nobody predicted.","O B L H","*","crisis peak scarce concurrent",{"kind":"change","effect":"a surge rule must exist before the surge"}),
]

ACCEPTANCE = [
 ("ACC-SCHEMA-VALID","every delivered record validates against the published rules","A mechanical pass over the delivered set against a published definition.","C O L","*","audit version routine collab",{"check_mode":"machine","observable":"validator exit status and error list","judgment_needed":None}),
 ("ACC-NO-DUP-ID","no identifier denotes two things in the delivered set","A uniqueness check over the identifier column.","C O L P","*","collab dispute version routine",{"check_mode":"machine","observable":"duplicate identifier count is zero","judgment_needed":None}),
 ("ACC-ROUNDTRIP","export then re-import reproduces the content","A round trip that must lose nothing that was declared to survive it.","C P O","*","version collab audit routine",{"check_mode":"machine","observable":"byte or field-level diff is empty","judgment_needed":None}),
 ("ACC-UNIT-DECLARED","every quantity carries a unit from the declared table","No bare numbers anywhere in the deliverable.","*","*","audit routine version collab",{"check_mode":"machine","observable":"count of quantities without a unit is zero","judgment_needed":None}),
 ("ACC-METHOD-CITED","every reported value cites the method that produced it","A number without its method is not a result.","B P E O","*","audit uncert routine version",{"check_mode":"machine","observable":"every value row carries a method identifier","judgment_needed":None}),
 ("ACC-VERSION-STAMPED","every output carries the version of the rules that produced it","Comparability depends on knowing which rules applied.","*","*","version audit long routine",{"check_mode":"machine","observable":"version field present and resolvable","judgment_needed":None}),
 ("ACC-COVERAGE-PCT","a stated proportion of the target set is actually covered","Coverage claimed is coverage measured.","*","*","audit uncert routine public",{"check_mode":"machine","observable":"covered divided by target exceeds the threshold","judgment_needed":None}),
 ("ACC-LATENCY-BOUND","the response happens within a stated time bound","Measured at the ninety-fifth percentile, not on a good day.","C P O","*","peak safety routine crisis",{"check_mode":"machine","observable":"p95 latency below the stated bound","judgment_needed":None}),
 ("ACC-CAPACITY-RESPECTED","the plan never exceeds the stated capacity","Summed draw against the pool, at the peak.","*","*","scarce concurrent peak audit",{"check_mode":"machine","observable":"peak simultaneous draw below capacity","judgment_needed":None}),
 ("ACC-BUDGET-RESPECTED","spend stays within the approved envelope","Committed plus forecast against the envelope.","O L H","*","scarce audit routine divauth",{"check_mode":"machine","observable":"committed plus forecast below the envelope","judgment_needed":None}),
 ("ACC-DEADLINE-MET","the deliverable exists before the stated day","A date test, applied to the artefact, not the intention.","*","*","peak audit routine irrev",{"check_mode":"machine","observable":"artefact timestamped before the deadline day","judgment_needed":None}),
 ("ACC-TRACE-TO-SOURCE","every published figure traces to a named source record","Any figure that cannot be traced is reported as untraceable.","C O L","*","audit uncert public long",{"check_mode":"machine","observable":"count of untraceable figures is zero","judgment_needed":None}),
 ("ACC-REJECT-REASONED","every rejected record is reported with a reason code","Rejections are published, not silently dropped.","C O L","*","audit routine public version",{"check_mode":"machine","observable":"rejects file row count equals rejected count","judgment_needed":None}),
 ("ACC-DEGRADES-SAFELY","on loss of a dependency the declared safe state is entered","Tested by removing the dependency, not by asserting it.","P C B","*","safety crisis maint remote",{"check_mode":"machine","observable":"observed state after induced loss equals declared safe state","judgment_needed":None}),
 ("ACC-REVOCATION-PROPAGATES","a withdrawal takes effect downstream within a stated interval","Measured in wall-clock time from withdrawal to refusal.","C L O","*","privacy irrev audit divauth",{"check_mode":"machine","observable":"elapsed time from revocation to first refusal","judgment_needed":None}),
 ("ACC-ACCESS-CONTROL","only the authorised scope is reachable","Probed from outside the scope, not reasoned about.","C L O","*","privacy audit safety routine",{"check_mode":"machine","observable":"out-of-scope probe returns refusal","judgment_needed":None}),
 ("ACC-PII-ABSENT","no personal identifier appears in the published artefact","A scan of the artefact for identifying fields.","C L B H","*","privacy public audit routine",{"check_mode":"machine","observable":"identifier scan returns no hits","judgment_needed":None}),
 ("ACC-REPRODUCIBLE","an independent party reproduces the figure from the stated inputs","Someone else, with the inputs, gets the same number.","*","*","audit collab uncert long",{"check_mode":"mixed","observable":"independent recomputation within tolerance","judgment_needed":"whether the inputs given were the inputs actually used"}),
 ("ACC-INDEPENDENT-RECOMPUTE","a second assessor recomputes the score within tolerance","Self-assessment plus legal consequence needs an outside check.","O L P","*","audit dispute public version",{"check_mode":"mixed","observable":"assessor difference within the stated tolerance","judgment_needed":"whether the assessor applied the same interpretation"}),
 ("ACC-CALIBRATION-WITHIN","the instrument reads within tolerance of the reference","Compared against something traceably better.","P B C","*","maint audit routine safety",{"check_mode":"machine","observable":"deviation from reference within tolerance","judgment_needed":None}),
 ("ACC-DIMENSION-CORRECT","a dimensional check passes on every derived quantity","Units multiply out to what the quantity claims to be.","P C B E","*","audit routine version collab",{"check_mode":"machine","observable":"dimensional analysis returns no mismatch","judgment_needed":None}),
 ("ACC-MASS-BALANCE","inputs and outputs balance within tolerance","Continuity, checked rather than assumed.","P E B","*","audit routine uncert maint",{"check_mode":"machine","observable":"closure error below the stated tolerance","judgment_needed":None}),
 ("ACC-FIT-TOLERANCE","the physical part fits within the stated tolerance","Measured on the made part, not on the drawing.","P","*","routine audit maint scarce",{"check_mode":"machine","observable":"measured dimension within tolerance band","judgment_needed":None}),
 ("ACC-LOAD-TESTED","the object withstands the stated load with margin","Loaded until the stated margin, and inspected after.","P","*","safety audit irrev routine",{"check_mode":"machine","observable":"no failure at rated load times margin","judgment_needed":None}),
 ("ACC-DURABILITY-CYCLES","the object survives a stated number of cycles","Cycled to the number, then examined.","P H","*","maint long audit routine",{"check_mode":"machine","observable":"function retained after the cycle count","judgment_needed":None}),
 ("ACC-LEGIBLE-AT-DISTANCE","the artefact is legible under the stated conditions","Read at the distance and light where it will be used.","P H","*","public safety lowcap routine",{"check_mode":"mixed","observable":"correct reading by test readers at the stated distance","judgment_needed":"whether the test conditions match the real setting"}),
 ("ACC-UNDERSTOOD-BY-USER","a first-time user completes the task unaided","Watched, not asked.","H C O","*","lowcap learn public solo",{"check_mode":"human","observable":"completion without intervention","judgment_needed":"whether the observed users represent the intended ones"}),
 ("ACC-TASK-COMPLETION","a stated proportion of users complete the task","A rate, measured on real attempts.","C O H","*","public lowcap peak routine",{"check_mode":"mixed","observable":"completion rate above the threshold","judgment_needed":"whether abandonment was caused by the artefact"}),
 ("ACC-EXPERT-REVIEW","a qualified reviewer judges the work adequate against written criteria","Judgment, but against criteria written before the work.","*","*","audit dispute collab version",{"check_mode":"human","observable":"signed reviewer statement against each criterion","judgment_needed":"the substantive adequacy judgment itself"}),
 ("ACC-COMMUNITY-ACCEPT","the affected community accepts the result in a recorded decision","Acceptance by the people affected, recorded as a decision.","H L E O","*","collab public dispute long",{"check_mode":"human","observable":"minuted decision naming who participated","judgment_needed":"whether participation was representative"}),
 ("ACC-DISAGREEMENT-RECORDED","disagreements are retained rather than resolved away","Both accounts survive in the record.","L O E H","*","dispute audit collab long",{"check_mode":"mixed","observable":"each conflict has both accounts attached","judgment_needed":"whether the accounts are fairly stated"}),
 ("ACC-CAVEAT-RENDERED","the stated caveat appears with the headline figure","Rendered in the headline, not in a footnote.","*","*","uncert public audit routine",{"check_mode":"mixed","observable":"caveat text present in the same view as the figure","judgment_needed":"whether the caveat is intelligible to that audience"}),
 ("ACC-JUDGMENT-DOCUMENTED","each judgment call is recorded with who made it","Not the judgment reviewed, but the judgment recorded.","*","*","audit dispute divauth routine",{"check_mode":"mixed","observable":"every judgment field has a named author and criterion","judgment_needed":"whether the criterion was applied honestly"}),
 ("ACC-RESUMES-FROM-PARTIAL","the process resumes from partial state without restarting","Interrupted mid-way, then continued.","*","*","interrupt crisis lowcap routine",{"check_mode":"machine","observable":"completed work retained after induced interruption","judgment_needed":None}),
 ("ACC-DRILL-PASSED","a rehearsal is completed within the stated time by the real parties","The people who would actually do it, doing it.","P O L E","*","crisis collab safety irrev",{"check_mode":"mixed","observable":"drill completed within the time box","judgment_needed":"whether the drill resembled the real event"}),
 ("ACC-HANDOVER-COMPLETE","the receiving party can continue without contacting the sender","Tested by not allowing the contact.","*","*","handover interrupt audit routine",{"check_mode":"human","observable":"receiver completes the next step unaided","judgment_needed":"whether the next step was representative"}),
 ("ACC-TRAINEE-COMPETENT","a trainee performs the procedure unsupervised to criterion","Demonstrated, not attended.","O H B","*","learn safety lowcap routine",{"check_mode":"mixed","observable":"criterion-referenced performance record","judgment_needed":"whether the criterion captures competence"}),
 ("ACC-AUDIENCE-RESPONSE","an audience reports the intended understanding or response","Asked afterwards, against what was intended beforehand.","H O","R P S J 6","public collab learn peak",{"check_mode":"human","observable":"post-event responses against the stated intent","judgment_needed":"the interpretation of the responses"}),
 ("ACC-AESTHETIC-BRIEF","the work meets a written artistic brief judged by a named panel","Aesthetic judgment, made accountable by writing the brief first.","H O","R P 6","collab dispute public long",{"check_mode":"human","observable":"panel decision against each brief clause","judgment_needed":"the aesthetic judgment itself"}),
 ("ACC-ACCESSIBILITY-PASS","the artefact meets the stated accessibility criteria","Checked with the assistive technology, not only the checker.","C H P O","*","public lowcap audit routine",{"check_mode":"mixed","observable":"criteria pass list plus assistive-technology walkthrough","judgment_needed":"whether the walkthrough covered real tasks"}),
 ("ACC-LANGUAGE-PARITY","every language version carries the same obligations","Not translated words, but equal duties.","O L H","*","multiling audit public collab",{"check_mode":"mixed","observable":"clause-by-clause obligation comparison","judgment_needed":"equivalence of legal effect"}),
 ("ACC-SAFETY-INTERLOCK","the unsafe action is impossible rather than discouraged","Attempted, and found to be blocked.","P B C","*","safety irrev audit routine",{"check_mode":"machine","observable":"attempted unsafe action is refused","judgment_needed":None}),
 ("ACC-NO-SILENT-FAILURE","every failure is surfaced rather than producing plausible output","Faults injected; output either correct or loudly absent.","C P B","*","safety uncert maint audit",{"check_mode":"machine","observable":"injected fault produces an error, not a value","judgment_needed":None}),
 ("ACC-CONFLICT-DETECTED","a seeded conflict is detected by the check","The check is tested with something it should catch.","C O L P","*","audit version collab routine",{"check_mode":"machine","observable":"seeded conflict appears in the check output","judgment_needed":None}),
 ("ACC-SPARE-AVAILABLE","a replacement part is obtainable for a stated period","A commitment tested by ordering one.","P O H","*","maint long audit lowcap",{"check_mode":"mixed","observable":"part obtainable within the stated lead time","judgment_needed":"whether the supply is durable or momentary"}),
 ("ACC-WITHIN-EMISSIONS","the stated environmental limit is not exceeded","Measured at the point the limit applies.","E P","*","audit routine safety long",{"check_mode":"machine","observable":"measured value below the limit at the compliance point","judgment_needed":None}),
 ("ACC-COST-PER-UNIT","cost per unit stays under the stated ceiling","Total cost divided by units actually delivered.","O H L","*","scarce audit routine peak",{"check_mode":"machine","observable":"realised cost per delivered unit below ceiling","judgment_needed":None}),
 ("ACC-EQUITY-CHECK","the distribution of benefit across groups is reported and reviewed","Who gained is reported, not assumed even.","L O H E","*","public audit dispute long",{"check_mode":"mixed","observable":"benefit distribution table by group","judgment_needed":"whether the grouping is the one that matters"}),
 ("ACC-STALENESS-RENDERED","the age of every displayed value is visible to the reader","The reader can tell live from last-seen from silent.","C P O","*","peak uncert public routine",{"check_mode":"machine","observable":"every displayed value carries an age or a silence marker","judgment_needed":None}),
 ("ACC-WITNESS-RETAINED","a checked satisfying assignment is retained with the deliverable","The evidence that it fits is kept, not just the claim.","*","*","audit collab routine version",{"check_mode":"machine","observable":"stored assignment re-verifies against the constraints","judgment_needed":None}),
]

SCALE = [
 ("SCL-MOLECULE","molecular and sub-cellular scale","Structures and reactions below the level of a whole cell.","B P","M C Q 1 2 3","routine uncert version audit",{"band":"micro","span":"sub-cellular"}),
 ("SCL-CELL-CULTURE","bench-scale cell or tissue culture","Living material kept alive on a bench for a defined period.","B","M Q 1 3","scarce routine irrev safety",{"band":"micro","span":"bench"}),
 ("SCL-SPECIMEN","a single organism or specimen","One individual, followed or examined.","B E","A Q M 1 3 4","routine handover uncert long",{"band":"individual","span":"one organism"}),
 ("SCL-HERD-FLOCK","a herd, flock, apiary or pen","A managed group of animals treated as one unit and many individuals.","B E","A 4","seasonal routine long remote",{"band":"group","span":"managed group"}),
 ("SCL-FIELD-PLOT","a field plot or trial site","A bounded piece of ground under a controlled treatment.","E B","A 1 4","seasonal routine collab uncert",{"band":"local","span":"plot"}),
 ("SCL-FARM","a whole farm or holding","One enterprise on land, with everything that implies.","E O H","A 4","seasonal routine solo long",{"band":"enterprise","span":"holding"}),
 ("SCL-CATCHMENT","a river catchment","A hydrological unit that ignores administrative boundaries.","E","E A O 1","seasonal long dispute crisis",{"band":"landscape","span":"catchment"}),
 ("SCL-FOREST-STAND","a forest stand or plantation block","Trees managed together on a decadal cycle.","E B","A 1 4","long seasonal remote uncert",{"band":"landscape","span":"stand"}),
 ("SCL-REEF-HABITAT","a reef, wetland or habitat patch","A place defined by what lives in it.","E B","A R 1 4","long seasonal uncert dispute",{"band":"landscape","span":"habitat"}),
 ("SCL-MIGRATORY-RANGE","a migratory range across jurisdictions","A population whose range no single authority covers.","E B","A U 1 4","long collab divauth seasonal",{"band":"regional","span":"cross-border range"}),
 ("SCL-BENCH","a laboratory bench","One working surface, one operator, one method at a time.","B P","M 1 2 3","scarce routine solo audit",{"band":"micro","span":"bench"}),
 ("SCL-INSTRUMENT","a single instrument or sensor station","One device whose readings other things depend on.","P C E B","*","maint scarce routine uncert",{"band":"device","span":"one instrument"}),
 ("SCL-MACHINE-CELL","a machine cell on a shop floor","A few machines and the people who set them.","P","C 2","routine handover maint peak",{"band":"local","span":"cell"}),
 ("SCL-PRODUCTION-LINE","a production line","A sequence where every station waits for the one before.","P O","C 2","peak routine maint concurrent",{"band":"facility","span":"line"}),
 ("SCL-FACTORY","a whole plant","Many lines, shared services and one site boundary.","P O","C 2","routine peak long audit",{"band":"facility","span":"plant"}),
 ("SCL-MINE-SITE","a mine site and its immediate surroundings","An operation whose consequences extend past its fence.","P E","B 1 2","safety long irrev dispute",{"band":"facility","span":"site"}),
 ("SCL-SUBSTATION","an electrical substation and its feeders","A node where the network's state becomes local and physical.","P C","D 2","safety concurrent peak maint",{"band":"facility","span":"substation"}),
 ("SCL-PIPE-NETWORK","a water or gas distribution network","Buried infrastructure known mostly by inference.","P E","E D 2","maint crisis uncert long",{"band":"regional","span":"network"}),
 ("SCL-VEHICLE","a single vehicle or vessel","One moving thing with its own state and log.","P","H C 2","maint routine remote safety",{"band":"device","span":"one vehicle"}),
 ("SCL-FLEET","a fleet of vehicles","Many moving things allocated centrally.","P O C","H G 2","peak concurrent scarce routine",{"band":"enterprise","span":"fleet"}),
 ("SCL-PORT-TERMINAL","a port or freight terminal","A place where custody changes hands under time pressure.","P O L","H","handover peak concurrent audit",{"band":"facility","span":"terminal"}),
 ("SCL-CONSTRUCTION-SITE","a construction site","A place that is different every week and dangerous every day.","P","F 2","safety concurrent handover peak",{"band":"facility","span":"site"}),
 ("SCL-BUILDING-ROOM","a single room or zone","The scale at which comfort, safety and use are actually experienced.","P H","F L Q P","routine maint lowcap public",{"band":"local","span":"room"}),
 ("SCL-BUILDING","a whole building","One structure with a design intent and an operating reality.","P O H","F L 2","maint long handover routine",{"band":"facility","span":"building"}),
 ("SCL-CAMPUS","a campus, estate or portfolio","Many buildings under one operator with inconsistent records.","P O","F L P Q","long routine collab version",{"band":"enterprise","span":"estate"}),
 ("SCL-KITCHEN","a commercial or institutional kitchen","A production space with a legal safety regime and no slack.","P H B","I T","peak safety routine lowcap",{"band":"local","span":"kitchen"}),
 ("SCL-STAGE-VENUE","a stage, hall or venue","A space that exists for one event at a time.","P H O","R S P","peak public scarce collab",{"band":"local","span":"venue"}),
 ("SCL-STREET","a street or block","Where public space meets private frontage.","P H L","H G L O","public concurrent routine dispute",{"band":"local","span":"street"}),
 ("SCL-NEIGHBOURHOOD","a neighbourhood","Small enough to know, large enough to disagree.","H L E O","*","public collab dispute long",{"band":"community","span":"neighbourhood"}),
 ("SCL-CITY","a city","One authority, many operators, and everybody's daily life.","L O E C","*","public peak divauth long",{"band":"regional","span":"city"}),
 ("SCL-REGION","a sub-national region","The level at which national rules meet local conditions.","L O E","*","divauth long version public",{"band":"regional","span":"region"}),
 ("SCL-NATION","a national jurisdiction","One legal system, one statistical frame, many exceptions.","L O C","*","version audit long public",{"band":"national","span":"nation"}),
 ("SCL-CROSS-BORDER","a cross-border arrangement","Two or more legal systems that must interoperate anyway.","L O C E","*","divauth multiling collab long",{"band":"international","span":"cross-border"}),
 ("SCL-GLOBAL-NETWORK","a global network of independent participants","No centre, many implementations, one specification.","C O","*","collab version long public",{"band":"international","span":"global"}),
 ("SCL-PERSON","one person","The scale at which everything is either usable or not.","H B","*","solo lowcap learn privacy",{"band":"individual","span":"one person"}),
 ("SCL-HOUSEHOLD","one household","An organisation with no organisation.","H","T I S Q P","solo lowcap routine safety",{"band":"household","span":"household"}),
 ("SCL-EXTENDED-FAMILY","an extended family or care network","People bound by obligation rather than contract.","H B","T Q S","collab lowcap long interrupt",{"band":"household","span":"care network"}),
 ("SCL-SMALL-TEAM","a small team","Few enough people that coordination is conversation.","O H","*","collab routine handover lowcap",{"band":"team","span":"team"}),
 ("SCL-DEPARTMENT","a department within an organisation","Enough people that process replaces memory.","O","*","routine handover version divauth",{"band":"organization","span":"department"}),
 ("SCL-SME","a small or medium enterprise","One organisation without specialist functions.","O H","*","lowcap routine peak audit",{"band":"organization","span":"firm"}),
 ("SCL-LARGE-ORG","a large organisation","Many parts that must agree without meeting.","O","*","divauth version audit long",{"band":"organization","span":"enterprise"}),
 ("SCL-SUPPLY-CHAIN","a multi-tier supply chain","Parties who know their neighbours and not the chain.","O P L","*","collab audit version dispute",{"band":"network","span":"supply chain"}),
 ("SCL-MARKET","a market of many buyers and sellers","No party can instruct another and all of them respond to price.","O C","*","concurrent peak public version",{"band":"network","span":"market"}),
 ("SCL-COOPERATIVE","a cooperative or member association","Members who are also owners and also customers.","O H","*","collab dispute lowcap long",{"band":"organization","span":"cooperative"}),
 ("SCL-COMMUNITY-GROUP","a voluntary community group","Commitment without budget, continuity without contracts.","H O","*","collab lowcap seasonal public",{"band":"community","span":"group"}),
 ("SCL-CLASSROOM","a classroom or cohort","Thirty different starting points and one timetable.","H O","P","learn peak routine lowcap",{"band":"group","span":"cohort"}),
 ("SCL-WARD-CLINIC","a ward, clinic or practice","Where care is delivered and records are made in the gaps.","B O","Q 3","peak handover safety privacy",{"band":"facility","span":"clinic"}),
 ("SCL-HOSPITAL-SYSTEM","a hospital or health system","Many services that must join up around one person.","B O L","Q 3","divauth handover peak long",{"band":"enterprise","span":"health system"}),
 ("SCL-COURT-TRIBUNAL","a court, tribunal or hearing","A forum where the record is the decision.","L","O 5","dispute audit public routine",{"band":"organization","span":"tribunal"}),
 ("SCL-AGENCY","a public agency","A body that must act only as its powers allow.","L O","O 5","audit divauth version public",{"band":"organization","span":"agency"}),
 ("SCL-MULTI-AGENCY","a multi-agency arrangement","Several bodies, one person's problem.","L O B","*","divauth collab handover crisis",{"band":"network","span":"multi-agency"}),
 ("SCL-DATA-CENTRE","a data centre or compute cluster","Physical infrastructure people treat as abstract.","C P","J 2","peak scarce maint routine",{"band":"facility","span":"cluster"}),
 ("SCL-SOFTWARE-SERVICE","a running software service","Something that must keep answering while it is being changed.","C","J 2","version concurrent maint peak",{"band":"service","span":"service"}),
 ("SCL-PROTOCOL-NETWORK","a protocol with many independent implementations","A specification whose users cannot be instructed.","C O","J 2","collab version dispute long",{"band":"network","span":"protocol"}),
 ("SCL-ARCHIVE-COLLECTION","an archive, library or collection","Material held for a future nobody can specify.","H O L","R M 6","long handover audit version",{"band":"organization","span":"collection"}),
 ("SCL-ORBIT","an observatory, orbit or remote-sensing programme","Instruments nobody can reach once deployed.","P C E","M 1 2","irrev scarce long collab",{"band":"international","span":"observatory"}),
 ("SCL-WORKSHOP-BENCH","a repair workshop or maker bench","A place where one broken thing is dealt with at a time.","P H","S C G","maint lowcap collab routine",{"band":"local","span":"workshop"}),
 ("SCL-CAMP-SETTLEMENT","a camp or informal settlement","People living where services were never planned.","H L E","U O Q","crisis remote lowcap collab",{"band":"community","span":"settlement"}),
]

# --------------------------------------------------------------------------
# Grounding: every inventory item in the three supplied assets is walked once.
# Each entry maps "<source>:<item id>" to the ingredient it contributes to,
# or to the token "SKIP:<reason>".  The item label is read back out of the
# asset file itself so the recorded provenance uses the inventory's own label.
# --------------------------------------------------------------------------
GROUNDING = {
 # ---- assets/01.raw.md (137 items) ----
 "01:A-01":"INP-FIELD-POLYGON","01:A-02":"INP-LAB-METHOD-LIST","01:A-03":"PRD-REGISTRY-SERVICE",
 "01:A-04":"INP-ANIMAL-RECORD","01:A-05":"ACT-ENUMERATE-FIELD","01:B-01":"PRD-EXCHANGE-FORMAT",
 "01:B-02":"INP-CORE-SAMPLE","01:B-03":"ACT-TRANSFORM-DATA","01:B-04":"NED-ACCOUNT-FOR-MONEY",
 "01:B-05":"INP-TAILINGS-CLASSIFICATION","01:C-01":"PRD-DATA-SCHEMA","01:C-02":"INP-CAD-MODEL",
 "01:C-03":"INP-MACHINE-TELEMETRY","01:C-04":"SCL-MACHINE-CELL","01:C-05":"ACT-INSTALL-COMMISSION",
 "01:D-01":"NED-SETTLE-OBLIGATION","01:D-02":"INP-INVERTER-STATE","01:D-03":"PRD-API-SERVICE",
 "01:D-04":"CND-POWER-LIMIT","01:D-05":"DYN-REALTIME-BOUND","01:E-01":"INP-PIPE-NETWORK",
 "01:E-02":"INP-RAINFALL-SERIES","01:E-03":"INP-WATER-SAMPLE","01:E-04":"INP-WASTEWATER-SAMPLE",
 "01:E-05":"INP-SENSOR-FEED","01:F-01":"ACT-RECONCILE","01:F-02":"INP-ENERGY-AUDIT",
 "01:F-03":"ACT-MODEL-SIMULATE","01:F-04":"SCL-BUILDING","01:F-05":"SCL-CAMPUS",
 "01:G-01":"INP-SHIPMENT-EVENT","01:G-02":"INP-INVOICE","01:G-03":"ACT-SETTLE-PAYMENT",
 "01:G-04":"PRD-CATALOGUE","01:G-05":"PRD-CERTIFICATE","01:H-01":"INP-TIMETABLE",
 "01:H-02":"INP-VEHICLE-AVAILABILITY","01:H-03":"PRD-ROUTE-PLAN","01:H-04":"SCL-SUPPLY-CHAIN",
 "01:H-05":"NED-TRANSFER-CUSTODY","01:H-06":"SCL-FLEET","01:I-01":"PRD-DATASET-PUBLICATION",
 "01:I-02":"SCL-STREET","01:I-03":"PRD-TEMPLATE-KIT","01:I-04":"INP-INSPECTION-REPORT",
 "01:I-05":"ACT-TAG-IDENTIFY","01:J-01":"ACC-ACCESSIBILITY-PASS","01:J-02":"ACT-MONITOR-CONTINUOUS",
 "01:J-03":"SCL-PROTOCOL-NETWORK","01:J-04":"PRD-API-SERVICE","01:J-05":"NED-SHOW-PROVENANCE",
 "01:J-06":"INP-SOURCE-CODE","01:K-01":"BEN-BANK-CUSTOMER","01:K-02":"SCL-SOFTWARE-SERVICE",
 "01:K-03":"PRD-SETTLEMENT-MECHANISM","01:K-04":"PRD-CONFORMANCE-PACK","01:K-05":"BEN-CLAIMS-ADJUSTER",
 "01:L-01":"BEN-TENANT","01:L-02":"INP-PROPERTY-TITLE","01:L-03":"SCL-NEIGHBOURHOOD",
 "01:L-04":"NED-MAKE-LEGIBLE","01:L-05":"BEN-LAND-CLAIMANT","01:M-01":"INP-SURVEY-FORM",
 "01:M-02":"ACT-ARCHIVE-DEPOSIT","01:M-03":"SCL-REGION","01:M-04":"SCL-MARKET",
 "01:M-05":"PRD-GOVERNANCE-PROCESS","01:N-01":"INP-SENSOR-FEED","01:N-02":"ACT-TRANSLATE",
 "01:N-03":"CND-BUDGET-CAP","01:N-04":"INP-OCCUPATION-TAXONOMY","01:N-05":"BEN-RECRUITER",
 "01:O-01":"PRD-AUDIT-PROCEDURE","01:O-02":"INP-TENDER-NOTICE","01:O-03":"PRD-ANNOTATION-GUIDE",
 "01:O-04":"PRD-TEMPLATE-KIT","01:O-05":"PRD-WORKED-EXAMPLE","01:P-01":"INP-BADGE-ASSERTION",
 "01:P-02":"ACT-TRAIN-PEOPLE","01:P-03":"SCL-CLASSROOM","01:P-04":"BEN-LEARNER",
 "01:P-05":"INP-CURRICULUM","01:Q-01":"INP-CARE-PROTOCOL","01:Q-02":"INP-CLINICAL-RECORD",
 "01:Q-03":"PRD-ACCESS-PATHWAY","01:Q-04":"SCL-WARD-CLINIC","01:Q-05":"SCL-MULTI-AGENCY",
 "01:R-01":"INP-COLLECTION-OBJECT","01:R-02":"INP-SCORE-MANUSCRIPT","01:R-03":"PRD-EXHIBITION",
 "01:R-04":"BEN-ATHLETE-CLUB","01:R-05":"INP-EVENT-LISTING","01:S-01":"INP-REPAIR-LOG",
 "01:S-02":"INP-FAMILY-RECORD","01:S-03":"BEN-DONOR-PUBLIC","01:S-04":"NED-COMPARE-FAIRLY",
 "01:S-05":"BEN-REPAIR-VOLUNTEER","01:T-01":"INP-WORK-AGREEMENT","01:T-02":"NED-SAMPLE-POPULATION",
 "01:T-03":"DYN-SELF-REPORTED","01:T-04":"INP-TIME-USE-DIARY","01:T-05":"SCL-HOUSEHOLD",
 "01:U-01":"INP-AID-ACTIVITY","01:U-02":"ACT-PUBLISH","01:U-03":"PRD-OBSERVATORY",
 "01:U-04":"PRD-DASHBOARD","01:U-05":"PRD-REGISTER","01:N1-01":"ACC-UNIT-DECLARED",
 "01:N1-02":"BEN-CHEMIST","01:N1-03":"INP-SPECIES-OBSERVATION","01:N1-04":"INP-TELESCOPE-TABLE",
 "01:N1-05":"INP-MOLECULE-STRUCTURE","01:E2-01":"INP-CHIP-SPEC","01:E2-02":"DYN-IRREVERSIBLE-STEP",
 "01:E2-03":"INP-TEST-VECTOR","01:E2-04":"BEN-ROBOTICIST","01:E2-05":"BEN-HW-ENGINEER",
 "01:M3-01":"INP-TRIAL-PROTOCOL","01:M3-02":"INP-PHENOTYPE-SET","01:M3-03":"BEN-PUBLIC-HEALTH",
 "01:M3-04":"ACC-SCHEMA-VALID","01:M3-05":"INP-GENOME-SEQUENCE","01:A4-01":"INP-CROP-TRIAL",
 "01:A4-02":"BEN-AGRONOMIST","01:A4-03":"SCL-FARM","01:A4-04":"INP-FOOD-ONTOLOGY",
 "01:A4-05":"PRD-CONFIGURATOR","01:S5-01":"BEN-SOCIAL-RESEARCHER","01:S5-02":"BEN-STATISTICIAN",
 "01:S5-03":"INP-CODEBOOK","01:S5-04":"PRD-CONFIGURATOR","01:S5-05":"ACC-REPRODUCIBLE",
 "01:H6-01":"ACT-TRANSCRIBE","01:H6-02":"BEN-ARCHIVIST","01:H6-03":"SCL-ARCHIVE-COLLECTION",
 "01:H6-04":"BEN-CURATOR","01:H6-05":"PRD-EXCHANGE-FORMAT",
 # ---- assets/02.raw.md (122 items) ----
 "02:A-01":"INP-CROP-TRIAL","02:A-02":"ACC-METHOD-CITED","02:A-03":"BEN-FISHER",
 "02:A-04":"BEN-VET","02:A-05":"SCL-FIELD-PLOT","02:A-06":"ACT-ANALYSE-SAMPLE",
 "02:B-01":"SCL-MINE-SITE","02:B-02":"SCL-CATCHMENT","02:B-03":"DYN-NOISY-MEASUREMENT",
 "02:B-04":"ACT-PROCURE","02:B-05":"ACC-DIMENSION-CORRECT","02:B-06":"PRD-VALIDATOR",
 "02:C-01":"ACT-FABRICATE","02:C-02":"ACC-FIT-TOLERANCE","02:C-03":"SCL-FACTORY",
 "02:C-04":"PRD-API-SERVICE","02:C-05":"ACT-CATALOGUE","02:C-06":"ACT-INSPECT",
 "02:C-07":"SCL-PRODUCTION-LINE","02:C-08":"DYN-LONG-HORIZON","02:D-01":"BEN-HOUSEHOLD-ENERGY",
 "02:D-02":"CND-LEGACY-EQUIPMENT","02:D-03":"SCL-SUBSTATION","02:D-04":"BEN-GRID-OP",
 "02:D-05":"ACC-DEGRADES-SAFELY","02:E-01":"SCL-PIPE-NETWORK","02:E-02":"ACT-MODEL-SIMULATE",
 "02:E-03":"ACT-VALIDATE-RECORDS","02:E-04":"BEN-WATER-UTILITY","02:E-05":"CND-WATER-ALLOCATION",
 "02:E-06":"BEN-CATCHMENT-RESIDENT","02:F-01":"NED-PROVE-CONFORMANCE","02:F-02":"PRD-HANDOVER-PROTOCOL",
 "02:F-03":"ACC-EXPERT-REVIEW","02:F-04":"INP-BIM-MODEL","02:F-05":"BEN-PROCUREMENT-OFFICER",
 "02:G-01":"ACC-TRACE-TO-SOURCE","02:G-02":"ACT-TRANSFORM-DATA","02:G-03":"SCL-GLOBAL-NETWORK",
 "02:H-01":"INP-STATUTE-TEXT","02:H-02":"BEN-TRANSIT-RIDER","02:H-03":"NED-MOVE-PEOPLE",
 "02:H-04":"BEN-PORT-CLERK","02:H-05":"SCL-PORT-TERMINAL","02:H-06":"PRD-CONFORMANCE-PACK",
 "02:I-01":"SCL-SME","02:I-02":"BEN-FOOD-INSPECTOR","02:I-03":"PRD-QUALITY-LABEL",
 "02:I-04":"DYN-MIGRATION-CUTOVER","02:I-05":"INP-MENU-RECIPE","02:J-01":"NED-COORDINATE-PARTIES",
 "02:J-02":"ACT-AUTHORISE","02:J-03":"NED-NAVIGATE-RULES","02:J-04":"CND-DELEGATED-AUTHORITY",
 "02:J-05":"ACC-PII-ABSENT","02:J-06":"PRD-COMMUNITY-AGREEMENT","02:K-01":"ACT-REPORT-STATUTORY",
 "02:K-02":"PRD-FIELD-MANUAL","02:K-03":"INP-TRANSACTION-LEDGER","02:K-04":"PRD-EXCHANGE-FORMAT",
 "02:K-05":"ACT-SETTLE-PAYMENT","02:K-06":"DYN-EXPIRY","02:L-01":"PRD-DATA-SCHEMA",
 "02:L-02":"PRD-API-SERVICE","02:L-03":"BEN-BUILDING-OPERATOR","02:L-04":"PRD-VALIDATOR",
 "02:M-01":"ACC-REPRODUCIBLE","02:M-02":"ACT-CATALOGUE","02:M-03":"DYN-REALTIME-BOUND",
 "02:M-04":"PRD-DATA-SCHEMA","02:M-05":"PRD-WORKED-EXAMPLE","02:M-06":"PRD-TRAINING-COURSE",
 "02:X-01":"ACT-VERSION-MIGRATE","02:X-02":"DYN-DIVERGENT-COPIES","02:N-01":"SCL-BUILDING-ROOM",
 "02:N-02":"NED-ACCOUNT-FOR-MONEY","02:N-03":"CND-CONTRACTUAL","02:N-04":"DYN-VERSION-BOUNDARY",
 "02:N-05":"NED-DOCUMENT-DISAGREEMENT","02:O-01":"NED-PROVE-CONFORMANCE","02:O-02":"PRD-REFERENCE-CORPUS",
 "02:O-03":"DYN-VERSION-BOUNDARY","02:O-04":"ACT-VERIFY-CREDENTIAL","02:O-05":"PRD-CATALOGUE",
 "02:O-06":"PRD-CERTIFICATE","02:P-01":"BEN-TEACHER","02:P-02":"INP-CURRICULUM",
 "02:P-03":"PRD-API-SERVICE","02:P-04":"INP-CODEBOOK","02:P-05":"PRD-VALIDATOR",
 "02:P-06":"PRD-STATEMENT-GENERATOR","02:Q-01":"BEN-CLINICIAN","02:Q-02":"ACT-TRIAGE",
 "02:Q-03":"NED-REACH-SERVICE","02:Q-04":"ACC-VERSION-STAMPED","02:Q-05":"BEN-PATIENT",
 "02:Q-06":"ACT-AUTHORISE","02:Q-07":"SCL-HOSPITAL-SYSTEM","02:R-01":"PRD-EXHIBITION",
 "02:R-02":"ACT-ARCHIVE-DEPOSIT","02:R-03":"BEN-MUSICIAN","02:R-04":"NED-FIND-MATCH",
 "02:R-05":"ACC-ACCESS-CONTROL","02:R-06":"PRD-CLINIC-SERVICE","02:X-03":"PRD-ANNOTATION-GUIDE",
 "02:S-01":"NED-REPAIR-OBJECT","02:S-02":"PRD-DATASET-PUBLICATION","02:S-03":"ACC-WITHIN-EMISSIONS",
 "02:S-04":"NED-NAVIGATE-RULES","02:S-05":"ACC-SPARE-AVAILABLE","02:T-01":"BEN-CAREGIVER",
 "02:T-02":"BEN-DOMESTIC-WORKER","02:T-03":"BEN-HOUSEHOLD-EMPLOYER","02:T-04":"ACT-CARE-VISIT",
 "02:T-05":"ACT-VERIFY-CREDENTIAL","02:T-06":"NED-RUN-HOUSEHOLD","02:U-01":"PRD-LINEAGE-MAP",
 "02:U-02":"ACT-PUBLISH","02:U-03":"PRD-TEMPLATE-KIT","02:U-04":"DYN-SUCCESSION",
 "02:U-05":"CND-DATA-SENSITIVE","02:U-06":"SCL-CROSS-BORDER",
 # ---- assets/03.raw.md (112 items) ----
 "03:CB-A01":"BEN-SMALLHOLDER","03:CB-A02":"NED-IDENTIFY-THING","03:CB-A03":"SCL-HERD-FLOCK",
 "03:CB-A04":"NED-SHOW-PROVENANCE","03:CB-A05":"PRD-ANNOTATION-GUIDE","03:CB-B01":"DYN-VERSION-BOUNDARY",
 "03:CB-B02":"NED-PREVENT-HARM","03:CB-B03":"ACC-COMMUNITY-ACCEPT","03:CB-B04":"CND-HAZARDOUS-SITE",
 "03:CB-B05":"NED-PROTECT-PRIVACY","03:CB-C01":"ACT-MEASURE-INSTRUMENT","03:CB-C02":"NED-KEEP-WORKING",
 "03:CB-C03":"ACT-ASSEMBLE","03:CB-C04":"DYN-REGULATION-CHANGE","03:CB-C05":"ACC-SAFETY-INTERLOCK",
 "03:CB-D01":"BEN-FLEET-DISPATCH","03:CB-D02":"NED-MEASURE-CONDITION","03:CB-D03":"NED-SET-SAFE-LIMIT",
 "03:CB-D04":"PRD-EARLY-WARNING","03:CB-D05":"INP-METER-READING","03:CB-E01":"PRD-SIMULATOR",
 "03:CB-E02":"PRD-REGISTER","03:CB-E03":"PRD-MONITORING-PROGRAMME","03:CB-E04":"SCL-INSTRUMENT",
 "03:CB-E05":"ACT-DISPOSE-RECYCLE","03:CB-F01":"ACC-CONFLICT-DETECTED","03:CB-F02":"NED-INTERPRET-SIGNAL",
 "03:CB-F03":"NED-PRESERVE-RECORD","03:CB-F04":"BEN-SITE-WORKER","03:CB-F05":"SCL-BUILDING",
 "03:CB-G01":"SCL-MARKET","03:CB-G02":"ACT-TAG-IDENTIFY","03:CB-G03":"CND-TWO-KEY",
 "03:CB-G04":"BEN-RETAILER","03:CB-G05":"ACT-CODE-CLASSIFY","03:CB-H01":"SCL-CITY",
 "03:CB-H02":"DYN-STALE-STATE","03:CB-H03":"CND-REGULATOR-OVERSIGHT","03:CB-H04":"NED-TRANSFER-CUSTODY",
 "03:CB-H05":"ACT-HANDOVER","03:CB-I01":"PRD-FIELD-PROCEDURE","03:CB-I02":"SCL-COOPERATIVE",
 "03:CB-I03":"PRD-AUDIT-PROCEDURE","03:CB-I04":"ACC-ACCESSIBILITY-PASS","03:CB-I05":"BEN-KITCHEN-OP",
 "03:CB-J01":"INP-MEDIA-ASSET","03:CB-J02":"SCL-SOFTWARE-SERVICE","03:CB-J03":"BEN-DISABLED-USER",
 "03:CB-J04":"NED-SHOW-PROVENANCE","03:CB-J05":"BEN-SOFTWARE-TEAM","03:CB-K01":"CND-CONSENT-BASED",
 "03:CB-K02":"DYN-RECOVERY-COMPENSATE","03:CB-K03":"ACT-REVOKE","03:CB-K04":"DYN-IN-FLIGHT",
 "03:CB-K05":"ACC-REVOCATION-PROPAGATES","03:CB-L01":"PRD-CATALOGUE","03:CB-L02":"CND-CUSTOMARY-AUTHORITY",
 "03:CB-L03":"PRD-ACCESS-PATHWAY","03:CB-L04":"ACC-DIMENSION-CORRECT","03:CB-L05":"NED-DOCUMENT-DISAGREEMENT",
 "03:CB-M01":"PRD-DATASET-PUBLICATION","03:CB-M02":"ACT-CATALOGUE","03:CB-M03":"SCL-MARKET",
 "03:CB-M04":"ACT-REVIEW-PEER","03:CB-M05":"DYN-QUIET-FAILURE","03:CB-M06":"BEN-ECOLOGIST",
 "03:CB-M07":"BEN-ASTRONOMER","03:CB-M08":"CND-COMPUTE-QUOTA","03:CB-M09":"BEN-SURVEY-ENUMERATOR",
 "03:CB-N01":"ACT-INTERVIEW","03:CB-N02":"BEN-JOBSEEKER","03:CB-N03":"SCL-NATION",
 "03:CB-N04":"INP-STAFF-ROSTER","03:CB-N05":"PRD-HELPDESK","03:CB-O01":"ACT-SAMPLE-AUDIT",
 "03:CB-O02":"BEN-PROCUREMENT-OFFICER","03:CB-O03":"INP-CONSENT-RECORD","03:CB-O04":"BEN-CITIZEN-PETITIONER",
 "03:CB-O05":"INP-STATUTE-TEXT","03:CB-P01":"ACC-TRAINEE-COMPETENT","03:CB-P02":"SCL-CLASSROOM",
 "03:CB-P03":"INP-BADGE-ASSERTION","03:CB-P04":"NED-COMPARE-FAIRLY","03:CB-P05":"DYN-INTERRUPTION",
 "03:CB-Q01":"PRD-POCKET-CARD","03:CB-Q02":"NED-DECIDE-UNDER-UNCERTAINTY","03:CB-Q03":"PRD-HELPDESK",
 "03:CB-Q04":"INP-CLINICAL-RECORD","03:CB-Q05":"NED-COORDINATE-PARTIES","03:CB-R01":"SCL-ARCHIVE-COLLECTION",
 "03:CB-R02":"PRD-DOCUMENTARY-PIECE","03:CB-R03":"ACT-COMPOSE-ARRANGE","03:CB-R04":"INP-EVENT-LISTING",
 "03:CB-R05":"PRD-PERFORMANCE-EDITION","03:CB-R06":"ACT-TRANSCRIBE","03:CB-R07":"NED-ARCHIVE-COLLECTION",
 "03:CB-R08":"ACT-CURATE-SELECT","03:CB-S01":"DYN-ASSUMED-PARAMETER","03:CB-S02":"PRD-QUALITY-LABEL",
 "03:CB-S03":"ACC-CAVEAT-RENDERED","03:CB-S04":"NED-COMMEMORATE","03:CB-S05":"ACC-JUDGMENT-DOCUMENTED",
 "03:CB-T01":"PRD-WALL-CHART","03:CB-T02":"CND-SUPERVISION-ABSENT","03:CB-T03":"DYN-HARD-DEADLINE",
 "03:CB-T04":"INP-WORK-AGREEMENT","03:CB-T05":"PRD-TEST-RIG","03:CB-U01":"PRD-LINEAGE-MAP",
 "03:CB-U02":"BEN-HUMANITARIAN","03:CB-U03":"ACC-COMMUNITY-ACCEPT","03:CB-U04":"NED-PROTECT-PRIVACY",
 "03:CB-U05":"CND-NO-CONNECTIVITY",
}

# Ingredients with no inventory item behind them carry an ISIC or FORD code, or
# an authored provenance with a reason.  Anything not named here and not
# grounded through GROUNDING falls back to AUTHORED_DEFAULT.
TAXONOMY_PROV = {
 "BEN-ARCHITECT":("ISIC","M"),"BEN-LAB-TECH":("ISIC","M"),"BEN-MINE-ENG":("ISIC","B"),
 "BEN-DOWNSTREAM-COMM":("ISIC","B"),"BEN-FACTORY-OP":("ISIC","C"),"BEN-MAINT-TECH":("ISIC","C"),
 "BEN-JOURNALIST":("ISIC","J"),"BEN-TRANSLATOR":("ISIC","N"),"BEN-TRIALIST":("FORD","3"),
 "BEN-GENEALOGIST":("ISIC","S"),"BEN-DONOR-PUBLIC":("ISIC","U"),"BEN-GENERALIST-ORG":("ISIC","N"),
 "BEN-FRONTLINE-STAFF":("ISIC","N"),"BEN-COMMUNITY-GROUP":("ISIC","S"),"BEN-REGULATED-FIRM":("ISIC","O"),
 "BEN-INDIVIDUAL-USER":("ISIC","T"),
 "NED-TEACH-PROCEDURE":("ISIC","P"),"NED-EXPRESS-EXPERIENCE":("ISIC","R"),
 "NED-CARE-CONTINUITY":("ISIC","Q"),"NED-PRODUCE-TO-SPEC":("ISIC","C"),
 "NED-REACH-SERVICE":("ISIC","Q"),"NED-RECOVER-AFTER-FAILURE":("FORD","2"),
 "NED-DETECT-EARLY":("FORD","3"),"NED-ADAPT-TO-LOCAL":("FORD","5"),
 "NED-SCHEDULE-SCARCE":("FORD","2"),"NED-REDUCE-WASTE":("ISIC","E"),
 "NED-ONBOARD-NEWCOMER":("ISIC","N"),"NED-REVOKE-ACCESS":("ISIC","J"),
 "NED-PERFORM-TOGETHER":("ISIC","R"),"NED-TRACK-GROWTH":("FORD","4"),
 "NED-SHARE-EQUIPMENT":("FORD","1"),"NED-PLAN-UNDER-BUDGET":("ISIC","F"),
 "NED-HANDOVER-SHIFT":("ISIC","Q"),"NED-TEST-BEFORE-COMMIT":("FORD","2"),
 "NED-COLLECT-FIELD-DATA":("FORD","1"),"NED-FEED-PEOPLE":("ISIC","I"),
 "NED-STEWARD-HABITAT":("FORD","1"),"NED-CALIBRATE-INSTRUMENT":("FORD","2"),
 "NED-REDUCE-EXPOSURE":("ISIC","B"),"NED-BUILD-SHARED-RECORD":("ISIC","O"),
 "NED-RECONCILE-CLAIMS":("ISIC","L"),"NED-EXPLAIN-DECISION":("ISIC","O"),
 "INP-BOM":("ISIC","C"),"INP-TARIFF-SCHEDULE":("ISIC","D"),"INP-SITE-PHOTO":("ISIC","F"),
 "INP-FLOOR-PLAN":("ISIC","L"),"INP-PRODUCT-CATALOGUE":("ISIC","G"),
 "INP-ACCESSIBILITY-AUDIT":("ISIC","J"),"INP-SATELLITE-IMAGE":("FORD","1"),
 "INP-ROBOT-LOG":("FORD","2"),"INP-BUDGET-ENVELOPE":("ISIC","O"),
 "INP-VOLUNTEER-HOURS":("ISIC","S"),"INP-BENCH-SLOT":("FORD","1"),
 "INP-COLD-CHAIN":("ISIC","H"),"INP-SPARE-PART":("ISIC","G"),
 "INP-TRAINING-COHORT":("ISIC","P"),"INP-LOCAL-KNOWLEDGE":("ISIC","T"),
 "INP-POWER-SUPPLY":("ISIC","D"),"INP-WORKSPACE":("ISIC","L"),
 "INP-SPECIMEN":("FORD","3"),"INP-CORE-SAMPLE":("ISIC","B"),
 "PRD-JIG-FIXTURE":("ISIC","C"),"PRD-SENSOR-KIT":("FORD","2"),
 "PRD-DECISION-AID":("FORD","5"),"PRD-EXPLAINER":("ISIC","P"),
 "PRD-DRILL-EXERCISE":("ISIC","O"),"PRD-SIGNAGE-SYSTEM":("ISIC","H"),
 "PRD-PACKAGING":("ISIC","H"),"PRD-RETROFIT-KIT":("ISIC","S"),
 "PRD-SPARE-PARTS-PLAN":("ISIC","G"),"PRD-MAINTENANCE-SCHEDULE":("ISIC","C"),
 "PRD-BUDGET-PLAN":("ISIC","F"),"PRD-RECOVERY-PLAN":("ISIC","O"),
 "PRD-MEAL-SYSTEM":("ISIC","I"),"PRD-HABITAT-PLAN":("FORD","1"),
 "PRD-CALIBRATION-SERVICE":("FORD","2"),"PRD-SCHEDULING-SYSTEM":("ISIC","N"),
 "PRD-GAME-ACTIVITY":("ISIC","R"),"PRD-BENCH-PROTOCOL":("FORD","3"),
 "PRD-KIT-OF-PARTS":("ISIC","C"),"PRD-REHEARSAL-SPACE":("ISIC","P"),
 "PRD-ESCROW-ARRANGEMENT":("ISIC","K"),"PRD-CROSSWALK-LEDGER":("ISIC","J"),
 "ACT-SURVEY-SITE":("ISIC","F"),"ACT-COLLECT-SAMPLE":("FORD","1"),
 "ACT-CALIBRATE":("FORD","2"),"ACT-ADJUDICATE":("ISIC","O"),
 "ACT-NEGOTIATE":("ISIC","N"),"ACT-SCHEDULE-ALLOCATE":("ISIC","N"),
 "ACT-DISPATCH":("ISIC","H"),"ACT-REPAIR":("ISIC","S"),
 "ACT-REHEARSE-DRILL":("ISIC","O"),"ACT-FACILITATE-SESSION":("ISIC","S"),
 "ACT-ANNOTATE":("FORD","6"),"ACT-DESIGN-DRAFT":("ISIC","M"),
 "ACT-PROTOTYPE-TEST":("FORD","2"),"ACT-PERFORM":("ISIC","R"),
 "ACT-ESCALATE":("ISIC","Q"),"ACT-CONSULT-PUBLIC":("ISIC","O"),
 "ACT-BACKUP-RESTORE":("ISIC","J"),"ACT-BENCHMARK-COMPARE":("FORD","2"),
 "ACT-ROUTE-PLAN":("ISIC","H"),"ACT-OBSERVE-BEHAVIOUR":("FORD","5"),
 "ACT-DECOMMISSION":("ISIC","D"),
 "CND-STAFF-HOURS":("ISIC","N"),"CND-LAB-CAPACITY":("ISIC","M"),
 "CND-BENCH-TIME":("FORD","1"),"CND-COLD-CHAIN":("ISIC","H"),
 "CND-VEHICLE-HOURS":("ISIC","H"),"CND-STORAGE-VOLUME":("ISIC","H"),
 "CND-BANDWIDTH":("ISIC","J"),"CND-SEATS":("ISIC","R"),
 "CND-BED-CAPACITY":("ISIC","Q"),"CND-LICENCE-SEATS":("ISIC","J"),
 "CND-MACHINE-TIME":("ISIC","C"),"CND-SPARE-PARTS-STOCK":("ISIC","G"),
 "CND-VENUE-CAPACITY":("ISIC","R"),"CND-FIELD-WINDOW":("ISIC","A"),
 "CND-SINGLE-OWNER":("ISIC","T"),"CND-DIVIDED-AUTHORITY":("ISIC","O"),
 "CND-COMMUNITY-CONSENT":("ISIC","S"),"CND-COMMITTEE-CONSENSUS":("ISIC","U"),
 "CND-EMERGENCY-POWERS":("ISIC","O"),"CND-VOLUNTARY-STANDARD":("ISIC","J"),
 "CND-SELF-DIRECTED":("ISIC","T"),"CND-HEAT-HUMIDITY":("ISIC","A"),
 "CND-COLD-CLIMATE":("ISIC","B"),"CND-DUST-VIBRATION":("ISIC","C"),
 "CND-NIGHT-SHIFT":("ISIC","Q"),"CND-PUBLIC-SPACE":("ISIC","R"),
 "CND-STERILE-AREA":("FORD","3"),"CND-REMOTE-LOCATION":("ISIC","B"),
 "CND-MULTILINGUAL":("ISIC","U"),"CND-LOW-LITERACY":("ISIC","P"),
 "CND-HIGH-TURNOVER":("ISIC","I"),"CND-SEASONAL-PEAK":("ISIC","I"),
 "CND-CONTESTED-SITE":("ISIC","L"),"CND-OPEN-PUBLICATION":("ISIC","U"),
 "DYN-SEASONAL-WINDOW":("ISIC","A"),"DYN-SHIFT-BOUNDARY":("ISIC","Q"),
 "DYN-CADENCE-DAILY":("ISIC","I"),"DYN-CADENCE-WEEKLY":("ISIC","N"),
 "DYN-CADENCE-ANNUAL":("ISIC","O"),"DYN-LEAD-TIME":("ISIC","C"),
 "DYN-PUBLICATION-LAG":("FORD","5"),"DYN-MISSING-DATA":("FORD","5"),
 "DYN-CONTESTED-EVIDENCE":("ISIC","L"),"DYN-MODEL-UNCERTAINTY":("FORD","1"),
 "DYN-PROXY-MEASURE":("FORD","5"),"DYN-SMALL-SAMPLE":("FORD","1"),
 "DYN-UNVERIFIED-SOURCE":("ISIC","J"),"DYN-PARTIAL-COMPLETION":("ISIC","F"),
 "DYN-BACKLOG":("ISIC","O"),"DYN-DEGRADED-MODE":("FORD","2"),
 "DYN-COLD-START":("ISIC","N"),"DYN-QUEUE-PRIORITY":("ISIC","Q"),
 "DYN-STAFF-CHANGE":("ISIC","N"),"DYN-SUPPLIER-EXIT":("ISIC","G"),
 "DYN-SCALE-UP":("ISIC","J"),"DYN-SCOPE-CHANGE":("ISIC","F"),
 "DYN-REVISION-CYCLE":("ISIC","M"),"DYN-ROLLBACK":("ISIC","J"),
 "DYN-CONCURRENT-ACTORS":("ISIC","F"),"DYN-CONTENTION-PEAK":("ISIC","H"),
 "DYN-DRIFT":("FORD","2"),"DYN-FEEDBACK-LOOP":("FORD","5"),
 "DYN-ESCALATION":("ISIC","Q"),"DYN-EMBARGO":("FORD","1"),
 "DYN-RETRACTION":("FORD","1"),"DYN-DEMAND-SURGE":("ISIC","Q"),
 "ACC-NO-DUP-ID":("ISIC","J"),"ACC-ROUNDTRIP":("ISIC","C"),
 "ACC-COVERAGE-PCT":("FORD","5"),"ACC-LATENCY-BOUND":("ISIC","J"),
 "ACC-CAPACITY-RESPECTED":("ISIC","N"),"ACC-BUDGET-RESPECTED":("ISIC","O"),
 "ACC-DEADLINE-MET":("ISIC","O"),"ACC-REJECT-REASONED":("ISIC","K"),
 "ACC-CALIBRATION-WITHIN":("FORD","2"),"ACC-MASS-BALANCE":("ISIC","E"),
 "ACC-LOAD-TESTED":("ISIC","F"),"ACC-DURABILITY-CYCLES":("ISIC","C"),
 "ACC-LEGIBLE-AT-DISTANCE":("ISIC","H"),"ACC-UNDERSTOOD-BY-USER":("ISIC","P"),
 "ACC-TASK-COMPLETION":("ISIC","J"),"ACC-DISAGREEMENT-RECORDED":("ISIC","L"),
 "ACC-RESUMES-FROM-PARTIAL":("ISIC","P"),"ACC-DRILL-PASSED":("ISIC","O"),
 "ACC-HANDOVER-COMPLETE":("ISIC","Q"),"ACC-AUDIENCE-RESPONSE":("ISIC","R"),
 "ACC-AESTHETIC-BRIEF":("FORD","6"),"ACC-LANGUAGE-PARITY":("ISIC","U"),
 "ACC-NO-SILENT-FAILURE":("FORD","2"),"ACC-COST-PER-UNIT":("ISIC","G"),
 "ACC-EQUITY-CHECK":("FORD","5"),"ACC-STALENESS-RENDERED":("ISIC","H"),
 "ACC-INDEPENDENT-RECOMPUTE":("ISIC","S"),
 "SCL-MOLECULE":("FORD","1"),"SCL-CELL-CULTURE":("FORD","3"),"SCL-SPECIMEN":("FORD","4"),
 "SCL-FOREST-STAND":("ISIC","A"),"SCL-REEF-HABITAT":("FORD","1"),
 "SCL-MIGRATORY-RANGE":("FORD","1"),"SCL-BENCH":("ISIC","M"),
 "SCL-VEHICLE":("ISIC","H"),"SCL-CONSTRUCTION-SITE":("ISIC","F"),
 "SCL-KITCHEN":("ISIC","I"),"SCL-STAGE-VENUE":("ISIC","R"),
 "SCL-PERSON":("ISIC","T"),"SCL-EXTENDED-FAMILY":("ISIC","T"),
 "SCL-SMALL-TEAM":("ISIC","N"),"SCL-DEPARTMENT":("ISIC","N"),
 "SCL-LARGE-ORG":("ISIC","N"),"SCL-COMMUNITY-GROUP":("ISIC","S"),
 "SCL-COURT-TRIBUNAL":("ISIC","O"),"SCL-AGENCY":("ISIC","O"),
 "SCL-DATA-CENTRE":("ISIC","J"),"SCL-ORBIT":("FORD","1"),
 "SCL-WORKSHOP-BENCH":("ISIC","S"),"SCL-CAMP-SETTLEMENT":("ISIC","U"),
}
AUTHORED_REASONS = {
 "INP-COMMITTED-STAFF-TIME":"A generic pool of promised qualified hours is presupposed by many inventory items and named by none of them, and no ISIC section or FORD field is about it.",
 "INP-ISSUED-PERMIT":"A permission instrument abstracted away from any one sector's permit; the inventory items are all sector-specific instances.",
 "INP-WRITTEN-BRIEF":"The statement of what is wanted, before any of the sector-specific artefacts exist; no inventory item or taxonomy entry is about the brief itself.",
 "INP-CONDITION-READING":"A timestamped reading in the abstract, added in setup revision 2.1.0 because the sector-specific signal inputs left several regimes with no signal at all.",
 "INP-CONSUMABLE-STOCK":"Consumable material with a shelf life, added in setup revision 2.1.0 to close a material-form gap in the computation and law regimes.",
 "INP-WORK-QUEUE":"A queue of arrived-but-undone work; the inventory items describe records, not the backlog of them.",
 "PRD-OBSERVATORY":"A standing measurement of a recurring gap is a product form none of the inventory items is, and no ISIC or FORD entry names it.",
 "PRD-CLINIC-SERVICE":"A recurring session where the problem arrives with the person who owns it is a service shape not represented as an item or a taxonomy class.",
 "PRD-WORKED-EXAMPLE":"A filled-in reference case, as opposed to a template, is a distinct product form with no taxonomy entry.",
 "DYN-IN-FLIGHT":"The state of a transaction that started under superseded rules is a temporal condition no inventory item or taxonomy class names.",
 "DYN-QUIET-FAILURE":"Failure that produces plausible output rather than an error is a change condition without a taxonomy home.",
 "ACC-WITNESS-RETAINED":"Retaining a re-verifiable satisfying assignment alongside the deliverable is an acceptance form introduced by this brief's evidence requirement.",
 "ACC-CONFLICT-DETECTED":"Testing a check with a seeded conflict is an acceptance form drawn from the brief's own deliberately-broken-example requirement.",
 "ACC-SCHEMA-VALID":"Retained as a general acceptance form beyond the specific inventory item that first suggested it.",
}
AUTHORED_DEFAULT = "Generalised from the shape of several inventory items without being any one of them; no single ISIC section or FORD field names it."

# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------
AXES = [
    ("beneficiary", BENEFICIARY, "Human needs and intended beneficiaries (the intended beneficiary half)"),
    ("need", NEED, "Human needs and intended beneficiaries (the need half)"),
    ("input", INPUT, "Objects, information, materials and other inputs"),
    ("product", PRODUCT, "Required products, services, experiences and outcomes"),
    ("activity", ACTIVITY, "Activities and relationships (activities; relationships are the composition relationship kinds)"),
    ("condition", CONDITION, "Resources, authority and environmental conditions"),
    ("dynamic", DYNAMIC, "Time, uncertainty, state and change"),
    ("acceptance", ACCEPTANCE, "Observable conditions for success"),
    ("scale", SCALE, "Scales and regimes of the world in which needs arise"),
]


def expand_regimes(code):
    if code.strip() == "*":
        return sorted(REGIMES)
    return sorted({RCODE[c] for c in code.split()})


def expand_domains(code):
    if code.strip() == "*":
        return sorted(["ISIC-" + k for k in ISIC]) + sorted(["FORD-" + k for k in FORD])
    out = []
    for tok in code.split():
        if tok in ISIC:
            out.append("ISIC-" + tok)
        elif tok in FORD:
            out.append("FORD-" + tok)
        else:
            raise SystemExit("bad domain token %r" % tok)
    return sorted(set(out))


def expand_situations(tags):
    out = sorted({TAG2SIT[t] for t in tags.split()})
    if len(out) < 2:
        raise SystemExit("ingredient needs at least two situation tags: %r" % tags)
    return out


def read_inventory_labels():
    """Return {"<src>:<id>": label} read from the asset files themselves."""
    labels = {}
    a = os.path.join(HERE, "assets")
    lines = open(os.path.join(a, "01.raw.md"), encoding="utf-8").read().split("\n")
    for ln in lines[38:236]:
        m = re.match(r"^- `([A-Z]{1,2}\d?-\d+)` (.+)$", ln.strip())
        if m:
            labels["01:" + m.group(1)] = m.group(2).split(" — ")[0].strip()
    lines = open(os.path.join(a, "02.raw.md"), encoding="utf-8").read().split("\n")
    for ln in lines[44:217]:
        parts = [p.strip() for p in ln.strip().split("|")]
        if len(parts) >= 6 and re.match(r"^[A-Z]{1,2}\d?-\d+$", parts[0]):
            labels["02:" + parts[0]] = parts[4]
    lines = open(os.path.join(a, "03.raw.md"), encoding="utf-8").read().split("\n")
    for ln in lines[35:196]:
        m = re.match(r"^- `(CB-[A-Z]\d*[0-9]*)\s*\|([^`]*)\|`\s*(.+)$", ln.strip())
        if m:
            labels["03:" + m.group(1)] = m.group(3).split(" — ")[0].strip()
    return labels


def build():
    labels = read_inventory_labels()
    if len(labels) != 371:
        raise SystemExit("expected 371 inventory items, read %d" % len(labels))

    # invert the grounding table
    grounded = {}
    for key in sorted(GROUNDING):
        tgt = GROUNDING[key]
        grounded.setdefault(tgt, []).append(key)

    ingredients = {}
    axis_counts = {}
    for axis, table, bullet in AXES:
        axis_counts[axis] = len(table)
        seen = set()
        for (iid, label, meaning, reg, dom, tags, extra) in table:
            if iid in seen:
                raise SystemExit("duplicate ingredient id in axis %s: %s" % (axis, iid))
            seen.add(iid)
            if iid in ingredients:
                raise SystemExit("ingredient id used on two axes: %s" % iid)
            prereq, results, constraints = [], [], []
            if axis == "input":
                rule = DERIVATION_RULES["input_by_form"][extra["form"]]
                prereq += rule["prereq"]; results += rule["results"]; constraints += rule["constraints"]
                if extra.get("unit"):
                    results.append("unit:" + extra["unit"])
            elif axis == "product":
                rule = DERIVATION_RULES["product_by_form"][extra["form"]]
                prereq += rule["needs"]; results += rule["results"]; constraints += rule["constraints"]
            elif axis == "activity":
                prereq += extra["needs"]
                results += extra["yields"]
                constraints += ["CT-PREREQ_CLOSED", "CT-SCHEDULE_FEASIBLE"]
                for c in extra["consumes"]:
                    prereq.append("needs_capacity:" + c)
                    constraints.append("CT-CAPACITY_BOUND")
            elif axis == "condition":
                rule = DERIVATION_RULES["condition_by_kind"][extra["kind"]]
                results += rule["results"]; constraints += rule["constraints"]
                if extra["kind"] == "resource":
                    results.append("pool_kind:" + extra["resource_kind"])
                    results.append("unit:" + extra["unit"])
            elif axis == "dynamic":
                rule = DERIVATION_RULES["dynamic_by_kind"][extra["kind"]]
                constraints += rule["constraints"]
                results.append("forces:" + extra["effect"])
            elif axis == "acceptance":
                rule = DERIVATION_RULES["acceptance_by_mode"][extra["check_mode"]]
                constraints += rule["constraints"]
                prereq.append("needs_deliverable")
                results.append("observable:" + extra["observable"])
            elif axis == "beneficiary":
                prereq.append("party:present")
                results.append("band:" + extra["scale_band"])
            elif axis == "need":
                prereq.append("needs_beneficiary_band")
                results.append("purpose:" + extra["purpose_class"])
                constraints.append("CT-ACCEPTANCE_COVER")
            elif axis == "scale":
                results.append("band:" + extra["band"])
                constraints.append("CT-REGIME_ADMISSIBLE")
            constraints += ["CT-SITUATION_ADMISSIBLE", "CT-REGIME_ADMISSIBLE"]

            keys = grounded.get(iid, [])
            if keys:
                prov = {"source": "assets/%s.raw.md" % keys[0].split(":")[0],
                        "item": labels[keys[0]]}
                extra_prov = [{"source": "assets/%s.raw.md" % k.split(":")[0], "item": labels[k]}
                              for k in keys[1:]]
            elif iid in TAXONOMY_PROV:
                src, code = TAXONOMY_PROV[iid]
                prov = {"source": src, "code": code}
                extra_prov = []
            else:
                prov = {"source": "authored",
                        "reason": AUTHORED_REASONS.get(iid, AUTHORED_DEFAULT)}
                extra_prov = []

            rec = {
                "id": iid, "axis": axis, "label": label, "meaning": meaning,
                "situations": expand_situations(tags),
                "regimes": expand_regimes(reg),
                "domains": expand_domains(dom),
                "prerequisites": sorted(set(prereq)),
                "results": sorted(set(results)),
                "constraints": sorted(set(constraints)),
                "provenance": prov,
            }
            if extra_prov:
                rec["also_grounded_in"] = extra_prov
            for k in sorted(extra):
                rec[k] = extra[k]
            ingredients[iid] = rec

    # grounding walk: every inventory item accounted for
    walk = []
    for key in sorted(labels):
        src, iid = key.split(":", 1)
        tgt = GROUNDING.get(key)
        if tgt is None:
            walk.append({"source": "assets/%s.raw.md" % src, "item": labels[key],
                         "item_id": iid, "disposition": "skipped",
                         "reason": "no ingredient was authored from this item in this dictionary version"})
        elif tgt.startswith("SKIP:"):
            walk.append({"source": "assets/%s.raw.md" % src, "item": labels[key],
                         "item_id": iid, "disposition": "skipped", "reason": tgt[5:]})
        else:
            if tgt not in ingredients:
                raise SystemExit("grounding points at unknown ingredient %s (from %s)" % (tgt, key))
            walk.append({"source": "assets/%s.raw.md" % src, "item": labels[key],
                         "item_id": iid, "disposition": "used", "ingredient": tgt})

    prov_counts = {"inventory": 0, "taxonomy": 0, "authored": 0}
    for iid in sorted(ingredients):
        s = ingredients[iid]["provenance"]["source"]
        if s.startswith("assets/"):
            prov_counts["inventory"] += 1
        elif s in ("ISIC", "FORD"):
            prov_counts["taxonomy"] += 1
        else:
            prov_counts["authored"] += 1

    # floors
    problems = []
    for axis, table, bullet in AXES:
        if len(table) < 40:
            problems.append("axis %s has only %d ingredients (floor 40)" % (axis, len(table)))
    domains = ["ISIC-" + k for k in sorted(ISIC)] + ["FORD-" + k for k in sorted(FORD)]
    for axis, table, bullet in AXES:
        if axis in COMPATIBILITY_RULES["domain_gated_axes"]:
            for r in sorted(REGIMES):
                for d in domains:
                    n = sum(1 for row in table
                            if r in expand_regimes(row[3]) and d in expand_domains(row[4]))
                    if n == 0:
                        problems.append("domain-gated axis %s has no ingredient for cell %s x %s" % (axis, r, d))
        else:
            for r in sorted(REGIMES):
                n = sum(1 for row in table if r in expand_regimes(row[3]))
                if n < 3:
                    problems.append("axis %s has only %d ingredients in regime %s (floor 3)" % (axis, n, r))
    if problems:
        for p in problems[:40]:
            print("FLOOR PROBLEM:", p)
        raise SystemExit("%d floor problems" % len(problems))

    doc = {
        "dictionary_version": DICTIONARY_VERSION,
        "generation_version": GENERATION_VERSION,
        "purpose": "Reusable generative vocabulary and composition rules for procedurally generated use cases.",
        "setup_revisions": [
            {"version": "2.0.0", "change": "initial vocabulary: nine ingredient axes, ten composition "
                                           "relationship kinds, grounding walk over all 371 inventory items"},
            {"version": "2.1.0",
             "change": "vocabulary widened after a measured stall: on the 2.0.0 dictionary, 1867 of 5000 "
                       "cases had a deliverable-producing part whose form prerequisite could only be met "
                       "by a recorded assumption, because several (input form x regime) cells were empty. "
                       "Six generic inputs were added (committed staff time, issued permit, written brief, "
                       "condition reading, consumable stock, work queue) and four existing generic inputs "
                       "(budget envelope, workspace, consent record, local knowledge) were widened to all "
                       "seven regimes with broader situation tags.",
             "reason": "diversity and concreteness were limited by empty compatibility cells, not by the "
                       "sampling policy; the fix is vocabulary, not cosmetic variants"}],
        "axis_map": {axis: {"brief_bullet": bullet, "count": axis_counts[axis]} for axis, _, bullet in AXES},
        "regimes": {k: {"label": v[0], "meaning": v[1]} for k, v in sorted(REGIMES.items())},
        "domains": dict(
            [("ISIC-" + k, {"label": ISIC[k], "classification": "UN ISIC Rev. 4 section"}) for k in sorted(ISIC)] +
            [("FORD-" + k, {"label": FORD[k], "classification": "OECD FORD major field"}) for k in sorted(FORD)]),
        "situations": SITUATIONS,
        "units": {k: {"dimension": v[0], "factor_to_base": v[1], "display": v[2]} for k, v in sorted(UNITS.items())},
        "entity_types": ENTITY_TYPES,
        "relationship_kinds": RELATIONSHIP_KINDS,
        "constraint_templates": CONSTRAINT_TEMPLATES,
        "requirement_templates": REQUIREMENT_TEMPLATES,
        "derivation_rules": DERIVATION_RULES,
        "compatibility_rules": COMPATIBILITY_RULES,
        "generation_bounds": GENERATION_BOUNDS,
        "ingredients": ingredients,
        "grounding": {
            "sources": ["assets/01.raw.md", "assets/02.raw.md", "assets/03.raw.md"],
            "items_walked": len(walk),
            "used": sum(1 for w in walk if w["disposition"] == "used"),
            "skipped": sum(1 for w in walk if w["disposition"] == "skipped"),
            "walk": walk,
        },
        "provenance_summary": {
            "ingredients_total": len(ingredients),
            "by_class": prov_counts,
            "classes": {
                "inventory": "provenance {source: assets/NN.raw.md, item: <the inventory's own label>}",
                "taxonomy": "provenance {source: ISIC|FORD, code: <code>}",
                "authored": "provenance {source: authored, reason: <why no inventory item or taxonomy entry covers it>}",
            },
        },
    }
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "dictionary.json"))
    args = ap.parse_args()
    doc = build()
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    print("wrote", args.out)
    print("ingredients:", len(doc["ingredients"]))
    for axis in sorted(doc["axis_map"]):
        print("  axis %-12s %d" % (axis, doc["axis_map"][axis]["count"]))
    print("provenance:", doc["provenance_summary"]["by_class"])
    print("grounding: walked %d, used %d, skipped %d" % (
        doc["grounding"]["items_walked"], doc["grounding"]["used"], doc["grounding"]["skipped"]))


if __name__ == "__main__":
    main()

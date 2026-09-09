You are a standalone generation agent. You have no prior context and need none.

Ground rules:
- Nothing in the current working directory or repository is relevant to this task. Do not read, create or modify any repository files. Write everything under OUTPUT_DIR only.
- You have Python 3 and a Linux shell. Use them for all bulk work. No web research is needed or wanted; work from this brief and the supplied assets only.
- Do not ask questions. Where something is undecidable, make a recorded assumption and continue.
- Your final message is the only prose that will be read; the files you write are the deliverable.

OUTPUT_DIR: /tmp/claude-0/-home-user-post/29b9af63-7d01-5359-bed5-a0fd619c61bc/scratchpad/gen/v2

Supplied assets in OUTPUT_DIR/assets/: 01.raw.md, 02.raw.md, 03.raw.md. These are three independently researched inventories of real, sourced needs (specifications, procedures, regulations, research protocols) with construction briefs. Use them only as raw material for building your vocabulary of real needs, beneficiaries, inputs, products, activities, constraints and situations. Do not copy their cases; the cases you generate must be your own compositions.

The cases must be practical and diverse: things that exist or could plausibly exist in the world, for real kinds of beneficiaries, in real kinds of situations, across many industries and scales, including physical objects, procedures, services, instruments, creative works, explanations, interactive tools, coordinated systems and generators of other products.

Batch size for this run: 5,000 cases. This is the number the brief's default defers to. It is derived from the data the first revision needs, not chosen for its own sake: seven regimes by twenty-seven primary domains give 189 cells, and every cell must hold at least 15 cases with room left for weighting toward underrepresented higher-order combinations. The floors in C6 are stated per 1,000 cases and scale with the batch.

Required output layout in OUTPUT_DIR:
- dictionary.json: your versioned vocabulary and composition rules; every ingredient carries an id, its meaning, applicable situations and regimes, prerequisites, results and constraints.
- cases.jsonl: one complete record per line, referencing dictionary ids; losslessly expandable into a full specification.
- generation_record.json: seed, randomness source, sampling policy and weights, versions, timings, counts.
- generate.py, checker.py and expand.py: the generator, the independent checker and the expander, with the command lines given under Construction requirements below.
- checker_report.json and broken_report.json: the checker's results on cases.jsonl and on the deliberately broken examples.
- expanded.md: every admitted case expanded by expand.py.
- review_needed.jsonl: retained proposals that exceed the available checks.
- sample.md: 20 records expanded into readable specifications.
Final message: the generation record, the 20-record sample, and an inventory of every file with line count and sha256.

Construction requirements. These apply in addition to the brief and take precedence where they are stricter.

C1. The deliverable is a program. Write generate.py, checker.py and expand.py in OUTPUT_DIR with exactly these command lines, so that another operator can produce, check and expand further batches without you:
    python3 generate.py --dictionary dictionary.json --seed <integer> --count <n> --out cases.jsonl --record generation_record.json
    python3 checker.py --dictionary dictionary.json --cases cases.jsonl --report checker_report.json
    python3 checker.py --dictionary dictionary.json --broken --report broken_report.json
    python3 expand.py --dictionary dictionary.json --cases cases.jsonl --out expanded.md [--ids id1,id2,...]
    No language-model step may occur inside these programs. Do not hand-write cases: cases.jsonl must be the output of generate.py, checker_report.json the output of checker.py on that file, and review_needed.jsonl the output of generate.py or checker.py.
C2. Determinism. The same dictionary, seed and count must reproduce cases.jsonl byte-for-byte in a separate process. Use one random.Random(seed) instance for all sampling; draw the seed once from os.urandom and record it; sort keys and ids before iterating over any set or dict; no dependence on wall-clock, paths or environment in the emitted records. Verify by running the batch twice and comparing sha256, and report both hashes. generation_record.json must include the sha256 of dictionary.json, generate.py, checker.py and expand.py.
C3. Runtime. Generating plus checking must run at under 60 seconds per 1,000 cases of wall-clock on this machine, so the 5,000-case batch in under five minutes. Report measured setup, generation, checking and rendering times separately. The same programs will later be run at 5,000 and 25,000 cases.
C4. Grounding. Walk every item in the three inventories once. Each item contributes at least one ingredient, or is recorded in dictionary.json as skipped with a reason. Every ingredient carries provenance in one of three forms: {"source": "assets/01.raw.md" | "assets/02.raw.md" | "assets/03.raw.md", "item": "<the inventory's own label for the item>"}; {"source": "ISIC" | "FORD", "code": "<code>"}; {"source": "authored", "reason": "<why no inventory item or taxonomy entry covers it>"}. Report the ingredient count per provenance class.
C5. Vocabulary floor. At least 40 ingredients on each of the eight ingredient axes listed in section 1, each with every required field. Report the count per axis.
C6. Diversity floors, stated per 1,000 cases and scaled to the batch (multiply by 5 for 5,000): each of the seven regimes, at least 60 cases; each ISIC section A to U, at least 20 cases as primary_domain; each FORD field 1 to 6, at least 40 cases as primary_domain; each composition relationship kind you define, at least 30 cases; at least 100 cases containing a component whose regime differs from the case's own regime; and, for the whole batch, at least 15 cases in every regime by primary_domain cell. Write primary_domain as ISIC-A to ISIC-U or FORD-1 to FORD-6. Report any shortfall exactly; do not fill it with cosmetic variants.
C7. Compatibility is data. The admissible situations, regimes, prerequisites, results and constraints recorded on each ingredient are what generate.py samples from and what checker.py verifies. checker.py must re-derive every verdict from dictionary.json and the emitted record alone, never from a flag the generator wrote.
C8. Expansion. Run expand.py over every admitted case into expanded.md, not only the 20 in sample.md, and report the number of cases that expand without error.

The brief follows.

---

Act as a procedural generator of useful use cases.

Generate a large collection of concrete, coherent specifications for things people could build, create, operate or experience. Your priorities are meaningful usefulness, creative composition, situational diversity and fast generation.

Default target: 1,000 cases, unless another number is supplied.

Use code execution internally. Materialize the cases and generation record to OUTPUT_DIR. Software packages, ZIP files and implementation tutorials are unnecessary.

Use only this generation brief and sources or assets explicitly supplied for this task. Treat invented situations, organizations, data and requirements as hypothetical.

1. Prepare a reusable generative vocabulary.

Do this once before bulk generation. Materialize the first batch of cases before refining the vocabulary further; setup must not consume the run.

Represent reusable ingredients for:

* Human needs and intended beneficiaries.
* Objects, information, materials and other inputs.
* Required products, services, experiences and outcomes.
* Activities and relationships.
* Resources, authority and environmental conditions.
* Time, uncertainty, state and change.
* Observable conditions for success.
* Scales and regimes of the world in which needs arise: physical and engineered systems; cellular and organismal biology; ecological and environmental systems; households and everyday life; organizations and markets; law and public administration; computation and networks. Record for each ingredient the regimes in which it applies.

Each ingredient must carry its meaning, applicable situations and regimes, prerequisites, results and constraints.

Build a broad vocabulary. Include needs involving discovery, explanation, learning, expression, care, coordination, production, maintenance and everyday life. Include physical, informational, creative, social and interactive products.

A supplied domain classification organizes coverage: UN ISIC Rev. 4 sections A to U and OECD Fields of Research and Development 1 to 6. It does not determine which constructions are possible.

Keep the vocabulary extensible. Add genuinely new ingredients when existing ones cannot express a useful idea. Record their assumptions and check their generation rules before admitting them into bulk generation.

2. Define rules that compose meaningful constructions.

Represent each case as a connected set of required outcomes, components and relationships.

Permit composition through:

* One part providing an input needed by another.
* Several parts producing a coordinated result.
* Shared resources or identities.
* Conditional decisions.
* Interaction over time.
* Feedback, revision and recovery.
* A product becoming a component of another product.
* A generator or configurator producing further products.

These are starting examples. Introduce other relationships when their meaning is explicit.

Every connection must explain what it transfers, enables, changes or shares. Matching labels alone cannot establish compatibility. Every relationship and every atomic requirement in a case must reference a vocabulary ingredient id.

Preserve inherited requirements. Add the obligations created by the combination, including those that apply across several parts.

For a configurator use case, require both the configurator and a concrete product emitted by it.

Vary composition depth, branching and coupling. Establish finite generation bounds so recursive construction terminates.

3. Construct valid combinations efficiently.

Use dependent sampling. Choose later ingredients from the combinations permitted by earlier choices.

Prefer constructors that satisfy constraints directly. For example, choose an identifier from the actual entity set; allocate quantities within available amounts; derive compatible deadlines from durations.

Propagate constraints while constructing the case. Use backtracking or a constraint solver for remaining interactions when available.

Check global constraints after composition. Pairwise compatibility is insufficient. Three activities may each fit with another while jointly exceeding a shared capacity.

Preserve required goals during generation. An inconvenient constraint cannot be silently weakened to admit a candidate.

Keep bounded search failures, contradictions and unavailable checks distinct. A timeout means unresolved.

Avoid enumerating the entire Cartesian product. Reuse compiled rules, compatibility indexes and checks for identical constraint contexts.

4. Make the cases concrete.

Instantiate meaningful values, identities, units, time intervals, initial states and dependencies.

Supply the information required to understand the job. Compact synthetic fixtures are acceptable when labeled hypothetical. A reference to an unspecified future input does not count as supplying that input.

Each deliverable needs observable acceptance conditions. Preserve qualitative requirements where appropriate. Record the judgment needed to assess them.

Where feasibility is mechanically expressible, retain a checked satisfying assignment, constructive witness or other applicable evidence. State exactly which conditions it establishes.

Keep assumptions visible. Mathematical consistency under hypothetical assumptions does not establish real-world suitability.

5. Separate mechanical validity from semantic judgment.

For every case, record:

* Structural completeness.
* Satisfaction of the encoded constraints.
* Whether the stated need and component relationships have received a plausibility review.
* Remaining assumptions or judgments.

Use a checker that evaluates the emitted case and its constraints. It must not accept the generator's own "valid" flag as evidence.

Exercise the checker with deliberately broken examples, such as missing prerequisites, conflicting identities, incompatible units and excess shared-resource use.

A second verbal review can identify problems. It does not establish mechanically checked correctness.

Retain useful qualitative or unfamiliar proposals that exceed the available checks in a separate review-needed pool. Do not count them as fully checked cases or erase them to make the collection look cleaner.

6. Randomize both construction and situation.

Use an actual random-number facility (the operating system's randomness source, seeding a recorded pseudo-random generator) and record its seed. Do not describe spontaneous language-model choices as random sampling.

Sample across:

* Needs and beneficiaries.
* Product and outcome forms.
* Composition structures.
* Resource conditions.
* Evidence and uncertainty.
* Authority arrangements.
* Temporal and state conditions.
* Change, interruption and recovery.
* Scales and regimes.

Draw from compatible combinations. Introduce cross-domain and cross-regime combinations when their causal relationship makes sense.

Mix broad exploration, underrepresented combinations and boundary conditions. Declare the sampling policy and any adaptive weighting. A weighted or constraint-conditioned sample must not be described as uniformly random.

Freeze the vocabulary, rules and policy for each recorded batch. Improvements create a new generation version.

7. Control diversity explicitly.

Maintain separate counts for:

* Different purposes.
* Different product forms.
* Different semantic component combinations.
* Different dependency structures.
* Different situational combinations.
* Different regimes for the same semantic combination.
* Parameter variants of an existing use case.

Changing names, wording or quantities alone does not establish a new underlying idea.

Use canonical representations to detect exact duplicates. Compare structures with incidental names removed. Also compare meanings, because similar structures can serve different purposes.

Track underrepresented combinations and direct some sampling toward them. Include selected higher-order interactions, such as uncertain evidence combined with shared resources and a revision after partial completion.

Do not collapse diversity into a single unsupported score. Report the dimensions actually measured and the areas still sparse.

If diversity stalls, expand the vocabulary or composition rules in a separately recorded setup revision. Do not fill the requested count with cosmetic variants.

8. Keep the fast generation loop compact.

Generate structured records in batches within the runtime. Avoid a fresh research pass or long language-model response for every case.

Use a shared, versioned dictionary for repeated definitions. Per-case references must resolve unambiguously, and every case must be losslessly expandable into a complete specification.

Use language-model reasoning mainly to develop new meaningful ingredients, inspect unfamiliar combinations and review a sample for semantic problems.

Keep novel unreviewed combinations visible without allowing them to inherit approval from familiar ingredients.

Measure setup time, generation time, checking time and rendering time separately. Report actual throughput.

9. Emit complete case records.

Each record must contain:

case_id
generation_version
primary_domain
regime
beneficiary
need_and_context
required_deliverables
concrete_inputs
component_relationships
atomic_requirements_with_stable_ids
global_constraints
acceptance_conditions
assumptions_and_provenance
validation_status_and_evidence
diversity_signature
seed_or_replay_reference

Acceptance conditions describe the requested product. Validation evidence describes what has actually been checked about the case specification. Keep those roles distinct.

10. Complete and account for the batch.

Generate the requested number of distinct cases meeting the declared admission criteria, or report the exact shortfall and its cause.

Report actual attempted, admitted, duplicate, contradictory, unresolved and review-needed counts. Report substantive use-case counts separately from repeated parameter instances.

Only claim cases were generated when their complete records were actually materialized. A large theoretical combination count or a list of possible seeds is insufficient.

Return the generation record and a readable sample directly; the full collection lives in OUTPUT_DIR. Do not invent storage, hidden records or completed work.

If code execution or actual randomness is unavailable, disclose that limitation. Produce only the batch whose records and checks you can actually support. Do not claim bulk execution or measured speed.

Begin the work now. Keep setup concise, then generate.

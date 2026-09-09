You are a standalone research agent. You have no prior context and need none.

Ground rules:
- Nothing in the current working directory or repository is relevant to this task. Do not read, create or modify any repository files. If you need scratch space, use only /tmp/claude-0/-home-user-post/29b9af63-7d01-5359-bed5-a0fd619c61bc/scratchpad/agent (create it if needed).
- Network facts for this environment: WebSearch works for any topic and returns titles, URLs and snippets. WebFetch succeeds only for github.com and raw.githubusercontent.com; every other host is blocked by policy and returns EGRESS_BLOCKED. Do not retry a blocked host and do not try to route around the block.
- For every source you cite, record its status: READ if you fetched and read the original text, or SNIPPET if you relied on search results only. Prefer primary sources whose original text is hosted on GitHub so that you can read them. Snippet-only sources are allowed, but mark every requirement taken from them as unverified against the original.
- Cite only what you actually searched or read. Do not invent URLs, section numbers or dates.
- Do not ask questions. Where something is undecidable, make a recorded assumption and continue.
- Work until the brief is complete or every shortage is recorded explicitly, then return the entire deliverable in your final message. Your final message is the only thing that will be read. Do not summarize or truncate it: include every construction brief, the full source inventory, the sampling record, and the separate proposal and stress collections.

The brief follows, verbatim.

---

Research real needs and develop diverse, concrete proposals for useful things people could build.

Think expansively. A proposal might be a physical object, a service, an operating procedure, a research instrument, a creative work, an explanation, an interactive tool, a coordinated system or a generator that produces other useful things. These examples do not limit the possibilities.

Your priorities are creativity, meaningful composition and situational diversity.

1. Find independently expressed needs.

Use original requirements, research protocols, operating procedures, procurement documents, interface specifications and other primary sources.

Use official UN ISIC and OECD Fields of Research and Development classifications to organize discovery. Record the versions used. Cover every top-level category and find at least five eligible cases from distinct originating projects or organizations per category. Record shortages explicitly.

Read the original material. Preserve its required outcomes and relevant constraints. Group copied specifications, shared templates and trivial variants into common origin clusters.

2. Imagine useful constructions.

For each need, identify the beneficiary, the situation and what a successful result would enable them to do.

Explore several materially different constructions that could serve that need. Use cross-domain analogies, unfamiliar combinations, different product forms and changes in who creates or uses an output.

Explain the practical value of each proposal. Different names, industries, formats or parameter values alone do not establish a new idea.

Preserve deliverables explicitly required by a source. Keep invented alternatives and combinations in a separately labeled proposal collection.

3. Compose larger useful wholes.

For each promising proposal, ask:

* What inputs or supporting products does it need?
* What becomes possible once it exists?
* Which parts share information, identities, materials, equipment, people, time or authority?
* What useful outcome emerges from their combination?
* Could a reusable builder or configurator serve repeated instances of the need?

Allow recursive composition. A complete product can become a component of another product.

Explain every connection through its actual purpose. Record what passes between the parts and what must remain consistent across them. Preserve requirements inherited from each part.

When proposing a generator or configurator, specify both the generator and a concrete product it must produce.

4. Explore different situations.

Vary purposes, beneficiaries, product forms and operating conditions.

Consider discovery, expression, learning, care, coordination, maintenance and creation. Explore situations involving uncertainty, competing needs, scarce resources, changing evidence, divided authority, concurrent activity, interruption or irreversible effects.

Explain how each substantive variation changes the required product, its relationships or its conditions for success.

Avoid filling the collection with renamed versions of the same underlying idea.

5. Write complete construction briefs.

For each case, provide:

* Stable case ID and primary domain.
* Beneficiary, problem and context.
* Source organization, title, URL, date/version and exact section or page.
* Required deliverables and available inputs.
* Atomic requirements with stable IDs.
* Component relationships and their purposes.
* Constraints across the whole product.
* Observable acceptance criteria.
* Assumptions, missing information and unresolved meanings.

Distinguish source facts, interpretations and hypothetical additions. Preserve relevant quantities, units, identities, timing, dependencies, exceptions, uncertainty, authority, state, external effects and revision conditions.

Acceptance criteria must follow the source. Label additional proposed criteria as requiring acceptance. Retain unresolved feasibility questions.

6. Review and freeze the collection.

Compare the cases by purpose, product form, relationships, constraints and situation. Identify repeated patterns and seek additional independently grounded cases during discovery.

Freeze and deduplicate the sourced inventory before sampling. Obtain a seed from an actual randomness tool. Record the seed, runtime, sampling algorithm and ordered inventory.

Select two distinct-origin sourced cases per category without replacement. Preserve shortages and every selected case.

Freeze the selected requirements. Then create one separately labeled hypothetical stress variation per selected case. State the changed condition and its consequences without silently deleting inherited requirements.

Return the construction briefs, source inventory, sampling record and separate proposal and stress collections directly in your answer.

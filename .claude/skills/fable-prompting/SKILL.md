---
name: fable-prompting
description: Reference for building on Claude Fable 5.1 / Mythos 5.1 via the Anthropic API — effort levels, progress-update thinking blocks, batching tool calls in agent loops, append-only history and thinking-block binding, client-side compaction summaries, search triggering at low effort, refusal false positives, max_tokens headroom at xhigh/max, non-blocking subagents, vision crop tools. Use when writing or debugging code that calls the API or an agent harness.
---

# Prompting Claude Fable 5.1 — integration reference

Source: Claude Docs → Prompt engineering → "Prompting Claude Fable 5.1"
(fetched 2026-09-02). Behavioral rules for sessions in this repo live in
`CLAUDE.md`; this file covers decisions made when building a harness or
calling the API directly. Existing Fable 5 prompts generally work unchanged
on 5.1; the sections below are the differences worth knowing. Prompt text
meant to be pasted into a system prompt or user message is kept verbatim in
fenced blocks.

Fable 5.1 runs safety classifiers and can return `stop_reason: "refusal"`;
see Safeguard false positives.

## Symptom → section

| You observe | Section |
| --- | --- |
| Unsure which effort level, or latency/cost higher than the task warrants | Effort levels |
| Little or no text between tool calls | Progress updates |
| One tool call per turn in agent loops | Batch tool calls |
| Requests fail with "bound to a different conversation", or the harness edits earlier turns | Append-only history |
| Prose runs long and dense | Writing density |
| Chat replies carry less structure than the content needs | Formatting in chat |
| Summaries reproduce source wording without marking it | Quoting sources |
| Turn ends before the work is done, or asks permission for requested work | Finish the whole task |
| Client-side compaction drops constraints or exact details | Compaction summaries |
| Unrequested fixes, or more test files than the task called for | Scope and tests |
| Answers from memory instead of searching at low effort | Search at low effort |
| Benign coding requests return `stop_reason: "refusal"` | Safeguard false positives |
| Whole files rewritten for small changes | Targeted edits |
| Long deliverables at xhigh/max take too long or hit max_tokens | Long outputs |
| Lead agent idles while subagents run | Subagents |
| Chart and dense-image answers miss detail | Vision |

## Effort levels

- Start at the default, `high`, then sweep `low`, `medium`, `xhigh`, `max`
  against your own evals. Effort is the primary intelligence/latency/cost
  control. Re-run the sweep even if you did one on Fable 5: level names
  don't map to the same amount of thinking across models.
- Gains over Fable 5 show up at every level and are largest at the higher
  ones. `medium` roughly matches Fable 5 at lower cost. `low` is often
  competitive with Opus and Sonnet on cost per task while scoring higher, so
  include it wherever you'd otherwise run a smaller model at higher effort.
- Two effort-specific behaviors: at `low`, fewer search/retrieval calls (see
  Search at low effort); at `xhigh`/`max`, longer thinking before a long
  deliverable (see Long outputs).

## Progress updates

Fable 5.1 writes fewer user-facing updates during long tool-calling turns
than Fable 5, more so at higher effort and in longer chains.

1. Confirm your client receives updates at all. The model's notes between
   tool calls come back as progress-update thinking blocks, which are empty
   under the default `thinking.display: "omitted"`. Set `display: "updates"`
   (beta header `thinking-display-updates-2026-08-18`) and render each
   non-empty thinking block as a status line, or `"summarized"` to get them
   with summarized reasoning.
2. Audit the system prompt for lines that suppress narration ("hold all
   findings for the final response") and remove them before adding anything.
3. If you still want more, add to the system prompt:

```text
Before you start, say in a line what you're about to do; brief updates while you work help the user follow along. Close with a short recap that stands on its own — what you found, what you did, and what's next — so a reader who only sees the last message has the full picture.
```

If the product collapses or hides tool output, say so, or the model may run
commands to "show" output the UI never displays. Deliver as a turn-scoped
system message (`clear_at: "next_user_message"`, beta):

```text
Only you see that command's output — the user's terminal shows at most a few lines of it. If the user needs to read any of it, put it in your reply.
```

## Batch tool calls

Fable 5.1 issues parallel calls when a request names several things to
fetch. The exception is coding and computer-use loops where the next
independent calls are implied rather than requested; there it may issue one
per turn. Quality is unaffected, but each extra turn costs tokens, a round
trip, and wall-clock time. Nudge:

```text
First privately list what you need next; then request every item that doesn't depend on another's result in this one response.
```

Placement: each time you send tool results back, append the nudge after that
user message as a turn-scoped system message (`role: "system"`, `clear_at:
"next_user_message"`; beta header `mid-conversation-system-clear-at-2026-08-21`).
Once a later user message exists the API clears earlier copies, so the model
reads only the newest one. Without the beta, put the sentence in a text block
after the `tool_result` blocks in the same user message.

Append a fresh copy each turn and leave earlier copies where they are,
byte-for-byte. Cleared copies cost no input tokens. Deleting or rewriting
them is an edit to earlier turns: it restarts the prompt cache from that
point and invalidates later thinking blocks (see Append-only history).

Reference loop showing the placement:

```python
import anthropic
from anthropic.types.beta import (
    BetaMessageParam,
    BetaToolParam,
    BetaToolResultBlockParam,
)

client = anthropic.Anthropic()

BATCH_NUDGE = (
    "First privately list what you need next; then request every item "
    "that doesn't depend on another's result in this one response."
)
# In-memory files stand in for a working directory so the sample runs anywhere.
FILES = {
    "pyproject.toml": """\
[project]
name = "demo"
version = "0.1.0"
description = "Demo project for the batching example"
""",
    "README.md": """\
# demo

A small demo project. Run `demo --help` for usage.
""",
}
tools: list[BetaToolParam] = [
    {
        "name": "read_file",
        "description": "Read a UTF-8 text file from the working directory.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    }
]
messages: list[BetaMessageParam] = [
    {"role": "user", "content": "Summarize pyproject.toml and README.md."}
]

while True:
    response = client.beta.messages.create(
        model="claude-fable-5-1",
        max_tokens=16000,
        betas=["mid-conversation-system-clear-at-2026-08-21"],
        tools=tools,
        messages=messages,
    )
    # Append the assistant turn exactly as returned, thinking blocks included.
    messages.append({"role": "assistant", "content": response.content})
    if response.stop_reason != "tool_use":
        break
    tool_results: list[BetaToolResultBlockParam] = []
    for block in response.content:
        if block.type == "tool_use":
            raw_path = block.input.get("path")
            path = raw_path if isinstance(raw_path, str) else ""
            if path in FILES:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": FILES[path],
                    }
                )
            else:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"File not found: {path}",
                        "is_error": True,
                    }
                )
    # Send the tool results as the user turn, then a fresh copy of the nudge as a
    # turn-scoped system message. Leave earlier copies in place: the API clears them,
    # so the model sees only the newest one.
    messages.append({"role": "user", "content": tool_results})
    messages.append(
        {"role": "system", "content": BATCH_NUDGE, "clear_at": "next_user_message"}
    )

print(next((block.text for block in response.content if block.type == "text"), ""))
```

## Append-only history

- Append each assistant turn exactly as the API returned it, thinking blocks
  included, and don't edit earlier turns between requests.
- For accounts created on or after 2026-08-31, thinking blocks are valid only
  in the exact conversation that produced them. Replaying a thinking block
  after its prefix (system prompt, tool list, or any earlier message) changed
  returns a 400, or drops the affected blocks with
  `thinking.block_binding.prefix_mismatch_behavior: "drop_block"` (beta header
  `thinking-binding-controls-2026-08-01`). Future models are expected to
  enforce this for all accounts; adopt the pattern now.
- The edits that trip the check are the ones that restart the prompt cache:
  injecting and removing per-turn reminders, summarizing older turns in
  place, changing the system prompt mid-session. Instead: send per-turn
  reminders as turn-scoped system messages, change instructions or tools with
  a mid-conversation system message, and let server-side compaction or
  context editing do trimming.
- Client-side compaction: replace the whole history with one summary message
  plus the new user turn and replay nothing else. No thinking blocks carry
  over, so nothing fails. Cache reads are cheaper on 5.1, so compacting early
  to save cost may no longer be the right tradeoff; try later compaction points.
- To find edits the harness already makes: run a session with
  `prefix_mismatch_behavior: "drop_block"` and log `input_transformations`, or
  capture the exact requests over a few turns and confirm consecutive requests
  are byte-identical up to the appended turns.

## Writing density

Fewer stock phrases and less jargon than earlier models, but sometimes denser
than Fable 5: longer sentences, fewer paragraph breaks. Define the
anti-pattern, in a user message (preferred) or the system prompt:

```text
Mannered prose substitutes metaphor and flourish for direct statement. Instead of "a parameter worth varying," the mannered writer produces "a dial worth turning." Instead of "this point still matters," they write "this point earns its keep." The phrases exist to display the writer, not to convey the idea, and readers can tell. That is why mannered prose irritates: it makes the reader work harder so the writer can perform. It is also imprecise. Metaphors drag in connotations the writer did not choose and cannot control. The fix is to say what you mean. When a literal phrase is available, use it.
```

The short version also tends to work: `Please remove all mannered prose.`

## Formatting in chat

Earlier models overused bullets and bold, and many prompts carry
anti-formatting rules to hold that down. Fable 5.1 leans the other way. Remove
anti-formatting language or replace it with a rule that says when formatting
is appropriate:

```text
Use lists and bullet points when asked to, or when the content is multifaceted enough that they help with clarity. If the person explicitly requests minimal formatting, always format your responses without bullet points, headers, lists, or bold emphasis, as requested. In conversational, personal, or emotional exchanges, keep to plain prose.
```

## Quoting sources

When summarizing documents, Fable 5.1 is more likely than Fable 5 to
reproduce passages without marking them as quotations. Add one complete
example to the system prompt: the request, the response, and why it's
correct. Replace the `[web_search: ...]` lines with your own tool's name so
the model reads them as templated tool output.

```text
<example>
<user>look up how the Riverton Ledger and the Coast Dispatch each covered the Harbor Bridge closure and compare their reporting</user>
<response>
[web_search: Harbor Bridge closure Riverton Ledger]
[web_search: Harbor Bridge closure Coast Dispatch]
Both outlets agree on the basics: the bridge closed on March 3 after inspectors found cracked welds, and the state expects repairs to take about eight months. Where they differ is emphasis. The Ledger treats it as a local-economy story. The Dispatch frames it as a funding failure; its editorial calls the closure "entirely foreseeable." Read together, the Ledger explains who is affected now and the Dispatch explains how it came to this — neither account alone gives the whole picture.
</response>
<rationale>CORRECT: The response is organized around where the two outlets agree and differ, not as a walk through either article. Each outlet's reporting is conveyed in one or two sentences of the assistant's own indirect speech. One short marked phrase from one source; every other claim is reworded. The response is still specific and complete.</rationale>
</example>
```

## Finish the whole task

Fable 5.1 runs long tasks without much methodology guidance, but on complex
asynchronous workloads it sometimes describes the next step instead of doing
it ("Next, I'll …") or stops to ask permission for a step the request already
covered. Two system-prompt additions mitigate this; apply both. If prompt
length is constrained, use only the first, which keeps most of the effect.
The opening sentence (the user isn't watching) carries much of it; keep it as
written. If the product needs the model to stop for specific confirmations,
add a sentence after it listing them. The block can make the model less
likely to ask about ambiguous requests; check that tradeoff on your tasks.

```text
You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking 'Want me to…?' or 'Shall I…?' will block the work. For reversible actions that follow from the original request, proceed without asking. Stop only for destructive actions or genuine scope changes the user must decide. Offering follow-ups after the task is done is fine; asking permission before doing the work is not.

Exception: when the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment. Report your findings and stop. Don't apply a fix until they ask for one.

Before ending your turn, check your last paragraph. If it is a plan, an analysis, a question, a list of next steps, or a promise about work you have not done ('I'll…', 'let me know when…'), do that work now with tool calls. That includes retrying after errors and gathering missing information yourself. Do not stop because the context or session is long. End your turn only when the task is complete or you are blocked on input only the user can provide.

Before running a command that changes system state (such as restarts, deletes, or config edits), check that the evidence actually supports that specific action. A signal that pattern-matches to a known failure may have a different cause.
```

```text
# Delivering work
The user's request — or the plan they approved — sets the scope, and the scope is the deliverable: don't quietly narrow, widen, or swap it. Read ambiguity the way a careful colleague would: make routine judgment calls yourself, and check in only when different readings would lead to materially different work. If you see a real problem with the task as specified, say so in a sentence or two and keep building under stated assumptions; if the user hears the concern and reaffirms, that is their decision, so deliver the full request.

If a question comes up partway, first do everything that doesn't depend on the answer; then state the assumption you made, or — when going ahead on a wrong guess would be unsafe or would make the work useless — put the question at the end of a turn that also delivers that progress. If one part turns out to be blocked, complete every other part in full and say exactly what you left out and why — the whole task is the deliverable, and scaling it down is the user's call, not yours. A step you have decided on is something to run, not to announce: describing the next step and ending the turn leaves it undone until the user replies.

Keep changes to what the request needs. Something else you notice worth doing — cleanup or documentation the task didn't call for, a change to a file the task didn't require — is a suggestion to make at the end, not a change to make; actions clearly beyond what the ask implies, and risky or destructive ones, still need the user's go-ahead.
```

## Compaction summaries

Server-side compaction already tells the model what to preserve. For
client-side compaction, use this summarization instruction:

```text
Summarize the transcript inside <summary></summary> tags. Include relevant information in the summary such that this conversation will be continued by a new context window without needing to redo work or be reprovided with relevant constraints or context. Be sure to preserve: (1) any difficulties or problems that came up, and how they were handled or resolved; (2) any possibilities, options, or approaches that were raised, tried, or set aside, and why; (3) anything that was asked for, decided, agreed, ruled out, or established as a preference, constraint, or boundary — stated exactly; (4) exactly where things stand now — what has been covered, settled, or completed so far; (5) anything still open, unresolved, promised, or expected to happen next; (6) specific details that would be hard to reconstruct — names, numbers, dates, exact wording, links or references — kept exactly. Be complete on these even at the cost of length; keep everything else concise. Weight the two voices differently: keep what the user said, asked for, shared, or established carefully and close to their own words; your own explanations and reasoning can be condensed much further, to what they concluded or produced — as long as nothing in the six items above is dropped.
```

## Scope and tests

On open-ended features Fable 5.1 delivers what's asked and sometimes more:
nearby fixes, unrequested extensions, more committed test files than the
change warrants. With this instruction, unrequested additions and committed
test code drop substantially with no measurable change in task success:

```text
If, while working or testing, you find a pre-existing bug, a performance concern, or behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the requested behavior cannot work without it; report it as a follow-up in your summary. Where the task is ambiguous, implement the reading its wording and the surrounding code most directly support, state that assumption in your summary, and don't build for the other readings as well. Verify your work however you like; scratch scripts and quick checks need not be kept. Commit tests only where the task asks for them or this repository already keeps tests for this kind of change, sized like the neighboring test files — roughly one focused test per stated behavior — and don't turn scratch checks into additional permanent test files. This is about extras only: implement every behavior the task asks for, completely.
```

## Search at low effort

At `low`, Fable 5.1 is less likely than Fable 5 to call a search or
retrieval tool and more likely to answer from memory. Simplest fix: raise
effort for the affected turns rather than the whole conversation. Otherwise,
in the system prompt, say that recognizing a name isn't knowing its current
state:

```text
When a query centers on a name you do not confidently recognize, or recognize from a fast-moving area like AI models and developer tools where the landscape shifts within months, the name itself is the thing to verify: search before answering, and include the name as the user wrote it in at least one query alongside any reformulations. This holds even when you have some background on it — partial background is exactly what makes an out-of-date answer sound authoritative, so familiarity is not a reason to skip the search.
```

## Safeguard false positives

Fewer than Fable 5 at launch, and finding vulnerabilities in source code is
permitted. A blocked request returns `stop_reason: "refusal"`. Three
situations make false positives more likely:

- Compile-check phrasing: ask "Are there any bugs in this program?" rather
  than "Does this program compile without errors?"
- Lesser-known languages: give context on what the language is and how it
  works, e.g. access to its documentation.
- Base64 in tool output: remove it from what enters the model's context.

## Targeted edits

Fable 5.1 is more likely than Fable 5 to rewrite an entire text file rather
than make a targeted edit. The result is usually the same, but unless the
file is short or mostly changing, a rewrite costs output tokens and time.
Append to the system prompt or first user message:

```text
The number of tokens used to edit files is best minimized, all else being equal. Therefore, when it will not affect the end result, try to surgically edit a file rather than rewrite the entire thing.
```

## Long outputs

At `xhigh` and especially `max`, the model can draft much of a long
deliverable in its thinking and then write it again as the reply. Prefer
`high` for these requests and move up only where you've measured a quality
gain. If you do run them at `xhigh`/`max`:

- Set `max_tokens` to leave room for thinking plus the reply.
- Append the following to the end of the user message, replacing
  `[max_tokens]` with the request's actual value (e.g. 64,000). It makes the
  thinking much shorter on prose and code requests.

```text
Everything produced in one reply, including any reasoning or drafting done before the reply, counts toward a single limit of about [max_tokens] tokens. If that limit is reached before the reply is finished, the person receives a cut-off response and has to start over. Composing an entire output or deliverable in full as reasoning and then again as a reply would double the length of the turn without improving the result, so don't do that.

Instead, when the person has asked for a long or effort-intensive deliverable such as a multi-section document, a large table or dataset, or a complete code file, spend extra effort on understanding the request, checking the inputs the answer depends on, settling the structure and other difficult decisions, and otherwise using the reasoning space to reason and the output space to write an output. Usually it is not needed to draft an output multiple times.
```

## Subagents

Don't force the lead agent to stop and wait for each subagent. Letting the
lead continue lowers average time to completion at similar quality, tokens,
and cost. Setup:

1. The tool that starts a subagent returns immediately.
2. Each subagent's result comes back to the lead in a later user message.
3. Give the lead a separate tool to call when it wants to wait for a result.

The model still often chooses to wait; savings come from the runs where it
carries on.

## Vision

On dense charts and complex images, Fable 5.1 does its best work when it can
iteratively analyze, crop, and visually verify. Run it as an agent with a
container holding the raw images and basic image libraries (PIL, OpenCV). If
a container is too much overhead, a crop tool alone delivers most of the
uplift: return a chosen region cropped and enlarged, so the model can examine
details and scale test-time compute with image tokens.

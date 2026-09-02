# Compiled AI, industry by industry

Date: 2026-09-01. This document explains, in plain words, how the compiled AI method is applied in twelve industries. The first part states the method once. Each sampler after it states one workflow in one industry: the rules you compile, how you do it step by step, who still signs by law, and the outcome. Every regulation and standard in this document is public and was checked on the internet before it was written here. Nothing in this document comes from a private or employer document.

## Part 1. The method, once

### The idea

Today, when a decision inside a regulated process needs an answer, someone opens the rulebook or asks a model, every time. The rulebook is re-read on every decision. The answer differs from run to run. Nobody can check the answer except by reading again.

Compiled AI reverses the order. You read the rulebook once, up front. You turn it into rules that a program can run. You check those rules once. At decision time there is no model in the room. There is a rule, a record of which rule applied, and the sentence of the rulebook it came from.

The word compiled is borrowed from software. An interpreter reads the program every time it runs. A compiler translates the program once and runs the translation. A model reading policy at decision time is an interpreter. Turning policy into rules ahead of time is compiling.

The word neurosymbolic means this: a neural model proposes, and a symbolic checker decides. The model reads a sentence and proposes what kind of rule it is and what the rule says. The checker verifies what can be verified mechanically. A reviewer answers the one question that cannot be verified mechanically, once per sentence, and the answer becomes a permanent test. After that, the model is gone.

### The chain

The same chain applies in every industry. Each step is one tool with one job.

1. Read. A PDF reader gives every character of the source document with its page and position. The tool is pdfplumber. Nothing is summarized.
2. Cut. A sentence splitter cuts the text into sentences with their positions. The tool is spaCy's sentencizer, with rules added for numbered legal paragraphs.
3. Propose. A language model reads one sentence and proposes a typed statement: a definition, a condition, a step, a precedence, or a decision that the sentence reserves to a role. The proposal includes the actor, the condition, the action, and the exact quote it rests on. The output is forced into a fixed schema by pydantic. This step is neural. Nothing downstream trusts it.
4. Check. A checker verifies every mechanical item: the quote is byte-exact in the source, the actor is a term the document defines, the connective maps to the statement type by a fixed table, and a sentence that specifies a role compiled as a reserved decision and not as a rule. This step is symbolic.
5. Confirm. A reviewer runs a written checklist. Every mechanical item is already answered by the checker. One item remains for the reviewer: the model generated one example that the sentence allows and one that it forbids, and the reviewer answers whether the two examples say what the sentence says. The answer is recorded, and two reviewers running the same checklist either agree or produce a recorded disagreement.
6. Generate. The model drafts the rule as a small function over a typed case record. This step is neural.
7. Prove. A type checker rejects a malformed function, and a property tester runs the confirmed examples and thousands of generated cases against every invariant. The tools are mypy and hypothesis. A confirmed example is a permanent test from this point on.
8. Reconcile. A constraint solver checks that all the rules are consistent, and when they are not, it returns the smallest set of sentences that contradict each other. The tool is z3. A contradiction between two sites or two states is a variation point, which is a rule that applies in one place and not another. A contradiction inside one scope is a real conflict and goes back to the owner of the document.
9. Order. A graph library builds the precedence of the steps from the before, after, and prior-to sentences, and it computes the order of the workflow. The tool is networkx. The order is computed, not drawn.
10. Seal. A digest is computed for every rule from the bytes of its source sentence. The tool is hashlib. A rebuild from the same sources produces the same digests. A change to one sentence changes one digest.

Steps three and six are neural. Every other step is symbolic. After step ten, nothing neural runs.

### The libraries

Each step of the chain is one library with one job. Every library here is open source or part of Python itself, except the checker, which is a few hundred lines of our own code.

- pdfplumber. An open-source Python library that opens a PDF and returns every character with its page, its position, and its size, and also the words and the tables. In the chain it is the reader. Its output is the only source of truth for a quote. A quote is accepted only if its characters are found, in order, in the pdfplumber output.
- spaCy. An open-source natural language library. Its sentencizer splits text into sentences by punctuation rules and records where each sentence starts and ends. In the chain it is the cutter. It runs with added rules for numbered paragraphs such as (b)(2), so a legal paragraph is not split at the wrong place.
- anthropic. The Python SDK for the Claude models. In the chain it is the proposer, used twice: once to propose what kind of statement a sentence is, and once to draft a rule function from a confirmed statement. It is the only neural component. Its output is never used directly. It goes to the checker.
- pydantic. An open-source library that defines typed records and rejects any value that does not match the type. In the chain it forces the model's output into a fixed schema, and at runtime it types the case record: a claim, a change proposal, a request. A record that is missing a field or has a field of the wrong type is rejected before any rule runs.
- The checker. Our own code. It verifies the mechanical items of the checklist: the quote is byte-exact in the pdfplumber output, the actor is a term the document defines, the connective maps to the statement type by the fixed table, and a sentence that specifies a role compiled as a reserved decision and not as a rule.
- mypy. An open-source type checker for Python. In the chain it rejects a drafted rule function whose inputs and outputs do not match the types of the case record, before the function is ever run.
- hypothesis. An open-source property-based testing library. You state a property, such as no Class I change is approved by the contractor alone, and hypothesis generates thousands of cases, searches for one that breaks the property, and shrinks the failing case to its simplest form. In the chain it runs the confirmed examples as permanent tests and hunts for a counterexample to every invariant.
- z3. A constraint solver from Microsoft Research, installed as z3-solver. Given a set of logical rules, it decides whether they can all be true at once. When they cannot, it returns the smallest set of rules that conflict, called the unsatisfiable core. In the chain it is the reconciler. It separates a variation between two sites from a real contradiction inside one document.
- networkx. An open-source graph library. In the chain it builds the precedence graph from the before, after, and prior-to sentences, computes the order of the steps by topological sort, and reports any cycle, which is an ordering contradiction in the source.
- hashlib. Part of the Python standard library. It computes a digest, which is a fixed-length fingerprint of any bytes. In the chain it seals each rule to the bytes of its source sentence, so a rebuild proves identity and a change to one sentence changes exactly one fingerprint.

### The runtime

A case arrives: a claim, a change proposal, a request, an application. It is typed into a record. The compiled rules run over the record. The result is one of two values. The first is a proof: the list of rules that applied, each with its source sentence. The second is a list of typed reasons: each one the clause the case tripped, and the remedy. There is no third outcome. A validation never fails to answer.

Where a law reserves a decision to a person, the runtime routes the proof or the reasons to that person, and the person records one decision. Everyone else evaluates nothing, because the machine already did.

### What is honest to say

The compile is not automatic. It is automatic proposal, mechanical checking, and one human answer per sentence, once. Natural language has no formal meaning, so the reviewer's answer cannot be mechanized. It can be made small, fixed in form, recorded, and turned into a test. A sentence like "reasonably designed" does not compile into a rule at all. It compiles into a reserved judgment, and a person makes it.

## Part 2. The samplers

Every sampler uses the chain above. The steps are referred to as follows: read, cut, propose, check, confirm, generate, prove, reconcile, order, seal, and run. Each step is performed by the library stated for it in Part 1, and each sampler states the library at the step.

### Aerospace and defense: an engineering change on a fielded part

The workflow. An engineer changes a part on a delivered system. The change is classified as Class I, which affects form, fit, function, or interface, or Class II, which does not. A configuration control board dispositions the change. Export control decides whether the technical data is controlled under the arms regulations or the commercial regulations. The supplier is qualified and a first article inspection is performed. A government inspector accepts the delivery.

The rules you compile. MIL-HDBK-61A and EIA-649 for the Class I and Class II definitions and who may approve each. The arms regulations at 22 CFR parts 120 to 130 for what is controlled and who may sign a license application. The commercial regulations at 15 CFR part 734 for what falls outside the arms regulations. FAR 1.602-1 for the authority of the contracting officer. DFARS 252.204-7012 for the cybersecurity requirement a supplier must meet. AS9100 clause 8.5.1.3 with AS9102 for first article inspection. DCMA Manual 2101-01 for acceptance of supplies.

How you do it. Read the handbook, the two export regulations, the FAR and DFARS clauses, and the quality standard with pdfplumber, so every sentence has a page and a position. Cut them into sentences with spaCy. Propose a type for each sentence through the anthropic SDK, with the output forced into a pydantic schema: the Class I definition is a definition, the approval sentence is a reserved decision, the thirty-day and inspection sentences are steps. Check every quote and every actor with the checker against the pdfplumber output. Confirm the examples: a change to a bolt torque that alters interface loads is Class I, and a drawing note correction is Class II. Generate the rules through the anthropic SDK over a pydantic change record that lists the affected characteristics, the technical data involved, the supplier, and the contract. Prove with mypy and hypothesis: no Class I change is ever approved by the contractor alone, and no controlled technical data is ever released without a license record. Reconcile the site tailoring against the handbook with z3, and record each tailoring as a variation point. Order the steps with networkx: classification before disposition, export review before any transfer of data, first article before production acceptance. Seal the rule base with hashlib. Run every change proposal through it.

Who still signs, and why. The empowered official signs an export license application, because 22 CFR 120.67 defines that person. The contracting officer binds the government, because FAR 1.602-1 says only that person may. The government inspector accepts the delivery, because acceptance is the government's act. Everyone else checks a record the machine prepared.

The outcome. An engineer submits a change and receives, in seconds, either a clean record with the sentences that applied or the exact clause tripped and the remedy. Export review runs only when the rules say data is controlled. When a standard changes, one sentence recompiles one rule.

### Banking and wealth: opening an account for a legal entity

The workflow. A client applies to open an account. The firm identifies the client, identifies the beneficial owners and the control person of a legal entity, screens the parties, assesses the source of wealth, and accepts the account.

The rules you compile. The customer due diligence rule at 31 CFR 1010.230, which defines a beneficial owner as anyone who owns 25 percent or more of the equity and one individual with significant responsibility to control the entity, and which requires a certification from the individual opening the account. FINRA Rule 4512, which lists the account record and requires the signature of a partner, officer, or manager accepting the account. FINRA Rule 2360 for options approval by a Registered Options Principal. FINRA Rule 3260 for acceptance of a discretionary account in writing. The anti-money laundering program rule at 31 CFR 1023.210 and the suspicious activity rule at 31 CFR 1023.320.

How you do it. Read the two regulations and the three FINRA rules with pdfplumber. Cut them with spaCy. Propose through the anthropic SDK into a pydantic schema: the 25 percent sentence is a definition, the certification sentence is a step by the client, the acceptance signature is a reserved decision. Check with the checker. Confirm the examples: an owner at 30 percent is a beneficial owner, and an owner at 20 percent is not, unless the owner is also the control person. Generate the rules through the anthropic SDK over a pydantic application record that lists the owners with percentages, the control person, the certifier, and the signer. Prove with mypy and hypothesis that every ownership structure closes at natural persons and that no account is accepted without the reserved signature. Reconcile the state and country variations with z3. Order the steps with networkx: identity before the case, the case before screening, screening before acceptance. Seal with hashlib and run.

Who still signs, and why. The client certifies the beneficial owners, because 31 CFR 1010.230 requires the certification from the individual opening the account. The partner, officer, or manager signs the acceptance, because FINRA Rule 4512 requires that signature. The Registered Options Principal approves options. The compliance officer designated under 31 CFR 1023.210 decides a confirmed screening match and a suspicious activity report.

The outcome. An application is validated in seconds against the regulation with the sentence attached. The acceptance signer sees a proof record instead of a file. The rework that today comes from a wrong figure found late is a typed reason found at entry.

### Insurance: adjudicating a property claim

The workflow. A policyholder reports a loss. The insurer acknowledges the claim, requests proof of loss, investigates, and accepts or denies the claim in writing with the reasons and the policy provision relied on.

The rules you compile. The NAIC Unfair Claims Settlement Practices Act, Model 900, which sets the acknowledgment and forms deadlines and lists the unfair practices. The state regulation that adopts it, for example California's Fair Claims Settlement Practices Regulations at 10 CCR 2695.7, which requires the insurer to accept or deny within forty calendar days of proof of claim, in writing, stating every basis and the policy provision relied on. The policy form itself, which is the contract.

How you do it. Read the model act, the state regulation, and the policy form with pdfplumber. Cut with spaCy. Propose through the anthropic SDK into a pydantic schema: the forty-day sentence is a step with a clock, the written-reasons sentence is a step with required fields, the coverage sentences of the policy are conditions. Check with the checker. Confirm the examples: a water loss from a burst pipe is covered under the policy example, and a flood is excluded. Generate the rules through the anthropic SDK over a pydantic claim record that lists the loss cause, the dates, the proof received, and the policy form. Prove with mypy and hypothesis that no denial can be generated without a stated basis and a cited provision, and that every clock starts on the date the regulation specifies. Reconcile the state regulations against each other with z3, so each state's deadline is a variation point. Order the steps with networkx: acknowledgment, proof of loss, investigation, determination. Seal with hashlib and run.

Who still signs, and why. The licensed adjuster signs the determination where the state requires a licensed adjuster to adjust the claim. Everyone else evaluates a record. The policyholder disputes a determination through the appeal the regulation specifies.

The outcome. Every claim receives a determination inside the state's clock, with the policy provision and the regulation sentence attached. A denial without a stated basis cannot be produced, because the rule base will not generate one.

### Healthcare payers and providers: prior authorization

The workflow. A provider requests authorization for a service. The payer decides within the regulated time, gives a specific reason for a denial, and has a qualified clinician review any adverse medical necessity decision.

The rules you compile. The CMS Interoperability and Prior Authorization final rule, CMS-0057-F, which requires a decision within seventy-two hours for an urgent request and seven calendar days for a standard request, and a specific reason for a denial. The Medicare Advantage rule at 42 CFR 422.566, under which an adverse medical necessity decision must be reviewed by a physician or other appropriate health care professional. The payer's own medical policy for the service, which states the clinical criteria.

How you do it. Read the final rule, the Medicare Advantage rule, and the medical policy with pdfplumber. Cut with spaCy. Propose through the anthropic SDK into a pydantic schema: the clocks are steps, the clinical criteria are conditions, the physician review is a reserved decision. Check with the checker. Confirm the examples: a request that meets every criterion in the policy is approved, and a request missing an imaging result is pended with the missing item specified. Generate the rules through the anthropic SDK over a pydantic request record that lists the diagnosis codes, the procedure codes, the criteria met, and the time received. Prove with mypy and hypothesis that no denial is issued without a specific reason and that no adverse medical necessity decision is issued without the clinician's record. Reconcile the medical policies of different plans with z3. Order the steps with networkx: completeness, criteria, clinician review where adverse, notice. Seal with hashlib and run.

Who still signs, and why. The physician or appropriate health care professional reviews an adverse medical necessity decision, because 42 CFR 422.566 requires it. The provider attests to the clinical facts. Everyone else evaluates a record.

The outcome. A request that meets the criteria is approved in minutes with the criteria listed. A denial always states the specific reason the rule requires. The clock never runs out silently, because the rule base tracks it.

### Pharmaceuticals and medical devices: a change to a manufacturing procedure

The workflow. A production team proposes a change to a written procedure or records a deviation from one. The quality unit reviews and approves or rejects. The change is implemented and the record is kept.

The rules you compile. 21 CFR 211.22, which gives the quality control unit the responsibility to approve or reject procedures and the authority to approve or reject anything that affects the product. 21 CFR 211.100, which requires written procedures, requires any deviation to be recorded and justified, and requires changes to be reviewed and approved by the quality control unit. For devices, the Quality Management System Regulation at 21 CFR part 820, which incorporates ISO 13485 by reference and applies from February 2026, for change control and design change.

How you do it. Read the two drug regulations and the device regulation, with the site's own change control procedure, with pdfplumber. Cut with spaCy. Propose through the anthropic SDK into a pydantic schema: the approval sentences are reserved decisions, the recording and justification sentences are steps with required fields. Check with the checker. Confirm the examples: a change to a mixing time is a change requiring quality approval, and a typo correction in a form is a documentation correction under the site procedure. Generate the rules through the anthropic SDK over a pydantic change record that lists the procedure, the affected steps, the justification, and the approver. Prove with mypy and hypothesis that no change is implemented without the quality unit's record and that every deviation has a justification. Reconcile the site procedure against the regulation with z3. Order the steps with networkx: proposal, impact assessment, quality approval, implementation, effectiveness check. Seal with hashlib and run.

Who still signs, and why. The quality control unit approves or rejects, because 21 CFR 211.22 gives that unit the authority and 21 CFR 211.100 requires its approval. Everyone else prepares the record.

The outcome. A change request cannot reach implementation without the quality unit's decision, and the decision is made over a complete record with every required field present. An inspector reading the record sees the regulation sentence beside each step.

### Energy and utilities: a configuration change on a critical cyber system

The workflow. An operator changes the configuration of a system that affects the bulk electric system. The change is authorized, the baseline is updated within the required time, and the security policies are reviewed and approved on schedule.

The rules you compile. NERC CIP-010, which requires a documented baseline configuration and an update of the baseline within thirty calendar days of completing a change that deviates from it. NERC CIP-003, which requires the CIP Senior Manager to review and approve the cyber security policies at least once every fifteen calendar months. The entity's own change management procedure.

How you do it. Read the two standards and the procedure with pdfplumber. Cut with spaCy. Propose through the anthropic SDK into a pydantic schema: the thirty-day and fifteen-month sentences are steps with clocks, the approval sentence is a reserved decision. Check with the checker. Confirm the examples: a firmware update is a baseline deviation, and a password change is not. Generate the rules through the anthropic SDK over a pydantic change record that lists the asset, the baseline elements affected, the authorization, and the completion date. Prove with mypy and hypothesis that every baseline deviation has an update within thirty days and that no policy runs past fifteen months without the approval record. Reconcile the procedure against the standard with z3. Order the steps with networkx: authorization, change, verification, baseline update. Seal with hashlib and run.

Who still signs, and why. The CIP Senior Manager approves the policies, because CIP-003 specifies that role. The entity's designated approver authorizes each change under its own procedure. Everyone else evaluates a record.

The outcome. A configuration change is recorded and its baseline update is scheduled at the moment the change completes. An audit reads the record and the standard sentence together.

### Government: a request for public records

The workflow. A member of the public requests records. The agency determines within twenty working days whether to comply, notifies the requester of the determination and the reasons, and on a denial states the right to appeal.

The rules you compile. The Freedom of Information Act at 5 U.S.C. 552(a)(6), which sets the twenty-working-day determination, requires notice of the reasons, requires notice of the right to appeal within not less than ninety days, and sets the twenty-working-day appeal determination. The nine exemptions in 5 U.S.C. 552(b). The agency's own FOIA regulation.

How you do it. Read the statute and the agency regulation with pdfplumber. Cut with spaCy. Propose through the anthropic SDK into a pydantic schema: the clocks are steps, each exemption is a condition, the notice sentences are steps with required fields. Check with the checker. Confirm the examples: a request for a contract is released with pricing redacted under the exemption for confidential commercial information, and a request for a personnel file is denied under the personal privacy exemption. Generate the rules through the anthropic SDK over a pydantic request record that lists the records located, the exemptions claimed per record, and the dates. Prove with mypy and hypothesis that no denial is issued without the reasons and the appeal notice, and that every clock is computed in working days. Reconcile agency regulations against the statute with z3. Order the steps with networkx: receipt, search, review, determination, notice. Seal with hashlib and run.

Who still signs, and why. The official responsible for the denial is identified in the notice, because the statute requires the notice to state the name and title or position of each person responsible. The head of the agency or the designee decides the appeal. Everyone else prepares the record.

The outcome. Every request receives a determination inside the statutory clock, with the exemption sentence attached to every redaction. An appeal reads the same record.

### Manufacturing: a nonconforming part

The workflow. An inspector finds a part that does not meet its requirement. The part is identified and controlled, a disposition is decided, the customer is informed where required, and the cause is corrected so it does not recur.

The rules you compile. ISO 9001:2015 clause 8.7, which requires nonconforming outputs to be identified and controlled and lists the dispositions, and which requires the record to identify the authority that decided the action. Clause 10.2, which requires reaction, cause analysis, corrective action, and an effectiveness review. For automotive, IATF 16949 clause 8.7.1.1, which requires customer authorization before a use-as-is or repair disposition.

How you do it. Read the two standards and the plant's nonconformance procedure with pdfplumber. Cut with spaCy. Propose through the anthropic SDK into a pydantic schema: the disposition sentences are conditions, the customer authorization is a reserved decision, the effectiveness review is a step. Check with the checker. Confirm the examples: a dimension out of tolerance on a safety characteristic requires customer authorization for use as is, and a cosmetic scratch on a non-visible surface is corrected under the plant's own authority. Generate the rules through the anthropic SDK over a pydantic nonconformance record that lists the characteristic, the deviation, the disposition, and the authority. Prove with mypy and hypothesis that no use-as-is disposition on a customer part is closed without the customer's authorization record. Reconcile the plant procedure against the standard with z3. Order the steps with networkx: identify, contain, disposition, correct, verify. Seal with hashlib and run.

Who still signs, and why. The customer authorizes a concession where IATF 16949 requires it. The authority the plant designates decides every other disposition, because ISO 9001 requires the record to identify that authority. Everyone else prepares the record.

The outcome. A nonconformance is dispositioned against the standard with the clause attached, and a corrective action cannot close without its effectiveness review.

### Technology and software: a request from a person for their data

The workflow. A person asks a company what personal data it processes about them and for a copy. The company verifies the identity, locates the data, applies the exemptions, and responds within one month.

The rules you compile. GDPR Article 15, which states the right of access and the information the response must contain. Article 12, which requires the response without undue delay and within one month, extendable by two further months for complex or numerous requests with notice inside the first month. The company's own retention schedule and data map.

How you do it. Read the two articles and the data map with pdfplumber. Cut with spaCy. Propose through the anthropic SDK into a pydantic schema: the one-month sentence is a step with a clock, the list of information in Article 15 is a set of required fields, the extension sentence is a condition. Check with the checker. Confirm the examples: a request from a verified customer for the data in the billing system is answered with the categories, the purposes, the recipients, and the copy, and a request that includes another person's data is answered with that person's data withheld. Generate the rules through the anthropic SDK over a pydantic request record that lists the identity verification, the systems searched, the fields returned, and the dates. Prove with mypy and hypothesis that every response contains every field Article 15 lists and that no clock exceeds one month without a recorded extension notice. Reconcile the retention schedule against the data map with z3. Order the steps with networkx: verify, locate, apply exemptions, respond. Seal with hashlib and run.

Who still signs, and why. The regulation reserves no signature. The data protection officer is consulted where the company has one. The person making the request confirms their identity.

The outcome. A request is answered inside the month with every required field present, and the record shows which system each field came from.

### Logistics and supply chain: a customs entry

The workflow. Goods arrive. The importer or its broker classifies the goods, values them, files the entry, files the entry summary within ten working days, and declares under oath that the invoice is true.

The rules you compile. 19 CFR part 141 for entry and entry summary, with the entry summary on CBP Form 7501 within ten working days of entry. The Harmonized Tariff Schedule for classification by name, use, and material. 19 U.S.C. 1485 for the importer's declaration under oath. 19 CFR part 111 for who may transact customs business as a broker.

How you do it. Read the entry regulation, the tariff schedule chapters for the goods, the declaration statute, and the broker regulation with pdfplumber. Cut with spaCy. Propose through the anthropic SDK into a pydantic schema: the ten-day sentence is a step with a clock, the tariff headings are conditions on the goods' name, use, and material, the declaration is a reserved decision by the importer of record. Check with the checker. Confirm the examples: a steel bolt of a given size classifies under its heading, and the same bolt plated with zinc classifies under the same heading with the plating noted. Generate the rules through the anthropic SDK over a pydantic entry record that lists the goods, the classification, the value, the parties, and the dates. Prove with mypy and hypothesis that every entry summary is filed inside ten working days and that no entry is transmitted without the importer's declaration. Reconcile the tariff notes against each other with z3. Order the steps with networkx: arrival, entry, classification, valuation, summary, declaration. Seal with hashlib and run.

Who still signs, and why. The importer of record makes the declaration under oath, because 19 U.S.C. 1485 requires it. A licensed customs broker transacts the customs business when the importer uses one, because 19 CFR part 111 requires the license. Everyone else prepares the record.

The outcome. An entry is classified with the tariff heading and its note attached, and the summary clock is tracked from arrival.

### Legal and professional services: a conflict check on a new matter

The workflow. A lawyer opens a new matter. The firm checks the parties against current and former clients. Where a conflict exists, the lawyer determines whether it can be waived, and each affected client gives informed consent confirmed in writing.

The rules you compile. ABA Model Rule 1.7, under which a conflict may be waived only if the lawyer reasonably believes the representation can be competent and diligent and each affected client gives informed consent confirmed in writing. Rule 1.9 for former clients. Rule 1.10, under which one lawyer's conflict is imputed to the firm. The state's adopted version of each rule.

How you do it. Read the three rules in the state's version with pdfplumber. Cut with spaCy. Propose through the anthropic SDK into a pydantic schema: the imputation sentence is a definition of who counts, the waiver conditions are conditions, and one of them, the lawyer's reasonable belief, is a reserved judgment, and the written consent is a reserved decision by the client. Check with the checker. Confirm the examples: a new matter adverse to a current client of another partner is a conflict by imputation, and a matter adverse to a former client on an unrelated subject is not. Generate the rules through the anthropic SDK over a pydantic matter record that lists the parties, the adverse parties, the current and former clients matched, and the consents. Prove with mypy and hypothesis that no matter opens with an unwaived conflict and that no waiver exists without the written consent record. Reconcile the state versions against the model rules with z3. Order the steps with networkx: intake, match, determination, consent, opening. Seal with hashlib and run.

Who still signs, and why. Each affected client gives informed consent confirmed in writing, because Rule 1.7 requires it. The lawyer makes the reasonable-belief determination, because the rule reserves that judgment. Everyone else prepares the record.

The outcome. A conflict is found at intake with the rule sentence attached, and a matter cannot open until the consent records exist.

### Telecommunications: porting a customer's number

The workflow. A customer moves a telephone number to a new carrier. The new carrier collects the authorization and the validation fields, submits the request to the old carrier, and the port completes within the regulated interval.

The rules you compile. 47 CFR 52.35, under which a simple port must complete within one business day, with the business day and hours defined, and with the request received between 8 a.m. and 1 p.m. local time to activate at midnight the same day. The FCC's validation rule, under which the old carrier may require only the account number, the telephone number, the ZIP code, and a passcode where one exists. The letter of authorization the customer signs.

How you do it. Read the porting regulation and the validation order with pdfplumber. Cut with spaCy. Propose through the anthropic SDK into a pydantic schema: the interval sentence is a step with a clock, the validation fields are required fields, the authorization is a reserved decision by the customer. Check with the checker. Confirm the examples: a single-line request with the four fields received at noon activates at midnight, and a request received at 2 p.m. activates the next business day. Generate the rules through the anthropic SDK over a pydantic port record that lists the fields, the receipt time, and the authorization. Prove with mypy and hypothesis that no port is submitted without the authorization and that no valid simple port exceeds one business day. Reconcile the carriers' order forms against the regulation with z3. Order the steps with networkx: authorization, validation, submission, activation. Seal with hashlib and run.

Who still signs, and why. The customer authorizes the port, because the port is the customer's act. The regulation reserves nothing else to a person.

The outcome. A port request is validated against the regulation at entry and completes inside the interval, with the rule sentence attached to every rejection.

## Part 3. What every sampler has in common

- The rules are public. Every sampler compiles a regulation or a standard anyone can read, plus the organization's own procedure.
- The person who stays is the person the law specifies. The empowered official, the contracting officer, the acceptance signer, the quality unit, the CIP Senior Manager, the clinician, the client. The list is short, and it is the same list a regulator would write.
- The outcome is the same shape. A case comes back clean with the sentences that applied, or it comes back with the clause it tripped and the remedy. A person who signs sees that record and nothing else.
- The compile is honest. A model proposes. Checkers decide every item that has a decidable form. One reviewer answers one question per sentence, once, and the answer becomes a test.

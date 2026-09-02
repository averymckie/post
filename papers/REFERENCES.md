# References

Bibliography of prior work that the Compiled AI method rests on. Built 2026-09-02 under one rule: an entry is listed as verified only if a page showing its title and authors was fetched, and the entry names the URL fetched. Entries that could not be fetched are listed as unverified with what was tried, rather than dropped or filled in from memory.

Caveat: the bibliographic hosts (the DOI resolver, arXiv, the ACM Digital Library, Springer, the ACL Anthology site, Semantic Scholar, dblp, Crossref, and the publishers) were blocked by the network policy of the session that produced this file. Verification used publisher source data on GitHub (ACL Anthology XML, the JOSS Crossref deposit, PMLR volume sources), Microsoft Research pages, and author-maintained citation files, each entry saying which. Re-run the unverified entries against the primary hosts from an unrestricted network.

Verification date: 2026-09-02.

**How verification was done (read this first).** The session's egress proxy blocked every general bibliographic host tried: doi.org / dx.doi.org, arxiv.org (and export/mirror hosts), dl.acm.org, link.springer.com, aclanthology.org, joss.theoj.org, Semantic Scholar (site + API), dblp (3 hosts), Crossref (API, search, content negotiation), OpenAlex, OpenCitations, Unpaywall, OpenAIRE, BASE, RePEc, Wiley, OUP, IEEE Xplore / computer.org, SAGE, PMLR, OpenReview, NeurIPS/ICML/ICLR sites, OECD (all hosts), Zenodo, Wikipedia/Wikidata, Google Scholar, Bing, and every university/author homepage attempted. Only two channels were reachable:

1. `www.microsoft.com/en-us/research/...` publication pages and PDFs (used for Catala, Z3, and three extras).
2. GitHub, via read-only `git clone` — which gives access to **publisher source data mirrored on GitHub** (the ACL Anthology's canonical XML in `acl-org/acl-anthology`, JOSS's Crossref deposit XML in `openjournals/joss-papers`, PMLR's volume source in `mlresearch/v235`) and to **author-maintained citation files** (`CITATION.cff`, README BibTeX).

Each entry below states exactly what was fetched. Entries whose only source is an author-maintained repository are tagged **[author-repo]**; their venue/DOI fields come from the authors' own citation block, not from a publisher page. Metadata that appeared only in web-search result snippets (never on a fetched page) is **not** used in any Verified citation; it is mentioned only in the Unverified section, explicitly labelled.

---

### Verified

#### Candidates from the original list (11 of 23)

1. **Merigoux, Denis; Chataing, Nicolas; Protzenko, Jonathan. "Catala: A Programming Language for the Law." *Proceedings of the ACM on Programming Languages* 5(ICFP), Article 77, 29 pages, August 2021 (ICFP 2021). DOI 10.1145/3473582.**
   Fetched: https://www.microsoft.com/en-us/research/publication/catala-a-programming-language-for-the-law/ (title, authors, "ICFP 2021", July 2021); journal/volume/article/DOI from the authors' own BibTeX in https://github.com/CatalaLang/catala-website (file `src/pages/Publications.res`, obtained by git clone).
   Why it matters: the closest prior "statute to faithful-by-construction executable" language; the paper's fidelity claim is the benchmark our LLM-propose / symbolic-check / human-confirm pipeline must meet without hand translation.

2. **MacIver, David R.; Hatfield-Dodds, Zac; and many other contributors. "Hypothesis: A new approach to property-based testing." *Journal of Open Source Software* 4(43): 1891, 21 November 2019. DOI 10.21105/joss.01891.**
   Fetched: JOSS's Crossref deposit for the article, https://github.com/openjournals/joss-papers (file `joss.01891/10.21105.joss.01891.crossref.xml`, git clone; shows journal, volume 4, issue 43, page 1891, authors, date, DOI) and https://github.com/HypothesisWorks/hypothesis (`CITATION.cff`, `paper.md`).
   Why it matters: the property-based tester that fuzzes every drafted typed rule function; its "confirmed example becomes a permanent test" workflow (Hypothesis's example database) mirrors our reviewer-confirmed test corpus.

3. **de Moura, Leonardo; Bjørner, Nikolaj. "Z3: An Efficient SMT Solver." *Tools and Algorithms for the Construction and Analysis of Systems* (TACAS 2008), Springer, March 2008. DOI 10.1007/978-3-540-78800-3_24.**
   Fetched: https://www.microsoft.com/en-us/research/publication/z3-an-efficient-smt-solver/ (title, authors, venue, publisher, DOI, date); also listed at https://www.microsoft.com/en-us/research/people/nbjorner/publications/. LNCS volume and page numbers were not shown, so they are omitted.
   Why it matters: the solver used to check the compiled rule set for consistency and to return unsatisfiable cores that localize conflicting rules.

4. **Pan, Liangming; Albalak, Alon; Wang, Xinyi; Wang, William Yang. "Logic-LM: Empowering Large Language Models with Symbolic Solvers for Faithful Logical Reasoning." *Findings of the Association for Computational Linguistics: EMNLP 2023*, Singapore, December 2023, pp. 3806–3824. DOI 10.18653/v1/2023.findings-emnlp.248.**
   Fetched: ACL Anthology source record in https://github.com/acl-org/acl-anthology (file `data/xml/2023.findings.xml`, git clone); authors' BibTeX in https://github.com/teacherpeterpan/Logic-LLM. Note: the Anthology record spells the last author "William Wang"; the authors' BibTeX uses "William Yang Wang".
   Why it matters: canonical "LLM formalizes, symbolic solver decides" architecture; our pipeline generalizes it from single questions to a whole regulatory document and removes the model from decision time.

5. **Olausson, Theo X.; Gu, Alex; Lipkin, Ben; Zhang, Cedegao E.; Solar-Lezama, Armando; Tenenbaum, Joshua B.; Levy, Roger P. "LINC: A Neurosymbolic Approach for Logical Reasoning by Combining Language Models with First-Order Logic Provers." *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing*, Singapore, December 2023, pp. 5153–5176. DOI 10.18653/v1/2023.emnlp-main.313.** (Authors' README marks the first four as equal contributors.)
   Fetched: ACL Anthology source record (`data/xml/2023.emnlp.xml`, same repo as above); authors' BibTeX in https://github.com/benlipkin/linc.
   Why it matters: shows that translating text to first-order logic and letting a prover execute beats letting the model reason — the same division of labour as our typed rules plus z3.

6. **Ye, Xi; Chen, Qiaochu; Dillig, Isil; Durrett, Greg. "SatLM: Satisfiability-Aided Language Models Using Declarative Prompting." NeurIPS 2023 (authors' BibTeX: "Proceedings of NeurIPS", 2023).** [author-repo]
   Fetched: https://github.com/xiye17/SAT-LM (README citation block, git clone). The NeurIPS proceedings page was not reachable; no DOI/pages given.
   Why it matters: has the LLM emit declarative constraints that a SAT/SMT solver discharges — the precedent for compiling rules into z3-checkable form rather than executing them in the model.

7. **Sun, Chuyue; Sheng, Ying; Padon, Oded; Barrett, Clark. "Clover: Closed-Loop Verifiable Code Generation." arXiv:2310.17807 [cs.SE], 2023.** [author-repo]
   Fetched: https://github.com/ChuyueSun/Clover (README citation block, git clone). A later conference version was not verified, so none is cited.
   Why it matters: checks mutual consistency of code, docstring and formal annotation before accepting generated code — the same closed-loop acceptance test we apply between quote, typed statement and Python rule.

8. **Wu, Haoze; Barrett, Clark; Narodytska, Nina. "Lemur: Integrating Large Language Models in Automated Program Verification." *The Twelfth International Conference on Learning Representations* (ICLR 2024).** [author-repo]
   Fetched: https://github.com/ai-ar-research/Lemur-program-verification (README citation block, git clone; links arXiv 2310.04870).
   Why it matters: a sound calculus in which LLM proposals are admitted only after a verifier validates them — the formal justification for treating the model as an untrusted oracle behind a symbolic gate.

9. **Dahl, Matthew; Magesh, Varun; Suzgun, Mirac; Ho, Daniel E. "Large Legal Fictions: Profiling Legal Hallucinations in Large Language Models." *Journal of Legal Analysis* 16(1): 64–93, 2024. DOI 10.1093/jla/laae003.** [author-repo]
   Fetched: https://github.com/reglab/legal_hallucinations (README "Please cite our article as follows", git clone).
   Why it matters: measures how often general LLMs fabricate legal content — the failure mode the zero-fabrication (byte-exact quote) guarantee is designed to eliminate.

10. **Willard, Brandon T.; Louf, Rémi. "Efficient Guided Generation for Large Language Models." arXiv:2307.09702, 2023.** [author-repo]
    Fetched: https://github.com/dottxt-ai/outlines (README "Cite Outlines", git clone).
    Why it matters: finite-state constrained decoding is how the proposer is forced to emit schema-valid typed rule statements, so type errors are prevented at generation rather than repaired later.

11. **Beurer-Kellner, Luca; Fischer, Marc; Vechev, Martin. "Guiding LLMs The Right Way: Fast, Non-Invasive Constrained Generation." *Proceedings of the 41st International Conference on Machine Learning* (ICML 2024), PMLR 235: 3658–3673, 2024.**
    Fetched: PMLR's volume source https://github.com/mlresearch/v235 (file `_posts/2024-07-08-beurer-kellner24a.md`, git clone; this is the data from which proceedings.mlr.press/v235/beurer-kellner24a.html is generated; lists title, authors, container title, volume, pages, date).
    Why it matters: shows constrained decoding can be subword-aligned so it does not degrade task accuracy — evidence that forcing typed output does not cost extraction quality.

#### Additional works (8)

12. **Pennisi, Andrea; González Hernández, Elvira; Koivula, Nina. "NOMOS: Navigating Obligation Mining in Official Statutes." *Proceedings of the Natural Legal Language Processing Workshop 2023*, Singapore, December 2023, pp. 8–16. DOI 10.18653/v1/2023.nllp-1.2.** (category a)
    Fetched: ACL Anthology source record in https://github.com/acl-org/acl-anthology (file `data/xml/2023.nllp.xml`, git clone).
    Why it matters: obligation extraction from statutes is the direct precursor of our sentence-by-sentence typed statement extraction (definitions, conditions, steps, reserved decisions).

13. **Holzenberger, Nils; Van Durme, Benjamin. "Connecting Symbolic Statutory Reasoning with Legal Information Extraction." *Proceedings of the Natural Legal Language Processing Workshop 2023*, Singapore, December 2023, pp. 113–131. DOI 10.18653/v1/2023.nllp-1.12.** (categories a, b)
    Fetched: ACL Anthology source record (`data/xml/2023.nllp.xml`).
    Why it matters: bridges information extraction from statute text to a symbolic statutory reasoner — the same extraction-to-formal-rule handoff, and it evaluates on statutory-reasoning benchmarks.

14. **Guha, Neel; Nyarko, Julian; Ho, Daniel E.; Ré, Christopher; Chilton, Adam; Narayana, Aditya; Chohlas-Wood, Alex; Peters, Austin; Waldon, Brandon; Rockmore, Daniel N.; Zambrano, Diego; Talisman, Dmitry; Hoque, Enam; Surani, Faiz; Fagan, Frank; Sarfaty, Galit; Dickinson, Gregory M.; Porat, Haggai; Hegland, Jason; Wu, Jessica; Nudell, Joe; Niklaus, Joel; Nay, John; Choi, Jonathan H.; Tobia, Kevin; Hagan, Margaret; Ma, Megan; Livermore, Michael; Rasumov-Rahe, Nikon; Holzenberger, Nils; Kolt, Noam; Henderson, Peter; Rehaag, Sean; Goel, Sharad; Gao, Shang; Williams, Spencer; Gandhi, Sunny; Zur, Tom; Iyer, Varun; Li, Zehua. "LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models." arXiv:2308.11462 [cs.CL], 2023.** [author-repo] (category b)
    Fetched: https://github.com/HazyResearch/legalbench (README citation block, git clone). The NeurIPS Datasets & Benchmarks venue was not verified and is omitted.
    Why it matters: the standard legal-reasoning benchmark (including rule-application tasks) against which compiled, deterministic rule evaluation can be compared to direct LLM answering.

15. **Rashkin, Hannah; Nikolaev, Vitaly; Lamm, Matthew; Aroyo, Lora; Collins, Michael; Das, Dipanjan; Petrov, Slav; Tomar, Gaurav Singh; Turc, Iulia; Reitter, David. "Measuring Attribution in Natural Language Generation Models." *Computational Linguistics* 49(4): 777–840, December 2023. DOI 10.1162/coli_a_00486.** (category c)
    Fetched: ACL Anthology source record (`data/xml/2023.cl.xml`, git clone).
    Why it matters: defines "attributable to identified sources" (AIS), the evaluation frame in which byte-exact quote grounding is the strongest possible attribution.

16. **Bjørner, Nikolaj (Microsoft Research); Jayaraman, Karthick (Microsoft Azure). "Checking Cloud Contracts in Microsoft Azure."** (category d)
    Fetched: author-version PDF hosted by Microsoft Research, https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/nbjorner-icdcit2015.pdf (page 1 shows title, authors, affiliations, abstract). The fetched page does not show the venue or year; search-result titles attribute it to ICDCIT 2015 (LNCS 8956), which was not fetched and is therefore not included in the citation.
    Why it matters: Z3 continuously checking production access-control and routing rule sets for contract violations in industry — precedent for SMT-based consistency checking of a compiled rule set at scale.

17. **Gligorić, Kristina; Zrnic, Tijana; Lee, Cinoo; Candès, Emmanuel; Jurafsky, Dan. "Can Unconfident LLM Annotations Be Used for Confident Conclusions?" *Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)*, Albuquerque, April 2025, pp. 3514–3533. DOI 10.18653/v1/2025.naacl-long.179.** (category e)
    Fetched: ACL Anthology source record (`data/xml/2025.naacl.xml`, git clone).
    Why it matters: gives a statistically valid way to combine LLM outputs with a human-verified subset — the principled basis for the one-confirmation-per-sentence reviewer step and for reporting confidence over the compiled rule set.

18. **Coupette, Corinna; Beckedorf, Janis; Hartung, Dirk; Bommarito, Michael; Katz, Daniel Martin. "Measuring Law Over Time: A Network Analytical Framework with an Application to Statutes and Regulations in the United States and Germany." *Frontiers in Physics* 9, 2021. DOI 10.3389/fphy.2021.658463.** [author-repo] (category f)
    Fetched: authors' organisation repositories https://github.com/QuantLaw/Measuring-Law-Over-Time and https://github.com/QuantLaw/legal-data-preprocessing (README citations, git clone). The Frontiers page was not reachable; article number omitted.
    Why it matters: models statutes and regulations as cross-reference/dependency networks — the framing behind ordering steps by precedence with networkx and detecting cycles.

19. **Endres, Madeline; Fakhoury, Sarah; Chakraborty, Saikat; Lahiri, Shuvendu. "Can Large Language Models Transform Natural Language Intent into Formal Method Postconditions?" *The ACM International Conference on the Foundations of Software Engineering* (FSE 2024), July 2024. DOI 10.1145/3660791.** (category g)
    Fetched: https://www.microsoft.com/en-us/research/publication/formalizing-natural-language-intent-into-program-specifications-via-large-language-models/ (title, authors, venue, year, DOI).
    Why it matters: NL-to-formal-specification synthesis validated by tests — the nearest analogue to drafting each rule as a typed Python function and validating it with mypy and Hypothesis.

#### Verified alternates (not counted toward the 8; swap in if preferred)

- **Gao, Tianyu; Yen, Howard; Yu, Jiatong; Chen, Danqi. "Enabling Large Language Models to Generate Text with Citations." *Proceedings of EMNLP 2023*, Singapore, December 2023, pp. 6465–6488. DOI 10.18653/v1/2023.emnlp-main.398.** Fetched: ACL Anthology source record (`data/xml/2023.emnlp.xml`); authors' BibTeX in https://github.com/princeton-nlp/ALCE. (category c — citation-grounding evaluation.)
- **Cosler, Matthias; Hahn, Christopher; Mendoza, Daniel; Schmitt, Frederik; Trippel, Caroline. "nl2spec: Interactively Translating Unstructured Natural Language to Temporal Logics with Large Language Models." *Computer Aided Verification* (CAV 2023), Lecture Notes in Computer Science, Springer Nature Switzerland, Cham, eds. Constantin Enea and Akash Lal, 2023, pp. 383–396. DOI 10.1007/978-3-031-37703-7_18.** [author-repo] Fetched: https://github.com/realChrisHahn2/nl2spec (Readme BibTeX, git clone). (category g — interactive human-in-the-loop NL-to-formal-spec.)
- **Chakraborty, Saikat; Ebner, Gabriel; Bhat, Siddharth; Fakhoury, Sarah; Fatima, Sakina; Lahiri, Shuvendu; Swamy, Nikhil. "Towards Neural Synthesis for SMT-Assisted Proof-Oriented Programming." *International Conference on Software Engineering* (ICSE 2025), April 2025.** Fetched: https://www.microsoft.com/en-us/research/publication/towards-neural-synthesis-for-smt-assisted-proof-oriented-programming/ (no DOI shown). (categories d, g — LLM proposals checked by an SMT-backed verifier.)

---

### Unverified

No metadata below should be cited until a canonical page is opened. Where search-result snippets (never fetched pages) showed metadata, it is reported only as "search snippets say", for re-checking.

- **Candidate 2 — Sergot, Sadri, Kowalski, Kriwaczek, Hammond, Cory, "The British Nationality Act as a Logic Program" (CACM 1986?).** Tried: dl.acm.org, cacm.acm.org, dlnext.acm.org, doi.org/dx.doi.org, Crossref (API, search, data.crossref.org, crosscite), Semantic Scholar, dblp (dblp.org, dblp.uni-trier.de, dblp.dagstuhl.de), OpenAlex, OpenCitations, Unpaywall, OpenAIRE, BASE, Scilit, ScienceOpen, OUCI, scite, Kowalski's Imperial page, Bing, Google Scholar — all blocked by the egress proxy. No author-maintained GitHub source exists. Not verified.
- **Candidate 3 — OECD OPSI, "Cracking the code: Rulemaking for humans and machines" (2020?).** Tried: oecd-opsi.org, www.oecd.org, www.oecd-ilibrary.org, read.oecd-ilibrary.org, doi.org, RePEc (ideas + EconPapers), Digital Government Hub, logic.stanford.edu mirror, Zenodo — all blocked. GitHub code search found only third-party citations (no OECD/OPSI-owned file). Search snippets say: James Mohun and Alex Roberts, OECD Working Papers on Public Governance No. 42, 2020, DOI 10.1787/3afe6ba5-en. Not verified.
- **Candidate 4 — Athan et al., LegalRuleML (~2013).** Tried: dl.acm.org, academia.edu, Swansea Cronfa, governatori.net, docs.oasis-open.org, oasis-open.org TC page, wiki.ruleml.org — all blocked. The OASIS TC's own repository (https://github.com/oasis-tcs/legalruleml) is reachable but contains no citation of the ICAIL paper. Search snippets say: Tara Athan, Harold Boley, Guido Governatori, Monica Palmirani, Adrian Paschke, Adam Wyner, "OASIS LegalRuleML", ICAIL 2013, pp. 3–12, DOI 10.1145/2514601.2514603. Not verified.
- **Candidate 5 — Claessen & Hughes, "QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs" (ICFP 2000).** Tried: dl.acm.org, Chalmers (two hosts), Tufts and Northwestern PDF mirrors, CiteSeerX — blocked; Hackage (reachable) and the QuickCheck repository (https://github.com/nick8325/quickcheck, cloned) show Koen Claessen as the software author but do not cite the paper. Partial, non-canonical evidence: the JOSS Crossref deposit for Hypothesis lists reference DOI 10.1145/351240.351266 (no title attached), and third-party bib files circulate **two different DOIs** for this paper (10.1145/351240.351266 — proceedings; 10.1145/357766.351266 — SIGPLAN Notices issue). Not verified; pick the DOI deliberately once a canonical page is opened.
- **Candidate 8 — Liffiton & Sakallah, "Algorithms for computing minimal unsatisfiable subsets of constraints" (JAR 2008?).** Tried: link.springer.com, rd.springer.com, Sakallah's and Liffiton's homepages — blocked; no author-owned GitHub file cites it. Not verified.
- **Candidate 9 — Garcez & Lamb, "Neurosymbolic AI: The 3rd Wave" (Artif. Intell. Rev. 2023 / arXiv 2020).** Tried: arXiv (three hosts), Springer, City Research Online, Lamb's UFRGS page, Zenodo — blocked. No author repository. Not verified.
- **Candidate 10 — Kautz, "The Third AI Summer" (AI Magazine 2022).** Tried: Wiley Online Library, AAAI OJS, aaai.org, Rochester and henrykautz.com pages, Zendy — blocked. Search snippets say: AI Magazine 43(1): 105–125, 2022, and show **two DOIs in circulation** (10.1002/aaai.12036 at Wiley; 10.1609/aimag.v43i1.19122 at AAAI OJS). Not verified; the title also appears with the subtitle "AAAI Robert S. Engelmore Memorial Lecture" — check which form the publisher uses.
- **Candidate 16 — First, Rabe, Ringer, Brun, "Baldur: Whole-Proof Generation and Repair with Large Language Models" (ESEC/FSE 2023).** Tried: dl.acm.org, arXiv, Illinois Experts, 2023.esec-fse.org, UMass (Brun) page, dependenttyp.es, research.google — blocked; GitHub search found only third-party reading lists, no author-owned citation file. Search snippets say: ESEC/FSE 2023, pp. 1229–1241, DOI 10.1145/3611643.3616243. Not verified.
- **Candidate 18 — Magesh, Surani, Dahl, Suzgun, Manning, Ho, "Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools" (2024; JELS 2025?).** Tried: Wiley, arXiv, dho.stanford.edu PDF, hai.stanford.edu, isps.yale.edu, RePEc — blocked; no RegLab GitHub repository for this paper was found (unlike Candidate 17). Search snippets say: Journal of Empirical Legal Studies 22(2): 216–242, 2025, DOI 10.1111/jels.12413; arXiv 2405.20362. Not verified.
- **Candidate 19 — Lamb & Zacchiroli, "Reproducible Builds: Increasing the Integrity of Software Supply Chains" (IEEE Software 2022).** Tried: IEEE Xplore, computer.org CSDL, upsilon.cc, chris-lamb.co.uk, reproducible-builds.org, arXiv, HAL — blocked; a GitHub search of the reproducible-builds organisation returned nothing. Warning: third-party citations found on GitHub disagree on the issue number (39(2) vs 39(3)) and some garble the authors' first names — do not cite from memory.
- **Candidate 20 — Cohen, "A Coefficient of Agreement for Nominal Scales" (Educ. Psychol. Meas. 1960).** Tried: SAGE, APA PsycNet, Wikipedia, PMC (a citing article's reference list), Garfield "Citation Classic" PDF, Wikidata/Scholia — blocked. Not verified.
- **Candidate 23 — Horace He et al., Thinking Machines Lab, "Defeating Nondeterminism in LLM Inference" (2025).** thinkingmachines.ai is blocked. Partial evidence: the lab's companion repository https://github.com/thinking-machines-lab/batch_invariant_ops (README, git clone) describes itself as "a companion library release to https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/", which confirms the post's URL and title slug but shows no byline or date. Search snippets say: by Horace He, Thinking Machines Lab, September 2025. Authorship and date not verified.

**Extras considered but not verifiable in this session (not listed above):** Katz & Bommarito 2014 (Artif. Intell. Law), Sleimi et al. (RE 2018 / EMSE 2021), Backes et al. Zelkova (FMCAD 2018), Goldstein et al. "Property-Based Testing in Practice" (ICSE 2024), Pangakis et al. "Automated Annotation with Generative AI Requires Validation" (arXiv 2023), Holzenberger et al. SARA dataset (NLLP 2020, CEUR) — every host for these was blocked and no author-owned citation file was found.

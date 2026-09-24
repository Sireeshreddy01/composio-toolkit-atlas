# Toolkit Atlas — Composio AI Product Ops assessment

A single-page case study covering all 100 apps in the assignment: what they do, authentication, development access, API breadth, existing MCP evidence, buildability and primary sources.

- **Live case study:** https://sireeshreddy01.github.io/composio-toolkit-atlas/
- **Research date:** 24 September 2026
- **Scope:** public documentation research, not authenticated integration testing.
- **AI disclosure:** Codex performed research, semantic review, implementation and browser checks. Independent human checks remain pending and are explicitly shown on the page.

## Run in under a minute

Python 3.9+; standard library only. No package installation, model subscription or API keys are required to reproduce the frozen output.

```sh
git clone https://github.com/Sireeshreddy01/composio-toolkit-atlas.git
cd composio-toolkit-atlas
python3 run.py
python3 -m http.server 8000
```

Open http://localhost:8000. You can also open `index.html` directly: all case-study data, styling and JavaScript are embedded. Filters and exports work without a backend.

## Run the research collector

```sh
python3 run.py --refresh             # all 100 seed URLs, new timestamped run
python3 run.py --refresh --limit 5   # small live smoke run
python3 run.py --check-sources       # refresh cited-source retrieval ledger
```

Live collection requires internet access. It fetches only public URLs; it never signs into apps, creates accounts or calls authenticated business APIs. Eight workers, a 25-second timeout per URL and a 3 MB response cap keep the collector bounded. Output goes to ignored `runs/`, preserving the baseline and reviewed facts.

`--refresh` collects new **candidate signals**, not new verified conclusions. The research is a hybrid agent/script workflow: Python performs repeatable collection, and the Codex agent searches and interprets primary evidence. To repeat the semantic stage, use [RESEARCH_PROMPT.md](RESEARCH_PROMPT.md) with a browsing-capable agent and review its changes. No Composio SDK implementation or autonomous fact-validation capability is claimed.

## What the workflow does

1. Freeze the 100 app identities and categories in `data/apps.tsv`.
2. Collect page text, timestamps, status, content hash and keyword guesses using `scripts/research.py`.
3. Have the agent verify the scoped product, auth, account path, API resources and MCP evidence against vendor documentation. Keep unknowns explicit in `data/reviewed.tsv` and `data/mcp.json`.
4. Cross-check a reproducible diagnostic sample of two apps per category. Use browser rendering for dynamic pages and a documentation index for stale URLs. Preserve initial predictions and actual revisions.
5. Run `scripts/build.py` to validate the set, compute counts and emit `index.html`, `data/atlas.json` and `data/atlas.csv`.

The initial HTTP pass returned 85 successful fetches out of 100 in 30.99 seconds. That is the collector runtime only, not total research time. Semantic interpretation and browser investigation took additional work.

## Verification and honest limits

The sample was selected before writing the reviewed dataset, using seed 20260924 and two IDs per category. All 20 IDs are preserved in `data/sample-plan.json`.

The diagnostic rubric examines 60 fields: auth, REST/GraphQL-family protocol and development-access status for each sampled app. Unknowns count as incomplete. The baseline has 12 supported fields; the evidence-reviewed output has 53. Seven access fields remain unresolved.

**This is same-agent documentation agreement and completion, not independent accuracy.** The same agent authored the findings and rubric checks. Auth credit means at least one predicted method is supported, not that all methods are exhaustively validated. HTTP resource APIs are normalized to the REST family. MCP coverage, API breadth and buildability are outside the 60-field score. Do not generalize this sample to all 100 apps.

Real failures include:

- Freshdesk: an unrelated Enterprise keyword made a trial-capable API look gated.
- Mailchimp and MongoDB Atlas: navigation text caused incorrect GraphQL guesses.
- Gumroad: the plain HTTP collector saw a shell; the browser exposed the OAuth/REST documentation.
- Squarespace: the paid custom-app restriction does not apply uniformly to OAuth Extensions.
- Consensus: the old MCP documentation returned 404; current docs established a shared free API/MCP allowance.
- iPayX: REST documentation disagreed on base URL and payload shape. A separate MCP page established a free path; the integration remains conditional pending contract clarification.

HTTP 200 checks establish retrievability only. The source ledger preserves errors and blocked pages. Sources were also examined through search results and browser rendering; an HTTP failure is not a claim that the API is absent.

No authenticated app calls, paid accounts, production mutations or independent human checks were completed. Paygent Connect's identity and PitchBook's exact API contract remain unresolved. `Account check` indicates a gap in this research, not a claim that the API must be paid.

## Decision labels

- **Build:** documentation supports a free, trial, sandbox or local path for the scoped prototype. Production permissions, billing and distribution review can still apply.
- **Conditional:** a plan, admin, approval, customer-access or API-contract question needs resolution.
- **Investigate:** insufficient product identity or contract detail to choose an implementation.

Auth methods are non-exclusive; API key, Basic and token categories can overlap. Existing MCP evidence includes beta and partial implementations. `Not established` means no implementation was confirmed in checked sources; it does not prove absence. Breadth is described by resource families rather than invented endpoint counts.

Some development-access judgments combine multiple sources. Linear combines Free-plan admin roles with admin API-key rights. Supabase combines free projects with project API credentials. Coda combines all-plan API limits with its token documentation. Those rows explicitly label the inference and scope; no signup or credential issuance was tested.

## Files

- `index.html`: self-contained deliverable.
- `site/template.html`: editable page template.
- `data/apps.tsv`: frozen app set and seed URLs.
- `data/first-pass.json`: frozen real collector output, with copyrighted snippets omitted; guesses, hashes and timings preserved.
- `data/review-pass1.tsv`: first enriched draft, before later corrections.
- `data/reviewed.tsv`, `data/mcp.json`: current agent-reviewed evidence.
- `data/revisions.json`: actual before/after revisions after the first enriched draft.
- `data/sample-plan.json`, `data/audit.json`: sample design, review rubric and findings.
- `data/source-checks.json`: source retrieval metadata.
- `data/atlas.json`, `data/atlas.csv`: generated machine-readable data.
- `data/human-review.json`: pending human review record; never mark complete without a person checking.
- `scripts/research.py`, `scripts/verify_sources.py`, `scripts/build.py`: collector, source check and offline build.
- `RESEARCH_PROMPT.md`: instructions for repeating the semantic agent pass.
- `CANDIDATE_GUIDE.md`: plain-language explanation and interview preparation.

## Human handoff

The brief asks for human checks and candidate understanding. The page includes five targeted primary-source checks. A person must inspect them, record actual findings and corrections, and understand the workflow before representing those checks as complete. Update the review record and page only after that happens.

Submission requires the live-page URL and this repository URL. The form also asks for one file. The self-contained HTML or packaged source can be supplied, subject to its allowed file types. The form has not been submitted by this repository's workflow.

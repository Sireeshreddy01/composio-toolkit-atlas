# Toolkit Atlas — Composio AI Product Ops assessment

A single-page case study covering all 100 apps in the assignment: what they do, authentication, development access, API breadth, existing MCP evidence, buildability and primary sources.

- **Live case study:** https://sireeshreddy01.github.io/composio-toolkit-atlas/
- **Research date:** 24 September 2026
- **Scope:** public documentation research, not authenticated integration testing.
- **AI disclosure:** Codex performed research, semantic review, implementation and browser checks. Independent human checks remain pending and are explicitly shown on the page.

## Read or present the case study

The page has six sections: executive summary, key findings, recommendations, method and validation, the application library, and next steps. **Start presentation** opens a guided section-by-section view; a dismissible first-visit tip explains navigation. Use the buttons or arrow keys to advance, or Escape to exit. The app grid and library open evidence records. Filters and exports include selected records.

### Run directly on the page

Select **Try an example** or **Run checks here**. No installation is needed:

1. **Research example:** four steps replay the saved Freshdesk finding from an incorrect access prediction to the reviewed record and proposed implementation test. This does not perform a new source review.
2. **Run dataset checks:** JavaScript checks all 100 embedded records, category and source coverage, recomputes summary counts, and recalculates the 20-app diagnostic sample from initial predictions and reviewed rows against the saved agent-authored rubric. Results and exact executable code are visible; the result can be downloaded as JSON. This is consistency checking, not independent fact verification.
3. **Assessment API console:** prominently linked from the landing page and header. It makes real GET requests for this project's published JSON resources: an app record, all 100 app assessments, category findings, recommendations, source evidence and verification results. Edit app IDs or category slugs; inspect the response body, browser-exposed headers, HTTP status, byte count and timing. Cancel, copy cURL or download the result. These are static research data endpoints, not fresh vendor API calls or a live model execution. No sign-in, API key or local installation.
4. **Research run:** inspect the recorded automated research execution by app and claim. See source links, retrieval timestamps, citation hashes/binding results, second-pass judgments and remaining uncertainty. Download the full sanitized run. This is explicitly a recorded run, not a simulated new AI invocation.

**The self-contained HTML has the same tools.** Research, replay and dataset checks work offline. Live API requests need internet and a browser that permits the published site’s CORS policy. Open the HTML in a browser, not a cloud-drive preview that disables scripts.

All 100 apps now have a distinct proposed workflow, next action, observable pass condition and alternative/follow-up route in `data/action-plans.json`. These are plans, not completed integration tests. Five feasibility experiments are prioritized: GitHub public reads, Freshdesk trial ticket reads, Linear GraphQL issue queries, Stripe test customers and Mermaid local rendering. Customer demand and engineering cost must still determine commercial priority.

The visual design pairs a warm paper landing page with a charcoal presentation stage, orange accents, embedded Geist / Geist Mono typography and a clickable 100-app integration map. Research references: [Composio’s current homepage](https://composio.dev/) for its technical typography and dark product presentation, and [Y Combinator](https://www.ycombinator.com/) for its restrained orange and warm neutral palette. This is an original assessment presentation, not an official Composio or YC site; their logos and artwork are not reproduced.

`site/report.css` contains the design system. The build embeds that CSS and local WOFF2 fonts into the single HTML deliverable so the design works offline. Font files were obtained through Google Fonts; SIL Open Font License notices are included in `site/fonts/` and in the generated HTML.

## Run in under a minute

Python 3.9+; standard library only. No package installation, model subscription or API keys are required to reproduce the frozen output.

```sh
git clone https://github.com/Sireeshreddy01/composio-toolkit-atlas.git
cd composio-toolkit-atlas
python3 run.py
python3 -m http.server 8000
```

Open http://localhost:8000. You can also open `index.html` directly: all case-study data, styling and JavaScript are embedded. Filters and exports work without a backend.

## Run a fresh research and verification pipeline (optional)

Reviewers do not need this setup to examine the submission or send live requests on the page. Reproducing a **new model-backed run** requires Python 3.9+, internet and the [official Codex CLI](https://developers.openai.com/codex/cli/) signed in with a supported account. The runner preserves the user's model configuration and does not embed credentials in the deliverable.

```sh
python3 run.py --research --ids 13,46       # two-app semantic smoke run
python3 run.py --research                  # all 100 apps, batches of five
python3 run.py --resume runs/<run-directory> # retry incomplete batches
python3 run.py --refresh --limit 5         # original keyword baseline collector
python3 run.py --check-sources             # cited-source HTTP metadata only
```

The semantic runner performs the full sequence:

1. Load the app identities and previously discovered official URLs, **withholding reviewed answers** from model inputs. It does not claim independent source discovery.
2. Fetch public source pages with eight workers, a 25-second timeout and 3 MB cap. Remove navigation/scripts and select bounded excerpts balanced across auth, development access, API surface and MCP.
3. Invoke `codex exec` for schema-constrained extraction with exact source citations.
4. Invoke a separate-context verification pass to challenge the scope and semantic support of every claim.
5. Bind each citation to the correct app/source and normalized source text. Reject invented quotes, failed sources and missing or duplicate verification fields. Preserve inferred/unresolved/conflicting claims.
6. Derive conservative decisions and generate `report.json` and `report.html` in a new ignored `runs/` directory. Resume reuses the frozen packet and completed validated batches; it does not silently refresh old evidence.

**Published execution scope:** the expanded run collected 320 public sources for all 100 apps (264 readable HTTP results) and completed semantic verification for 20 apps before packaging. The remaining 80 are not claimed as freshly verified by that run; they retain the separate 100-app documentation-reviewed dataset. The fully completed two-app smoke runs are also preserved. A post-run AI check corrected Close's overly broad self-serve classification; the original decision and reason are retained.

The runner's packet, prompts and model logs remain local because they contain copied source passages. The published `data/research-run.json` retains original summaries, source metadata, hashes, offsets and judgments without republishing the raw documents. Reviewed records are not automatically overwritten by an incomplete HTTP-only pass. The browser viewer exposes differences between the two layers.

A real two-app regression test improved supported fields from **1/8 to 5/8** after fixing source-excerpt selection. `data/retrieval-iteration.json` preserves the before/after outputs. This is retrieval and claim-support improvement, **not an independent accuracy score**.

Dynamic pages, access gates and incomplete source indexes can still require browser investigation. The verifier is the same model in a fresh context; citation binding establishes occurrence, not truth. No Composio SDK or Composio MCP execution is claimed. Composio's brief encourages them but does not require that implementation.

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
- `site/template.html`: editable page structure and reviewer tools.
- `site/report.css`, `site/fonts/`: visual system and embedded, licensed typography.
- `data/apps.tsv`: frozen app set and seed URLs.
- `data/first-pass.json`: frozen real collector output, with copyrighted snippets omitted; guesses, hashes and timings preserved.
- `data/review-pass1.tsv`: first enriched draft, before later corrections.
- `data/reviewed.tsv`, `data/mcp.json`: current agent-reviewed evidence.
- `data/revisions.json`: actual before/after revisions after the first enriched draft.
- `data/sample-plan.json`, `data/audit.json`: sample design, review rubric and findings.
- `data/source-checks.json`: source retrieval metadata.
- `data/atlas.json`, `data/atlas.csv`: generated machine-readable data.
- `data/human-review.json`: pending human review record; never mark complete without a person checking.
- `scripts/research_pipeline.py`, `schemas/`, `prompts/`: end-to-end semantic research runner.
- `data/research-run.json`: sanitized recorded pipeline output, embedded in the HTML.
- `data/retrieval-iteration.json`: actual before/after source-selection regression.
- `data/action-plans.json`: 100 specific workflows, pass criteria and follow-up routes.
- `data/agent-spotchecks.json`: fresh AI source checks, explicitly distinct from human review.
- `scripts/research.py`, `scripts/verify_sources.py`, `scripts/build.py`: baseline collector, source check and offline build.
- `RESEARCH_PROMPT.md`: instructions for repeating the semantic agent pass.
- `CANDIDATE_GUIDE.md`: plain-language explanation and interview preparation.

## Human handoff

The brief asks for human checks and candidate understanding. The page includes five targeted primary-source checks. A person must inspect them, record actual findings and corrections, and understand the workflow before representing those checks as complete. Update the review record and page only after that happens.

Submission requires the live-page URL and this repository URL. The form also asks for one file. The self-contained HTML or packaged source can be supplied, subject to its allowed file types. The form has not been submitted by this repository's workflow.

## Interface validation

Run `node tests/reviewer-tools.test.cjs` to check the exact functions embedded in the HTML template: corrupted dataset inputs, request/parameter validation, host restriction, full response retention, headers, schema mismatches, HTTP/network failures and cancellation. Run `python3 -m unittest discover -s tests -p 'test_*.py'` for fabricated citations, wrong-app sources, failed HTTP evidence, missing/duplicate verification, semantic rejection and the long-index regression. Failure-path unit tests use fixtures, not vendor requests.

The earlier browser demo also made a real public GitHub request during UI verification on 24 September 2026: HTTP 200, expected repository response, 446 ms. The sanitized result is saved in `evidence/github-public-read.json`. This is one unauthenticated public read, separate from the 100-app documentation study and its unchanged authenticated-test count.

The final console replaces generic repository metadata requests with assessment-specific JSON endpoints generated under `api/`. They serve the same versioned research as the HTML. Request parameters choose actual app/category resource paths. The public-data demo is explicitly distinct from authenticated tests of vendor integrations.

All six final assessment-resource requests returned HTTP 200 in a real browser, including cross-origin reads from the local single-file preview. See `evidence/assessment-console-browser-checks.json`.

# Repeat the semantic research pass

Use a browsing-capable agent with this repository as context. This prompt documents the operational workflow; it is not a transcript of private reasoning and does not claim a single unattended LLM call produced all findings.

## Task

Research every row of `data/apps.tsv`. Preserve IDs and categories. Begin with `python3 run.py --refresh` and examine the new run. Treat keyword outputs as untrusted candidate signals.

For each app:

1. Resolve the intended product and deployment scope. Follow assignment hints. Do not silently substitute a similarly named vendor.
2. Find primary sources for authentication, credential creation, free/trial eligibility, paid/admin/partner gates and public API resource families.
3. Separate account signup from API entitlement, development from production, private use from distribution, and management APIs from product/data APIs.
4. Check for a vendor-supported MCP. Record exact scope and maturity. Do not infer a native MCP from support for hosting third-party servers. Do not claim absence from a failed search.
5. Write concise original summaries with source URLs. Label inferred and unresolved claims. Do not reproduce large documentation excerpts.
6. Assign Build, Conditional or Investigate using the README definitions. Do not call an untested API integration working.

Update `data/reviewed.tsv` and `data/mcp.json` only after reviewing evidence. Preserve `data/first-pass.json` and `data/review-pass1.tsv`. Append actual changed fields, reason, method and sources to `data/revisions.json`.

## Verification

Use the fixed `data/sample-plan.json` sample. Check auth, protocol and development access against the scoped documentation. A sampled row's access is Unknown if free/trial eligibility remains open; a public-app approval path alone must not make a private-key path universally gated.

Use a browser when HTTP returns an empty shell, a misleading page or stale URL. Record the tool/method actually used. An agent checking its own answer is not an independent human reviewer. Do not create test results, user checks, accounts or successful API responses that did not occur.

Run `python3 run.py --check-sources`, inspect errors without equating them to absent APIs, then `python3 run.py`. Have a person independently check the five human-review claims and record their actual date and findings.

# Understand the assessment before you submit

Composio needs to decide whether an app can become a tool an AI agent can call. The assignment is research and prioritization, not a requirement to build 100 integrations.

## Your 60-second explanation

“This case study covers all 100 requested apps. A Python collector fetched public documentation and generated rough guesses. Codex then researched vendor sources, checked a 20-app sample, used browser rendering where needed, and produced an interactive matrix with evidence. The early guesses made mistakes such as reading an Enterprise menu item as a pricing gate. The final page separates documented prototype paths, conditional integrations, and unresolved identity or contract questions. The checks establish documentation support, not that every API call works.”

The newer runner also performs structured extraction and a separate AI verification pass automatically, checks citations against collected text, and generates a fresh report. Reviewers can inspect its saved output on the website. The API console makes actual GET requests for published assessment records; it is separate from the documentation research. Neither demonstrates authenticated testing of all 100 apps. Composio SDK/MCP execution is not claimed.

Use that explanation only after you understand it. Do not claim you wrote code unaided or performed tests that did not happen.

## Terms in plain language

- **API:** the structured interface software uses to read or change an app's data.
- **API key / personal token:** a credential attached to a request. It normally has an owner and permissions.
- **OAuth2:** a user authorizes an integration to access selected resources. The integration gets a token instead of collecting the user's password.
- **Basic auth:** a username/password-shaped HTTP header. Some vendors put an API key in the username field; that still needs careful key handling.
- **REST:** APIs organized around resource endpoints. **GraphQL:** an API where the client requests fields through a schema. Meta's Graph API is not GraphQL.
- **MCP:** a protocol for exposing tools to AI clients. An existing MCP server can save integration work, but may expose only part of an app.
- **Sandbox:** a development environment with test data. Access does not imply permission to operate in production.
- **Self-serve:** a developer can get started without sales or a partner agreement. This case study distinguishes free/trial access from a paid self-serve subscription.

## What the numbers do and do not mean

The page computes its totals from the data; use the live page for current counts. Buildability is a documentation-based recommendation. A successful HTTP fetch only means a document was retrieved.

The sample checks 20 apps and 3 fields per app. Supported fields increased from 12/60 in the simple keyword baseline to 53/60 after agent evidence review. Seven access fields still lack a supported answer. This is not 88% independent accuracy: the same agent did the research and checking, auth only needs one supported method, and other fields are outside that metric.

## Five human checks to complete

Read the linked source and compare it with the app's row on the page. Report any disagreement. Do not simply mark the checklist without opening the sources.

1. **Salesforce:** the free Developer Edition route is separate from a customer's production API entitlement. [Source](https://developer.salesforce.com/docs/platform/api-rest/guide/quickstart-dev-org.html)
2. **Squarespace:** custom API-key applications require Commerce Advanced; OAuth Extensions can support customers on any plan. [Source](https://developers.squarespace.com/commerce-apis/authentication-and-permissions)
3. **iPayX:** the MCP guide describes 10 free audits/day. Two REST guides show different base URLs/payloads, so confirm the contract before coding. [MCP](https://www.ipayx.ai/docs/mcp-server), [REST](https://www.ipayx.ai/docs/api), [sandbox-labeled page](https://www.ipayx.ai/developers/sandbox)
4. **Consensus:** the current free tier provides 30 calls per month shared between API and MCP. The ordinary API key uses x-api-key. [Source](https://docs.consensus.app/api-plans-and-access)
5. **Mermaid CLI:** this is a local diagram-rendering program; an agent can invoke a bounded command without a remote account or OAuth. [Source](https://github.com/mermaid-js/mermaid-cli)

After checking, provide the date, your findings and any corrections. Human review stays pending until then.

## Likely interview questions

**Why not trust the first pass?** It sees words without reliably understanding their scope. “Enterprise” in navigation and “GraphQL” in an unrelated link caused real errors.

**Why so many conditional verdicts?** The docs often explain credentials without proving a free plan includes the intended API. Record the gap instead of inventing access.

**What would you build first?** A narrow read action in a documented free or sandbox environment, then one reversible write. Test scopes, errors, pagination and rate limits before broadening.

**How would you improve reliability?** Use structured API specifications, field-specific evidence, change detection and separate reviewers. Validate representative calls with authorized test credentials. Keep uncertainty and provenance in the output.

**What is still missing?** Independent human review, authenticated integration tests, and clarification of unresolved entitlements and product identity. The page says this openly.

## Give a reviewer the easiest route

Open the live page and choose **Start presentation** for the findings. Choose **Try the API console — No setup** to request app findings, category data, recommendations or verification evidence. The reviewer workspace also contains the Freshdesk example, saved dataset checks and the recorded research run. The complete HTML contains the same interface. Live requests need internet; the saved findings and checks do not. No reviewer needs to install the Python/Codex development environment merely to inspect your submission.

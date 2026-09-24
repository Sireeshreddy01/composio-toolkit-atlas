#!/usr/bin/env python3
"""Validate reviewed evidence and build the self-contained case study offline."""
import collections,csv,html,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
SELF={'Free','Sandbox','Trial','Local'}
GATED={'Paid','Admin / paid','Approval'}
def read_tsv(name):
    with (ROOT/'data'/name).open() as f:return list(csv.DictReader(f,delimiter='\t'))
def read_json(name):return json.loads((ROOT/'data'/name).read_text())
def normalized_surface(value):
    # Diagnostic rubric accepts documented HTTP resource APIs as REST-family.
    return 'GraphQL' if value.startswith('GraphQL') else 'REST' if ('REST' in value or 'HTTP' in value) else 'Unknown'
def access_group(value):return 'Self-serve' if value in SELF else 'Gated' if value in GATED else 'Unknown'
def next_action(row):
    """Planning recommendations derived from findings, never completed tests."""
    special={
        46:'Compare custom-app plan requirements with the OAuth Extensions route for the intended workflow.',
        84:'Obtain the exact vendor URL and product identity before choosing an integration route.',
        85:'Evaluate the documented MCP path; ask the vendor to reconcile the conflicting REST contracts.',
        90:'Request the licensed API contract, authentication details and a test-access option.',
        98:'Wrap local rendering as a bounded agent tool, then test a small diagram.'}
    if row['id'] in special:return special[row['id']]
    if row['verdict']=='Build':
        if row['access']=='Local':return 'Run a small local test, then define input, timeout and output limits.'
        if row['access']=='Sandbox':return 'Use an authorized sandbox and test one scoped workflow with test data.'
        if row['mcp']:return 'Compare the documented MCP tools with the target workflow, then test with authorized access.'
        return 'Use the documented development path and test one small, scoped API workflow.'
    actions={
        'Plan check':'Confirm the exact API allowance for a free or trial account; ask the vendor if the docs do not settle it.',
        'Admin':'Work with an authorized administrator to confirm tenant permissions and credential setup.',
        'Subscription':'Confirm the required plan and ask whether a developer sandbox or trial is available.',
        'Approval':'Map the app-review requirements and request approved developer or partner access.',
        'Customer access':'Obtain an authorized customer test tenant and confirm its API permissions.',
        'Production entitlement':'Separate sandbox testing from production approval and confirm the production requirements.',
        'Commercial access':'Request a scoped API agreement and a test-access option.',
        'Conflicting docs':'Ask the vendor to confirm the supported endpoint and request schema.'}
    return actions.get(row['blocker'],'Resolve the documented prerequisite, then compare supported API, MCP, CLI or export routes.')
def alternative_action(row):
    """Proposed authorized endpoint investigation, never a completed result."""
    if row['id']==84 or row['access']=='Local':return ''
    if row['verdict']=='Build':return ''
    return (f"In an authorized {row['app']} account, capture the browser requests for one read workflow. "
            "Identify the endpoint, HTTP method, parameters and response schema; reproduce the request with authorized access. "
            "Record session dependencies, pagination, limits and repeatability before implementing a tool wrapper. "
            "Use this route for features already available to that account.")
def build():
    seeds=read_tsv('apps.tsv'); reviewed=read_tsv('reviewed.tsv');mcp=read_json('mcp.json')
    baseline=read_json('first-pass.json');audit=read_json('audit.json');plan=read_json('sample-plan.json')
    assert len(seeds)==len(reviewed)==100
    assert [int(x['id']) for x in seeds]==[int(x['id']) for x in reviewed]==list(range(1,101))
    assert set(collections.Counter(x['category'] for x in seeds).values())=={10}
    assert sorted(x['id'] for x in audit['checks'])==plan['sample_ids']
    rows=[]
    for seed,row in zip(seeds,reviewed):
        item={**seed,**row,'id':int(row['id'])};item['auth']=row['auth'].split(',');item['sources']=[x for x in row['sources'].split(';') if x]
        assert item['sources'] or item['id']==84
        assert all(x.startswith('https://') for x in item['sources'])
        assert row['verdict'] in {'Build','Conditional','Investigate'}
        assert row['access'] in SELF|GATED|{'Account check','Unresolved'}
        item['access_group']=access_group(row['access']);item['mcp']=mcp.get(row['id']);item['next_action']=next_action(item);item['alternative_action']=alternative_action(item);rows.append(item)
    byid={x['id']:x for x in rows};first={x['id']:x for x in baseline['results']}
    evaluations=[]
    for check in audit['checks']:
        initial=first[check['id']];final=byid[check['id']]
        def assess(auth,surface,access):
            return [bool(set(auth)&set(check['auth'])),surface==check['surface'] and surface!='Unknown',access==check['access'] and access!='Unknown']
        before=assess([initial.get('auth_guess','Unknown')],initial.get('surface_guess','Unknown'),initial.get('access_guess','Unknown'))
        after=assess(final['auth'],normalized_surface(final['surface']),final['access_group'])
        evaluations.append({**check,'app':final['app'],'before':before,'after':after,'initial':{k:initial.get(k,'Unknown') for k in ('auth_guess','surface_guess','access_guess')},'sources':final['sources']})
    stats={'verdict':dict(collections.Counter(x['verdict'] for x in rows)),
      'access':dict(collections.Counter(x['access_group'] for x in rows)),
      'auth':dict(collections.Counter(a for x in rows for a in x['auth'])),
      'blocker':dict(collections.Counter(x['blocker'] for x in rows if x['verdict']!='Build')),
      'mcp':len(mcp),'sample_before':sum(sum(x['before']) for x in evaluations),'sample_after':sum(sum(x['after']) for x in evaluations),'sample_fields':len(evaluations)*3,
      'sample_unresolved':sum(x['access']=='Unknown' for x in evaluations),
      'initial_fetches':sum(x['status']==200 for x in baseline['results']), 'initial_seconds':baseline['elapsed_seconds']}
    source_checks=read_json('source-checks.json');stats['sources']=len(source_checks);stats['source_ok']=sum(x['status']==200 for x in source_checks)
    payload={'as_of':'2026-09-24','scope':'100 assignment apps; documentation review, not authenticated integration tests','rows':rows,'stats':stats,'audit':{**audit,'checks':evaluations},'sample_plan':plan,'revisions':read_json('revisions.json'),'source_checks':source_checks}
    data=json.dumps(payload,ensure_ascii=False).replace('</','<\\/')
    template=(ROOT/'site/template.html').read_text();assert template.count('@@DATA@@')==1
    (ROOT/'index.html').write_text(template.replace('@@DATA@@',data))
    (ROOT/'data/atlas.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False))
    fields=['id','app','category','description','auth','access','access_detail','surface','verdict','blocker','next_action','alternative_action','note','sources','mcp_kind','mcp_scope','mcp_url']
    with (ROOT/'data/atlas.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader()
        for row in rows:
            out={k:row.get(k,'') for k in fields};out['auth']='; '.join(row['auth']);out['sources']='; '.join(row['sources'])
            for k in ['kind','scope','url']:out['mcp_'+k]=(row['mcp'] or {}).get(k,'')
            writer.writerow(out)
    print(json.dumps({'validation':'passed','apps':100,'stats':stats},indent=2))
    return payload
if __name__=='__main__':build()

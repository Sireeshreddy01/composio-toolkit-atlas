#!/usr/bin/env python3
"""Validate reviewed evidence and build the self-contained case study offline."""
import base64,collections,csv,html,json,pathlib
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
def build():
    seeds=read_tsv('apps.tsv'); reviewed=read_tsv('reviewed.tsv');mcp=read_json('mcp.json')
    actions={x['id']:x for x in read_json('action-plans.json')}
    assert set(actions)==set(range(1,101))
    assert len({x['next_action'] for x in actions.values()})==100
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
        item['access_group']=access_group(row['access']);item['mcp']=mcp.get(row['id']);item.update({k:v for k,v in actions[item['id']].items() if k!='id'});rows.append(item)
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
    payload['research_run']=read_json('research-run.json') if (ROOT/'data/research-run.json').exists() else None
    payload['retrieval_iteration']=read_json('retrieval-iteration.json')
    data=json.dumps(payload,ensure_ascii=False).replace('</','<\\/')
    template=(ROOT/'site/template.html').read_text();assert template.count('@@DATA@@')==1
    font_css=[]
    for family,file,weight in [('Geist','geist-latin.woff2','400 700'),('Geist Mono','geist-mono-latin.woff2','400 500')]:
        encoded=base64.b64encode((ROOT/'site/fonts'/file).read_bytes()).decode()
        font_css.append("@font-face{font-family:'"+family+"';font-style:normal;font-weight:"+weight+";font-display:swap;src:url(data:font/woff2;base64,"+encoded+") format('woff2')}")
    font_license='<script type="text/plain" id="font-licenses">'+ '\n\n'.join((ROOT/'site/fonts'/name).read_text() for name in ('Geist-OFL.txt','Geist-Mono-OFL.txt'))+'</script>'
    page=template.replace('@@DATA@@',data).replace('@@CSS@@',(ROOT/'site/report.css').read_text()).replace('@@FONTS@@','\n'.join(font_css))
    (ROOT/'index.html').write_text(page.replace('<head>','<head>\n'+font_license))
    (ROOT/'data/atlas.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False))
    fields=['id','app','category','description','auth','access','access_detail','surface','verdict','blocker','workflow','next_action','success_criterion','alternative_action','note','sources','mcp_kind','mcp_scope','mcp_url']
    with (ROOT/'data/atlas.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader()
        for row in rows:
            out={k:row.get(k,'') for k in fields};out['auth']='; '.join(row['auth']);out['sources']='; '.join(row['sources'])
            for k in ['kind','scope','url']:out['mcp_'+k]=(row['mcp'] or {}).get(k,'')
            writer.writerow(out)
    # Public static JSON resources: the same evidence as the HTML, readable without setup.
    api=ROOT/'api';(api/'apps').mkdir(parents=True,exist_ok=True);(api/'evidence').mkdir(exist_ok=True);(api/'categories').mkdir(exist_ok=True)
    def resource(path,kind,**content):
        (api/path).write_text(json.dumps({'kind':kind,'as_of':payload['as_of'],'scope':'Published documentation-research snapshot; not a fresh vendor API test.',**content},indent=2,ensure_ascii=False)+'\n')
    resource('apps.json','app_collection',count=len(rows),apps=rows)
    category_slugs={'CRM & Sales':'crm-sales','Support & Helpdesk':'support-helpdesk','Communications':'communications','Marketing & Social':'marketing-social','Ecommerce':'ecommerce','Data & SEO':'data-seo','Developer & Infra':'developer-infra','Productivity':'productivity','Finance & Fintech':'finance-fintech','AI & Media':'ai-media'}
    for category,slug in category_slugs.items():
        subset=[r for r in rows if r['category']==category]
        resource('categories/'+slug+'.json','category_assessment',category=category,count=len(subset),verdict=dict(collections.Counter(r['verdict'] for r in subset)),development_access=dict(collections.Counter(r['access_group'] for r in subset)),apps=subset)
    for row in rows:
        resource('apps/'+str(row['id'])+'.json','app_assessment',app=row)
        urls=set(row['sources']+([row['mcp']['url']] if row['mcp'] else []))
        resource('evidence/'+str(row['id'])+'.json','evidence_record',id=row['id'],app=row['app'],sources=sorted(urls),retrieval_checks=[x for x in source_checks if x['url'] in urls],additional_run=next((x for x in (payload['research_run'] or {}).get('records',[]) if x['id']==row['id']),None),human_review='pending',authenticated_test=False)
    resource('priorities.json','recommendation_queue',basis='Feasibility experiments; commercial priority still needs customer demand and effort estimates.',first_experiments=[byid[i] for i in [61,13,73,81,98]],all_actions=read_json('action-plans.json'))
    resource('verification.json','verification_report',diagnostic=payload['audit'],diagnostic_counts={k:stats[k] for k in ['sample_before','sample_after','sample_fields','sample_unresolved']},additional_run=payload['research_run'],retrieval_iteration=payload['retrieval_iteration'],human_review=read_json('human-review.json'),agent_spotchecks=read_json('agent-spotchecks.json'))
    print(json.dumps({'validation':'passed','apps':100,'stats':stats},indent=2))
    return payload
if __name__=='__main__':build()

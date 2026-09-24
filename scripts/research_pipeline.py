#!/usr/bin/env python3
"""Fetch public evidence, extract scoped claims, verify them, and render a new run.

Model backend: the user's signed-in Codex CLI. This file is the deliverable's
research runner; no credentials or model access are embedded in the website.
"""
import argparse, concurrent.futures, datetime, hashlib, html, json, pathlib, re
import shutil, subprocess, sys, tempfile, time, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIELDS=('authentication','development_access','api_surface','mcp')

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def norm(s):return re.sub(r'\s+',' ',s).strip()
def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

class Document(HTMLParser):
    def __init__(self):super().__init__();self.skip=[];self.parts=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if self.skip:
            if tag not in ('br','img','meta','link','input','hr','wbr','source'):self.skip.append(tag)
            return
        if tag in ('script','style','noscript','nav','aside','footer','header','svg') or attrs.get('aria-hidden')=='true':self.skip.append(tag);return
        if tag in ('p','div','li','section','h1','h2','h3','h4','tr','br'):self.parts.append('\n')
        if tag=='a' and attrs.get('href'):self.links.append(attrs['href'])
    def handle_endtag(self,tag):
        if self.skip:
            if tag in self.skip:
                # Recover from malformed HTML without retaining a stuck hidden state.
                i=len(self.skip)-1-self.skip[::-1].index(tag);self.skip=self.skip[:i]
            return
        if tag in ('p','div','li','section','h1','h2','h3','h4','tr'):self.parts.append('\n')
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)
    def text(self):return '\n'.join(norm(x) for x in ''.join(self.parts).splitlines() if norm(x))

TOPICS={
    'authentication':re.compile(r'authenticat|authoriz|oauth|API.key|bearer|credential|access.token|personal.token',re.I),
    'development_access':re.compile(r'free|trial|sandbox|developer.account|plan|subscription|entitle|paid|pricing|approval|partner|self.host',re.I),
    'api_surface':re.compile(r'RESTful|REST.API|GraphQL|HTTP.API|API.provides|API.allows|endpoint|command.line|CLI|resources',re.I),
    'mcp':re.compile(r'model.context.protocol|MCP|tools.list|MCP.server',re.I)}
def excerpt(text,limit=12000):
    # Allocate evidence space per research question. A long API index must not
    # consume the entire packet before auth/access prose is reached.
    lines=text.splitlines();chosen=set();budget=max(1800,(limit-600)//4)
    for pattern in TOPICS.values():
        ranked=[]
        for i,line in enumerate(lines):
            hits=len(pattern.findall(line))
            if not hits:continue
            prose_bonus=7 if 60<=len(line)<=1300 else 0
            entitlement_bonus=8 if re.search(r'(trial|free).{0,100}(API|calls|requests)|API.{0,100}(trial|free)|require.{0,80}(plan|approval|subscription)',line,re.I) else 0
            score=min(hits,5)*3+prose_bonus+entitlement_bonus-(5 if line.startswith('/') else 0)
            ranked.append((score,i))
        used=0
        for score,i in sorted(ranked,key=lambda x:(-x[0],x[1])):
            block=set(range(max(0,i-1),min(len(lines),i+2)))-chosen
            size=sum(len(lines[j])+1 for j in block)
            if not block or size>budget-used:continue
            chosen.update(block);used+=size
    intro=[];intro_size=0
    for i,line in enumerate(lines[:8]):
        if intro_size+len(line)>600:break
        intro.append(i);intro_size+=len(line)+1
    chosen.update(intro)
    selected='\n'.join(lines[i] for i in sorted(chosen))
    return selected[:limit],len(norm(selected))<len(norm(text))

def fetch(url):
    result={'url':url,'retrieved_at':utc(),'status':None,'final_url':url,'text':'','error':None}
    if urllib.parse.urlparse(url).scheme!='https':result['error']='Only HTTPS public source URLs are accepted';return result
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ToolkitAtlasResearch/2.0 (public documentation research)','Accept':'text/html,text/plain,application/json'})
        with urllib.request.urlopen(req,timeout=25) as response:
            raw=response.read(3_000_001);result['status']=response.status;result['final_url']=response.url;result['content_type']=response.headers.get('Content-Type','');result['truncated_bytes']=len(raw)>3_000_000
        raw=raw[:3_000_000];decoded=raw.decode('utf-8','replace')
        if 'html' in result['content_type']:
            parser=Document();parser.feed(decoded);text=parser.text()
        else:text=decoded
        result['sha256']=hashlib.sha256(text.encode()).hexdigest();result['text_chars']=len(text)
        result['text'],result['truncated_text']=excerpt(text)
        if len(result['text'])<100:result['error']='Insufficient readable content; may require browser rendering'
    except urllib.error.HTTPError as e:result['status']=e.code;result['error']=str(e)
    except Exception as e:result['error']=str(e)
    return result

def inputs(ids):
    # The curated source index supplies URLs only; reviewed answers are withheld.
    rows=json.loads((ROOT/'data/atlas.json').read_text())['rows'];selected=[]
    for r in rows:
        if ids and r['id'] not in ids:continue
        urls=list(dict.fromkeys(([r['url']] if r['url'] else [])+r['sources']+([r['mcp']['url']] if r['mcp'] else [])))
        selected.append({'id':r['id'],'app':r['app'],'category':r['category'],'sources':urls[:6]})
    return selected

def cli_call(prompt,schema,outdir,stem,timeout):
    if not shutil.which('codex'):raise RuntimeError('Codex CLI is required. Install it from the official documentation and run codex login. No fallback answers are fabricated.')
    prompt_file=outdir/(stem+'-prompt.txt');prompt_file.write_text(prompt)
    output=outdir/(stem+'-model.json')
    cmd=['codex','exec','--ephemeral','--sandbox','read-only','--skip-git-repo-check','--color','never','--output-schema',str(ROOT/'schemas'/schema),'--output-last-message',str(output),'-']
    # The execution context contains no project files; the model gets its packet on stdin.
    # Preserve the user's model and approval configuration; never bypass hook trust.
    with tempfile.TemporaryDirectory(prefix='toolkit-research-') as execution_dir:
        started=time.monotonic();started_at=utc()
        run=subprocess.run(cmd,input=prompt,text=True,capture_output=True,cwd=execution_dir,timeout=timeout)
    (outdir/(stem+'-log.txt')).write_text(run.stderr+'\n'+run.stdout)
    if run.returncode!=0 or not output.exists():raise RuntimeError(f'Codex {stem} failed (exit {run.returncode}); inspect its private run log.')
    raw=json.loads(output.read_text());write(outdir/(stem+'-execution.json'),{'started_at':started_at,'elapsed_seconds':round(time.monotonic()-started,2),'backend':'codex exec','returncode':run.returncode})
    return raw

def validate(records,verification,packet):
    sources={s['source_id']:s for s in packet['documents']};wanted={a['id'] for a in packet['apps']}
    if len(records)!=len(wanted) or {r['id'] for r in records}!=wanted:raise ValueError('Extraction app IDs do not exactly match the input')
    checks=verification['checks'];pairs=[(c['id'],c['field']) for c in checks]
    if len(pairs)!=len(set(pairs)) or set(pairs)!={(i,f) for i in wanted for f in FIELDS}:raise ValueError('Verification must contain exactly one check per app and field')
    lookup={(c['id'],c['field']):c for c in checks};results=[]
    for record in records:
        app=next(a for a in packet['apps'] if a['id']==record['id']);allowed=set(app['source_ids']);fields={}
        for field in FIELDS:
            claim=record[field];citations=[];binding=bool(claim['evidence'])
            for citation in claim['evidence']:
                source=sources.get(citation['source_id']);quote=norm(citation['quote']);text=norm(source.get('text','')) if source else ''
                bound=bool(source and source['source_id'] in allowed and source['status']==200 and not source['error'] and len(quote)>=12 and quote in text)
                binding=binding and bound
                citations.append({'source_id':citation['source_id'],'url':source['url'] if source else None,'retrieved_at':source['retrieved_at'] if source else None,'source_sha256':source.get('sha256') if source else None,'quote_sha256':hashlib.sha256(quote.encode()).hexdigest(),'normalized_offset':text.find(quote) if bound else None,'quote_binding_passed':bound})
            review=lookup[(record['id'],field)]
            status='supported' if claim['status']=='supported' and binding and review['assessment']=='supported' else 'inferred' if binding and claim['status'] in ('supported','inferred') and review['assessment'] in ('supported','inferred') else 'needs_review' if claim['status']!='unresolved' or review['assessment'] not in ('unresolved','unsupported') else 'unresolved'
            fields[field]={'answer':claim['answer'],'status':status,'caveat':claim['caveat'],'citation_binding_passed':binding,'verification':review,'citations':citations}
        critical=all(fields[f]['status']=='supported' for f in ('authentication','development_access','api_surface'))
        verdict='Prototype candidate' if critical and record['access_class']=='Self-serve' else 'Access prerequisite' if critical and record['access_class']=='Gated' else 'Review required'
        results.append({'id':record['id'],'app':app['app'],'category':app['category'],'product_scope':record['product_scope'],'fields':fields,'access_class':record['access_class'] if fields['development_access']['status']=='supported' else 'Unknown','verdict':verdict,'decision_reason':record['decision_reason'],'next_step':record['next_step']})
    return results

def report(run):
    e=html.escape;rows=[]
    for r in run['records']:
        fields=''.join('<div><b>'+e(f.replace('_',' ').title())+'</b> · '+e(c['status'])+'<p>'+e(c['answer'])+'</p><small>'+e(c['verification']['reason'])+'</small><p>'+''.join('<a href="'+e(s['url'] or '')+'">Source</a> ' for s in c['citations'])+'</p></div>' for f,c in r['fields'].items())
        rows.append('<details><summary>'+e(r['app'])+' — '+e(r['verdict'])+'</summary>'+fields+'<p>Next: '+e(r['next_step'])+'</p></details>')
    return '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Toolkit Atlas research run</title><style>body{font:16px/1.6 system-ui;max-width:1000px;margin:40px auto;padding:0 20px;background:#f8f7f3;color:#20211e}details{border-top:1px solid #ccc;padding:18px 0}summary{cursor:pointer;font-weight:600}small{color:#666}a{color:#a84915}details div{padding:14px 0;border-bottom:1px solid #ddd}</style><h1>Fresh research run</h1><p>'+e(run['run_at'])+' · '+str(len(run['records']))+' apps</p><p>'+e(run['limitations'])+'</p><pre>'+e(json.dumps(run['summary'],indent=2))+'</pre>'+''.join(rows)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ids',help='Comma-separated app IDs; omitted means all 100');p.add_argument('--batch-size',type=int,default=5);p.add_argument('--timeout',type=int,default=600);p.add_argument('--output',help='New run directory');p.add_argument('--resume',help='Resume an existing run; reuse its frozen input/source packet');p.add_argument('--collect-only',action='store_true');a=p.parse_args()
    if not 1<=a.batch_size<=10:p.error('batch-size must be 1..10')
    ids={int(x) for x in a.ids.split(',')} if a.ids else None
    if ids and not ids<=set(range(1,101)):p.error('App IDs must be 1..100')
    out=pathlib.Path(a.resume or a.output or ROOT/'runs'/('research-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))).resolve();out.mkdir(parents=True,exist_ok=True)
    if a.resume:
        manifest=json.loads((out/'manifest.json').read_text());packet=json.loads((out/'packet.json').read_text())
    else:
        if (out/'manifest.json').exists():p.error('Output already contains a run; use --resume or a new directory')
        appset=inputs(ids);urls=list(dict.fromkeys(u for app in appset for u in app['sources']))
        print(f'Collecting {len(urls)} public sources for {len(appset)} apps',flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:documents=list(pool.map(fetch,urls))
        for i,d in enumerate(documents):d['source_id']=f'S{i+1:03d}'
        index={d['url']:d['source_id'] for d in documents}
        packet={'apps':[{**{k:v for k,v in x.items() if k!='sources'},'source_ids':[index[u] for u in x['sources']]} for x in appset],'documents':documents}
        manifest={'run_at':utc(),'apps':[x['id'] for x in appset],'batch_size':a.batch_size,'source_index':'Previously discovered official URLs from data/atlas.json; reviewed answers excluded from model input','status':'collected','source_count':len(documents),'http_ok':sum(d['status']==200 and not d['error'] for d in documents)}
        write(out/'packet.json',packet);write(out/'manifest.json',manifest)
    print(json.dumps(manifest),flush=True)
    if a.collect_only:return
    records=[];failures=[];batch_size=manifest['batch_size']
    for offset in range(0,len(packet['apps']),batch_size):
        apps=packet['apps'][offset:offset+batch_size];needed={s for app in apps for s in app['source_ids']};part={'apps':apps,'documents':[d for d in packet['documents'] if d['source_id'] in needed]};stem=f'batch-{offset//batch_size+1:02d}'
        saved=out/(stem+'-validated.json')
        if saved.exists():records+=json.loads(saved.read_text());print(f'{stem}: resumed validated records',flush=True);continue
        print(f'{stem}: extracting {[x["app"] for x in apps]}',flush=True)
        try:
            extracted=cli_call((ROOT/'prompts/extract.md').read_text()+'\nEVIDENCE PACKET:\n'+json.dumps(part), 'research.json',out,stem+'-extract',a.timeout)
            print(f'{stem}: verifying extracted claims',flush=True)
            verified=cli_call((ROOT/'prompts/verify.md').read_text()+'\nEVIDENCE PACKET:\n'+json.dumps(part)+'\nPROPOSED RECORDS:\n'+json.dumps(extracted),'verification.json',out,stem+'-verify',a.timeout)
            result=validate(extracted['records'],verified,part);write(saved,result);records+=result
            print(f'{stem}: {len(result)} records validated; uncertainty retained',flush=True)
        except Exception as error:
            failures.append({'batch':stem,'ids':[x['id'] for x in apps],'error':str(error)});print(f'{stem}: FAILED {error}',flush=True)
        write(out/'progress.json',{'completed':len(records),'total':len(packet['apps']),'failures':failures})
    states={state:sum(c['status']==state for r in records for c in r['fields'].values()) for state in ('supported','inferred','unresolved','needs_review')}
    run={'run_at':manifest['run_at'],'completed_at':utc(),'method':'Live HTTP collection → Codex structured extraction → separate-context Codex semantic check → deterministic citation binding → conservative verdict → generated HTML','limitations':'Same-model automated review, not independent human accuracy. Uses a previously curated source index. Missing, blocked, truncated and dynamic pages remain unresolved. Citation binding proves text occurrence, not truth. No authenticated integrations are tested.','summary':{'requested_apps':len(packet['apps']),'completed_apps':len(records),'source_count':manifest['source_count'],'retrieved_sources':manifest['http_ok'],'field_statuses':states,'failed_batches':len(failures)},'records':sorted(records,key=lambda r:r['id']),'failures':failures}
    write(out/'report.json',run);(out/'report.html').write_text(report(run));manifest['status']='complete' if len(records)==len(packet['apps']) else 'incomplete';write(out/'manifest.json',manifest)
    print(json.dumps({'output':str(out),'status':manifest['status'],'summary':run['summary']}),flush=True)
    if failures:sys.exit(1)
if __name__=='__main__':main()

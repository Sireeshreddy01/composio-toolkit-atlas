#!/usr/bin/env python3
"""Reproducible evidence collection. No accounts, keys or model dependency.

First-pass signals are intentionally NOT verified facts. Curated records are
separate; re-running collection never overwrites an analyst's decisions.
"""
import argparse, concurrent.futures, csv, datetime, hashlib, json, pathlib, re, time, urllib.request
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.hidden=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','noscript'): self.hidden+=1
    def handle_endtag(self, tag):
        if tag in ('script','style','noscript'): self.hidden=max(0,self.hidden-1)
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)

def collect(row):
    result=dict(row); result['id']=int(row['id'])
    result['checked_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result['status']='unresolved'; result['signals']={}; result['bytes']=0
    url=row['url']
    if not url: result['error']='No unambiguous vendor URL in assignment'; return result
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ToolkitAtlasResearch/1.0 (public documentation research)'})
        with urllib.request.urlopen(req,timeout=25) as response:
            raw=response.read(3_000_000); result.update(status=response.status, final_url=response.url, bytes=len(raw))
        parser=Text(); parser.feed(raw.decode('utf-8','replace'))
        body=re.sub(r'\s+',' ',' '.join(parser.parts))
        result['sha256']=hashlib.sha256(body.encode()).hexdigest()
        result['text_chars']=len(body)
        patterns={'OAuth2':r'oauth\s*(?:2(?:\.0)?)?', 'API key':r'api[ -]?key', 'Basic':r'basic auth', 'Token':r'bearer|access token|personal access token', 'GraphQL':r'graphql','REST':r'\bREST\b','MCP':r'model context protocol|\bMCP\b','Trial/free':r'free (?:trial|plan|tier|account)|start.{0,15}trial','Gate':r'enterprise|contact sales|admin approval|paid plan|partner approval'}
        for label, pattern in patterns.items():
            hits=list(re.finditer(pattern,body,re.I))
            if hits: result['signals'][label]=[body[max(0,m.start()-80):m.end()+150] for m in hits[:3]]
        result['auth_guess']=next((x for x in ('OAuth2','API key','Basic','Token') if x in result['signals']),'Unknown')
        result['surface_guess']='GraphQL' if 'GraphQL' in result['signals'] else 'REST' if 'REST' in result['signals'] else 'Unknown'
        result['access_guess']='Gated' if 'Gate' in result['signals'] else 'Self-serve' if 'Trial/free' in result['signals'] else 'Unknown'
        result['mcp_guess']='Mention found' if 'MCP' in result['signals'] else 'Not found in fetched page'
    except Exception as e: result['error']=str(e)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int);p.add_argument('--input',default='data/apps.tsv');p.add_argument('--output',default='runs/latest.json');p.add_argument('--workers',type=int,default=8);args=p.parse_args()
    with (ROOT/args.input).open() as f: rows=list(csv.DictReader(f,delimiter='\t'))[:args.limit]
    start=time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool: results=list(pool.map(collect,rows))
    payload={'run_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':round(time.monotonic()-start,2),'method':'HTTP fetch + deterministic keyword baseline; requires semantic review','results':results}
    dest=ROOT/args.output;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(payload,indent=2))
    print(json.dumps({'apps':len(results),'fetched':sum(x['status']==200 for x in results),'elapsed_seconds':payload['elapsed_seconds'],'output':str(dest)}))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Fetch each unique cited URL; preserve failures instead of treating them as no API.
This checks retrievability and documentation signals, not authenticated API behavior.
"""
import concurrent.futures,csv,json,pathlib,sys
from research import collect
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    rows=list(csv.DictReader((ROOT/'data/reviewed.tsv').open(),delimiter='\t'))
    urls={u for r in rows for u in r['sources'].split(';') if u}
    mcp=ROOT/'data/mcp.json'
    if mcp.exists(): urls.update(x['url'] for x in json.loads(mcp.read_text()).values() if x.get('url'))
    source_rows=[{'id':i,'app':'Evidence source','url':u} for i,u in enumerate(sorted(urls),1)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(collect,source_rows))
    # Public ledger contains metadata only, avoiding republication of documentation.
    ledger=[{k:v for k,v in x.items() if k not in ('signals','app','bytes')} for x in results]
    (ROOT/'data/source-checks.json').write_text(json.dumps(ledger,indent=2))
    # Optional private debug output is deliberately outside the repository.
    if len(sys.argv)>1:pathlib.Path(sys.argv[1]).write_text(json.dumps(results,indent=2))
    print(json.dumps({'sources':len(results),'HTTP_200':sum(x['status']==200 for x in results),'failed_or_blocked':sum(x['status']!=200 for x in results)}))
if __name__=='__main__':main()

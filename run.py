#!/usr/bin/env python3
"""Build the frozen case study, collect sources, or run semantic research."""
import argparse,datetime,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--refresh',action='store_true',help='Run the original keyword collector; does not replace reviewed facts')
p.add_argument('--research',action='store_true',help='Collect source evidence, extract claims with Codex, verify and generate a new report')
p.add_argument('--ids',help='Comma-separated app IDs for --research; omitted means all 100')
p.add_argument('--batch-size',type=int,default=5,help='Apps per model request (1..10)')
p.add_argument('--resume',help='Resume the semantic research run in this directory')
p.add_argument('--check-sources',action='store_true',help='Refresh the cited-source HTTP ledger')
p.add_argument('--limit',type=int,help='Limit original keyword collection to N apps')
a=p.parse_args()
if a.research or a.resume:
    cmd=[sys.executable,str(ROOT/'scripts/research_pipeline.py'),'--batch-size',str(a.batch_size)]
    if a.ids:cmd+=['--ids',a.ids]
    if a.resume:cmd+=['--resume',a.resume]
    subprocess.run(cmd,check=True,cwd=ROOT)
if a.refresh:
    name='runs/'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json'
    cmd=[sys.executable,str(ROOT/'scripts/research.py'),'--output',name]
    if a.limit:cmd+=['--limit',str(a.limit)]
    subprocess.run(cmd,check=True,cwd=ROOT)
if a.check_sources:subprocess.run([sys.executable,str(ROOT/'scripts/verify_sources.py')],check=True,cwd=ROOT)
subprocess.run([sys.executable,str(ROOT/'scripts/build.py')],check=True,cwd=ROOT)

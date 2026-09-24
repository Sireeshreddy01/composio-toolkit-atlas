#!/usr/bin/env python3
"""Offline build by default. Optional live public-document collection."""
import argparse,datetime,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--refresh',action='store_true',help='Collect all 100 public seed URLs into a NEW run; does not replace reviewed facts');p.add_argument('--check-sources',action='store_true',help='Refresh the cited-source HTTP ledger');p.add_argument('--limit',type=int,help='Limit live research to N apps');a=p.parse_args()
if a.refresh:
    name='runs/'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json'
    cmd=[sys.executable,str(ROOT/'scripts/research.py'),'--output',name]
    if a.limit:cmd+=['--limit',str(a.limit)]
    subprocess.run(cmd,check=True)
if a.check_sources:subprocess.run([sys.executable,str(ROOT/'scripts/verify_sources.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'scripts/build.py')],check=True)

// Test the exact functions embedded in the deliverable, including failed checks.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync('site/template.html','utf8');
const source=html.slice(html.indexOf('function runSavedChecks(data)'),html.indexOf('let checksResult='));
const context={URL,Date};vm.createContext(context);vm.runInContext(source,context);
const original=JSON.parse(fs.readFileSync('data/atlas.json','utf8'));
const run=data=>context.runSavedChecks(data);
assert.equal(run(original).passed,true);
for(const [name,change,check]of[
 ['duplicate app',d=>d.rows[1].id=1,'Assignment coverage'],
 ['wrong summary',d=>d.stats.verdict.Build++,'Published summary counts'],
 ['unsafe source',d=>d.rows[0].sources=['javascript:alert(1)'],'Source coverage'],
 ['wrong sample',d=>d.sample_plan.sample_ids[0]=100,'Sample selection'],
 ['changed prediction',d=>d.audit.checks.find(c=>c.id===13).initial.access_guess='Self-serve','Diagnostic score reproducibility'],
 ['missing record',d=>d.rows.splice(0,1),'Assignment coverage']
]){const d=structuredClone(original);change(d);const result=run(d);assert.equal(result.passed,false,name);assert.equal(result.checks.find(c=>c.name===check).passed,false,name)}
const requestSource=html.slice(html.indexOf('const REQUEST_PRESETS='),html.indexOf('let activeRequest='));
function makeContext(fetch){const context={fetch,AbortController,setTimeout,clearTimeout,performance,Date,URL,TextEncoder};vm.createContext(context);vm.runInContext(requestSource,context);return context}
const rc=makeContext();
const request=(preset='repo',owner='Sireeshreddy01',repo='composio-toolkit-atlas',params='{}')=>rc.buildPublicRequest(preset,owner,repo,params);
for(const args of [['repo','bad/owner'],['repo','owner','..'],['repo','owner','repo','[]'],['issues','owner','repo','{"per_page":101}'],['issues','owner','repo','{"state":"secret"}'],['repo','owner','repo','{"access_token":"secret"}'],['repo','owner','repo','broken']])assert.throws(()=>request(...args));
assert.equal(new URL(request('issues','owner','repo','{"page":2,"per_page":5}').endpoint).searchParams.get('page'),'2');
(async()=>{
 const response=(status,body)=>({status,ok:status>=200&&status<300,statusText:'Mock',headers:new Map([['x-ratelimit-remaining','50']]),text:async()=>JSON.stringify(body)});
 const run=async(fetch,req=request(),signal)=>makeContext(fetch).sendPublicRequest(req,signal);
 const good=await run(async(url,options)=>{assert.equal(options.credentials,'omit');assert.equal(options.method,'GET');return response(200,{id:123,full_name:'Sireeshreddy01/composio-toolkit-atlas',private:false})});assert.equal(good.passed,true);assert.equal(good.body.id,123);assert.equal(good.headers['x-ratelimit-remaining'],'50');assert.ok(good.response_bytes>0);
 assert.equal((await run(async()=>response(200,{id:1,full_name:'wrong/repo',private:false}))).passed,false);
 const limited=await run(async()=>response(403,{message:'API rate limit exceeded'}));assert.equal(limited.passed,false);assert.equal(limited.http_status,403);assert.equal(limited.body.message,'API rate limit exceeded');assert.ok(limited.elapsed_ms>=0);
 assert.equal((await run(async()=>{throw new TypeError('Failed to fetch')})).http_status,null);
 const cancelled=await run(async()=>{const e=new Error('Abort');e.name='AbortError';throw e});assert.match(cancelled.error,/cancelled/);
 const empty=await run(async()=>response(200,[]),request('issues'));assert.equal(empty.passed,true);
 assert.equal((await run(async()=>response(204,null),request('contributors'))).passed,true);
 assert.equal((await run(async()=>response(200,{JavaScript:20}),request('languages'))).passed,true);
 assert.equal((await run(async()=>response(200,{sha:'a',path:'README.md'}),request('readme'))).passed,true);
 await assert.rejects(()=>run(async()=>{throw new Error('Must never fetch')},{...request(),endpoint:'https://evil.example/'}),/Only the supported/);
 console.log('Dataset corruption checks, request validation, response bodies/headers, schema checks, empty lists, HTTP/network/cancellation and host restriction passed.');
})().catch(e=>{console.error(e);process.exitCode=1});

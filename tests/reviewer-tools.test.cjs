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
const rc=makeContext();const request=(preset='app',params='{"app_id":13}')=>rc.buildAssessmentRequest(preset,params);
for(const args of [['app','{"app_id":101}'],['app','{"app_id":"../"}'],['app','[]'],['all','{"token":"secret"}'],['category','{"category":"other"}'],['app','broken']])assert.throws(()=>request(...args));
assert.match(request().endpoint,/api\/apps\/13.json$/);
(async()=>{
 const response=(status,body)=>({status,ok:status>=200&&status<300,statusText:'Mock',headers:new Map([['content-type','application/json']]),text:async()=>JSON.stringify(body)});
 const run=async(fetch,req=request(),signal)=>makeContext(fetch).sendAssessmentRequest(req,signal);
 for(const [preset,params,file]of [['app','{"app_id":13}','apps/13.json'],['all','{}','apps.json'],['category','{"category":"support-helpdesk"}','categories/support-helpdesk.json'],['priorities','{}','priorities.json'],['evidence','{"app_id":13}','evidence/13.json'],['verification','{}','verification.json']]){
  const req=request(preset,params),body=JSON.parse(fs.readFileSync('api/'+file,'utf8'));
  const good=await run(async(url,options)=>{assert.equal(options.credentials,'omit');assert.equal(options.method,'GET');assert.equal(url,req.endpoint);return response(200,body)},req);assert.equal(good.passed,true);assert.equal(good.body.kind,body.kind);
 }
 assert.equal((await run(async()=>response(200,{kind:'wrong',as_of:'2026-09-24'}))).passed,false);
 const failed=await run(async()=>response(404,{message:'Not found'}));assert.equal(failed.passed,false);assert.equal(failed.http_status,404);assert.equal(failed.body.message,'Not found');
 assert.equal((await run(async()=>{throw new TypeError('Failed to fetch')})).http_status,null);
 assert.match((await run(async()=>{const e=new Error('Abort');e.name='AbortError';throw e})).error,/cancelled/);
 await assert.rejects(()=>run(async()=>{throw new Error('Must never fetch')},{...request(),endpoint:'https://evil.example/'}),/Only this assessment/);
 console.log('Dataset checks, all six assessment resources, parameter validation, schema mismatches, HTTP/network/cancellation and host restriction passed.');
})().catch(e=>{console.error(e);process.exitCode=1});

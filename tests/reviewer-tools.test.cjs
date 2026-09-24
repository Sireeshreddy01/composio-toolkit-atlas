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
const requestSource=html.slice(html.indexOf('async function requestPublicRepository()'),html.indexOf("el('liveCode').textContent="));
async function testRequest(fetch){const context={fetch,AbortController,setTimeout,clearTimeout,performance,Date};vm.createContext(context);vm.runInContext(requestSource,context);return context.requestPublicRepository()}
(async()=>{
 const response=(status,body)=>({status,ok:status>=200&&status<300,statusText:'Mock',headers:new Map(),json:async()=>body});
 const good=await testRequest(async(url,options)=>{assert.equal(options.credentials,'omit');assert.equal(options.method,'GET');return response(200,{id:123,full_name:'Sireeshreddy01/composio-toolkit-atlas',private:false})});assert.equal(good.passed,true);
 const wrong=await testRequest(async()=>response(200,{id:123,full_name:'wrong/repo',private:false}));assert.equal(wrong.passed,false);
 const limited=await testRequest(async()=>response(403,{message:'API rate limit exceeded'}));assert.equal(limited.passed,false);assert.equal(limited.http_status,403);
 const blocked=await testRequest(async()=>{throw new TypeError('Failed to fetch')});assert.equal(blocked.passed,false);assert.equal(blocked.http_status,null);
 const timed=await testRequest(async()=>{const e=new Error('Timeout');e.name='AbortError';throw e});assert.match(timed.error,/Timed out/);
 console.log('Saved-data checks detect corrupt inputs; live-request success, schema failure, HTTP failure, network failure and timeout paths passed.');
})().catch(e=>{console.error(e);process.exitCode=1});

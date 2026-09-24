"""Behavioral checks: prevent unsupported citations from becoming supported claims."""
import copy,importlib.util,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pipeline',ROOT/'scripts/research_pipeline.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class PipelineChecks(unittest.TestCase):
    def setUp(self):
        self.packet={'apps':[{'id':1,'app':'Fixture','category':'Tests','source_ids':['S1']}], 'documents':[{'source_id':'S1','url':'https://example.com/docs','retrieved_at':'2026-09-24','status':200,'error':None,'text':'Trial accounts include API access for developer testing.'}]}
        claim={'answer':'Trial API access is included.','status':'supported','evidence':[{'source_id':'S1','quote':'Trial accounts include API access','explanation':'Explicit entitlement.'}],'caveat':''}
        self.record={'id':1,'product_scope':'Test API','access_class':'Self-serve','decision_reason':'Trial','next_step':'Read a test item',**{f:copy.deepcopy(claim) for f in m.FIELDS}}
        self.checks={'checks':[{'id':1,'field':f,'assessment':'supported','reason':'Explicit support.'} for f in m.FIELDS]}
    def run_case(self):return m.validate([self.record],self.checks,self.packet)[0]
    def test_supported_requires_binding_and_semantic_support(self):
        self.assertEqual(self.run_case()['verdict'],'Prototype candidate')
        self.record['development_access']['evidence'][0]['quote']='Everything is unlimited and free'
        r=self.run_case();self.assertEqual(r['access_class'],'Unknown');self.assertEqual(r['fields']['development_access']['status'],'needs_review');self.assertEqual(r['verdict'],'Review required')
    def test_wrong_app_source_rejected(self):
        self.packet['apps'][0]['source_ids']=[]
        self.assertFalse(self.run_case()['fields']['authentication']['citation_binding_passed'])
    def test_http_failure_never_evidence(self):
        self.packet['documents'][0]['status']=403
        self.assertEqual(self.run_case()['verdict'],'Review required')
    def test_verifier_can_reject_bound_quote(self):
        self.checks['checks'][1]['assessment']='unsupported'
        self.assertEqual(self.run_case()['fields']['development_access']['status'],'needs_review')
    def test_missing_and_duplicate_checks_fail(self):
        self.checks['checks'].pop()
        with self.assertRaises(ValueError):self.run_case()
        self.checks['checks'].append(self.checks['checks'][0])
        with self.assertRaises(ValueError):self.run_case()
    def test_wrong_app_id_fails(self):
        self.record['id']=2
        with self.assertRaises(ValueError):self.run_case()
    def test_long_index_does_not_crowd_out_entitlement(self):
        text='\n'.join('/api/resource/'+str(i) for i in range(900))+'\nTrial accounts include API access with a limit of 50 requests per minute.\nUse your API key as the username in HTTP Basic authentication.'
        selected,truncated=m.excerpt(text)
        self.assertIn('Trial accounts include API access',selected);self.assertIn('HTTP Basic authentication',selected);self.assertLessEqual(len(selected),12000)
    def test_hidden_script_and_navigation_excluded(self):
        p=m.Document();p.feed('<nav><p>GraphQL</p></nav><main><p>Actual REST API</p><script>junk</script></main>')
        self.assertEqual(p.text(),'Actual REST API')
if __name__=='__main__':unittest.main()

import sys,json,tempfile,threading,unittest,urllib.request,urllib.error
from pathlib import Path
from http.server import HTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'debug'))
import server
from device_engine import Engine
class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();server.SAVED=Path(cls.tmp.name)/'saved-session.json'
        cls.http=HTTPServer(('127.0.0.1',0),server.Handler)
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
        cls.url='http://127.0.0.1:'+str(cls.http.server_port)
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join();cls.tmp.cleanup()
    def setUp(self):server.engine=Engine()
    def post(self,path,body,token=server.TOKEN):
        req=urllib.request.Request(self.url+path,json.dumps(body).encode(),{'Content-Type':'application/json','X-Debug-Token':token})
        with urllib.request.urlopen(req) as response:return json.load(response)
    def test_save_restore_and_replay(self):
        for a,v in [('touch','A'),('mode','TTL'),('rotate',1)]:self.post('/api/action',dict(action=a,value=v))
        saved=self.post('/api/save',{})['memory'];session=json.loads(server.SAVED.read_text())
        self.post('/api/action',dict(action='reset'));self.assertNotEqual(saved,server.engine.capture())
        self.assertEqual(saved,self.post('/api/load',{})['memory'])
        self.assertEqual(saved,self.post('/api/restore',session)['memory'])
    def test_invalid_restore_is_atomic(self):
        self.post('/api/action',dict(action='touch',value='SUB'));before=server.engine.capture()
        bad=server.engine.session();bad['actions'].append(dict(action='channel',value=900))
        with self.assertRaises(urllib.error.HTTPError) as cm:self.post('/api/restore',bad)
        self.assertEqual(cm.exception.code,400);cm.exception.close();self.assertEqual(before,server.engine.capture())
    def test_requires_session_token(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:self.post('/api/action',dict(action='reset'),token='bad')
        self.assertEqual(cm.exception.code,403);cm.exception.close()
    def test_serves_assets(self):
        for path,mime in [('/','text/html'),('/app.js','text/javascript'),('/style.css','text/css'),('/api/state','application/json')]:
            with urllib.request.urlopen(self.url+path) as r:self.assertIn(mime,r.headers['Content-Type']);self.assertTrue(r.read())
if __name__=='__main__':unittest.main()

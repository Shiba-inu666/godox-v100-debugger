"""Loopback-only debugger server. No device, USB, serial, or firmware write APIs."""
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json,secrets
from device_engine import Engine
ROOT=Path(__file__).parent
SAVED=ROOT.parent/'sessions'/'saved-session.json'
engine=Engine();TOKEN=secrets.token_hex(24)
class Handler(BaseHTTPRequestHandler):
    def reply(self,code,data,kind='application/json'):
        data=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode()
        self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if self.path=='/':self.reply(200,(ROOT/'index.html').read_text().replace('__TOKEN__',TOKEN).encode(),'text/html; charset=utf-8')
        elif self.path=='/app.js':self.reply(200,(ROOT/'app.js').read_bytes(),'text/javascript; charset=utf-8')
        elif self.path=='/style.css':self.reply(200,(ROOT/'style.css').read_bytes(),'text/css; charset=utf-8')
        elif self.path=='/api/state':self.reply(200,engine.snapshot())
        elif self.path=='/api/session':self.reply(200,dict(session=engine.session(),state=engine.snapshot()))
        else:self.reply(404,{'error':'Not found'})
    def do_POST(self):
        global engine
        if self.path not in ['/api/action','/api/restore','/api/save','/api/load']:return self.reply(404,{'error':'Not found'})
        if self.headers.get('X-Debug-Token')!=TOKEN:return self.reply(403,{'error':'页面会话已过期，请刷新'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=262144:raise ValueError('请求大小无效')
            req=json.loads(self.rfile.read(size))
            if not isinstance(req,dict):raise ValueError('无效请求')
            if self.path=='/api/action':result=engine.action(req['action'],req.get('value'))
            elif self.path=='/api/restore':engine=Engine.restore(req);result=engine.snapshot()
            elif self.path=='/api/save':
                SAVED.parent.mkdir(exist_ok=True)
                temp=SAVED.with_suffix('.tmp');temp.write_text(json.dumps(engine.session(),ensure_ascii=False,indent=2));temp.replace(SAVED)
                result=engine.snapshot()
            else:
                if not SAVED.exists():raise ValueError('尚未保存本地会话')
                engine=Engine.restore(json.loads(SAVED.read_text()));result=engine.snapshot()
            self.reply(200,result)
        except (ValueError,KeyError,TypeError) as e:self.reply(400,{'error':str(e)})
        except Exception as e:self.reply(500,{'error':type(e).__name__+': '+str(e),'preserved':True})
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);p.add_argument('--open',action='store_true');a=p.parse_args()
    server=HTTPServer(('127.0.0.1',a.port),Handler)
    print(f'V100F debugger v3: http://127.0.0.1:{a.port}',flush=True)
    if a.open:
        import webbrowser,threading
        threading.Timer(0.3,lambda:webbrowser.open(f'http://127.0.0.1:{a.port}')).start()
    server.serve_forever()

"""Churchracersja practice leaderboard. Run behind an HTTPS reverse proxy."""
import hashlib, json, os, secrets, sqlite3, threading, time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
DB = os.environ.get('LEADERBOARD_DB', 'leaderboard.sqlite3')
ORIGIN = os.environ.get('ALLOWED_ORIGIN', 'https://unlockgen.github.io')
limits = defaultdict(deque)
limit_lock = threading.Lock()
def connect():
    db=sqlite3.connect(DB, timeout=15)
    db.execute('PRAGMA foreign_keys=ON')
    return db
with connect() as db:
    db.execute('CREATE TABLE IF NOT EXISTS players (id TEXT PRIMARY KEY)')
    db.execute('CREATE TABLE IF NOT EXISTS scores (player TEXT REFERENCES players(id), mode TEXT, name TEXT, country TEXT, ms INTEGER, PRIMARY KEY(player,mode))')
class Handler(BaseHTTPRequestHandler):
    def reply(self, code, data):
        body=json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Access-Control-Allow-Origin',ORIGIN)
        self.send_header('Vary','Origin')
        self.send_header('Cache-Control','no-store')
        self.end_headers(); self.wfile.write(body)
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin',ORIGIN)
        self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type, Authorization')
        self.end_headers()
    def do_GET(self):
        u=urlparse(self.path)
        if u.path!='/scores': return self.reply(404,{'error':'Not found'})
        mode=parse_qs(u.query).get('mode',['sportsman'])[0]
        if mode not in ('sportsman','pro'): return self.reply(400,{'error':'Invalid format'})
        with connect() as db:
            rows=db.execute('SELECT name,country,ms FROM scores WHERE mode=? ORDER BY ms,name,player LIMIT 20',(mode,)).fetchall()
        self.reply(200,[dict(zip(('name','country','ms'),r)) for r in rows])
    def do_POST(self):
        if self.headers.get('Origin')!=ORIGIN: return self.reply(403,{'error':'Origin not allowed'})
        now=time.monotonic()
        # Reverse proxies should additionally apply per-client limits at the edge.
        with limit_lock:
            for key in list(limits):
                while limits[key] and limits[key][0]<now-60: limits[key].popleft()
                if not limits[key]: del limits[key]
            q=limits[self.client_address[0]]
            if len(q)>=60: return self.reply(429,{'error':'Try again shortly'})
            q.append(now)
        if self.path=='/players':
            token=secrets.token_urlsafe(32)
            with connect() as db: db.execute('INSERT INTO players VALUES (?)',(hashlib.sha256(token.encode()).hexdigest(),))
            return self.reply(201,{'token':token})
        if self.path!='/scores': return self.reply(404,{'error':'Not found'})
        auth=self.headers.get('Authorization','')
        if not auth.startswith('Bearer ') or len(auth)>200: return self.reply(401,{'error':'Missing player token'})
        player=hashlib.sha256(auth[7:].encode()).hexdigest()
        with connect() as db:
            if not db.execute('SELECT 1 FROM players WHERE id=?',(player,)).fetchone(): return self.reply(401,{'error':'Invalid player token'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=2048: raise ValueError()
            p=json.loads(self.rfile.read(length))
            if not isinstance(p,dict): raise ValueError()
            name=p.get('name');country=p.get('country');mode=p.get('mode');ms=p.get('ms')
            if not isinstance(name,str) or not 1<=len(name.strip())<=24 or any(ord(c)<32 for c in name): raise ValueError()
            if country not in ('JM','US','GB','CA','TT','BB','OTHER') or mode not in ('sportsman','pro') or type(ms)!=int or not 0<=ms<=1800: raise ValueError()
        except (ValueError,TypeError): return self.reply(400,{'error':'Invalid score'})
        with connect() as db:
            db.execute('INSERT INTO scores VALUES (?,?,?,?,?) ON CONFLICT(player,mode) DO UPDATE SET name=excluded.name,country=excluded.country,ms=MIN(scores.ms,excluded.ms)',(player,mode,name.strip(),country,ms))
        self.reply(200,{'saved':True})
    def log_message(self, *args): pass
if __name__=='__main__':
    ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','8080'))),Handler).serve_forever()

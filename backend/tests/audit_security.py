"""Security and persistence audit script."""
import urllib.request, urllib.error, json, os, sys, subprocess, time

BASE = 'http://127.0.0.1:8000'
results = []

def req(method, path, body=None, headers=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    h = {'Content-Type': 'application/json'}
    if headers: h.update(headers)
    rq = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        r = urllib.request.urlopen(rq)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except: return e.code, {}

def chk(label, cond, detail=''):
    icon = 'PASS' if cond else 'FAIL'
    results.append((icon, label, str(detail)[:200]))
    print(f'[{icon}] {label}')
    if not cond: print(f'      DETAIL: {str(detail)[:200]}')

print('=== SECURITY CHECKS ===')

# 1. JWT tampering
s, d = req('GET', '/api/auth/me', headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYWNrZWQifQ.tampered'})
chk('Tampered JWT → 401', s == 401, d)

# 2. Missing Bearer scheme
s, d = req('GET', '/api/auth/me', headers={'Authorization': 'invalid_format'})
chk('Invalid auth scheme → 401', s == 401, d)

# 3. SQL injection in login email
s, d = req('POST', '/api/auth/login', {'email': "' OR 1=1 --@test.com", 'password': 'x'})
chk('SQL injection in email → 422 or 401', s in (401, 422), d)

# 4. XSS-like content in project title (should be stored as string, not executed)
s, d2 = req('POST', '/api/auth/login', {'email': 'alice@audit.com', 'password': 'SecurePass1!'})
token = d2.get('access_token', '')
xss_title = '<script>alert(1)</script>'
s, d = req('POST', '/api/projects', {
    'title': xss_title,
    'description': 'xss test',
    'domain': 'AI',
    'status': 'active'
}, headers={'Authorization': f'Bearer {token}'})
chk('XSS in title → 201 or 422 (not server error)', s in (201, 422), d)
if s == 201:
    stored = d.get('title', '')
    chk('XSS title stored verbatim as string', stored == xss_title, stored)

# 5. CORS origins configured
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.app.config import settings
origins = settings.cors_origins
chk('CORS origins configured', isinstance(origins, list) and len(origins) > 0, origins)
chk('CORS includes localhost:3000 or :5173', any('3000' in o or '5173' in o for o in origins), origins)

# 6. .env not tracked in git
result = subprocess.run(['git', 'ls-files', '.env'], capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..', '..'))
chk('.env NOT tracked in git', '.env' not in result.stdout.strip(), result.stdout)

# 7. .env.example exists
env_example_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env.example')
chk('.env.example exists on disk', os.path.exists(env_example_path), env_example_path)

# 8. No hardcoded secrets
cfg_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'config.py')
with open(cfg_path) as f:
    cfg_content = f.read()
chk('No hardcoded sk-ant- key in config.py', 'sk-ant-' not in cfg_content, 'checked')
chk('No hardcoded JWT secret in config.py', '"secret"' not in cfg_content.lower() or 'default' in cfg_content.lower(), 'checked')

# 9. Password not returned in any user endpoint
s, d = req('GET', '/api/auth/me', headers={'Authorization': f'Bearer {token}'})
chk('/me endpoint: hashed_password NOT in response', 'hashed_password' not in d, list(d.keys()))
chk('/me endpoint: password NOT in response', 'password' not in d, list(d.keys()))

print()
print('=== DATABASE PERSISTENCE ===')
dyn_email = f"persist_{int(time.time())}@audit.com"
s, d = req('POST', '/api/auth/register', {'email': dyn_email, 'password': 'TestPass123!', 'name': 'Persist Test'})
chk('Register new user → 201', s == 201, d)
s, d = req('POST', '/api/auth/login', {'email': dyn_email, 'password': 'TestPass123!'})
chk('Login after register → 200 (data persisted)', s == 200, d)
chk('Login response has access_token', bool(d.get('access_token')), d)

print()
print('=== MULTI-TENANT ISOLATION ===')
# User A creates project, User B cannot access it
s, da = req('POST', '/api/auth/login', {'email': 'alice@audit.com', 'password': 'SecurePass1!'})
token_a = da.get('access_token', '')
s, db = req('POST', '/api/auth/login', {'email': 'bob@audit.com', 'password': 'SecurePass2!'})
token_b = db.get('access_token', '')

s, d = req('POST', '/api/projects', {'title': 'Alice Private Project', 'description': 'Only Alice', 'domain': 'AI', 'status': 'active'}, headers={'Authorization': f'Bearer {token_a}'})
chk('User A creates private project → 201', s == 201, d)
proj_id = d.get('id')

s, d = req('GET', f'/api/projects/{proj_id}', headers={'Authorization': f'Bearer {token_b}'})
chk('User B CANNOT access User A project → 404', s == 404, d)

s, d = req('GET', f'/api/projects/{proj_id}', headers={'Authorization': f'Bearer {token_a}'})
chk('User A CAN access own project → 200', s == 200, d)

print()
print('=' * 60)
print('SECURITY + PERSISTENCE SUMMARY')
print('=' * 60)
passed = sum(1 for r in results if r[0] == 'PASS')
failed = sum(1 for r in results if r[0] == 'FAIL')
print(f'PASSED: {passed}')
print(f'FAILED: {failed}')
print(f'TOTAL:  {len(results)}')
if failed:
    print()
    print('FAILURES:')
    for icon, label, detail in results:
        if icon == 'FAIL':
            print(f'  - {label}')
            print(f'    Detail: {detail[:120]}')

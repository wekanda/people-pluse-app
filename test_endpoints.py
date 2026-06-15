import urllib.request, urllib.parse, json

base = 'https://people-pluse-backend-1.onrender.com'

print("Testing available endpoints:")
print()

endpoints = [
    '/api/health',
    '/api/employees',
    '/api/employees/',
    '/api/leave/requests',
    '/auth/me',
]

for ep in endpoints:
    try:
        resp = urllib.request.urlopen(base + ep, timeout=5)
        print(f"✓ {ep}: {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"✗ {ep}: HTTP {e.code}")
    except Exception as e:
        print(f"✗ {ep}: {type(e).__name__}")

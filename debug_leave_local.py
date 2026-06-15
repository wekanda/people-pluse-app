import urllib.request, urllib.parse, json

base = 'http://127.0.0.1:9999'

print("Testing against LOCAL backend at", base)
print()

# Get staff token
try:
    req = urllib.request.Request(
        base + '/auth/token',
        data=urllib.parse.urlencode({
            'username': 'live_staff@peoplepluse.com',
            'password': 'LiveStaff123!'
        }).encode(),
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    resp = urllib.request.urlopen(req)
    staff_tok = json.loads(resp.read().decode())['access_token']
    print("✓ Got staff token")
except Exception as e:
    print(f"✗ Auth failed: {e}")
    exit(1)

# Try leave request
leave = {
    'employee_id': 1,
    'start_date': '2026-07-10',
    'end_date': '2026-07-12',
    'reason': 'Test leave',
    'type': 'Annual Leave'
}

print("\nCreating leave request...")
try:
    req = urllib.request.Request(
        base + '/api/leave/request',
        data=json.dumps(leave).encode(),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {staff_tok}'
        }
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read().decode())
    print("✓ Success:", result)
except urllib.error.HTTPError as e:
    err_text = e.read().decode()
    print(f"✗ HTTP {e.code}:")
    print(err_text[:500])

import urllib.request, urllib.parse, json

base = 'https://people-pluse-backend-1.onrender.com'

# Get staff token
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

# Check user details
req = urllib.request.Request(
    base + '/auth/me',
    headers={'Authorization': f'Bearer {staff_tok}'}
)
resp = urllib.request.urlopen(req)
me = json.loads(resp.read().decode())
print("Current user:", me)
print()

# Try leave request with error details
leave = {
    'employee_id': 1,
    'start_date': '2026-07-10',
    'end_date': '2026-07-12',
    'reason': 'Test leave',
    'type': 'Annual Leave'
}

print("Sending leave request:")
print(json.dumps(leave, indent=2))
print()

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
    print(err_text)
    
    # Try to parse as JSON
    try:
        err = json.loads(err_text)
        print("\nParsed error:", json.dumps(err, indent=2))
    except:
        print("Error body (raw):", err_text)

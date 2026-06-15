import urllib.request, urllib.parse, json, sys

base = 'https://people-pluse-backend-1.onrender.com'

print("=" * 60)
print("DEPLOYMENT VERIFICATION TEST")
print("=" * 60)

# Test 1: Check employees
print("\n1. CHECKING EMPLOYEES:")
try:
    resp = urllib.request.urlopen(base + '/api/employees/?limit=5')
    emps = json.loads(resp.read().decode())
    print(f"   ✓ Found {len(emps)} employees")
    if emps:
        print(f"   First employee: id={emps[0]['id']}, name={emps[0]['full_name']}")
    else:
        print("   ⚠ No employees in database!")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 2: Authenticate live staff
print("\n2. AUTHENTICATING LIVE STAFF:")
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
    print(f"   ✓ Got token: {staff_tok[:30]}...")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 3: Create leave request with first employee ID
print(f"\n3. CREATING LEAVE REQUEST (employee_id={emps[0]['id']}):")
try:
    leave = {
        'employee_id': emps[0]['id'],
        'start_date': '2026-07-10',
        'end_date': '2026-07-12',
        'reason': 'Test leave request',
        'type': 'Annual Leave'
    }
    req = urllib.request.Request(
        base + '/api/leave/request',
        data=json.dumps(leave).encode(),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {staff_tok}'
        }
    )
    resp = urllib.request.urlopen(req)
    leave_resp = json.loads(resp.read().decode())
    print(f"   ✓ Leave created: id={leave_resp['id']}, status={leave_resp['status']}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode()
    print(f"   ✗ HTTP {e.code}: {err_body}")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 4: Authenticate manager
print("\n4. AUTHENTICATING LIVE MANAGER:")
try:
    req = urllib.request.Request(
        base + '/auth/token',
        data=urllib.parse.urlencode({
            'username': 'live_manager@peoplepluse.com',
            'password': 'LiveManager123!'
        }).encode(),
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    resp = urllib.request.urlopen(req)
    manager_tok = json.loads(resp.read().decode())['access_token']
    print(f"   ✓ Got token: {manager_tok[:30]}...")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 5: Approve leave
print(f"\n5. APPROVING LEAVE (id={leave_resp['id']}):")
try:
    req = urllib.request.Request(
        base + f"/api/leave/approve/{leave_resp['id']}",
        data=b'',
        method='PUT',
        headers={'Authorization': f'Bearer {manager_tok}'}
    )
    resp = urllib.request.urlopen(req)
    appr = json.loads(resp.read().decode())
    print(f"   ✓ Approved: {appr}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode()
    print(f"   ✗ HTTP {e.code}: {err_body}")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 6: Verify leave status
print(f"\n6. VERIFYING LEAVE STATUS:")
try:
    req = urllib.request.Request(
        base + f"/api/leave/requests?employee_id={emps[0]['id']}",
        headers={'Authorization': f'Bearer {manager_tok}'}
    )
    resp = urllib.request.urlopen(req)
    leaves = json.loads(resp.read().decode())
    print(f"   ✓ Found {len(leaves)} leave requests")
    for leave in leaves:
        if leave['id'] == leave_resp['id']:
            print(f"   ✓ Our leave: status={leave['status']}, days={leave['days']}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✓")
print("=" * 60)

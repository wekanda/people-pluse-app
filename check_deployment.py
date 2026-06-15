import urllib.request, urllib.parse, json
base='https://people-pluse-backend-1.onrender.com'

print("=== CHECKING LIVE ACCOUNTS ===")
for acct in [{'email':'live_staff@peoplepluse.com','password':'LiveStaff123!'},{'email':'live_manager@peoplepluse.com','password':'LiveManager123!'}]:
    try:
        req=urllib.request.Request(base+'/auth/token', data=urllib.parse.urlencode({'username':acct['email'],'password':acct['password']}).encode(), headers={'Content-Type':'application/x-www-form-urlencoded'})
        tok=json.loads(urllib.request.urlopen(req).read().decode())['access_token']
        req2=urllib.request.Request(base+'/auth/me', headers={'Authorization':'Bearer '+tok})
        me=json.loads(urllib.request.urlopen(req2).read().decode())
        print('✓ ME', acct['email'], me)
    except Exception as e:
        print(f"✗ {acct['email']}: {e}")

print("\n=== CHECKING EMPLOYEES ===")
try:
    emps=json.loads(urllib.request.urlopen(base+'/api/employees').read().decode())
    print(f"Total employees: {len(emps)}")
    for e in emps[:3]:
        print(f"  - {e['id']}: {e['full_name']} ({e['file_code']})")
except Exception as e:
    print(f"Error fetching employees: {e}")

print("\n=== ATTEMPTING LEAVE REQUEST ===")
try:
    req=urllib.request.Request(base+'/auth/token', data=urllib.parse.urlencode({'username':'live_staff@peoplepluse.com','password':'LiveStaff123!'}).encode(), headers={'Content-Type':'application/x-www-form-urlencoded'})
    staff_tok=json.loads(urllib.request.urlopen(req).read().decode())['access_token']
    
    # Try with first employee ID if available
    emp_id = 1
    leave={'employee_id':emp_id,'start_date':'2026-07-10','end_date':'2026-07-12','reason':'Test leave','type':'Annual Leave'}
    req2=urllib.request.Request(base+'/api/leave/request', data=json.dumps(leave).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer '+staff_tok})
    leave_resp=json.loads(urllib.request.urlopen(req2).read().decode())
    print('✓ LEAVE CREATED', leave_resp)
except urllib.error.HTTPError as e:
    print(f"✗ HTTP Error {e.code}: {e.read().decode()}")
except Exception as e:
    print(f"✗ Error: {e}")

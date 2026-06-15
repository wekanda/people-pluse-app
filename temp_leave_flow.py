import urllib.request, urllib.parse, json
base='https://people-pluse-backend-1.onrender.com'
staff={'email':'live_staff@peoplepluse.com','password':'LiveStaff123!'}
manager={'email':'live_manager@peoplepluse.com','password':'LiveManager123!'}
req=urllib.request.Request(base+'/auth/token', data=urllib.parse.urlencode({'username':staff['email'],'password':staff['password']}).encode(), headers={'Content-Type':'application/x-www-form-urlencoded'})
staff_tok=json.loads(urllib.request.urlopen(req).read().decode())['access_token']
leave={'employee_id':1,'start_date':'2026-07-10','end_date':'2026-07-12','reason':'Test leave','type':'Annual Leave'}
req2=urllib.request.Request(base+'/api/leave/request', data=json.dumps(leave).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer '+staff_tok})
leave_resp=json.loads(urllib.request.urlopen(req2).read().decode())
print('LEAVE CREATED', leave_resp)
reqm=urllib.request.Request(base+'/auth/token', data=urllib.parse.urlencode({'username':manager['email'],'password':manager['password']}).encode(), headers={'Content-Type':'application/x-www-form-urlencoded'})
manager_tok=json.loads(urllib.request.urlopen(reqm).read().decode())['access_token']
req3=urllib.request.Request(base+f"/api/leave/approve/{leave_resp['id']}", data=b'', headers={'Authorization':'Bearer '+manager_tok})
appr=json.loads(urllib.request.urlopen(req3).read().decode())
print('LEAVE APPROVED', appr)
req4=urllib.request.Request(base+f"/api/leave/requests?employee_id=1", headers={'Authorization':'Bearer '+manager_tok})
verify=json.loads(urllib.request.urlopen(req4).read().decode())
print('VERIFY', verify)

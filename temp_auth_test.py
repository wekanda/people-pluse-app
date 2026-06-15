import urllib.request, urllib.parse, json
base='https://people-pluse-backend-1.onrender.com'
accounts=[
    {'email':'live_admin@peoplepluse.com','password':'LiveAdmin123!'},
    {'email':'live_manager@peoplepluse.com','password':'LiveManager123!'},
    {'email':'live_staff@peoplepluse.com','password':'LiveStaff123!'}
]
for a in accounts:
    data=urllib.parse.urlencode({'username':a['email'],'password':a['password']}).encode()
    req=urllib.request.Request(base + '/auth/token', data=data, headers={'Content-Type':'application/x-www-form-urlencoded'})
    try:
        resp=urllib.request.urlopen(req)
        tok=json.loads(resp.read().decode())['access_token']
        print('TOKEN OK', a['email'], tok[:20]+'...')
        req2=urllib.request.Request(base + '/auth/me', headers={'Authorization':'Bearer '+tok})
        resp2=urllib.request.urlopen(req2)
        print('ME OK', a['email'], resp2.read().decode())
    except Exception as e:
        msg=str(e)
        if hasattr(e,'read'):
            try: msg=e.read().decode()
            except: pass
        print('FAIL', a['email'], msg)

import urllib.request, json, time

base = 'https://people-pluse-backend-1.onrender.com'

print("Waiting for Render deployment to complete...")
print("(This may take 2-3 minutes)")
print()

for attempt in range(60):
    try:
        resp = urllib.request.urlopen(base + '/api/health', timeout=5)
        # Now check if employees exist
        resp2 = urllib.request.urlopen(base + '/api/employees/', timeout=5)
        emps = json.loads(resp2.read().decode())
        
        if len(emps) > 0:
            print(f"✓ Deployment ready! Found {len(emps)} employees:")
            for e in emps:
                print(f"  - {e['id']}: {e['full_name']} ({e['file_code']})")
            break
        else:
            print(f"  [{attempt+1}/60] Employees not yet created...")
    except Exception as e:
        print(f"  [{attempt+1}/60] Waiting for deployment: {type(e).__name__}")
    
    time.sleep(2)
else:
    print("✗ Deployment timeout after 2 minutes")

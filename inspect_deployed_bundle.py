from pathlib import Path
import re
p = Path(r"C:\Users\WekandaSamuel\Desktop\deployed_index_BDlQeykL.js")
print('exists', p.exists())
print('size', p.stat().st_size)
text = p.read_text(encoding='utf-8', errors='ignore')
patterns = [
    r'URLSearchParams',
    r'new\s+URLSearchParams',
    r'append\(.*username',
    r'append\(.*password',
    r'auth/token',
    r'auth/me',
    r'x-www-form-urlencoded',
    r'Content-Type',
    r'People Pluse Login',
    r'Login failed',
]
for pat in patterns:
    m = re.search(pat, text)
    print(pat, 'FOUND' if m else 'MISSING')
    if m:
        start = max(0, m.start()-80)
        end = min(len(text), m.end()+80)
        print(text[start:end])
        print('---')

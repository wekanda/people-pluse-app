import pathlib, re
p = pathlib.Path(r"C:\Users\WekandaSamuel\Desktop\deployed_index_BDlQeykL.js")
text = p.read_text(encoding='utf-8', errors='ignore')
patterns = [r'URLSearchParams', r'new\s+URLSearchParams', r'append\(.*username', r'append\(.*password', r'auth/token', r'auth/me', r'x-www-form-urlencoded', r'Content-Type', r'People Pluse Login', r'Login failed']
for pat in patterns:
    m = re.search(pat, text)
    print(pat, 'FOUND' if m else 'MISSING')
    if m:
        start = max(m.start()-60, 0)
        end = min(m.end()+60, len(text))
        print(text[start:end])
        print('---')

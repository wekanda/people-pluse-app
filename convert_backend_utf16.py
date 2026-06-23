import os
import glob
import codecs

root = os.path.join(os.getcwd(), 'backend')
paths = glob.glob(os.path.join(root, '*.py')) + glob.glob(os.path.join(root, 'routers', '*.py'))
converted = []
for path in sorted(paths):
    with open(path, 'rb') as f:
        data = f.read()
    if b'\x00' in data:
        for enc in ['utf-16', 'utf-16-le', 'utf-16-be']:
            try:
                text = data.decode(enc)
                break
            except Exception:
                text = None
        if text is None:
            raise RuntimeError(f'Unable to decode {path}')
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        converted.append((path, enc))

print('converted', converted)

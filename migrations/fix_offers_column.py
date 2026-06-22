import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)) or '.')
from database import engine

print('Checking offers table columns...')
from sqlalchemy import text
with engine.connect() as conn:
    res = conn.execute(text("PRAGMA table_info('offers')")).fetchall()
    cols = [r[1] for r in res]
    print('Existing columns:', cols)
    to_add = []
    if 'applicant_id' not in cols:
        to_add.append("applicant_id INTEGER")
    if 'position' not in cols:
        to_add.append("position VARCHAR")
    if 'start_date' not in cols:
        to_add.append("start_date DATE")
    if 'created_at' not in cols:
        to_add.append("created_at DATETIME")
    if to_add:
        for coldef in to_add:
            print('Adding column:', coldef)
            conn.execute(text(f"ALTER TABLE offers ADD COLUMN {coldef}"))
        print('Added columns:', to_add)
    else:
        print('All expected columns present.')

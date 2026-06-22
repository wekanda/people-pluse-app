import sqlite3
conn = sqlite3.connect('people_pluse.db')
cur = conn.cursor()
cur.execute("PRAGMA table_info('offers')")
rows = cur.fetchall()
print('rows:', rows)
print('columns:', [r[1] for r in rows])
conn.close()

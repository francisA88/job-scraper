''' Database read/write operations for saving job links. This is necessary so the script can check if a job has been previously found, and doesn't send it twice.'''

import sqlite3

db = sqlite3.connect(".database.sqlite3")
cursor = db.cursor()

def create_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS job_links(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   link TEXT UNIQUE NOT NULL 
                   );''')
    db.commit()

def link_exists(link:str) ->bool:
    cursor.execute("SELECT 1 FROM job_links WHERE link=? LIMIT 1;", (link,))
    return bool(cursor.fetchone())

def save_link(link:str):
    cursor.execute("INSERT OR IGNORE INTO job_links (link) values (?)", (link,))
    db.commit()

# Create a table first
create_table()
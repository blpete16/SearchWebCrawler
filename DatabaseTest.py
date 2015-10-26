
import sqlite3

DATABASEFILE = "index.db"
terminate = False

def makeconn():
    return sqlite3.connect(DATABASEFILE)

def ShowMeURLS():
    conn = makeconn()
    c = conn.cursor()
    c.execute("SELECT url FROM urls")
    rows = c.fetchall()
    for row in rows:
        print "hello" + str(row[0])
    conn.commit()
    conn.close()

ShowMeURLS()

import sqlite3
import os

PGFOLDER = '/home/brian/Desktop/gradschool/InfoRetrieval/DataStore/FullPages/'
DATABASEFILE = '/home/brian/Desktop/gradschool/InfoRetrieval/DataStore/index.db'

conn = sqlite3.connect(DATABASEFILE)
c = conn.cursor()

#c.execute("UPDATE urls SET url = replace(url, '\n', '')")
#c.execute("UPDATE urls SET email = replace(email, '\n', '')")

c.execute("SELECT DISTINCT author FROM urls")
rows = c.fetchall()

for row in rows:
    author = row[0]
    c.execute('SELECT id FROM urls WHERE author = "' + author + '"')
    copyrows = c.fetchall()
    print copyrows
    print len(copyrows)
    if(len(copyrows) > 1):
        for cval in xrange(0, len(copyrows)):
            print cval
            badid = copyrows[cval][0]
            print badid
            fname = PGFOLDER + str(badid)
            if(os.path.isfile(fname)):
                os.remove(fname)
            c.execute('DELETE FROM term_index WHERE url_id = ' + str(badid))
            c.execute('DELETE FROM urls WHERE id = '+ str(badid))
            

conn.commit()
conn.close()


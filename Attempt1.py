#references for writing this included
#beautiful soup homepage 
#http://h3manth.com/new/blog/2013/web-crawler-with-python-twisted/

import os
from bs4 import BeautifulSoup
from twisted.web.client import getPage
import sqlite3

STARTNEW = True
url_buffer = []
BASEFILE = "baseurls.dat"
DATABASEFILE = "index.db"

def makeconn():
    return sqlite3.connect(DATABASEFILE)

def extractPageInfo(html):
    soup = BeautifulSoup(html)
    soup.prettify()
    for atag in soup.findAll('a'):
        print alink
    for titletag in soup.findAll('Title'):
        print titletag
    
def CrawlPage(url, masterindex):
    deferred = getPage(url)
    deferred.addCallback(extractPageInfo)
    #deferred.addCallback(unionWithMaster, masterindex)
        
    
def CrawlPages():
    if(not os.path.isfile(DATABASEFILE)):
        conn = makeconn()
        c = conn.cursor()
        c.execute('''CREATE TABLE urls 
                      (id integer primary key, url text not null, author text, visited bit )''')
        filebase = open(BASEFILE, 'r')
        for line in filebase:
            val = sql_safe_text(line)
            c.execute('INSERT INTO urls (url) VALUES ("' + val + '")')
        filebase.close()
        conn.commit()
        conn.close()
    while(True):
        

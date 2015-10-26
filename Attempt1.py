#references for writing this included
#beautiful soup homepage 
#http://h3manth.com/new/blog/2013/web-crawler-with-python-twisted/

import os
from Utilities import *
from bs4 import BeautifulSoup
from twisted.web.client import getPage
from twisted.internet import reactor
import sqlite3
import time
import thread
from threading import Thread

SLEEPTIME = 10
STARTNEW = True
url_buffer = []
BASEFILE = "baseurls.dat"
DATABASEFILE = "index.db"
terminate = False

def makeconn():
    return sqlite3.connect(DATABASEFILE)

def GrabLink(url, atag):
    val = atag.attrs["href"]
    dbgprint(val)
    return val

def extractPageInfo(html, url, hop=0):
    dbgprint("First line extract")
    soup = BeautifulSoup(html, 'html.parser')
    soup.prettify()
    atags = soup.findAll('a')
    for atag in atags:
        linktext = GrabLink(url, atag)
        #dbgprint(atag)
    titles = soup.findAll('title')
    for titletag in titles:
        dbgprint(titletag)
    
def CrawlPage(url, hop=0):
    deferred = getPage(url)
    dbgprint("before deferred add")
    deferred.addCallback(extractPageInfo, url, hop=hop)
        
    
def Setup():
    if(not os.path.isfile(DATABASEFILE)):
        conn = makeconn()
        c = conn.cursor()
        c.execute('''CREATE TABLE urls 
                      (id integer primary key, url text not null, author text, visited bit )''')
        filebase = open(BASEFILE, 'r')
        for line in filebase:
            val = sql_safe_text(line)
            c.execute('INSERT INTO urls (url, visited) VALUES ("' + val + '", 0)')
        filebase.close()
        conn.commit()
        conn.close()

def PrimeDeferreds():
    conn = makeconn()
    c = conn.cursor()
    dbgprint("Before query")
    c.execute('SELECT * FROM urls WHERE visited=0')
    rows = c.fetchall()
    for row in rows:
        idval = row[0]
        urlval = row[1]
        urlvalascii = urlval.encode('ascii','ignore')
        dbgprint("Before crawlpage: " + urlvalascii)
        CrawlPage(urlvalascii, hop=5)

if __name__ == "__main__":
    Setup()
    PrimeDeferreds()
    reactor.callLater(5, reactor.stop)
    reactor.run()
    print "Got here"

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

def GetAuthor(soup):
    title = soup.find('title')
    if(title is None):return ""
    if(title.string is None):return ""
    return title.string

def GrabLink(url, atag):
    try:
        val = atag.attrs["href"]
        if(val.startswith("mailto")):
            return None
        if(".edu" in val) or(".com" in val) or (".org" in val):
            pass
        else:
            val = url + val
        #dbgprint(val)
        return val
    except KeyError, e:
        return None

def modifyDatabase(url, author):
    if(author is None or author ==""):
        return
    conn = makeconn()
    c = conn.cursor()
    c.execute('SELECT ID FROM urls WHERE url="'+url+'"')
    
    rows = c.fetchall()
    if(rows is None or len(rows) == 0):
        c.execute('INSERT INTO urls (url, visited, author) VALUES ("' + url + '", 0, "' + author + '")')
    else:
        idval = rows[0][0]
        c.execute('UPDATE urls SET url="'+ url + '",visited=0,author="'+author+'" WHERE id = ' + str(idval))
    conn.commit()
    conn.close()

def extractPageInfo(html, url, hop=0):
    dbgprint("First line extract")
    soup = BeautifulSoup(html, 'html.parser')
    soup.prettify()
    dbgprint("Before Get Author")
    author = GetAuthor(soup)

    dbgprint("Before ModDB")
    modifyDatabase(url, author)

    atags = soup.findAll('a')
    dbgprint("Before For Loop")
    for atag in atags:
        linktext = GrabLink(url, atag)
        if(not linktext is None):
            dbgprint(linktext)
            #CrawlPage(linktext, hop - 1)
    
def CrawlPage(url, hop=0):
    if(hop < 0):return
    if(url is None):return
    urlvalascii = url.encode('ascii','ignore')
    deferred = getPage(urlvalascii)
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
    conn.close()
    for row in rows:
        idval = row[0]
        urlval = row[1]
        urlvalascii = urlval.encode('ascii','ignore')
        dbgprint("Before crawlpage: " + urlvalascii)
        CrawlPage(urlvalascii, hop=0)

def monitorThread():
    while(True):
        time.sleep(5)
        conn = makeconn()
        c = conn.cursor()
        c.execute("SELECT id FROM urls")
        rows = c.fetchall()
        conn.commit()
        conn.close()
        if(len(rows) > 100):
            reactor.callFromThread(reactor.stop)
            break;


if __name__ == "__main__":
    Setup()
    PrimeDeferreds()
    t = Thread(target=monitorThread)
    t.start()
    #reactor.callLater(5, reactor.stop)
    reactor.run()
    print "Got here"

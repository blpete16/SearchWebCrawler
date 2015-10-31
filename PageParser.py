#references for writing this included
#beautiful soup homepage 
#http://h3manth.com/new/blog/2013/web-crawler-with-python-twisted/

import os
from Utilities import *
from bs4 import BeautifulSoup
from twisted.web.client import getPage
from twisted.internet import reactor
from twisted.python import log
from stemming.porter2 import stem
import sqlite3
import time
import thread
from threading import Thread
from BaseFileContainer import BaseFileContainer

SLEEPTIME = 10
STARTNEW = True
url_buffer = []
BASEFILE = "baseurls.dat"
DATABASEFILE = "index.db"
terminate = False

def makeconn():
    return sqlite3.connect(DATABASEFILE)

def sanitize(text):
    ZERO_ASCII = 48
    NINE_ASCII = 57
    CAPA_ASCII = 65
    CAPZ_ASCII = 90
    SPACE_ASCII = 32
    LOWA_ASCII = 97
    LOWZ_ASCII = 122

    output = ""
    for letter in text:
        asciival = ord(letter)
        if(asciival == SPACE_ASCII):
            output = output + letter
        if(asciival >= ZERO_ASCII and asciival <= NINE_ASCII):
            output = output + letter
        if(asciival >= CAPA_ASCII and asciival <= CAPZ_ASCII):
            output = output + str(unichr(32+asciival))
        if(asciival >= LOWA_ASCII and asciival <= LOWZ_ASCII):
            output = output + letter
    return output

def addterm(aterm, c, url_id):
    c.execute('INSERT OR IGNORE INTO terms(term) VALUES("'+aterm+'")')
    c.execute('INSERT INTO term_index(term, url_id) VALUES("'+aterm+'",'+str(url_id)+')') 

def pullTerms(soup, url_id):
    conn = makeconn()
    c = conn.cursor()
    textvals = soup.get_text()
    textlist = textvals.split()
    textlist = map(sanitize, textlist)
    textlist = map(stem, textlist)
    textlist = list(set(textlist))
    for term in textlist:
        addterm(term, c, url_id)
    conn.commit()
    conn.close()
    
def extractPageInfo(html, url_id):
    dbgprint("First line extract")
    soup = BeautifulSoup(html, 'html.parser')
    soup.prettify()

    dbgprint("Before ModDB")
    pullTerms(soup, url_id)
    
def CrawlPage(url, url_id):
    if(url is None):return
    urlvalascii = url.encode('ascii','ignore')
    deferred = getPage(urlvalascii)
    dbgprint("before deferred add")
    deferred.addCallback(extractPageInfo, url_id)
    deferred.addErrback(log.err)
    
def Setup():
    if(not os.path.isfile(DATABASEFILE)):
        dbgprint("SETTING UP!!")
        conn = makeconn()
        c = conn.cursor()
        c.execute('''CREATE TABLE urls 
                      (id integer primary key, url text not null, author text, visited bit )''')
        c.execute('''CREATE TABLE terms
                      (term text primary key)''')
        c.execute('''CREATE TABLE term_index
                      (term text, url_id integer, FOREIGN KEY(term) REFERENCES terms(term), FOREIGN KEY(url_id) REFERENCES urls(id))''')
        filebase = BaseFileContainer(BASEFILE)
        while True:
            tup = filebase.read()
            if(tup is None):
                break
            c.execute('INSERT INTO urls (url, author, visited) VALUES ("' + tup[0] + '","' + tup[1] + '", 0)')
    
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
        CrawlPage(urlvalascii, idval)


if __name__ == "__main__":
    Setup()
    PrimeDeferreds()
    reactor.callLater(5, reactor.stop)
    reactor.run()
    print "Got here"

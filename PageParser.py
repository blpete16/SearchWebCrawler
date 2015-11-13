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
import math
from threading import Thread
from BaseFileContainer import BaseFileContainer
from Utilities import PGFOLDER, DATABASEFILE

SLEEPTIME = 10
STARTNEW = True
url_buffer = []
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

def addterm(aterm, c, url_id, freq):
    c.execute('INSERT OR IGNORE INTO terms(_term, docs) VALUES("'+aterm+'",0)')
    c.execute('INSERT INTO term_index(_term, url_id, freq) VALUES("'+aterm+'",'+str(url_id)+ ',' + str(freq) + ')') 
    c.execute('SELECT docs FROM terms WHERE _term = "' + aterm + '"')
    fetched = c.fetchone()
    val = int(fetched[0])
    val = val + 1
    dbgprint (aterm + " SET TO " + str(val))
    c.execute('UPDATE terms SET docs=' + str(val) + ' WHERE _term = "' + aterm + '"')
    
    if(DEBUG):
        c.execute('SELECT docs FROM terms WHERE _term = "peterson"')
        rows = c.fetchall()
        if(len(rows) > 0):
            val = int(rows[0][0])
            if(val == 4):
                dbgprint("IT WAS THIS ONE!!!")
                dbgprint("ID  " + str(url_id))
                dbgprint("TERM  "+aterm)

def dropToFile(url_id, text):
    with open(PGFOLDER + str(url_id), 'w') as outfile:
        outfile.write(text.encode('utf8'))

def pullTerms(textvals, url_id):
    conn = makeconn()
    c = conn.cursor()
    textlist = textvals.split()
    textlist = map(sanitize, textlist)
    textlist = map(stem, textlist)
    singletextlist = list(set(textlist))
    singletextlist = filter(len, singletextlist)
    for term in singletextlist:
        freq = textlist.count(term)
        addterm(term, c, url_id, freq)

    c.execute("UPDATE urls SET visited = 1 WHERE id = " + str(url_id))
    conn.commit()
    conn.close()
    
def extractPageInfo(html, url_id):
    dbgprint("First line extract")
    soup = BeautifulSoup(html, 'html.parser')
    soup.prettify()

    dbgprint("Before ModDB")
    textvals = soup.get_text()
    dropToFile(url_id, textvals)
    pullTerms(textvals, url_id)

def Clean():
    conn = makeconn()
    c = conn.cursor()
    c.execute("DROP TABLE term_index")
    c.execute("DROP TABLE terms")
    conn.commit()
    c = conn.cursor()
    c.execute('''CREATE TABLE terms
                      (_term text primary key, docs integer, idf float)''')
    c.execute('''CREATE TABLE term_index
                      (_term text, url_id integer, freq integer, FOREIGN KEY(_term) REFERENCES terms(_term), FOREIGN KEY(url_id) REFERENCES urls(id))''')
    conn.commit()
    conn.close()
    
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
                      (_term text primary key, docs integer, idf float)''')
        c.execute('''CREATE TABLE term_index
                      (_term text, url_id integer, freq integer, FOREIGN KEY(_term) REFERENCES terms(_term), FOREIGN KEY(url_id) REFERENCES urls(id))''')
        filebase = BaseFileContainer()
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
    c.execute('SELECT * FROM urls')
    rows = c.fetchall()
    conn.close()
    for row in rows:
        idval = row[0]
        urlval = row[1]
        urlvalascii = urlval.encode('ascii','ignore')
        dbgprint("Before crawlpage: " + urlvalascii)
        if(not os.path.isfile(PGFOLDER+str(idval))):
            CrawlPage(urlvalascii, idval)
            dbgprint("SHOULD NOT BE HERE!")
        else:
            wholefile = ""
            with open(PGFOLDER+str(idval), 'r') as afile:
                wholefile = afile.read()
            pullTerms(wholefile, idval)

def calcIDF():
    
    conn = makeconn()
    c = conn.cursor()
    c.execute('SELECT COUNT(id) FROM urls')
    numpages = float(int(c.fetchone()[0]))
    c.execute('SELECT _term, docs from terms')
    rows = c.fetchall()
    for row in rows:
        term = str(row[0])
        docs = int(row[1])
        idf = math.log(numpages / docs)
        c.execute('UPDATE terms SET idf='+str(idf)+' WHERE _term ="' + term + '"')
    conn.commit()
    conn.close()


if __name__ == "__main__":
    Setup()
    Clean()
    PrimeDeferreds()
    reactor.callLater(5*60, reactor.stop)
    reactor.run()
    calcIDF()
    print "Got here"

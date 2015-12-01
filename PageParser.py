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

def addterm(aterm, c, url_id, freq, RImod):
    c.execute('SELECT id, docs FROM terms WHERE _term = "' + aterm + '"')
    fetched = c.fetchone()
    anid = ""
    if(fetched is None):
        c.execute('INSERT INTO terms(_term, docs) VALUES("'+aterm+'",1)')
        anid = c.lastrowid
    else:
        anid = str(fetched[0])
        dval = str(int(fetched[1]) + 1)
        c.execute('UPDATE terms SET docs =' + dval + ' WHERE id = '+ anid)
    c.execute('INSERT INTO term_index(_term_id, url_id, freq, RImod) VALUES(' + str(anid) + ','+str(url_id)+','+str(freq)+','+str(RImod)+')')

    
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

def findAllInds(toSearch, term):
	start = 0
	Rlist=[]
	while True:

		start = toSearch.find(term, start)
		if start == -1: 
			return Rlist
		Rlist.append(start)
		start += len(term) 



def findBestIndex(listOfInds, nearAndAfter):
	for i in listOfInds:
		if (i>nearAndAfter):
			return i
	return -1
	

def pullTerms(textvals, url_id):
    conn = makeconn()
    c = conn.cursor()
    Ind=textvals.find('Research Interest')
	

    textlist = textvals.split()
    textlist = map(sanitize, textlist)
    textlist = map(stem, textlist)
    singletextlist = list(set(textlist))
    goodsize = lambda s : len(s) > 0 and len(s) < 40
    singletextlist = filter(goodsize, singletextlist)
    for term in singletextlist:
	
        RImod=0	
        if (Ind != -1):
	    lInd = findAllInds(textvals, term)
	    oneInd = findBestIndex(lInd, Ind)
	    v= oneInd-Ind
            if (v>700 or v<0):	
		RImod=0
	    else:
		RImod=(700.0-v)/700.0

        freq = textlist.count(term)
        addterm(term, c, url_id, freq, RImod)

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
                      (id integer primary key, _term text, docs integer, idf float)''')
    c.execute('''CREATE TABLE term_index
                      (_term_id integer, url_id integer, freq integer, RImod float, FOREIGN KEY(_term_id) REFERENCES terms(id), FOREIGN KEY(url_id) REFERENCES urls(id))''')
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
    conn = None
    if(not os.path.isfile(DATABASEFILE)):

        conn = makeconn()
        c = conn.cursor()
        dbgprint("SETTING UP!!")
        c.execute('''CREATE TABLE urls 
                      (id integer primary key, url text not null, author text, email text, visited bit )''')
        c.execute('''CREATE TABLE terms
                      (id integer primary key, _term text, docs integer, idf float)''')
        c.execute('''CREATE TABLE term_index
                      (_term_id integer, url_id integer, freq integer, RImod float, FOREIGN KEY(_term_id) REFERENCES terms(id), FOREIGN KEY(url_id) REFERENCES urls(id))''')
        filebase = BaseFileContainer()
        while True:
            tup = filebase.read()
            if(tup is None):
                break
            c.execute('INSERT INTO urls (url, author, visited) VALUES ("' + tup[0] + '","' + tup[1] + '", 0)')
    
    else:

        conn = makeconn()
        c = conn.cursor()
        filebase = BaseFileContainer()
        while True:
            vals = filebase.read()
            if(vals is None):
                break
            c.execute('SELECT ID FROM urls WHERE url ="' + vals[0] + '"');
            fetched = c.fetchone()
            if( fetched is None):
                c.execute('INSERT INTO urls (url, author, visited, email) VALUES ("' + vals[0] + '","' + vals[1] + '",0,"'+vals[2]+'")')
            else:
                anid = str(fetched[0])
                c.execute('UPDATE urls SET email = "' + vals[2] + '" WHERE ID = ' + anid)

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
            #raise Exception('unfound file')
            CrawlPage(urlvalascii, idval)
            #dbgprint("SHOULD NOT BE HERE!")
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
    reactor.callLater(10*60, reactor.stop)
    reactor.run()
    calcIDF()
    print "Got here"


    c.execute('INSERT OR IGNORE INTO terms(_term, docs) VALUES("'+aterm+'",0)')
    c.execute('INSERT INTO term_index(_term, url_id, freq) VALUES("'+aterm+'",'+str(url_id)+ ',' + str(freq) + ')') 
    c.execute('SELECT docs FROM terms WHERE _term = "' + aterm + '"')
    fetched = c.fetchone()
    val = int(fetched[0])
    val = val + 1
    dbgprint (aterm + " SET TO " + str(val))
    c.execute('UPDATE terms SET docs=' + str(val) + ' WHERE _term = "' + aterm + '"')



While the cloud computing definition has evolved, basics remain. The three pillars of cloud -- public, private and hybrid –offer benefits like elasticity, flexibility and

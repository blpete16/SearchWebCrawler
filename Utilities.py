

PGFOLDER = '/home/brian/Desktop/gradschool/InfoRetrieval/DataStore/FullPagesTwo/'
DATABASEFILE = '/home/brian/Desktop/gradschool/InfoRetrieval/DataStore/indextwo.db'

DEBUG = True
def dbgprint(val):
    if(DEBUG):
        print(str(val))

def sql_safe_text(text):
    return text

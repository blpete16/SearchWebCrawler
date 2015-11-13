

PGFOLDER = '/home/brian/Desktop/gradschool/InfoRetrieval/DataStore/FullPages/'
DATABASEFILE = '/home/brian/Desktop/gradschool/InfoRetrieval/DataStore/index.db'

DEBUG = True
def dbgprint(val):
    if(DEBUG):
        print(str(val))

def sql_safe_text(text):
    return text

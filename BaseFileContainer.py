
BASEFILE = 'BaseWebpages.csv'

class BaseFileContainer():
    def __init__(self):
        self.filename = BASEFILE
        self.filestrm = open(self.filename, 'r')

    def read(self):
        aline = self.filestrm.readline()
        if(aline == ""):
            self.filestrm.close()
            return None
        vals = aline.split(',')
        if(len(vals < 6)):
            return self.read()
        twovals = vals[4:6]
        return twovals

    def close(self):
        self.filestrm.close()


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
        if(len(vals) < 6):
            return self.read()
        twovals = vals[4:7]
        if(len(twovals[0]) == 0 or len(twovals[1]) == 0):
            return self.read()
        for i in xrange(3):
            twovals[i] = twovals[i].strip()
        swap = twovals[1]
        twovals[1] = twovals[0]
        twovals[0] = swap
        return twovals

    def close(self):
        self.filestrm.close()


class BaseFileContainer():
    def __init__(self, filename):
        self.filename = filename
        self.filestrm = open(self.filename, 'r')

    def read(self):
        aline = self.filestrm.readline()
        if(aline == ""):
            self.filestrm.close()
            return None
        vals = aline.split(',')
        return vals

    def close(self):
        self.filestrm.close()

import struct, math

def makeFloat(a, b):
    if b == 0:
        return float(a)
    return a + b * 10**-(math.floor(math.log10(b))+1)
    
def bString(buf, offs=0):
    len = struct.unpack_from("<H", buf, offset=offs)[0]
    return (buf[offs+2:offs+len+2].decode("latin"), offs+len+2)

class pexParser:
    structure = {
        "header": {
            "magic": 0,
            "version": 0.0,
            "gameId": 0,
            "compilationTime": 0,
            "sourceName": "",
            "username": "",
            "machinename": ""
        },
        "strings": [],
        "debug": {
            "modificationTime": 0,
            "functionCount": 0,
            "functions": []
        },
        "flags": {},
        "objects": {},
    }
    readerPos = 0
    data = None
    def parseHeader(self, data=None, pos=None):
        if data == None:
            data = self.data
        if pos == None:
            pos = self.readerPos
            
        tmp = struct.unpack_from("<IBBHQ", data, offset=pos)
        self.structure["header"]["magic"] = tmp[0]
        self.structure["header"]["version"] = makeFloat(tmp[1],tmp[2])
        self.structure["header"]["gameId"] = tmp[3] 
        self.structure["header"]["compilationTime"] = tmp[4]
        pos = 16
        self.structure["header"]["sourceName"], pos = bString(data, pos)
        self.structure["header"]["username"], pos = bString(data, pos)
        self.structure["header"]["machinename"], pos = bString(data, pos)
        
        self.readerPos = pos
    
    def parseStringTable(self, data=None, pos=None):
        if data == None:
            data = self.data
        if pos == None:
            pos = self.readerPos
            
        cnt = struct.unpack_from("<H", data, offset=pos)[0]
        pos = pos + 2
        for i in range(cnt):
            tmp, pos = bString(data, pos)
            self.structure["strings"].append(tmp)
            
        self.readerPos = pos
        
    def parseDebugInfo(self, data=None, pos=None):
        if data == None:
            data = self.data
        if pos == None:
            pos = self.readerPos
            
        hasDebug, modTime, funcs = struct.unpack_from("<BQH", data, offset=pos)
        pos = pos + 1
        if hasDebug != 0:
            pos = pos + 10
            self.structure["debug"]["modificationTime"] = modTime
            #parse Debug function
            for i in range(funcs):
                oni, sni, fni, ft, ic = struct.unpack_from("<HHHBH",\
                    data, offset=pos)
                #print(ic)
                pos = pos + 9
                #TODO: Resolve these
                tmp = {
                    "object": self.structure["strings"][oni],
                    "state": self.structure["strings"][sni],
                    "function": self.structure["strings"][fni],
                    "type": self.structure["strings"][ft],
                    "lines": []
                };
                for x in range(ic):
                    tmp["lines"].append(struct.unpack_from("<H", data, offset=pos)[0])
                    pos = pos + 2
                self.structure["debug"]["functions"].append(tmp)
                
        self.readerPos = pos
        
    def parseUserFlags(self, data=None, pos=None):
        if data == None:
            data = self.data
        if pos == None:
            pos = self.readerPos
            
        cnt = struct.unpack_from("<H", data, offset=pos)[0]
        pos = pos + 2
        for i in range(cnt):
            nam, val = struct.unpack_from("<HB", data, offset=pos)
            pos = pos + 3
            self.structure["flags"][self.structure["strings"][nam]]=val
            
        self.readerPos = pos
    
    def parseObjectData(self, data=None, pos=None):
        if data == None:
            data = self.data
        if pos == None:
            pos = self.readerPos
            
        cnt = struct.unpack_from("<H", data, offset=pos)[0]
        pos = pos + 2
        for i in range(cnt):
            nam, siz, pcn, dci, uf, asn = struct.unpack_from("<HIHHIH",\
                data, offset=pos)
            pos = pos + 36
            tmp = {
                "name": self.structure["strings"][nam],
                "parentClass": self.structure["strings"][pcn],
                "docString": self.structure["strings"][dci],
                "userFlags": uf,
                "autoStateName": self.structure["strings"][asn],
                "variables": {},
                "properties": {},
                "states": {}
            }
            
            #Variable data
            siz = struct.unpack_from("<H", data, offset=pos)[0]
            pos = pos + 2
            for x in range(siz):
                nam, ntyp, flg, typ = struct.unpack_from("<HHIB", data,\
                    offset=pos)
                pos = pos + 10
                tmp["states"][self.structure["strings"][nam]] = {
                    "typeName": self.structure["strings"][ntyp],
                    "userFlags": flg,
                    "type": typ,
                    "value": None
                }
                if typ == 2:
                    tmp["states"][self.structure["strings"][nam]] = \
                        self.structure["strings"][struct.unpack_from("<H", \
                        data, offset=pos)[0]]
                elif typ == 3:
                    tmp["states"][self.structure["strings"][nam]]\
                        = struct.unpack_from("<i", data, offset=pos)[0]
                elif typ == 4:
                    tmp["states"][self.structure["strings"][nam]]\
                        = struct.unpack_from("<f", data, offset=pos)[0]
                elif typ == 5:
                    val = struct.unpack_from("<?", data, offset=pos)[0]
                    if val == True:
                        tmp["states"][self.structure["strings"][nam]] = True
                    else:
                        tmp["states"][self.structure["strings"][nam]] = False
                        
            #Property data
            siz = struct.unpack_from("<H", data, offset=pos)[0]
            pos = pos + 2
            for x in range(siz):
                nam, ntyp, flg, typ = struct.unpack_from("<HHIB", data,\
                    offset=pos)
                pos = pos + 10
                tmp["states"][self.structure["strings"][nam]] = {
                    "typeName": self.structure["strings"][ntyp],
                    "userFlags": flg,
                    "type": typ,
                    "value": None
                }
                if typ == 2:
                    tmp["states"][self.structure["strings"][nam]] = \
                        self.structure["strings"][struct.unpack_from("<H", \
                        data, offset=pos)[0]]
                elif typ == 3:
                    tmp["states"][self.structure["strings"][nam]]\
                        = struct.unpack_from("<i", data, offset=pos)[0]
                elif typ == 4:
                    tmp["states"][self.structure["strings"][nam]]\
                        = struct.unpack_from("<f", data, offset=pos)[0]
                elif typ == 5:
                    val = struct.unpack_from("<?", data, offset=pos)[0]
                    if val == True:
                        tmp["states"][self.structure["strings"][nam]] = True
                    else:
                        tmp["states"][self.structure["strings"][nam]] = False
            self.structure["objects"].append(tmp)
        self.readerPos = pos
    
    def parse(self):
        self.parseHeader()
        self.parseStringTable()
        self.parseDebugInfo()
        self.parseUserFlags()
        self.parseObjectData()
    
    def __init__(self, data):
        self.data = data

def load(data):
    parser = pexParser(data)
    parser.parse()
    return parser.structure
    
def test():
    print("Hello!")
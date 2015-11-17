#!/bin/python
import json
from libPapyrus import pex

#Set this to your Fallout 4 root folder
fallout_root = "C:/Program Files (x86)/Steam/steamapps/common/Fallout 4/"

def print_r(data, ret=False):
    if ret:
        return json.dumps(data,indent=4)
    print(json.dumps(data,indent=4))
    
f = open(fallout_root+"data/scripts/workshopscript.pex", "r+b")
data = f.read()
f.close()

print_r(pex.load(data))
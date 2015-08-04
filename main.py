from src.perdb import getDataObjects,loadPERdict

perdict = loadPERdict()
mtdict,keys,hoborhts = getDataObjects('CS',perdict)
for key in keys:
    print mtdict[key]
print hoborhts

mtdict,keys,hoborhts = getDataObjects('TOW',perdict)
for key in keys:
    print mtdict[key]
print hoborhts

mtdict,keys,hoborhts = getDataObjects('RHT',perdict)
for key in keys:
    print mtdict[key]
print hoborhts


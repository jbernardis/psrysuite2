import json
import re

with open("../data/layout.json", "r") as jfp:
    layout = json.load(jfp)

routes = layout["routes"]
routeMap = {}
for r in routes.keys():
    print("%s: " % r)
    
    blocks = r.split("Rt")[1]
    
    print("    %s" % blocks)
    b = re.findall(r'[A-Z]\d*', blocks)
    print("        %s" % str(b))
    if len(b) == 2:
        routeMap[(r, b[0])] = b[1]
        routeMap[(r, b[1])] = b[0]
        
for k in routeMap:
    print("%s: %s" % (str(k), routeMap[k]))
    
print(routeMap[("PRtP60P11", "P60")])


import json

with open("../data/trains.json", "r") as jfp:
    jdata = json.load(jfp)
    
    
print(json.dumps(jdata, indent=2))
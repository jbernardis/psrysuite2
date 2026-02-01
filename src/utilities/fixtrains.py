import json
import os


class MainClass:
    def __init__(self):
        fn = os.path.join(os.getcwd(), "trains.json")
        try:
            with open(fn, "r") as jfp:
                trains = json.load(jfp)
        except Exception as e:
            print("xxxx  Unable to open trains file: %s: %s" % (fn, str(e)))
            exit(1)

        for tr, trinfo in trains.items():
            print("Train %s" % tr)
            try:
                del trinfo["block"]
            except Exception as e:
                pass

            try:
                del trinfo["time"]
            except Exception as e:
                pass

            try:
                del trinfo["route"]
            except Exception as e:
                pass

            try:
                del trinfo["tmplate"]
            except Exception as e:
                pass

            seq = trinfo["sequence"]
            for s in seq:
                try:
                    del s["time"]
                except:
                    pass
                try:
                    del s["trigger"]
                except:
                    pass

        fn = os.path.join(os.getcwd(), "newtrains.json")
        try:
            with open(fn, "w") as jfp:
                json.dump(trains, jfp, indent=2)
        except:
            print("Unable to open trains file: %s" % fn)
            exit(1)

mc = MainClass()
        
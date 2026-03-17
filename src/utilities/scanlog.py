import json

fn = "c:\\Users\\jeff\\PSR\\rrserver.log"

lastTrain = {}

with open(fn, "r") as lfp:
	for line in lfp:
		if "HTTP Cmd receipt: " in line:
			pass

		elif "sending message: " in line:
			msg = line[41:].strip()
			ts = line[:23]
			m = eval(msg)
			cmd = list(m.keys())[0]
			if cmd == "train":
				parms = m["train"]
				for p in parms:
					trid = p.get("rname", None)
					if trid == "11":
						changes = []
						for k in ["iname", "rname", "east", "template", "loco", "engineer", "blocks", "stopped", "signal", "aspect", "aspecttype", "pastsignal"]:
							val = p.get(k, None)
							lval = lastTrain.get(k, None)
							if val != lval:
								if k == "blocks":
									changes.append("    Block changes")
									if val is None:
										bl = []
									else:
										bl = [b for b in val]
									if lval is None:
										lbl = []
									else:
										lbl = [b for b in lval]

									newb = [b for b in bl if b not in lbl]
									delb = [b for b in lbl if b not in bl]

									if len(newb) > 0:
										changes.append("        Train has entered blocks: %s" % (", ".join(newb)))
									if len(delb) > 0:
										changes.append("        Train has exited blocks: %s" % (", ".join(delb)))
									changes.append("        Train currently occupies blocks: %s" % (", ".join(bl)))

								else:
									changes.append("    %s has changed from %s to %s" % (k, lval, val))
							lastTrain[k] = val
						if len(changes) > 0:
							print("%s New train command" % ts)
							for c in changes:
								print(c)
						else:
							print("%s No change to train" % ts)

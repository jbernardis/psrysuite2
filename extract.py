import os
import shutil
from zipfile import ZipFile

zf = ZipFile("psrysuite-master.zip", "r")

zlist = zf.infolist()

zfdir = ""

for zi in zlist:
	if not zi.filename.startswith("psrysuite-master"):
		print("skipping %s" % zi.filename)
		continue

	if zi.filename.startswith("psrysuite-master/.idea"):
		print("skipping .idea file: %s" % zi.filename)
		continue

	if zi.filename.endswith(".gitignore"):
		print("skipping gitignore")
		continue

	if zi.filename.endswith(".project"):
		print("skipping .project")
		continue

	if zi.filename.endswith("todo.txt"):
		print("skipping todo.txt")
		continue

	if zi.is_dir():
		print("%s <=> %s" % (zi.filename, zi.filename[17:]))
		zfdir = zi.filename[17:]
		print("Processing directory %s => (%s)" % (zi.filename, zfdir))
		if len(zfdir) != 0:
			os.mkdir(zfdir)
	else:
		ozfn = zi.filename[17:]
		zdata = zf.read(zi)
		print("       cp %s ==> (%s)" % (zi.filename, ozfn))
		with open(ozfn, "wb") as ozfp:
			ozfp.write(zdata)

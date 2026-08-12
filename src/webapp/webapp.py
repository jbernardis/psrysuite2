import os
import sys
import socket
import select
import time
import logging
from threading import Thread
from socketserver import ThreadingMixIn 
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


from dispatcher.settings import Settings
import utilities.HTML as HTML
from sigtool.signals import Signals
from sigtool.railroadserver import RRServer
from dispatcher.constants import aspectname, aspecttype
from rrserver.constants import nodeNames

logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "webapp.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)


class WebHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		app = self.server.getApp()

		parsed_path = urlparse(self.path)
		path = parsed_path.path[0 if parsed_path.path[0] != "/" else 1:]
		query = parse_qs(parsed_path.query, keep_blank_values=True)
		print("parsed path = %s" % str(parsed_path))
		print("Path: %s" % str(path))
		print("Query: %s" % str(query))
		print("Params: %s" % str(parsed_path.params))
		print("====================")

		if path == "favicon.ico":
			self.send_response(204)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			try:
				self.wfile.write(b"")
			except ConnectionAbortedError:
				logging.error("WEB Server connection aborted while sending")

		else:
			rc, html = app.dispatch([path, query, parsed_path.params])
			try:
				body = html.encode()
			except:
				body = html

			if rc == 200:
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				if body is None:
					body = b""

				try:
					self.wfile.write(body)
				except ConnectionAbortedError:
					logging.error("WEB Server connection aborted while sending %s response" % str(parsed_path.path))
			else:
				self.send_response(400)
				self.send_header("Content-type", "text/plain")
				self.end_headers()
				self.wfile.write(body)


class WebThreadingHTTPServer(ThreadingMixIn, HTTPServer):
	def serve_dcc(self):
		self.rKillSocket, self.wKillSocket = socket.socketpair()
		self.haltServer = False
		while self.haltServer == False:
			#r = select.select([self.socket], [], [], 0)[0]
			r = select.select([self.socket, self.rKillSocket], [], [], None)[0]
			if r and self.socket in r:
				self.handle_request()

			elif r and self.rKillSocket in r:
				self.rKillSocket.recv(1)  # Clear the byte from the pipe
				logging.info('Web Server Select interrupted/killed intentionally!')
				self.haltServer = True

			else:
				# pass
				time.sleep(0.0001) # yield to other threads

		try:
			self.rKillSocket.close()
		except Exception as e:
			logging.debug("rKillSocket exception: %s" % str(e))

		try:
			self.wKillSocket.close()
		except Exception as e:
			logging.debug("wKillSocket exception: %s" % str(e))

	def setApp(self, app):
		self.app = app

	def getApp(self):
		return self.app

	def shut_down(self):
		self.haltServer = True
		self.wKillSocket.send(b'x')


class WebApp:
	def __init__(self, parent, ip, port, rrserver, signals):
		self.parent = parent
		self.rrserver = rrserver
		self.signals = signals
		self.selectedSignal = None
		self.server = WebThreadingHTTPServer((ip, port), WebHandler)
		self.server.setApp(self)
		self.thread = Thread(target=self.server.serve_dcc)
		self.thread.start()
		logging.info("Web server started")

	def getThread(self):
		return self.thread

	def getServer(self):
		return self.server

	def dispatch(self, url):
		return self.ProcessURL(url)

	def close(self):
		self.server.shut_down()

	def ProcessURL(self, urlinfo):
		path, query, params = urlinfo

		if path == "menuchoice":
			if "signal" in query.keys():
				return self.HTMLSignalTester()
			elif "getbits" in query.keys():
				return self.HTMLGetBits()
			elif "back" in query.keys():
				return self.HTMLMainMenu()
			else:
				return self.HTMLMainMenu(message="Invalid menu choice - Try again")

		elif path == "sigchoice":
			try:
				sigName = query['signallist'][0]
			except (KeyError, IndexError):
				sigName = None
				print("Unable to determine signal name from query: %s" % str(query))
			return self.HTMLSignalTester(signal=sigName)

		elif path in ["", "index"]:
			return self.HTMLMainMenu()

		elif path == "quit":
			self.parent.Kill()
			return 200, None

		return 400, "Invalid path: %s" % path

	def HTMLMainMenu(self, message=None):
		html = HTML.starthtml()

		html += HTML.startbody()
		btns = [
			HTML.button({"type": "submit", "id": "signal", "name": "signal"}, "Signal Tester"),
			HTML.button({"type": "submit", "id": "getbits", "name": "getbits"}, "Get O/I Bits"),
		]
		menu = HTML.form({"name": "mainmenu", "action": "/menuchoice", "method": "GET"}, " ".join(btns))
		html += menu
		if message is not None:
			html += message

		html += HTML.endbody()
		html += HTML.endhtml()
		return 200, html

	def HTMLSignalTester(self, signal=None):
		sigNames = self.signals.SigNames()
		html = HTML.starthtml()

		html += HTML.startbody()
		html += HTML.h1("Signal Tester")
		html += HTML.label({"for": "signallist"}, "Choose a Signal to test: ")

		choices = []
		if signal is None:
			self.selectedSignal = sigNames[0]

		else:
			self.selectedSignal = signal

		for sn in sigNames:
			opts = {"value": sn}
			if sn == self.selectedSignal:
				opts["selected"] = None
			choices.append(HTML.option(opts, sn))
		selectHtml = HTML.select({"name": "signallist", "id": "signallist", "onchange": "this.form.submit()"}, " ".join(choices))
		signalchoice = HTML.form({"name": "signalchoice", "action": "/sigchoice", "method": "GET"}, selectHtml)

		html += signalchoice

		aspectType = self.signals.GetAspectType(self.selectedSignal)
		atName = HTML.p("Aspect Type: %s" % aspecttype(aspectType))

		vals = self.signals.GetAspectBits(self.selectedSignal)
		bits = vals[0]
		nodeAddr = vals[1]
		bstr = ["(%d, %d)" % (b[0], b[1]) for b in bits]
		atBits = HTML.p("Bits: %s" % ", ".join(bstr))
		atNode = HTML.p("Node: %s (0x%x)" % (nodeNames[nodeAddr], nodeAddr))

		html += atName
		html += atBits
		html += atNode + "<br>"

		btn = HTML.button({"type": "submit", "id": "back", "name": "back"}, "Back")
		menu = HTML.form({"name": "signaltester", "action": "/index", "method": "GET"}, btn)
		html += menu
		html += HTML.endbody()
		html += HTML.endhtml()
		return 200, html

	def HTMLGetBits(self):
		html = HTML.starthtml()

		html += HTML.startbody()
		html += "Get Bits"
		btn = HTML.button({"type": "submit", "id": "back", "name": "back"}, "Back")
		menu = HTML.form({"name": "getbits", "action": "/index", "method": "GET"}, btn)
		html += menu
		html += HTML.endbody()
		html += HTML.endhtml()
		return 200, html


class WebAppServer:
	def __init__(self, settings):
		self.settings = settings
		self.forever = True

		self.rrServer = RRServer()

		logging.info("Connecting to RR Server at %s:%s" % (self.settings.ipaddr, self.settings.serverport))
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		self.signals = Signals(self.rrServer)

		logging.info("Starting Web server at address %s:%s" % (self.settings.ipaddr, self.settings.webappport))
		self.server = WebApp(self, self.settings.ipaddr, self.settings.webappport, self.rrServer, self.signals)

	def Kill(self):
		self.forever = False

	def Run(self):
		self.forever = True
		while self.forever:
			try:
				time.sleep(0.01)
			except KeyboardInterrupt:
				self.forever = False

		try:
			self.server.close()
		except:
			pass


# ofp = open(os.path.join(os.getcwd(), "output", "webapp.out"), "w")
# efp = open(os.path.join(os.getcwd(), "output", "webapp.err"), "w")
# sys.stdout = ofp
# sys.stderr = efp


settings = Settings()

svr = WebAppServer(settings)
svr.Run()



logging.info("Web server terminated")

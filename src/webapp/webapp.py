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

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from dispatcher.settings import Settings
import utilities.HTML as HTML
from sigtool.railroadserver import RRServer

from sigtester import SigTester
from getbits import GetBits
from blockadj import BlockAdjacency

logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "webapp.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

aspectValues = {
	1: [[0], [1]],
	2: [[0, 0], [0, 1], [1, 0], [1, 1]],
	3: [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]],
}


class WebHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		app = self.server.getApp()

		parsed_path = urlparse(self.path)
		path = parsed_path.path[0 if parsed_path.path[0] != "/" else 1:]
		query = parse_qs(parsed_path.query, keep_blank_values=True)
		logging.debug("parsed path = %s" % str(parsed_path))
		logging.debug("Path: %s" % str(path))
		logging.debug("Query: %s" % str(query))
		logging.debug("Params: %s" % str(parsed_path.params))
		logging.debug("====================")

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
	def __init__(self, parent, ip, port, rrserver):
		self.parent = parent
		self.rrserver = rrserver
		self.selectedSignal = None
		self.server = WebThreadingHTTPServer((ip, port), WebHandler)
		self.server.setApp(self)
		self.thread = Thread(target=self.server.serve_dcc)
		self.thread.start()

		self.sigTester = SigTester(self, self.rrserver)
		self.getBits = GetBits(self, self.rrserver)
		self.blockAdjacency = BlockAdjacency(self, self.rrserver)
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
				html = self.sigTester.ProcessURL(urlinfo)
				if html is None:
					html = self.HTMLMainMenu()
				return html

			elif "getbits" in query.keys():
				html = self.getBits.ProcessURL(urlinfo)
				if html is None:
					html = self.HTMLMainMenu()
				return html

			elif "blockadj" in query.keys():
				html = self.blockAdjacency.ProcessURL(urlinfo)
				if html is None:
					html = self.HTMLMainMenu()
				return html

			elif "back" in query.keys():
				return self.HTMLMainMenu()
			else:

				return self.HTMLMainMenu(message="Invalid menu choice - Try again")

		elif path in ["sigchoice", "aspectsend"]:
			html = self.sigTester.ProcessURL(urlinfo)
			if html is None:
				return self.HTMLMainMenu()
			return html

		elif path in ["nodechoice"]:
			html = self.getBits.ProcessURL(urlinfo)
			if html is None:
				return self.HTMLMainMenu()
			return html

		elif path in ["blockadj"]:
			html = self.blockAdjacency.ProcessURL(urlinfo)
			if html is None:
				return self.HTMLMainMenu()
			return html

		elif path in ["", "index"]:
			return self.HTMLMainMenu()

		elif path == "quit":
			self.parent.Kill()
			return 200, None

		elif path == "ping":
			return 200, None

		return 400, "Invalid wa path: %s" % path

	def HTMLMainMenu(self, message=None):
		css = self.StyleSheet()

		html = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css"}, css))

		html += HTML.startbody()
		html += HTML.h1({}, "PSRY WebApp")
		html += HTML.h2({}, "Main Menu")

		html += HTML.startdiv({"class": "menuindent"})
		html += "<br><br>"
		btns = [
			HTML.button({"type": "submit", "id": "signal", "name": "signal"}, "Signal Tester"),
			HTML.button({"type": "submit", "id": "getbits", "name": "getbits"}, "Get O/I Bits"),
			HTML.button({"type": "submit", "id": "blockadj", "name": "blockadj"}, "Block Adjacency"),
		]
		menu = HTML.form({"name": "mainmenu", "action": "/menuchoice", "method": "GET"}, "<br><br>".join(btns))
		html += menu
		if message is not None:
			html += message

		html += HTML.enddiv()

		html += HTML.endbody()
		html += HTML.endhtml()
		return 200, html

	def StyleSheet(self):
		css = HTML.StyleSheet()
		css.addElement("div.menuindent", {"padding-left": "60px"})
		css.addElement("h1", {"padding-left": "10px"})
		css.addElement("h2", {"padding-left": "15px"})
		css.addElement("div.backbutton", {"padding-left": "35px"})

		# css.addElement("p.header", {"font-family": 'Arial, sans-serif', "font-size": "30px", "font-weight": "bold"})
		return css


class WebAppServer:
	def __init__(self, settings):
		self.settings = settings
		self.forever = True

		self.rrServer = RRServer()

		logging.info("Connecting to RR Server at %s:%s" % (self.settings.ipaddr, self.settings.serverport))
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		logging.info("Starting Web server at address %s:%s" % (self.settings.ipaddr, self.settings.webappport))
		self.server = WebApp(self, self.settings.ipaddr, self.settings.webappport, self.rrServer)

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


ofp = open(os.path.join(os.getcwd(), "output", "webapp.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "webapp.err"), "w")
sys.stdout = ofp
sys.stderr = efp

settings = Settings()

svr = WebAppServer(settings)
svr.Run()

logging.info("Web server terminated")

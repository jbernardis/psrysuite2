import logging

FORWARD = 'F'
REVERSE = 'R'


class DCCRemote:
	def __init__(self, server):
		self.server = server

	def SetSpeed(self, loco, short=False, speed=0):
		self.SetSpeedAndDirection(loco, short=short, speed=speed)
		
	def SetDirection(self, loco, short=False, direction=FORWARD):
		self.SetSpeedAndDirection(loco, short=short, direction=direction)
						
	def SetSpeedAndDirection(self, loco, short=False, speed=None, direction=None):
		if speed is not None:
			if speed < 0 or speed > 128:
				logging.warning("speed value is out of range - %d - setting to 0" % speed)
				speed = 0

		if direction is not None:
			if direction not in [FORWARD, REVERSE]:
				logging.warning("invalid value for direction - %s - using FORWARD" % direction)
				direction = FORWARD

		parameters = {"loco": loco, "short": 1 if short else 0}
		if speed is not None:
			parameters["speed"] = speed
		if direction is not None:
			parameters["direction"] = direction

		self.server.SendRequest({"throttle": parameters})
		
	def SetFunction(self, loco, short=False, headlight=None, horn=None, bell=None):
		parameters = {"loco": loco, "short": 1 if short else 0}
		if headlight is not None:
			if headlight not in [0, 1]:
				logging.warning("headlight is not an allowable value - %s - assume 0=off" % headlight)
				headlight = 0
			parameters["headlight"] = headlight
		if horn is not None:
			if horn not in [0, 1]:
				logging.warning("horn is not an allowable value - %s - assume 0=off" % horn)
				horn = 0
			parameters["horn"] = horn
		if bell is not None:
			if bell not in [0, 1]:
				logging.warning("bell is not an allowable value - %s - assume 0=off" % bell)
				bell = 0
			parameters["bell"] = bell

		self.server.SendRequest({"function": parameters})


from dispatcher.district import District


class Yard (District):
	def __init__(self, name, frame, screen):
		District.__init__(self, name, frame, screen)

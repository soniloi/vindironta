class EventCollection:

	def __init__(self, events):
		self.events = events


	def get(self, event_key):
		return self.events.get(event_key)

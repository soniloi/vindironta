class EventCollection:

	def __init__(self, events):
		self.events = events
		self.puzzle_count = self.count_puzzles()


	def count_puzzles(self):
		return len([event for event in self.events.values() if event.is_puzzle()])


	def get(self, event_key):
		return self.events.get(event_key)

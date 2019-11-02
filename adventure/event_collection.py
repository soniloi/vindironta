class EventCollection:

	def __init__(self, events):
		self.events = events
		self.puzzle_count = self.count_puzzles()


	def count_puzzles(self):
		result = 0
		for multi_event in self.events.values():
			result += sum(1 for event in multi_event if event.is_puzzle())
		return result


	def get(self, event_key):
		return self.events.get(event_key)

class ItemContainer:

	def __init__(self):
		self.items = {}


	def contains(self, item):
		# TODO: enhance when implementing container items
		return item.data_id in self.items


	def insert(self, item):
		self.items[item.data_id] = item
		item.container = self


	def remove(self, item):
		if item.data_id in self.items:
			del self.items[item.data_id]


	def get_by_id(self, key):
		if key in self.items:
			return self.items[key]
		return None

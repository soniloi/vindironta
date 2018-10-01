class ItemContainer:

	def __init__(self):
		self.items = {}


	def has_items(self):
		return bool(self.items)


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
		return self.items.get(key)


	def gives_light(self):
		return any(item.gives_light() for item in self.items.values())

class ItemContainer:

	def __init__(self):
		self.items = {}


	def insert_item(self, item):
		self.items[item.data_id] = item


	def remove_item(self, item):
		if item.data_id in self.items:
			del self.items[item.data_id]


	def get_item(self, key):
		if key in self.items:
			return self.items[key]
		return None

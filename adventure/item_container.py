class ItemContainer:

	def __init__(self):
		self.items = {}


	def insert_item(self, item):
		self.items[item.data_id] = item


	def get_item(self, key):
		if key in self.items:
			return self.items[key]
		return None

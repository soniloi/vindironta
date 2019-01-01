class ItemCollection:

	def __init__(self, items_by_name, items_by_id):
		self.items_by_name = items_by_name
		self.items_by_id = items_by_id


	def get_by_name(self, item_name):
		return self.items_by_name.get(item_name)


	def get_by_id(self, item_id):
		return self.items_by_id.get(item_id)

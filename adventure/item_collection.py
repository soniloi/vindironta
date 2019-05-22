class ItemCollection:

	def __init__(self, item_lists_by_name, items_by_id):
		self.item_lists_by_name = item_lists_by_name
		self.items_by_id = items_by_id


	def get_list_by_name(self, item_name):
		return self.item_lists_by_name.get(item_name)


	def get_by_id(self, item_id):
		return self.items_by_id.get(item_id)

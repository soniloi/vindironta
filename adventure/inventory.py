from adventure.item_container import ItemContainer

class Inventory(ItemContainer):

	def __init__(self, capacity):
		ItemContainer.__init__(self)
		self.capacity = capacity


	def get_contents_description(self):
		result = ""
		for item in self.items.values():
			result += item.get_list_name()
		return result


	def can_accommodate(self, item):
		return self.get_current_size() + item.size <= self.capacity


	def get_current_size(self):
		result = 0
		for item in self.items.values():
			result = result + item.size
		return result


	def drop_all_items(self, location):
		for item in self.items.values():
			location.insert(item)
		self.items.clear()

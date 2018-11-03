from adventure.item_container import ItemContainer

class Inventory(ItemContainer):

	ATTRIBUTE_DEFAULT = 0x1

	def __init__(self, inventory_id, attributes, capacity):
		ItemContainer.__init__(self)
		self.inventory_id = inventory_id
		self.attributes = attributes
		self.capacity = capacity


	def get_contents_description(self):
		result = ""
		for item in self.items.values():
			result += item.get_list_name()
		return result


	def can_accommodate(self, item):
		return self.get_current_weight() + item.get_weight() <= self.capacity


	def get_current_weight(self):
		return sum(item.get_weight() for item in self.items.values())


	def drop_all_items(self, location):
		for item in self.items.values():
			location.insert(item)
		self.items.clear()

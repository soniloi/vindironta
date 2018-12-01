from adventure.data_element import NamedDataElement
from adventure.item_container import ItemContainer

class Inventory(NamedDataElement, ItemContainer):

	ATTRIBUTE_DEFAULT = 0x1

	def __init__(self, inventory_id, attributes, labels, capacity, location_ids=[]):
		NamedDataElement.__init__(self, data_id=inventory_id, attributes=attributes, labels=labels)
		ItemContainer.__init__(self)
		self.capacity = capacity
		self.location_ids = location_ids


	def is_default(self):
		return self.has_attribute(Inventory.ATTRIBUTE_DEFAULT)


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

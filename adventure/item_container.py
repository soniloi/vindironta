from copy import copy

class ItemContainer:

	def __init__(self):
		self.items = {}


	def has_items(self):
		return bool(self.items)


	def contains(self, item):
		for contained_item in self.items.values():
			if item == contained_item or contained_item.contains(item):
				return True
		return False


	def insert(self, item):
		if item.is_copyable():
			item = copy(item)
		self.items[item.data_id] = item
		item.update_container(self)


	def add(self, item):
		self.items[item.data_id] = item
		item.add_container(self)


	def remove(self, item):
		if item.data_id in self.items:
			del self.items[item.data_id]


	def get_by_id(self, key):
		return self.items.get(key)


	def gives_light(self):
		return any(item.gives_light() for item in self.items.values())


	def get_outermost_container(self):
		return self


	def can_accommodate(self, item):
		return True


	def is_sentient(self):
		return False

from adventure.inventory import Inventory

class Player:

	def __init__(self, location):
		self.location = location
		self.playing = True
		self.score = 0
		self.inventory = Inventory()


	def holding_items(self):
		return self.inventory.has_items()


	def has_items_nearby(self):
		return self.location.has_items()


	def is_carrying(self, item):
		return self.inventory.contains(item)

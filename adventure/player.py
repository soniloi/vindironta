from adventure.inventory import Inventory

class Player:

	def __init__(self, location):
		self.location = location
		self.playing = True
		self.score = 0
		self.inventory = Inventory()


	def is_carrying(self, item):
		return self.inventory.contains(item)

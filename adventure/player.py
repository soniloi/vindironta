from adventure.inventory import Inventory

class Player:

	INVENTORY_CAPACITY = 16

	def __init__(self, location):
		self.location = location
		self.previous_location = None
		self.playing = True
		self.score = 0
		self.inventory = Inventory(Player.INVENTORY_CAPACITY)
		self.current_command = None
		self.verbose = False
		self.instructions = 0


	def holding_items(self):
		return self.inventory.has_items()


	def has_items_nearby(self):
		return self.location.has_items()


	def is_carrying(self, item):
		return self.inventory.contains(item)


	def increment_instructions(self):
		self.instructions += 1


	def has_light_and_needs_no_light(self):
		return self.location.needs_no_light() and self.inventory.gives_light()


	def has_light(self):
		return self.location.gives_light() or self.inventory.gives_light()

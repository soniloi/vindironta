from adventure.inventory import Inventory

class Player:

	INVENTORY_CAPACITY = 16

	def __init__(self, initial_location, default_inventory, inventories_by_location={}):
		self.location = initial_location
		self.default_inventory = default_inventory
		self.inventories_by_location = inventories_by_location
		self.previous_location = None
		self.playing = True
		self.score = 0
		self.current_command = None
		self.current_args = []
		self.verbose = False
		self.instructions = 0
		self.alive = True
		self.immune = False


	def get_location_id(self):
		return self.location.data_id


	def get_adjacent_location(self, direction):
		return self.location.get_adjacent_location(direction)


	def get_obstructions(self):
		return self.location.get_obstructions()


	def see_location(self):
		self.location.seen = True


	def get_inventory(self):
		location_id = self.get_location_id()
		return self.inventories_by_location.get(location_id, self.default_inventory)


	def holding_items(self):
		return self.get_inventory().has_items()


	def has_non_silent_items_nearby(self):
		return self.location.has_non_silent_items()


	def is_carrying(self, item):
		return self.get_inventory().contains(item)


	def is_near_item(self, item):
		return self.location.contains(item)


	def has_or_is_near_item(self, item):
		return self.is_carrying(item) or self.is_near_item(item)


	def can_carry(self, item):
		return self.get_inventory().can_accommodate(item)


	def take_item(self, item):
		item.container.remove(item)
		self.get_inventory().insert(item)


	def drop_item(self, item):
		item.container.remove(item)
		self.location.insert(item)


	def lose_item(self, item):
		item.container.remove(item)


	def drop_all_items(self):
		self.get_inventory().drop_all_items(self.location)


	def describe_inventory(self):
		return self.get_inventory().get_contents_description()


	def increment_instructions(self):
		self.instructions += 1


	def decrement_instructions(self):
		self.instructions -= 1


	def get_arrival_location_description(self):
		return self.location.get_arrival_description(self.verbose)


	def get_full_location_description(self):
		return self.location.get_full_description()


	def has_light_and_needs_no_light(self):
		return self.location.needs_no_light() and self.get_inventory().gives_light()


	def has_light(self):
		return self.location.gives_light() or self.get_inventory().gives_light()


	def get_current_args(self):
		return self.current_args


	def reset_current_command(self):
		self.current_command = None
		self.current_args.clear()

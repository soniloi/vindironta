from adventure.element import DataElement
from adventure.inventory import Inventory

class Player(DataElement):

	ATTRIBUTE_PLAYING = 0x1
	ATTRIBUTE_ALIVE = 0x2
	ATTRIBUTE_IMMUNE = 0x4
	ATTRIBUTE_VERBOSE = 0x8

	def __init__(self, player_id, attributes, initial_location, default_inventory, inventories_by_location_id={}):
		DataElement.__init__(self, data_id=player_id, attributes=attributes)
		self.location = initial_location
		self.previous_location = None
		self.drop_location = initial_location
		self.score = 0
		self.current_command = None
		self.current_args = []
		self.instructions = 0
		self.completed_events = set()
		self.solved_puzzles = set()

		self.default_inventory = default_inventory
		self.inventories_by_location_id = inventories_by_location_id


	def get_location_id(self):
		return self.location.data_id


	def get_location(self):
		return self.location


	def set_location(self, location):
		self.location = location


	def get_previous_location(self):
		return self.previous_location


	def set_previous_location(self, previous_location):
		self.previous_location = previous_location


	def update_drop_location(self):
		self.drop_location = self.location


	def get_adjacent_location(self, direction):
		return self.location.get_adjacent_location(direction)


	def get_obstructions(self):
		return self.location.get_obstructions()


	def see_location(self):
		self.location.seen = True


	def get_inventory(self):
		location_id = self.get_location_id()
		return self.inventories_by_location_id.get(location_id, self.default_inventory)


	def holding_items(self):
		return self.get_inventory().has_items()


	def has_non_silent_items_nearby(self):
		return self.location.has_non_silent_items()


	def get_carried_item(self, item):
		return self.get_inventory().get_allow_copy(item)


	def get_nearby_item(self, item):
		return self.location.get_allow_copy(item)


	def can_carry(self, item):
		return self.get_inventory().can_accommodate(item)


	def take_item(self, item):
		item.remove_from_containers()
		self.get_inventory().insert(item)


	def drop_item(self, item):
		item.remove_from_containers()
		self.location.insert(item)


	def drop_all_items(self):
		self.get_inventory().drop_all_items(self.drop_location)


	def describe_inventory(self):
		return self.get_inventory().get_contents_description()


	def increment_instructions(self):
		self.instructions += 1


	def decrement_instructions(self):
		self.instructions -= 1


	def has_completed_event(self, event_id):
		return event_id in self.completed_events


	def complete_event(self, event_id):
		self.completed_events.add(event_id)


	def count_solved_puzzles(self):
		return len(self.solved_puzzles)


	def solve_puzzle(self, event_id):
		self.solved_puzzles.add(event_id)


	def get_arrival_location_description(self):
		return self.location.get_arrival_description(self.is_verbose())


	def get_full_location_description(self):
		return self.location.get_full_description()


	def has_light_and_needs_no_light(self):
		return self.location.needs_no_light() and self.get_inventory().gives_light()


	def has_light(self):
		return self.location.gives_light() or self.get_inventory().gives_light()


	def has_air(self):
		return self.location.gives_air() or self.get_inventory().gives_air()


	def can_burn(self):
		return self.get_inventory().allows_burning()


	def get_current_command(self):
		return self.current_command


	def get_current_args(self):
		return self.current_args


	def change_attribute(self, attribute, state):
		if state:
			self.set_attribute(attribute)
		else:
			self.unset_attribute(attribute)


	def is_playing(self):
		return self.has_attribute(Player.ATTRIBUTE_PLAYING)


	def set_playing(self, playing):
		self.change_attribute(Player.ATTRIBUTE_PLAYING, playing)


	def is_alive(self):
		return self.has_attribute(Player.ATTRIBUTE_ALIVE)


	def set_alive(self, alive):
		self.change_attribute(Player.ATTRIBUTE_ALIVE, alive)


	def is_immune(self):
		return self.has_attribute(Player.ATTRIBUTE_IMMUNE)


	def set_immune(self, immune):
		self.change_attribute(Player.ATTRIBUTE_IMMUNE, immune)


	def is_verbose(self):
		return self.has_attribute(Player.ATTRIBUTE_VERBOSE)


	def set_verbose(self, verbose):
		self.change_attribute(Player.ATTRIBUTE_VERBOSE, verbose)


	def reset_current_command(self):
		self.current_command = None
		self.current_args = []

from adventure.direction import Direction
from adventure.element import NamedDataElement
from adventure.item_container import ItemContainer

class Location(NamedDataElement, ItemContainer):

	ATTRIBUTE_GIVES_LIGHT = 0x1
	ATTRIBUTE_GIVES_AIR = 0x2
	ATTRIBUTE_GIVES_GRAVITY = 0x4
	ATTRIBUTE_NEEDS_NO_LIGHT = 0x10
	ATTRIBUTE_HAS_CEILING = 0x100
	ATTRIBUTE_HAS_FLOOR = 0x200

	def __init__(self, location_id, attributes, labels):
		NamedDataElement.__init__(self, data_id=location_id, attributes=attributes, labels=labels)
		ItemContainer.__init__(self)
		self.directions = {}
		self.seen = False


	def get_adjacent_location(self, direction):
		return self.directions.get(direction)


	def get_full_description(self):
		return [self.get_description(), self.get_contents_description()]


	def get_arrival_description(self, verbose):
		description = ""

		if self.seen and not verbose:
			description = self.longname
		else:
			description = self.get_description()

		return [description, self.get_contents_description()]


	def get_description(self):
		return self.longname + NamedDataElement.get_description(self)


	def get_contents_description(self):
		result = ""
		for item in self.items.values():
			result += item.get_non_silent_list_name()
		return result


	def get_drop_location(self):
		drop_location = self
		while not drop_location.has_floor():
			drop_location = drop_location.get_adjacent_location(Direction.DOWN)
		return drop_location


	def gives_light(self):
		if self.has_attribute(Location.ATTRIBUTE_GIVES_LIGHT):
			return True

		return ItemContainer.gives_light(self)


	def gives_air(self):
		if self.has_attribute(Location.ATTRIBUTE_GIVES_AIR):
			return True

		return ItemContainer.gives_air(self)


	def gives_gravity(self):
		return self.has_attribute(Location.ATTRIBUTE_GIVES_GRAVITY)


	def needs_no_light(self):
		return self.has_attribute(Location.ATTRIBUTE_NEEDS_NO_LIGHT)


	def has_ceiling(self):
		return self.has_attribute(Location.ATTRIBUTE_HAS_CEILING)


	def has_floor(self):
		return self.has_attribute(Location.ATTRIBUTE_HAS_FLOOR)


	def gives_tether(self):
		if self.gives_gravity() or self.has_ceiling():
			return True

		above = self.get_adjacent_location(Direction.UP)
		if above:
			return above.gives_gravity()

		return False


	def get_obstructions(self):
		return [item for item in self.items.values() if item.is_obstruction()]


	def can_reach(self, other_location):
		return any(direction == other_location for direction in self.directions.values())


	def has_non_silent_items(self):
		return any(not item.is_silent() for item in self.items.values())

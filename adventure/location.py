from adventure.data_element import DataElement
from adventure.item_container import ItemContainer

class Location(DataElement, ItemContainer):

	ATTRIBUTE_GIVES_LIGHT = 0x1
	ATTRIBUTE_NEEDS_NO_LIGHT = 0x10

	def __init__(self, location_id, attributes, shortname, longname, description):
		DataElement.__init__(self, data_id=location_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description)
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
		return self.longname + self.description


	def get_contents_description(self):
		result = ""
		for item in self.items.values():
			result += item.get_non_silent_list_name()
		return result


	def needs_no_light(self):
		return self.has_attribute(Location.ATTRIBUTE_NEEDS_NO_LIGHT)


	def gives_light(self):
		if self.has_attribute(Location.ATTRIBUTE_GIVES_LIGHT):
			return True

		return ItemContainer.gives_light(self)


	def get_obstructions(self):
		return [item for item in self.items.values() if item.is_obstruction()]


	def can_reach(self, other_location):
		return any(direction == other_location for direction in self.directions.values())

from adventure.data_element import DataElement
from adventure.item_container import ItemContainer

class Location(DataElement, ItemContainer):

	ATTRIBUTE_GIVES_LIGHT = 0x1

	def __init__(self, location_id, attributes, shortname, longname, description):
		DataElement.__init__(self, data_id=location_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description)
		ItemContainer.__init__(self)
		self.directions = {}
		self.visited = False


	def get_adjacent_location(self, direction):
		return self.directions.get(direction)


	def get_full_description(self):
		return [self.get_description(), self.get_contents_description()]


	def get_arrival_description(self):
		description = ""

		if self.visited:
			description = self.longname
		else:
			description = self.get_description()

		return [description, self.get_contents_description()]


	def get_description(self):
		return self.longname + self.description


	def get_contents_description(self):
		result = ""
		for item in self.items.values():
			result += self.get_item_description(item)
		return result


	def get_item_description(self, item):
		if not item.is_silent():
			return "\n\t" + item.longname
		return ""


	def gives_light(self):
		if self.has_attribute(Location.ATTRIBUTE_GIVES_LIGHT):
			return True

		return ItemContainer.gives_light(self)


	def get_obstructions(self):
		return [item for item in self.items.values() if item.is_obstruction()]

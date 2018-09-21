from adventure.data_element import DataElement
from adventure.item_container import ItemContainer

class Location(DataElement, ItemContainer):

	def __init__(self, location_id, attributes, shortname, longname, description):
		DataElement.__init__(self, data_id=location_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description)
		ItemContainer.__init__(self)
		self.directions = {}


	def get_full_description(self):
		return self.longname + self.description + self.get_contents_description()


	def get_contents_description(self):
		result = ""
		if self.items:
			result += ". You see the following nearby:"
			for item in self.items.values():
				result += "\n\t" + item.longname
		return result

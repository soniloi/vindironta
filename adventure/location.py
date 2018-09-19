from adventure.data_element import DataElement

class Location(DataElement):

	def __init__(self, location_id, attributes, shortname, longname, description):
		super().__init__(data_id=location_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description)
		self.directions = {}
		self.items = {}


	def get_full_description(self):
		return self.longname + self.description + self.get_contents_description()


	def get_contents_description(self):
		result = ""
		if self.items:
			result += ". You see the following nearby:"
			for item in self.items.values():
				result += "\n\t" + item.longname
		return result


	def insert_item(self, item):
		self.items[item.data_id] = item


	def get_item(self, key):
		if key in self.items:
			return self.items[key]
		return None

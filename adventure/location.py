from adventure.data_element import DataElement

class Location(DataElement):

	def __init__(self, location_id, attributes, shortname, longname, description):
		super().__init__(data_id=location_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description)
		self.directions = {}


	def get_full_description(self):
		return self.longname + self.description

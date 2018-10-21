class DataElement:

	def __init__(self, data_id, attributes, shortname, longname, description):
		self.data_id = data_id
		self.raw_attributes = attributes
		self.attributes = self.raw_attributes
		self.shortname = shortname
		self.longname = longname
		self.description = description


	def has_attribute(self, attribute):
		return self.attributes & attribute


	def set_attribute(self, attribute):
		self.attributes |= attribute


	def unset_attribute(self, attribute):
		self.attributes &= ~attribute

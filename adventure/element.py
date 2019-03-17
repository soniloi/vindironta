class Labels:

	def __init__(self, shortname, longname, description, extended_descriptions=[]):
		self.shortname = shortname
		self.longname = longname
		self.description = description
		self.extended_descriptions = extended_descriptions


class Element:

	def __init__(self, attributes):
		self.raw_attributes = attributes
		self.attributes = self.raw_attributes


	def has_attribute(self, attribute):
		return bool(self.attributes & attribute)


	def set_attribute(self, attribute):
		self.attributes |= attribute


	def unset_attribute(self, attribute):
		self.attributes &= ~attribute


	def toggle_attribute(self, attribute):
		self.attributes ^= attribute


class DataElement(Element):

	def __init__(self, data_id, attributes):
		Element.__init__(self, attributes)
		self.data_id = data_id


class NamedDataElement(DataElement):

	def __init__(self, data_id, attributes, labels):
		DataElement.__init__(self, data_id, attributes)
		self.shortname = labels.shortname
		self.longname = labels.longname
		self.description = labels.description
		self.extended_descriptions = labels.extended_descriptions
		self.extended_description_index = 0


	def get_description(self):
		return self.description + self.get_extended_description()


	def get_extended_description(self):
		return self.extended_descriptions[self.extended_description_index] \
			if self.extended_description_index < len(self.extended_descriptions) \
			else ""

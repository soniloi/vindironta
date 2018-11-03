from collections import namedtuple

Labels = namedtuple("Labels", "shortname longname description")


class DataElement:

	def __init__(self, data_id, attributes):
		self.data_id = data_id
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


class NamedDataElement(DataElement):

	def __init__(self, data_id, attributes, labels):
		DataElement.__init__(self, data_id, attributes)
		self.shortname = labels.shortname
		self.longname = labels.longname
		self.description = labels.description

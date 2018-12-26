from collections import namedtuple

Labels = namedtuple("Labels", "shortname longname description")

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

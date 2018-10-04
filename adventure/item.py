from adventure.data_element import DataElement

class Item(DataElement):

	ATTRIBUTE_MOBILE = 0x2
	ATTRIBUTE_OBSTRUCTION = 0x4
	ATTRIBUTE_GIVES_LIGHT = 0x10

	def __init__(self, item_id, attributes, shortname, longname, description, size, writing):
		super().__init__(data_id=item_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description)
		self.size = size
		self.writing = writing
		self.container = None


	def get_full_description(self):
		return self.description


	def is_portable(self):
		return self.has_attribute(Item.ATTRIBUTE_MOBILE)


	def is_obstruction(self):
		return self.has_attribute(Item.ATTRIBUTE_OBSTRUCTION)


	def gives_light(self):
		return self.has_attribute(Item.ATTRIBUTE_GIVES_LIGHT)

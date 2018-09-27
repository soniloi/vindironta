from adventure.data_element import DataElement

class Item(DataElement):

	ATTRIBUTE_MOBILE = 0x2

	def __init__(self, item_id, attributes, shortname, longname, description, size, writing):
		super().__init__(data_id=item_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description)
		self.size = size
		self.writing = writing
		self.container = None

	def is_portable(self):
		return self.has_attribute(Item.ATTRIBUTE_MOBILE)

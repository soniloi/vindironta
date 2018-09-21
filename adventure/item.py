from adventure.data_element import DataElement

class Item(DataElement):

	def __init__(self, item_id, attributes, shortname, longname, description, initial_container, size, writing):
		super().__init__(data_id=item_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description)
		self.container = initial_container
		self.size = size
		self.writing = writing

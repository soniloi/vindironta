class Item:

	def __init__(self, item_id, attributes, initial_location, size, shortname, longname, description, writing):
		self.item_id = item_id
		self.attributes = attributes
		self.location = initial_location
		self.size = size
		self.shortname = shortname
		self.longname = longname
		self.description = description
		self.writing = writing

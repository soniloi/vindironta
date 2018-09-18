from adventure.item import Item
from adventure.file_reader import FileReader


class ItemCollection:

	NO_WRITING = "0"

	def __init__(self, reader, location_collection):
		self.items = {}
		line = reader.read_line()
		while not line.startswith("---"):
			self.create_item(line, location_collection)
			line = reader.read_line()


	def create_item(self, line, location_collection):
		tokens = line.split("\t")

		item_id = self.parse_item_id(tokens[0])
		item_attributes = self.parse_item_attributes(tokens[1])
		item_location = self.parse_item_location(tokens[2], location_collection)
		item_size = self.parse_item_size(tokens[3])
		item_primary_shortname, item_shortnames = self.parse_item_shortnames(tokens[4])
		item_longname = tokens[5]
		item_description = tokens[6]
		item_writing = self.parse_item_writing(tokens[7])

		item = Item(
			item_id = item_id,
			attributes = item_attributes,
			size = item_size,
			shortname = item_primary_shortname,
			longname = item_longname,
			description = item_description,
			writing = item_writing,
			initial_location = item_location
		)

		for item_shortname in item_shortnames:
			self.items[item_shortname] = item


	def parse_item_id(self, token):
		return int(token)


	def parse_item_attributes(self, token):
		return int(token, 16)


	def parse_item_location(self, token, location_collection):
		return location_collection.get(int(token))


	def parse_item_size(self, token):
		return int(token)


	def parse_item_shortnames(self, token):
		item_shortnames = token.split(",")
		return (item_shortnames[0], item_shortnames)


	def parse_item_writing(self, token):
		if token == ItemCollection.NO_WRITING:
			return None
		return token


	def get(self, item_name):
		if item_name in self.items:
			return self.items[item_name]
		return None


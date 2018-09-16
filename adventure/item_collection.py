from adventure.item import Item
from adventure.file_reader import FileReader


class ItemCollection:

	NO_WRITING = "0"

	def __init__(self, reader):
		self.items = {}
		line = reader.read_line()
		while not line.startswith("---"):
			self.create_item(line)
			line = reader.read_line()


	def create_item(self, line):
		tokens = line.split("\t")

		item_id = int(tokens[0])
		item_attributes = int(tokens[1], 16)
		item_size = int(tokens[3])
		item_shortname = tokens[4]
		item_longname = tokens[5]
		item_description = tokens[6]
		item_writing = tokens[7]
		if item_writing == ItemCollection.NO_WRITING:
			item_writing = None

		item = Item(
			item_id = item_id,
			attributes = item_attributes,
			size = item_size,
			shortname = item_shortname,
			longname = item_longname,
			description = item_description,
			writing = item_writing
		)
		self.items[item_shortname] = item


	def get(self, item_name):
		if item_name in self.items:
			return self.items[item_name]
		return None


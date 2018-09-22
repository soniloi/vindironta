from adventure.item import Item
from adventure.file_reader import FileReader


class ItemCollection:

	NO_WRITING = "0"

	def __init__(self, reader, location_collection):
		self.items = {}
		item_containers = {}

		line = reader.read_line()
		while not line.startswith("---"):
			self.create_item(line, item_containers)
			line = reader.read_line()

		self.place_items(item_containers, location_collection)


	def create_item(self, line, item_containers):
		tokens = line.split("\t")

		item_id = self.parse_item_id(tokens[0])
		item_attributes = self.parse_item_attributes(tokens[1])
		item_container_id = self.parse_item_container_id(tokens[2])
		item_size = self.parse_item_size(tokens[3])
		item_primary_shortname, item_shortnames = self.parse_item_shortnames(tokens[4])
		item_longname = tokens[5]
		item_description = tokens[6]
		item_writing = self.parse_item_writing(tokens[7])

		item = Item(
			item_id = item_id,
			attributes = item_attributes,
			shortname = item_primary_shortname,
			longname = item_longname,
			description = item_description,
			size = item_size,
			writing = item_writing,
		)

		for item_shortname in item_shortnames:
			self.items[item_shortname] = item

		item_containers[item] = item_container_id


	def parse_item_id(self, token):
		return int(token)


	def parse_item_attributes(self, token):
		return int(token, 16)


	def parse_item_container_id(self, token):
		return int(token)


	def parse_item_size(self, token):
		return int(token)


	def parse_item_shortnames(self, token):
		item_shortnames = token.split(",")
		return (item_shortnames[0], item_shortnames)


	def parse_item_writing(self, token):
		if token == ItemCollection.NO_WRITING:
			return None
		return token


	# TODO: handle initial placement types other than Location
	def place_items(self, item_containers, location_collection):
		for item, container_id in item_containers.items():
			container = location_collection.get(container_id)
			if container:
				item.container = container
				container.insert(item)


	def get(self, item_name):
		if item_name in self.items:
			return self.items[item_name]
		return None


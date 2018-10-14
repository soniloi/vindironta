from adventure.item import Item, ContainerItem
from adventure.file_reader import FileReader


class ItemCollection:

	NO_WRITING = "0"

	def __init__(self, reader, containers):
		self.items = {}
		container_ids = {}

		line = reader.read_line()
		while not line.startswith("---"):
			self.create_item(line, container_ids, containers)
			line = reader.read_line()

		self.place_items(container_ids, containers)


	def create_item(self, line, container_ids, containers):
		tokens = line.split("\t")

		item_id = self.parse_item_id(tokens[0])
		attributes = self.parse_item_attributes(tokens[1])
		container_id = self.parse_item_container_id(tokens[2])
		size = self.parse_item_size(tokens[3])
		primary_shortname, shortnames = self.parse_item_shortnames(tokens[4])
		longname = tokens[5]
		description = tokens[6]
		writing = self.parse_item_writing(tokens[7])
		item = self.init_item(item_id=item_id, attributes=attributes, shortname=primary_shortname, longname=longname,
			description=description, size=size, writing=writing, containers=containers)

		for shortname in shortnames:
			self.items[shortname] = item

		container_ids[item] = container_id


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


	def init_item(self, item_id, attributes, shortname, longname, description, size, writing, containers):
		if attributes & Item.ATTRIBUTE_CONTAINER != 0:
			item = ContainerItem(item_id=item_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description, size=size, writing=writing)
			containers[item_id] = item
		else:
			item = Item(item_id=item_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description, size=size, writing=writing)

		return item


	# TODO: handle initial placement types other than Location
	def place_items(self, container_ids, containers):
		for item, container_id in container_ids.items():
			container = containers.get(container_id)
			if container:
				item.container = container
				container.insert(item)


	def get(self, item_name):
		if item_name in self.items:
			return self.items[item_name]
		return None


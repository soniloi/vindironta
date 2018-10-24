from adventure.item import Item, ContainerItem, SwitchableItem
from adventure.file_reader import FileReader


class ItemCollection:

	NO_WRITING = "0"

	def __init__(self, reader, elements):
		self.items = {}
		container_ids = {}
		switched_element_ids = {}

		line = reader.read_line()
		while not line.startswith("---"):
			self.create_item(line, container_ids, elements, switched_element_ids)
			line = reader.read_line()

		self.place_items(container_ids, elements)
		self.resolve_switches(switched_element_ids, elements)


	def create_item(self, line, container_ids, elements, switched_element_ids):
		tokens = line.split("\t")

		item_id = self.parse_item_id(tokens[0])
		attributes = self.parse_item_attributes(tokens[1])
		container_id = self.parse_item_container_id(tokens[2])
		size = self.parse_item_size(tokens[3])
		primary_shortname, shortnames = self.parse_item_shortnames(tokens[4])
		longname = tokens[5]
		description = tokens[6]
		writing = self.parse_item_writing(tokens[7])
		switching_info = self.parse_switching_info(tokens[8])

		item = self.init_item(
			item_id=item_id,
			attributes=attributes,
			shortname=primary_shortname,
			longname=longname,
			description=description,
			size=size,
			writing=writing,
			switched_element_ids=switched_element_ids,
			switching_info=switching_info,
		)

		elements[item_id] = item
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


	def parse_switching_info(self, token):
		if not token:
			return None, None

		switching_info = token.split(",")
		element_id = int(switching_info[0])
		attribute = int(switching_info[1], 16)
		off_string = switching_info[2]
		on_string = switching_info[3]

		return element_id, attribute, off_string, on_string


	def init_item(self, item_id, attributes, shortname, longname, description, size, writing,
		switched_element_ids, switching_info):

		if attributes & Item.ATTRIBUTE_CONTAINER != 0:
			item = ContainerItem(item_id=item_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description, size=size, writing=writing)

		elif attributes & Item.ATTRIBUTE_SWITCHABLE != 0:
			item = SwitchableItem(item_id=item_id, attributes=attributes, shortname=shortname, longname=longname,
			description=description, size=size, writing=writing, switching_info=switching_info)
			switched_element_ids[item] = switching_info[0]

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


	def resolve_switches(self, switched_element_ids, elements):
		for switching_item, switched_element_id in switched_element_ids.items():
			element = elements.get(switched_element_id)
			switching_item.switched_element = element


	def get(self, item_name):
		return self.items.get(item_name)

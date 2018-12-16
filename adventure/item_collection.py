from adventure.data_element import Labels
from adventure.item import Item, ContainerItem, SentientItem, SwitchableItem, SwitchInfo, WearableItem
from adventure.file_reader import FileReader


class ItemCollection:

	def __init__(self, reader, elements):
		self.items = {}
		self.items_by_id = {}
		container_ids_by_item = {}
		switched_element_ids = {}

		line = reader.read_line()
		while not line.startswith("---"):
			self.create_item(line, container_ids_by_item, elements, switched_element_ids)
			line = reader.read_line()

		self.place_items(container_ids_by_item, elements)
		self.resolve_switches(switched_element_ids, elements)


	def create_item(self, line, container_ids_by_item, elements, switched_element_ids):
		tokens = line.split("\t")

		item_id = self.parse_item_id(tokens[0])
		attributes = self.parse_item_attributes(tokens[1])
		container_ids = self.parse_item_container_ids(tokens[2])
		size = self.parse_item_size(tokens[3])
		primary_shortname, shortnames = self.parse_item_shortnames(tokens[4])
		longname = tokens[5]
		description = tokens[6]
		writing = self.parse_item_writing(tokens[7])
		switched_element_id, switch_info = self.parse_switch_info(tokens[8])
		attribute_when_worn = self.parse_wearing_info(tokens[9])
		labels = Labels(shortname=primary_shortname, longname=longname, description=description)

		item = self.init_item(
			item_id=item_id,
			attributes=attributes,
			labels=labels,
			size=size,
			writing=writing,
			switched_element_ids=switched_element_ids,
			switched_element_id=switched_element_id,
			switch_info=switch_info,
			attribute_when_worn=attribute_when_worn,
		)

		elements[item_id] = item
		for shortname in shortnames:
			self.items[shortname] = item
		self.items_by_id[item_id] = item

		container_ids_by_item[item] = container_ids


	def parse_item_id(self, token):
		return int(token)


	def parse_item_attributes(self, token):
		return int(token, 16)


	def parse_item_container_ids(self, token):
		container_id_tokens = token.split(",")
		return [int(container_id_token) for container_id_token in container_id_tokens]


	def parse_item_size(self, token):
		return int(token)


	def parse_item_shortnames(self, token):
		item_shortnames = token.split(",")
		return (item_shortnames[0], item_shortnames)


	def parse_item_writing(self, token):
		return token


	def parse_switch_info(self, token):
		if not token:
			return None, None

		switch_info = token.split(",")
		element_id = int(switch_info[0])
		attribute = int(switch_info[1], 16)
		off = switch_info[2]
		on = switch_info[3]

		switch_info = SwitchInfo(attribute=attribute, off=off, on=on)

		return element_id, switch_info


	def parse_wearing_info(self, token):
		if not token:
			return None
		return int(token, 16)


	def init_item(self, item_id, attributes, labels, size, writing,
		switched_element_id, switched_element_ids, switch_info, attribute_when_worn):

		if bool(attributes & Item.ATTRIBUTE_SENTIENT):
			item = SentientItem(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing)

		elif bool(attributes & Item.ATTRIBUTE_CONTAINER):
			item = ContainerItem(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing)

		elif bool(attributes & Item.ATTRIBUTE_SWITCHABLE):
			item = SwitchableItem(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing,
				switch_info=switch_info)
			switched_element_ids[item] = switched_element_id

		elif bool(attributes & Item.ATTRIBUTE_WEARABLE):
			item = WearableItem(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing,
				attribute_activated=attribute_when_worn)

		else:
			item = Item(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing)

		return item


	def place_items(self, container_ids_by_item, containers):
		for item, container_ids in container_ids_by_item.items():
			for container_id in container_ids:
				container = containers.get(container_id)
				if container:
					container.add(item)


	def resolve_switches(self, switched_element_ids, elements):
		for switching_item, switched_element_id in switched_element_ids.items():
			element = elements.get(switched_element_id)
			switching_item.switched_element = element


	def get(self, item_name):
		return self.items.get(item_name)


	def get_by_id(self, item_id):
		return self.items_by_id.get(item_id)

from adventure.element import Labels
from adventure.item import Item, ContainerItem, SentientItem, SwitchableItem, SwitchInfo, WearableItem

class ItemCollection:

	def __init__(self, item_inputs, elements_by_id):
		container_ids_by_item = {}
		switched_element_ids = {}
		self.items, self.items_by_id = self.parse_items(item_inputs, container_ids_by_item, elements_by_id, switched_element_ids)

		self.place_items(container_ids_by_item, elements_by_id)
		self.resolve_switches(switched_element_ids, elements_by_id)


	def parse_items(self, item_inputs, container_ids_by_item, elements_by_id, switched_element_ids):
		items = {}
		items_by_id = {}

		for item_input in item_inputs:
			item, shortnames = self.parse_item(item_input, container_ids_by_item, switched_element_ids)
			items_by_id[item.data_id] = item
			elements_by_id[item.data_id] = item

			for shortname in shortnames:
				items[shortname] = item


		return items, items_by_id


	def parse_item(self, item_input, container_ids_by_item, switched_element_ids):
		item_id = item_input["data_id"]
		attributes = int(item_input["attributes"], 16)
		labels, shortnames = self.parse_labels(item_input["labels"])
		size = item_input["size"]
		writing = item_input.get("writing")

		switched_element_id = None
		switch_info = None
		if "switch_info" in item_input:
			switched_element_id, switch_info = self.parse_switch_info(item_input["switch_info"])

		wearing_info = None
		if "wearing_info" in item_input:
			wearing_info = int(item_input["wearing_info"], 16)

		item = self.init_item(
			item_id=item_id,
			attributes=attributes,
			labels=labels,
			size=size,
			writing=writing,
			switched_element_ids=switched_element_ids,
			switched_element_id=switched_element_id,
			switch_info=switch_info,
			attribute_when_worn=wearing_info,
		)

		container_ids = item_input["container_ids"]
		container_ids_by_item[item] = container_ids

		return item, shortnames


	def parse_labels(self, label_input):
		shortnames = label_input["shortnames"]
		return Labels(shortnames[0], label_input["longname"], label_input["description"]), shortnames


	def parse_switch_info(self, switch_info_input):
		switched_element_id = switch_info_input["element_id"]
		switched_attribute = int(switch_info_input["attribute"], 16)
		off_switch = switch_info_input["off"]
		on_switch = switch_info_input["on"]
		return switched_element_id, SwitchInfo(attribute=switched_attribute, off=off_switch, on=on_switch)


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


	def resolve_switches(self, switched_element_ids, elements_by_id):
		for switching_item, switched_element_id in switched_element_ids.items():
			element = elements_by_id.get(switched_element_id)
			switching_item.switched_element = element


	def get(self, item_name):
		return self.items.get(item_name)


	def get_by_id(self, item_id):
		return self.items_by_id.get(item_id)

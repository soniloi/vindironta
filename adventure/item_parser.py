from collections import namedtuple

from adventure.element import Labels
from adventure.item import Item, ContainerItem, SentientItem, SwitchableItem, SwitchInfo, UsableItem, Transformation
from adventure.item_collection import ItemCollection
from adventure.token_translator import TokenTranslator

TransformationInfo = namedtuple("TransformationInfo", "replacement_id tool_id material_id")

class ItemParser:

	def parse(self, item_inputs, elements_by_id, commands_by_id):
		container_ids_by_item = {}
		switched_element_ids = {}
		transformation_infos = {}
		items_by_name, items_by_id, related_commands = self.parse_items(item_inputs, container_ids_by_item, elements_by_id,
			commands_by_id, switched_element_ids, transformation_infos)

		self.place_items(container_ids_by_item, elements_by_id)
		self.resolve_switches(switched_element_ids, elements_by_id)
		self.resolve_transformations(transformation_infos, elements_by_id)

		return ItemCollection(items_by_name, items_by_id), related_commands


	def parse_items(self, item_inputs, container_ids_by_item, elements_by_id, commands_by_id, switched_element_ids,
			transformation_infos):
		items_by_name = {}
		items_by_id = {}
		related_commands = {}

		for item_input in item_inputs:
			item, shortnames, related_command_id = self.parse_item(
				item_input, container_ids_by_item, switched_element_ids, transformation_infos)
			items_by_id[item.data_id] = item
			elements_by_id[item.data_id] = item

			for shortname in shortnames:
				items_by_name[shortname] = item

			if related_command_id:
				for shortname in shortnames:
					related_commands[shortname] = commands_by_id.get(related_command_id)

		return items_by_name, items_by_id, related_commands


	def parse_item(self, item_input, container_ids_by_item, switched_element_ids, transformation_infos):
		item_id = item_input["data_id"]
		attributes = int(item_input["attributes"], 16)
		labels, shortnames = self.parse_labels(item_input["labels"])
		size = item_input["size"]
		writing = item_input.get("writing")

		switched_element_id = None
		switch_info = None
		if "switch_info" in item_input:
			switched_element_id, switch_info = self.parse_switch_info(item_input["switch_info"])

		using_info = None
		if "using_info" in item_input:
			using_info = int(item_input["using_info"], 16)

		transformation_info = {}
		if "transformations" in item_input:
			self.parse_transformations(item_input["transformations"], transformation_info)

		list_template = None
		if "list_template" in item_input:
			list_template = self.parse_list_template(item_input["list_template"])

		related_command_id = item_input.get("related_command_id")

		item = self.init_item(
			item_id=item_id,
			attributes=attributes,
			labels=labels,
			size=size,
			writing=writing,
			switched_element_ids=switched_element_ids,
			switched_element_id=switched_element_id,
			switch_info=switch_info,
			attribute_when_used=using_info,
			list_template=list_template,
		)

		container_ids = item_input["container_ids"]
		container_ids_by_item[item] = container_ids
		transformation_infos[item] = transformation_info

		return item, shortnames, related_command_id


	def parse_labels(self, label_input):
		shortnames = label_input["shortnames"]
		extended_descriptions = label_input.get("extended_descriptions", [])
		return Labels(shortnames[0], label_input["longname"], label_input["description"], extended_descriptions), shortnames


	def parse_switch_info(self, switch_info_input):
		switched_element_id = switch_info_input["element_id"]
		switched_attribute = int(switch_info_input["attribute"], 16)
		off_switch = switch_info_input["off"]
		on_switch = switch_info_input["on"]
		return switched_element_id, SwitchInfo(attribute=switched_attribute, off=off_switch, on=on_switch)


	def parse_transformations(self, transformation_inputs, item_transformations):
		for transformation_input in transformation_inputs:
			command_id = transformation_input["command_id"]
			replacement_id = transformation_input["replacement_id"]
			tool_id = transformation_input.get("tool_id", None)
			material_id = transformation_input.get("material_id", None)
			item_transformations[command_id] = TransformationInfo(replacement_id=replacement_id, tool_id=tool_id, material_id=material_id)


	def parse_list_template(self, list_template_input):
		return TokenTranslator.translate_substitution_tokens(list_template_input)


	def init_item(self,
			item_id,
			attributes,
			labels,
			size,
			writing,
			switched_element_id,
			switched_element_ids,
			switch_info,
			attribute_when_used,
			list_template,
		):

		if bool(attributes & Item.ATTRIBUTE_SENTIENT):
			item = SentientItem(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing,
				list_template=list_template)

		elif bool(attributes & Item.ATTRIBUTE_CONTAINER):
			item = ContainerItem(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing,
				list_template=list_template)

		elif bool(attributes & Item.ATTRIBUTE_SWITCHABLE):
			item = SwitchableItem(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing,
				list_template=list_template, switch_info=switch_info)
			switched_element_ids[item] = switched_element_id

		elif bool(attributes & Item.ATTRIBUTE_WEARABLE) or bool(attributes & Item.ATTRIBUTE_SAILABLE):
			item = UsableItem(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing,
				list_template=list_template, attribute_activated=attribute_when_used)

		else:
			item = Item(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing,
				list_template=list_template)

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


	def resolve_transformations(self, transformation_infos_by_transformed, elements_by_id):
		for transformed_item, transformation_infos in transformation_infos_by_transformed.items():
			for command_id, transformation_info in transformation_infos.items():
				replacement = elements_by_id.get(transformation_info.replacement_id)
				tool = elements_by_id.get(transformation_info.tool_id)
				material = elements_by_id.get(transformation_info.material_id)
				transformed_item.transformations[command_id] = Transformation(replacement=replacement, tool=tool, material=material)

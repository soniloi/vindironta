from collections import namedtuple

from adventure.element import Labels
from adventure.item import Item, ContainerItem, ListTemplateType, SentientItem, SwitchableItem, SwitchInfo, Transformation, UsableItem
from adventure.item_collection import ItemCollection
from adventure.token_translator import TokenTranslator
from adventure.validation import Message, Severity

TransformationInfo = namedtuple("TransformationInfo", "replacement_id tool_id material_id")

class ItemParser:

	def parse(self, item_inputs, elements_by_id, commands_by_id):
		container_ids_by_item = {}
		switched_element_ids = {}
		transformation_infos = {}
		item_lists_by_name, items_by_id, related_commands, validation = self.parse_items(item_inputs,
			container_ids_by_item,elements_by_id, commands_by_id, switched_element_ids, transformation_infos)

		self.place_items(container_ids_by_item, elements_by_id)
		self.resolve_switches(switched_element_ids, elements_by_id, validation)
		self.resolve_transformations(transformation_infos, elements_by_id, commands_by_id, validation)
		self.validate_attributes(items_by_id, validation)

		return ItemCollection(item_lists_by_name, items_by_id), related_commands, validation


	def parse_items(self, item_inputs, container_ids_by_item, elements_by_id, commands_by_id, switched_element_ids,
			transformation_infos):
		item_lists_by_name = {}
		items_by_id = {}
		related_commands = {}
		validation = []

		for item_input in item_inputs:
			item, shortnames, related_command_id, container_ids, transformation_info = self.parse_item(item_input,
				switched_element_ids, validation)
			container_ids_by_item[item] = container_ids
			transformation_infos[item] = transformation_info
			self.add_item_by_id(items_by_id, elements_by_id, item, validation)
			self.add_item_by_name(item_lists_by_name, item, shortnames)
			self.resolve_related_command(item, commands_by_id, related_command_id, related_commands, shortnames, validation)

		return item_lists_by_name, items_by_id, related_commands, validation


	def parse_item(self, item_input, switched_element_ids, validation):
		item_id = self.parse_id(item_input)
		attributes = self.parse_attributes(item_input)
		labels, shortnames = self.parse_labels(item_input, validation, item_id)
		size = self.parse_size(item_input)
		writing = self.parse_writing(item_input, validation, item_id, labels.shortname)
		related_command_id = self.parse_related_command_id(item_input)
		switched_element_id, switch_info = self.parse_switch_info(attributes, item_input, related_command_id,
			validation, item_id, labels.shortname)
		using_info = self.parse_using_info(item_input)
		transformation_info = self.parse_transformation_info(item_input)
		list_templates = self.parse_list_templates(item_input)
		container_ids = self.parse_container_ids(item_input)

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
			list_templates=list_templates,
		)

		return item, shortnames, related_command_id, container_ids, transformation_info


	def parse_id(self, item_input):
		return item_input["data_id"]


	def parse_attributes(self, item_input):
		return int(item_input["attributes"], 16)


	def parse_labels(self, item_input, validation, item_id):
		label_input = item_input["labels"]
		shortnames = label_input["shortnames"]
		extended_descriptions = label_input.get("extended_descriptions", [])

		primary_shortname = None
		if shortnames:
			primary_shortname = shortnames[0]
		else:
			validation.append(Message(Message.ITEM_NO_SHORTNAMES, (item_id,)))

		return Labels(primary_shortname, label_input["longname"], label_input["description"], extended_descriptions), shortnames


	def parse_size(self, item_input):
		return item_input["size"]


	def parse_writing(self, item_input, validation, item_id, shortname):
		if not "writing" in item_input:
			return None

		writing_input = item_input["writing"]
		if not writing_input:
			validation.append(Message(Message.ITEM_WRITING_EMPTY, (item_id, shortname)))

		return writing_input


	def parse_related_command_id(self, item_input):
		return item_input.get("related_command_id")


	def parse_switch_info(self, attributes, item_input, related_command_id, validation, item_id, shortname):
		switched_element_id = None
		switch_info = None

		if (attributes & Item.ATTRIBUTE_SWITCHABLE):
			if "switch_info" in item_input:
				switch_info_input = item_input["switch_info"]
				switched_element_id = switch_info_input["element_id"]
				switched_attribute = int(switch_info_input["attribute"], 16)
				off_switch = switch_info_input["off"]
				on_switch = switch_info_input["on"]
				switch_info = SwitchInfo(attribute=switched_attribute, off=off_switch, on=on_switch)
			else:
				validation.append(Message(Message.ITEM_SWITCHABLE_NO_SWITCH_INFO, (item_id, shortname)))
			if not related_command_id:
				validation.append(Message(Message.ITEM_SWITCHABLE_NO_RELATED_COMMAND, (item_id, shortname)))

		elif "switch_info" in item_input:
			validation.append(Message(Message.ITEM_NON_SWITCHABLE_WITH_SWITCH_INFO, (item_id, shortname)))

		return switched_element_id, switch_info


	def parse_using_info(self, item_input):
		if not "using_info" in item_input:
			return None
		return int(item_input["using_info"], 16)


	def parse_transformation_info(self, item_input):
		transformation_info = {}
		if "transformations" in item_input:
			for transformation_input in item_input["transformations"]:
				command_id = transformation_input["command_id"]
				replacement_id = transformation_input["replacement_id"]
				tool_id = transformation_input.get("tool_id", None)
				material_id = transformation_input.get("material_id", None)
				transformation_info[command_id] = TransformationInfo(replacement_id=replacement_id, tool_id=tool_id, material_id=material_id)
		return transformation_info


	def parse_list_templates(self, item_input):
		list_templates = {}
		if "list_templates" in item_input:
			for template_type_key_input, list_template_input in item_input["list_templates"].items():
				template_type_key = template_type_key_input.upper()
				template_type = ListTemplateType[template_type_key]
				list_template = TokenTranslator.translate_substitution_tokens(list_template_input)
				list_templates[template_type] = list_template
		return list_templates


	def parse_container_ids(self, item_input):
		return item_input["container_ids"]


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
			list_templates,
		):

		if bool(attributes & Item.ATTRIBUTE_SENTIENT):
			item = SentientItem(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing,
				list_templates=list_templates)

		elif bool(attributes & Item.ATTRIBUTE_CONTAINER):
			item = ContainerItem(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing,
				list_templates=list_templates, )

		elif switch_info:
			item = SwitchableItem(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing,
				list_templates=list_templates, switch_info=switch_info)
			switched_element_ids[item] = switched_element_id

		elif self.item_is_usable(attributes):
			item = UsableItem(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing,
				list_templates=list_templates, attribute_activated=attribute_when_used)

		else:
			item = Item(item_id=item_id, attributes=attributes, labels=labels, size=size, writing=writing,
				list_templates=list_templates)

		return item


	def item_is_usable(self, attributes):
		return bool(attributes & Item.ATTRIBUTE_WEARABLE) or bool(attributes & Item.ATTRIBUTE_SAILABLE)


	def add_item_by_id(self, items_by_id, elements_by_id, item, validation):
		if item.data_id in items_by_id:
			validation.append(Message(Message.ITEM_SHARED_ID, (item.data_id,)))
		items_by_id[item.data_id] = item
		elements_by_id[item.data_id] = item


	def add_item_by_name(self, item_lists_by_name, item, shortnames):
		for shortname in shortnames:
			if not shortname in item_lists_by_name:
				item_lists_by_name[shortname] = []
			item_lists_by_name[shortname].append(item)


	def resolve_related_command(self, item, commands_by_id, related_command_id, related_commands, shortnames, validation):
		if related_command_id:
			if related_command_id in commands_by_id:
				related_command = commands_by_id[related_command_id]
				if item.is_switchable() and not related_command.is_switching():
					validation.append(Message(Message.ITEM_SWITCHABLE_NON_SWITCHING_RELATED_COMMAND, (item.data_id,
						item.shortname, related_command.data_id, related_command.primary)))
				for shortname in shortnames:
					related_commands[shortname] = commands_by_id.get(related_command_id)
			else:
				validation.append(Message(Message.ITEM_INVALID_RELATED_COMMAND, (related_command_id, item.data_id, item.shortname)))


	def place_items(self, container_ids_by_item, containers):
		for item, container_ids in container_ids_by_item.items():
			for container_id in container_ids:
				container = containers.get(container_id)
				if container:
					container.add(item)


	def resolve_switches(self, switched_element_ids, elements_by_id, validation):
		for switching_item, switched_element_id in switched_element_ids.items():
			if switched_element_id in elements_by_id:
				switching_item.switched_element = elements_by_id[switched_element_id]
			else:
				validation.append(Message(Message.ITEM_SWITCHABLE_INVALID_SWITCHED_ELEMENT, (switching_item.data_id,
					switching_item.shortname, switched_element_id)))


	def resolve_transformations(self, transformation_infos_by_transformed, elements_by_id, commands_by_id, validation):
		for transformed_item, transformation_infos in transformation_infos_by_transformed.items():
			for command_id, transformation_info in transformation_infos.items():
				self.resolve_transformation(transformed_item, command_id, transformation_info, elements_by_id, commands_by_id, validation)


	def resolve_transformation(self, transformed_item, command_id, transformation_info, elements_by_id, commands_by_id, validation):
		if not command_id in commands_by_id:
			validation.append(Message(Message.ITEM_TRANSFORMATION_COMMAND_UNKNOWN, (transformed_item.data_id,
				transformed_item.shortname, command_id)))
			return
		command = commands_by_id[command_id]
		self.resolve_transformation_command(transformed_item, command, transformation_info, elements_by_id, validation)


	def resolve_transformation_command(self, transformed_item, command, transformation_info, elements_by_id, validation):
		replacement_id = transformation_info.replacement_id
		if not replacement_id in elements_by_id:
			validation.append(Message(Message.ITEM_TRANSFORMATION_REPLACEMENT_UNKNOWN,
				(transformed_item.data_id, transformed_item.shortname, command.data_id, command.primary, replacement_id)))
			return
		replacement = elements_by_id[replacement_id]
		self.resolve_transformation_items(transformed_item, command, replacement, transformation_info, elements_by_id, validation)


	def resolve_transformation_items(self, transformed_item, command, replacement, transformation_info, elements_by_id, validation):
		if not isinstance(replacement, Item):
			validation.append(Message(Message.ITEM_TRANSFORMATION_REPLACEMENT_NON_ITEM,
				(transformed_item.data_id, transformed_item.shortname, command.data_id, command.primary,
				replacement.data_id, replacement.shortname)))
			return
		if transformed_item.is_mobile():
			if not replacement.is_mobile():
				validation.append(Message(Message.ITEM_TRANSFORMATION_REPLACEMENT_NON_MOBILE,
					(transformed_item.data_id, transformed_item.shortname, command.data_id, command.primary,
					replacement.data_id, replacement.shortname)))
			elif replacement.size > transformed_item.size:
				validation.append(Message(Message.ITEM_TRANSFORMATION_REPLACEMENT_TOO_LARGE,
					(transformed_item.data_id, transformed_item.shortname, command.data_id, command.primary,
					replacement.data_id, replacement.shortname)))
		tool = self.resolve_transformation_optional_item(transformed_item, command, elements_by_id, transformation_info.tool_id, "tool_id", validation)
		material = self.resolve_transformation_optional_item(transformed_item, command, elements_by_id, transformation_info.material_id, "material_id", validation)
		transformed_item.transformations[command.data_id] = Transformation(replacement=replacement, tool=tool, material=material)


	def resolve_transformation_optional_item(self, transformed_item, command, elements_by_id, item_id, field, validation):
		if not item_id:
			return None

		if not item_id in elements_by_id:
			validation.append(Message(Message.ITEM_TRANSFORMATION_OPTIONAL_UNKNOWN, (transformed_item.data_id,
				transformed_item.shortname, command.data_id, command.primary, field, item_id)))
			return None

		element = elements_by_id[item_id]
		if not isinstance(element, Item):
			validation.append(Message(Message.ITEM_TRANSFORMATION_OPTIONAL_NON_ITEM, (transformed_item.data_id,
				transformed_item.shortname, command.data_id, command.primary, field, item_id, element.shortname)))
			return None

		return element


	def validate_attributes(self, items_by_id, validation):
		for item in items_by_id.values():
			if item.is_copyable() and not item.is_liquid():
				validation.append(Message(Message.ITEM_COPYABLE_NON_LIQUID, (item.data_id, item.shortname)))
			if item.is_fragile() and not Item.COMMAND_ID_SMASH in item.transformations:
				validation.append(Message(Message.ITEM_FRAGILE_NO_SMASH_TRANSFORMATION, (item.data_id, item.shortname)))

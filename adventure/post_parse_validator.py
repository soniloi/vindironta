from adventure.direction import Direction
from adventure.item import ListTemplateType, UsableItem
from adventure.validation import Message, Severity

class PostParseValidator:

	def validate(self, data):
		command_validation = self.validate_commands(data.commands)
		inventory_validation = self.validate_inventories(data.inventories, data.locations)
		location_validation = self.validate_locations(data.locations)
		item_validation = self.validate_items(data.items)
		return command_validation + inventory_validation + location_validation + item_validation


	def validate_commands(self, command_collection):
		validation = []

		for command in command_collection.commands_by_id.values():
			self.validate_command_teleport(command, validation)
			self.validate_command_switchable(command, validation)

		return validation


	def validate_command_teleport(self, command, validation):
		if command.is_teleport():
			if not command.teleport_info:
				validation.append(Message(Message.COMMAND_TELEPORT_NO_TELEPORT_INFO, (command.data_id, command.primary)))
		elif command.teleport_info:
			validation.append(Message(Message.COMMAND_NON_TELEPORT_WITH_TELEPORT_INFO, (command.data_id, command.primary)))


	def validate_command_switchable(self, command, validation):
		if command.is_switchable():
			if not command.switch_info:
				validation.append(Message(Message.COMMAND_SWITCHABLE_NO_SWITCH_INFO, (command.data_id, command.primary)))
		elif command.switch_info:
			validation.append(Message(Message.COMMAND_NON_SWITCHABLE_WITH_SWITCH_INFO, (command.data_id, command.primary)))


	def validate_inventories(self, inventory_collection, location_collection):
		validation = []

		inventories = inventory_collection.inventories
		if len(inventories) < 1:
			validation.append(Message(Message.INVENTORY_NONE, ()))
		else:
			self.validate_inventories_default(inventories, validation)
			self.validate_inventories_non_default(inventories, location_collection.locations.keys(), validation)

		return validation


	def validate_inventories_default(self, inventories, validation):
		default_inventories = [inventory for inventory in inventories.values() if inventory.is_default()]
		if len(default_inventories) < 1:
			validation.append(Message(Message.INVENTORY_NO_DEFAULT, ()))
		elif len(default_inventories) > 1:
			validation.append(Message(Message.INVENTORY_MULTIPLE_DEFAULT, ([inventory.data_id for inventory in default_inventories],)))
		for inventory in default_inventories:
			if inventory.location_ids:
				validation.append(Message(Message.INVENTORY_DEFAULT_WITH_LOCATIONS, (inventory.data_id, inventory.shortname)))


	def validate_inventories_non_default(self, inventories, location_ids, validation):
		non_default_inventories = [inventory for inventory in inventories.values() if not inventory.is_default()]
		referenced_locations = {}
		for inventory in non_default_inventories:
			if not inventory.location_ids:
				validation.append(Message(Message.INVENTORY_NON_DEFAULT_NO_LOCATIONS, (inventory.data_id, inventory.shortname)))
			else:
				for location_id in inventory.location_ids:
					if not location_id in location_ids:
						validation.append(Message(Message.INVENTORY_NON_DEFAULT_UNKNOWN_LOCATION, (inventory.data_id, inventory.shortname, location_id)))
					elif location_id in referenced_locations:
						if referenced_locations[location_id] is inventory:
							validation.append(Message(Message.INVENTORY_NON_DEFAULT_DUPLICATE_LOCATION, (inventory.data_id, inventory.shortname, location_id)))
						else:
							validation.append(Message(Message.INVENTORY_NON_DEFAULT_SHARED_LOCATION, (inventory.data_id, inventory.shortname, location_id)))
					else:
						referenced_locations[location_id] = inventory


	def validate_locations(self, location_collection,):
		validation = []

		for location in location_collection.locations.values():
			self.validate_location_attributes(location, validation)

		return validation


	def validate_location_attributes(self, location, validation):
		if not location.has_floor() and not location.get_adjacent_location(Direction.DOWN):
			validation.append(Message(Message.LOCATION_NO_FLOOR_NO_DOWN, (location.data_id, Direction.DOWN.name)))
		if not location.has_land() and not location.has_floor():
			validation.append(Message(Message.LOCATION_NO_LAND_NO_FLOOR, (location.data_id,)))


	def validate_items(self, item_collection):
		validation = []

		for item in item_collection.items_by_id.values():
			self.validate_item_list_templates(item, validation)

		return validation


	def validate_item_list_templates(self, item, validation):
		list_templates = item.list_templates

		if item.is_switchable():
			if not (ListTemplateType.DEFAULT in list_templates or
					(ListTemplateType.LOCATION in list_templates and ListTemplateType.CARRYING in list_templates)):
				validation.append(Message(Message.ITEM_SWITCHABLE_NO_LIST_TEMPLATES, (item.data_id, item.shortname)))

		if self.item_is_usable(item):
			if not ListTemplateType.USING in list_templates:
				validation.append(Message(Message.ITEM_USABLE_NO_LIST_TEMPLATE_USING, (item.data_id, item.shortname)))
		elif ListTemplateType.USING in list_templates:
			validation.append(Message(Message.ITEM_NON_USABLE_WITH_LIST_TEMPLATE_USING, (item.data_id, item.shortname)))


	def item_is_usable(self, item):
		return isinstance(item, UsableItem)

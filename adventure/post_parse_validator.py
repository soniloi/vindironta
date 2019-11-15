from adventure.direction import Direction
from adventure.item import ContainerItem, Item, ListTemplateType, UsableItem
from adventure.location import Location
from adventure.validation import Message, Severity

class PostParseValidator:

	def validate(self, data):
		command_validation = self.validate_commands(data.commands)
		inventory_validation = self.validate_inventories(data.inventories, data.locations)
		location_validation = self.validate_locations(data.locations)
		item_validation = self.validate_items(data.items, data.commands.smash_command_ids)
		return command_validation + inventory_validation + location_validation + item_validation


	def validate_commands(self, command_collection):
		validation = []

		for command in command_collection.commands_by_id.values():
			self.validate_command_teleport(command, validation)
			self.validate_command_switchable(command, validation)

		if len(command_collection.smash_command_ids) > 1:
			validation.append(Message(Message.COMMAND_SMASH_MULTIPLE, ()))

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


	def validate_items(self, item_collection, smash_command_ids):
		validation = []

		smash_command_id = None
		if smash_command_ids:
			smash_command_id = smash_command_ids[0]

		for item in item_collection.items_by_id.values():
			self.validate_item_size(item, validation)
			self.validate_item_containers(item, validation)
			self.validate_item_list_templates(item, validation)
			self.validate_item_attributes(item, validation, smash_command_id)

		return validation


	def validate_item_size(self, item, validation):
		if item.size < Item.MIN_SIZE:
			validation.append(Message(Message.ITEM_BELOW_MINIMUM_SIZE, (item.data_id, item.shortname, item.size, Item.MIN_SIZE)))
		if isinstance(item, ContainerItem) and item.size < Item.MIN_SIZE + 1:
			validation.append(Message(Message.ITEM_CONTAINER_BELOW_MINIMUM_SIZE, (item.data_id, item.shortname, item.size, Item.MIN_SIZE)))


	def validate_item_containers(self, item, validation):
		for container in item.containers:
			if isinstance(container, Item) and container.size <= item.size:
				validation.append(Message(Message.ITEM_CONTAINER_TOO_SMALL, (item.data_id, item.shortname, item.size,
					container.data_id, container.shortname, container.size,)))


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


	def validate_item_attributes(self, item, validation, smash_command_id):
		self.validate_item_mobility(item, validation)
		self.validate_item_obstruction(item, validation)
		self.validate_item_usable(item, validation)
		if item.is_copyable() and not item.is_liquid():
			validation.append(Message(Message.ITEM_COPYABLE_NON_LIQUID, (item.data_id, item.shortname)))
		if item.is_fragile():
			if not smash_command_id:
				validation.append(Message(Message.ITEM_FRAGILE_NO_SMASH_COMMAND, ()))
			elif not smash_command_id in item.transformations:
				validation.append(Message(Message.ITEM_FRAGILE_NO_SMASH_TRANSFORMATION, (item.data_id, item.shortname)))


	def validate_item_mobility(self, item, validation):
		if not item.is_mobile():
			if any(not isinstance(container, Location) for container in item.containers):
				validation.append(Message(Message.ITEM_NON_MOBILE_NOT_AT_LOCATION, (item.data_id, item.shortname)))
			if item.is_sailable():
				validation.append(Message(Message.ITEM_NON_MOBILE_SAILABLE, (item.data_id, item.shortname)))
			if item.is_wearable():
				validation.append(Message(Message.ITEM_NON_MOBILE_WEARABLE, (item.data_id, item.shortname)))


	def validate_item_obstruction(self, item, validation):
		if item.is_obstruction():
			if len(item.containers) > 1:
				validation.append(Message(Message.ITEM_OBSTRUCTION_MULTIPLE_CONTAINERS, (item.data_id, item.shortname)))
			elif len(item.containers) == 1 and not isinstance(item.get_first_container(), Location):
				validation.append(Message(Message.ITEM_OBSTRUCTION_NOT_AT_LOCATION, (item.data_id, item.shortname)))


	def validate_item_usable(self, item, validation):
		if self.item_is_usable(item) and item.is_liquid():
			validation.append(Message(Message.ITEM_USABLE_LIQUID, (item.data_id, item.shortname)))
		if item.is_wearable() and item.is_sailable():
			validation.append(Message(Message.ITEM_WEARABLE_SAILABLE, (item.data_id, item.shortname)))

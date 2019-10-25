from adventure.validation import Message, Severity

class PostParseValidator:

	def validate(self, data):
		command_validation = self.validate_commands(data.commands)
		inventory_validation = self.validate_inventories(data.inventories)
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


	def validate_inventories(self, inventory_collection):
		validation = []

		inventories = inventory_collection.inventories
		if len(inventories) < 1:
			validation.append(Message(Message.INVENTORY_NONE, ()))
		else:
			default_inventory_ids = [inventory.data_id for inventory in inventories.values() if inventory.is_default()]
			if len(default_inventory_ids) < 1:
				validation.append(Message(Message.INVENTORY_NO_DEFAULT, ()))
			elif len(default_inventory_ids) > 1:
				validation.append(Message(Message.INVENTORY_MULTIPLE_DEFAULT, (default_inventory_ids,)))

		return validation


	def validate_locations(self, location_collection):
		return []


	def validate_items(self, item_collection):
		return []

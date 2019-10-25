from adventure.validation import Message, Severity

class PostParseValidator:

	def validate(self, data):
		command_validation = self.validate_commands(data.commands)
		inventory_validation = self.validate_inventories(data.inventories)
		location_validation = self.validate_locations(data.locations)
		item_validation = self.validate_items(data.items)
		return command_validation + inventory_validation + location_validation + item_validation


	def validate_commands(self, commands):
		validation = []

		for command in commands.commands_by_id.values():
			if command.is_teleport():
				if not command.teleport_info:
					validation.append(Message(Message.COMMAND_TELEPORT_NO_TELEPORT_INFO, (command.data_id, command.primary)))
			elif command.teleport_info:
				validation.append(Message(Message.COMMAND_NON_TELEPORT_WITH_TELEPORT_INFO, (command.data_id, command.primary)))

		return validation


	def validate_inventories(self, inventories):
		return []


	def validate_locations(self, locations):
		return []


	def validate_items(self, items):
		return []

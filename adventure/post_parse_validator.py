class PostParseValidator:

	def validate(self, data):
		command_validation = self.validate_commands(data.commands)
		inventory_validation = self.validate_inventories(data.inventories)
		location_validation = self.validate_locations(data.locations)
		item_validation = self.validate_items(data.items)
		return command_validation + inventory_validation + location_validation + item_validation


	def validate_commands(self, commands):
		return []


	def validate_inventories(self, inventories):
		return []


	def validate_locations(self, locations):
		return []


	def validate_items(self, items):
		return []

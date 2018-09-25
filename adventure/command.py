class Command:

	ATTRIBUTE_MOVEMENT = 0x40

	def __init__(self, command_id, attributes, function, primary):
		self.command_id = command_id
		self.attributes = attributes
		self.function = function
		self.primary = primary


	def has_attribute(self, attribute):
		return self.attributes & attribute != 0


	def execute(self, player, arg):
		if self.has_attribute(Command.ATTRIBUTE_MOVEMENT):
			arg = self.command_id
		return self.function(player, arg)

class Command:

	ATTRIBUTE_SECRET = 0x10
	ATTRIBUTE_MOVEMENT = 0x40

	def __init__(self, command_id, attributes, function, primary):
		self.command_id = command_id
		self.attributes = attributes
		self.function = function
		self.primary = primary


	def has_attribute(self, attribute):
		return self.attributes & attribute != 0


	def is_secret(self):
		return self.has_attribute(Command.ATTRIBUTE_SECRET)


	def execute(self, player, arg):
		if self.has_attribute(Command.ATTRIBUTE_MOVEMENT):
			arg = self.command_id

		template, content = self.function(player, arg)

		# TODO: revisit
		if not isinstance(content, list):
			content = [content]

		return template.format(*content)

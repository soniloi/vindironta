class Command:

	ATTRIBUTE_TAKES_ARG = 0x08
	ATTRIBUTE_SECRET = 0x10
	ATTRIBUTE_MOVEMENT = 0x40
	ATTRIBUTE_ARG_OPTIONAL = 0x80

	def __init__(self, command_id, attributes, resolver_function, handler_function, primary, aliases):
		self.command_id = command_id
		self.attributes = attributes
		self.resolver_function = resolver_function
		self.handler_function = handler_function
		self.primary = primary
		self.aliases = aliases


	def has_attribute(self, attribute):
		return self.attributes & attribute != 0


	def is_secret(self):
		return self.has_attribute(Command.ATTRIBUTE_SECRET)


	def execute(self, player, arg):
		template, content = self.resolver_function(self, player, arg)

		# TODO: revisit
		if not isinstance(content, list):
			content = [content]

		return template.format(*content)


class MovementCommand(Command):

	def __init__(self, command_id, attributes, resolver_function, handler_function, primary, aliases):
		Command.__init__(self, command_id, attributes, resolver_function, handler_function, primary, aliases)


	def execute(self, player, arg):
		arg = self.command_id
		return Command.execute(self, player, arg)


class ArgumentCommand(Command):

	def __init__(self, command_id, attributes, resolver_function, handler_function, primary, aliases, permissive):
		Command.__init__(self, command_id, attributes, resolver_function, handler_function, primary, aliases)
		self.permissive = permissive


class ArglessCommand(Command):

	def __init__(self, command_id, attributes, resolver_function, handler_function, primary, aliases):
		Command.__init__(self, command_id, attributes, resolver_function, handler_function, primary, aliases)

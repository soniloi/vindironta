class Command:

	ATTRIBUTE_TAKES_ARG = 0x08
	ATTRIBUTE_SECRET = 0x10
	ATTRIBUTE_MOVEMENT = 0x40
	ATTRIBUTE_ARG_OPTIONAL = 0x80
	ATTRIBUTE_SWITCHABLE = 0x100

	def __init__(self, command_id, attributes, resolver_function, handler_function, primary, aliases, permissive, off_switch, on_switch):
		self.command_id = command_id
		self.attributes = attributes
		self.resolver_function = resolver_function
		self.handler_function = handler_function
		self.primary = primary
		self.aliases = aliases
		self.permissive = permissive

		self.transitions = {}
		if off_switch:
			self.transitions[off_switch] = False
		if on_switch:
			self.transitions[on_switch] = True


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

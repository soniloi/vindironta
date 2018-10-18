class Command:

	ATTRIBUTE_ARG_ITEM_INVENTORY = 0x02
	ATTRIBUTE_ARG_ITEM_LOCATION = 0x04
	ATTRIBUTE_TAKES_ARG = 0x08
	ATTRIBUTE_SECRET = 0x10
	ATTRIBUTE_MOVEMENT = 0x40
	ATTRIBUTE_PERMISSIVE = 0x80
	ATTRIBUTE_SWITCHABLE = 0x100
	ATTRIBUTE_ARG_IS_ITEM = 0x200
	ATTRIBUTE_REQUIRES_VISION = 0x400

	def __init__(self, command_id, attributes, arg_function, handler_function, vision_function, primary, aliases,
			off_switch, on_switch):
		self.command_id = command_id
		self.attributes = attributes
		self.arg_function = arg_function
		self.handler_function = handler_function
		self.vision_function = vision_function
		self.primary = primary
		self.aliases = aliases

		self.transitions = {}
		if off_switch:
			self.transitions[off_switch] = False
		if on_switch:
			self.transitions[on_switch] = True


	def has_attribute(self, attribute):
		return self.attributes & attribute != 0


	def is_secret(self):
		return self.has_attribute(Command.ATTRIBUTE_SECRET)


	def is_permissive(self):
		return self.has_attribute(Command.ATTRIBUTE_PERMISSIVE)


	def requires_vision(self):
		return self.has_attribute(Command.ATTRIBUTE_REQUIRES_VISION)


	def takes_item_arg(self):
		return self.has_attribute(Command.ATTRIBUTE_ARG_IS_ITEM)


	def takes_item_arg_from_inventory(self):
		return self.has_attribute(Command.ATTRIBUTE_ARG_ITEM_INVENTORY)


	def takes_item_arg_from_location(self):
		return self.has_attribute(Command.ATTRIBUTE_ARG_ITEM_LOCATION)


	def takes_item_arg_from_inventory_only(self):
		return self.takes_item_arg_from_inventory() and not self.takes_item_arg_from_location()


	def takes_item_arg_from_location_only(self):
		return self.takes_item_arg_from_location() and not self.takes_item_arg_from_inventory()


	def takes_item_arg_from_inventory_or_location(self):
		return self.takes_item_arg_from_inventory() or self.takes_item_arg_from_location()


	def execute(self, player, arg):
		template, content = self.vision_function(self, player, arg)

		# TODO: revisit
		if not isinstance(content, list):
			content = [content]

		return template.format(*content)

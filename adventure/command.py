from adventure.data_element import DataElement

class Command(DataElement):

	ATTRIBUTE_TELEPORT = 0x2
	ATTRIBUTE_VERB_IS_FIRST_ARG = 0x4
	ATTRIBUTE_SECRET = 0x10
	ATTRIBUTE_MOVEMENT = 0x40
	ATTRIBUTE_SWITCHABLE = 0x100
	ATTRIBUTE_SWITCHING = 0x200
	ATTRIBUTE_REQUIRES_VISION = 0x400

	def __init__(self, command_id, attributes, arg_infos, resolver_functions, handler_function, primary,
			aliases, transitions, teleport_locations):
		DataElement.__init__(self, data_id=command_id, attributes=attributes)
		self.arg_infos = arg_infos
		self.resolver_functions = resolver_functions
		self.handler_function = handler_function
		self.primary = primary
		self.aliases = aliases
		self.transitions = transitions
		self.teleport_locations = teleport_locations


	def verb_is_first_arg(self):
		return self.has_attribute(Command.ATTRIBUTE_VERB_IS_FIRST_ARG)


	def is_secret(self):
		return self.has_attribute(Command.ATTRIBUTE_SECRET)


	def requires_vision(self):
		return self.has_attribute(Command.ATTRIBUTE_REQUIRES_VISION)


	def execute(self, player, args):

		for resolver_function in self.resolver_functions:

			success, body = resolver_function(self, player, *args)
			if not success:
				template, content = body
				return template.format(*content)

			args = body

		template, content = self.handler_function(self, player, *args)
		return template.format(*content)


class ArgInfo:

	ATTRIBUTE_MANDATORY = 0x1
	ATTRIBUTE_IS_ITEM = 0x2
	ATTRIBUTE_ITEM_LOCATION = 0x4
	ATTRIBUTE_ITEM_INVENTORY = 0x8

	def __init__(self, arg_attributes, linkers=[]):
		self.mandatory = bool(arg_attributes & ArgInfo.ATTRIBUTE_MANDATORY)
		self.is_item = bool(arg_attributes & ArgInfo.ATTRIBUTE_IS_ITEM)
		self.is_location_item = bool(arg_attributes & ArgInfo.ATTRIBUTE_ITEM_LOCATION)
		self.is_inventory_item = bool(arg_attributes & ArgInfo.ATTRIBUTE_ITEM_INVENTORY)
		self.linkers = linkers
		self.primary_linker = ""
		if linkers:
			self.primary_linker = linkers[0]


	def takes_item_arg_from_location_only(self):
		return self.is_location_item and not self.is_inventory_item


	def takes_item_arg_from_inventory_only(self):
		return self.is_inventory_item and not self.is_location_item


	def takes_item_arg_from_inventory_or_location(self):
		return self.is_location_item and self.is_inventory_item


	def is_valid_linker(self, linker):
		return linker in self.linkers

from adventure.data_element import DataElement

class Command(DataElement):

	ATTRIBUTE_TAKES_ARG = 0x08
	ATTRIBUTE_SECRET = 0x10
	ATTRIBUTE_MOVEMENT = 0x40
	ATTRIBUTE_PERMISSIVE = 0x80
	ATTRIBUTE_SWITCHABLE = 0x100
	ATTRIBUTE_REQUIRES_VISION = 0x400
	ATTRIBUTE_SWITCHING = 0x800

	def __init__(self, command_id, attributes, arg_info, arg_function, handler_function, vision_function, primary,
			aliases, off_switch, on_switch):
		DataElement.__init__(self, data_id=command_id, attributes=attributes)
		self.arg_info = arg_info
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


	def is_secret(self):
		return self.has_attribute(Command.ATTRIBUTE_SECRET)


	def is_permissive(self):
		return self.has_attribute(Command.ATTRIBUTE_PERMISSIVE)


	def requires_vision(self):
		return self.has_attribute(Command.ATTRIBUTE_REQUIRES_VISION)


	def takes_item_arg(self):
		return self.arg_info.is_item


	def takes_item_arg_from_inventory_only(self):
		return self.arg_info.takes_item_arg_from_inventory_only()


	def takes_item_arg_from_location_only(self):
		return self.arg_info.takes_item_arg_from_location_only()


	def takes_item_arg_from_inventory_or_location(self):
		return self.arg_info.takes_item_arg_from_inventory_or_location()


	def is_switching(self):
		return self.has_attribute(Command.ATTRIBUTE_SWITCHING)


	def execute(self, player, args):
		template, content = self.vision_function(self, player, args)

		# TODO: revisit
		if not isinstance(content, list):
			content = [content]

		return template.format(*content)


class ArgInfo:

	ATTRIBUTE_MANDATORY = 0x1
	ATTRIBUTE_IS_ITEM = 0x2
	ATTRIBUTE_ITEM_LOCATION = 0x4
	ATTRIBUTE_ITEM_INVENTORY = 0x8

	def __init__(self, arg_attributes):
		self.mandatory = bool(arg_attributes & ArgInfo.ATTRIBUTE_MANDATORY)
		self.is_item = bool(arg_attributes & ArgInfo.ATTRIBUTE_IS_ITEM)
		self.is_location_item = bool(arg_attributes & ArgInfo.ATTRIBUTE_ITEM_LOCATION)
		self.is_inventory_item = bool(arg_attributes & ArgInfo.ATTRIBUTE_ITEM_INVENTORY)


	def takes_item_arg_from_location_only(self):
		return self.is_location_item and not self.is_inventory_item


	def takes_item_arg_from_inventory_only(self):
		return self.is_inventory_item and not self.is_location_item


	def takes_item_arg_from_inventory_or_location(self):
		return self.is_location_item and self.is_inventory_item

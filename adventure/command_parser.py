from adventure.command import ArgInfo, Command
from adventure.command_collection import CommandCollection

class CommandParser:

	INDEX_ID = 0
	INDEX_ATTRIBUTES = 1
	INDEX_ARG_INFO = 2
	INDEX_LINK_INFO = 3
	INDEX_HANDLER = 4
	INDEX_NAMES = 5
	INDEX_SWITCHES = 6
	INDEX_TELEPORTS = 7


	def parse(self, command_inputs, resolvers):
		self.vision_resolver = resolvers.vision_resolver
		self.argument_resolver = resolvers.argument_resolver
		self.command_handler = resolvers.command_handler
		self.event_resolver = resolvers.event_resolver

		commands_by_name, commands_by_id = self.parse_commands(command_inputs)
		command_list = self.create_command_list(commands_by_name)

		return CommandCollection(commands_by_name, commands_by_id, command_list)


	def parse_commands(self, command_inputs):
		commands_by_name = {}
		commands_by_id = {}

		for command_input in command_inputs:
			command = self.parse_command(command_input)
			if command:
				for alias in command.aliases:
					commands_by_name[alias] = command
				commands_by_id[command.data_id] = command

		return commands_by_name, commands_by_id


	def parse_command(self, command_input):
		command_id = command_input["data_id"]
		attributes = int(command_input["attributes"], 16)
		arg_infos = self.parse_arg_infos(command_input.get("argument_infos"))
		resolver_functions = self.get_resolver_functions(attributes, arg_infos)
		command_handler_function = self.parse_handler_function(command_input["handler"])
		event_resolver_function = self.get_event_resolver_function()
		aliases = command_input["aliases"]
		switch_info = self.parse_switch_info(command_input.get("switch_info"))
		teleport_info = self.parse_teleport_info(command_input.get("teleport_info"))

		command = None
		if command_handler_function:
			resolver_functions.append(command_handler_function)
			resolver_functions.append(event_resolver_function)
			command = Command(
				command_id=command_id,
				attributes=attributes,
				arg_infos=arg_infos,
				resolver_functions=resolver_functions,
				aliases=aliases,
				switch_info=switch_info,
				teleport_info=teleport_info,
			)
		return command


	def parse_arg_infos(self, arg_info_inputs):
		arg_infos = []

		if arg_info_inputs:
			for arg_info_input in arg_info_inputs:
				attributes = int(arg_info_input["attributes"], 16)
				linkers = arg_info_input["linkers"]
				arg_infos.append(ArgInfo(attributes, linkers))

		return arg_infos


	def parse_switch_info(self, switch_info_input):
		switch_info = {}
		if switch_info_input:
			switch_info[switch_info_input["off"]] = False
			switch_info[switch_info_input["on"]] = True
		return switch_info


	def parse_teleport_info(self, teleport_info_inputs):
		teleport_infos = {}

		if teleport_info_inputs:
			for teleport_info_input in teleport_info_inputs:
				teleport_infos[teleport_info_input["source"]] = teleport_info_input["destination"]

		return teleport_infos


	def get_vision_function(self, attributes, arg_infos):
		if not bool(attributes & Command.ATTRIBUTE_REQUIRES_VISION):
			return None

		vision_function_name = "resolve_"
		if arg_infos:
			vision_function_name += "dark"
		else:
			vision_function_name += "light_and_dark"
		return self.vision_resolver.get_resolver_function(vision_function_name)


	def get_arg_function(self, attributes):
		arg_function_name = "resolve_"

		if bool(attributes & Command.ATTRIBUTE_TELEPORT):
			arg_function_name += "teleport"
		elif bool(attributes & Command.ATTRIBUTE_MOVEMENT):
			arg_function_name += "movement"
		elif bool(attributes & Command.ATTRIBUTE_SWITCHABLE):
			arg_function_name += "switchable"
		elif bool(attributes & Command.ATTRIBUTE_SWITCHING):
			arg_function_name += "switching"
		else:
			arg_function_name += "args"
		return self.argument_resolver.get_resolver_function(arg_function_name)


	def parse_handler_function(self, token):
		function_name = "handle_" + token
		return self.command_handler.get_resolver_function(function_name)


	def get_resolver_functions(self, attributes, arg_infos):
		vision_function = self.get_vision_function(attributes, arg_infos)
		arg_function = self.get_arg_function(attributes)

		resolver_functions = []
		if vision_function:
			resolver_functions.append(vision_function)
		if arg_function:
			resolver_functions.append(arg_function)

		return resolver_functions


	def get_event_resolver_function(self):
		return self.event_resolver.get_resolver_function("resolve_event")


	def create_command_list(self, commands_by_name):
		result = []
		for command in set(commands_by_name.values()):
			if not command.is_secret():
				command_aliases = "/".join(sorted(command.aliases))
				result.append(command_aliases)

		return ", ".join(sorted(result))
from adventure.command import ArgInfo, Command
from adventure.command_collection import CommandCollection
from adventure.validation import Message, Severity

class CommandParser:

	def parse(self, command_inputs, resolvers):
		self.vision_resolver = resolvers.vision_resolver
		self.argument_resolver = resolvers.argument_resolver
		self.command_handler = resolvers.command_handler
		self.event_resolver = resolvers.event_resolver
		self.life_resolver = resolvers.life_resolver

		commands_by_name, commands_by_id, teleport_infos, smash_command_id, validation = self.parse_commands(command_inputs)
		command_list = self.create_command_list(commands_by_name)

		return CommandCollection(commands_by_name, commands_by_id, command_list, smash_command_id), teleport_infos, validation


	def parse_commands(self, command_inputs):
		commands_by_name = {}
		commands_by_id = {}
		validation = []
		teleport_infos = {}

		smash_command_id = None
		for command_input in command_inputs:
			command, teleport_info, is_smash = self.parse_command(command_input, validation)
			if command:
				for alias in command.aliases:
					if alias in commands_by_name:
						if command is commands_by_name[alias]:
							validation.append(Message(Message.COMMAND_SHARED_ALIAS_SAME_COMMAND, (alias, command.data_id, command.primary)))
						else:
							validation.append(Message(Message.COMMAND_SHARED_ALIAS_DIFFERENT_COMMANDS, (alias, command.data_id, command.primary)))
					commands_by_name[alias] = command

				if command.data_id in commands_by_id:
					validation.append(Message(Message.COMMAND_SHARED_ID, (command.data_id, command.primary)))
				commands_by_id[command.data_id] = command

				if teleport_info:
					teleport_infos[command] = teleport_info

				if is_smash:
					smash_command_id = command.data_id

		return commands_by_name, commands_by_id, teleport_infos, smash_command_id, validation


	def parse_command(self, command_input, validation):
		command_id = command_input["data_id"]
		attributes = int(command_input["attributes"], 16)
		arg_infos = self.parse_arg_infos(command_input.get("argument_infos"))
		aliases = command_input["aliases"]
		switch_info = self.parse_switch_info(command_input.get("switch_info"))
		teleport_info = self.parse_teleport_info(command_input.get("teleport_info"), validation, command_id, aliases[0])

		command = None
		proceed, resolver_functions, is_smash = self.get_resolver_functions(attributes, arg_infos, command_input["handler"],
				validation, command_id, aliases[0])
		if proceed:
			command = Command(
			command_id=command_id,
			attributes=attributes,
			arg_infos=arg_infos,
			resolver_functions=resolver_functions,
			aliases=aliases,
			switch_info=switch_info,
		)

		return command, teleport_info, is_smash


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


	def parse_teleport_info(self, teleport_info_inputs, validation, command_id, primary):
		teleport_infos = {}

		if teleport_info_inputs:
			for teleport_info_input in teleport_info_inputs:
				source_id = teleport_info_input["source"]
				destination_id = teleport_info_input["destination"]
				if source_id in teleport_infos:
					validation.append(Message(Message.COMMAND_TELEPORT_SHARED_SOURCES, (source_id, command_id, primary, destination_id)))
				else:
					teleport_infos[source_id] = destination_id

		return teleport_infos


	def get_resolver_functions(self, attributes, arg_infos, handler_input, validation, command_id, primary):
		handler_function = self.get_handler_function(handler_input)
		if not handler_function:
			validation.append(Message(Message.COMMAND_UNRECOGNIZED_HANDLER, (handler_input, command_id, primary)))
			return False, (), False
		# TODO: remove when refactoring smash command
		is_smash = self.command_handler.is_smash_handler(handler_function)

		pre_vision_function = self.get_pre_vision_function(attributes, arg_infos)
		arg_function = self.get_arg_function(attributes)
		post_vision_function = self.get_post_vision_function(attributes)
		event_function = self.get_event_resolver_function()
		life_function = self.get_life_resolver_function()

		possible_functions = [pre_vision_function, arg_function, handler_function, post_vision_function, event_function, life_function]
		return True, [x for x in possible_functions if x], is_smash


	def get_pre_vision_function(self, attributes, arg_infos):
		if not bool(attributes & Command.ATTRIBUTE_REQUIRES_VISION):
			return None

		vision_function_name = "resolve_"
		if arg_infos:
			vision_function_name += "pre_dark"
		else:
			vision_function_name += "pre_light_and_dark"
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


	def get_handler_function(self, token):
		function_name = "handle_" + token
		return self.command_handler.get_resolver_function(function_name)


	def get_post_vision_function(self, attributes):
		if not bool(attributes & Command.ATTRIBUTE_POST_VISION):
			return None
		return self.vision_resolver.get_resolver_function("resolve_post_light_and_dark")


	def get_event_resolver_function(self):
		return self.event_resolver.get_resolver_function("resolve_event")


	def get_life_resolver_function(self):
		return self.life_resolver.get_resolver_function("resolve_life")


	def create_command_list(self, commands_by_name):
		result = []
		for command in set(commands_by_name.values()):
			if not command.is_secret():
				command_aliases = "/".join(sorted(command.aliases))
				result.append(command_aliases)

		return ", ".join(sorted(result))

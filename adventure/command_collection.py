from adventure.command import ArgInfo, Command
from adventure.file_reader import FileReader

class CommandCollection:

	INDEX_ID = 0
	INDEX_ATTRIBUTES = 1
	INDEX_ARG_INFO = 2
	INDEX_LINK_INFO = 3
	INDEX_HANDLER = 4
	INDEX_NAMES = 5
	INDEX_SWITCHES = 6
	INDEX_TELEPORTS = 7


	def __init__(self, reader, resolvers):
		self.vision_resolver = resolvers.vision_resolver
		self.argument_resolver = resolvers.argument_resolver
		self.command_handler = resolvers.command_handler
		self.commands = {}
		line = reader.read_line()
		while not line.startswith("---"):
			self.parse_command(line)
			line = reader.read_line()

		self.command_list = self.create_command_list()


	def parse_command(self, line):
		tokens = line.split("\t")

		command_id = self.parse_command_id(tokens[CommandCollection.INDEX_ID])
		attributes = self.parse_attributes(tokens[CommandCollection.INDEX_ATTRIBUTES])
		arg_infos = self.parse_arg_infos(tokens[CommandCollection.INDEX_ARG_INFO],
			tokens[CommandCollection.INDEX_LINK_INFO])
		arg_function = self.get_arg_function(attributes)
		handler_function = self.parse_handler_function(tokens[CommandCollection.INDEX_HANDLER])
		vision_function = self.get_vision_function(attributes, arg_infos)
		off_switch, on_switch = self.get_switches(tokens[CommandCollection.INDEX_SWITCHES], attributes)
		teleport_locations = self.get_teleport_locations(tokens[CommandCollection.INDEX_TELEPORTS], attributes)

		if handler_function and arg_function:
			(primary_command_name, command_names) = self.parse_command_names(tokens[CommandCollection.INDEX_NAMES])
			command = Command(
				command_id=command_id,
				attributes=attributes,
				arg_infos=arg_infos,
				arg_function=arg_function,
				handler_function=handler_function,
				vision_function=vision_function,
				primary=primary_command_name,
				aliases=command_names,
				off_switch=off_switch,
				on_switch=on_switch,
				teleport_locations=teleport_locations,
			)
			for command_name in command_names:
				self.commands[command_name] = command


	def parse_command_id(self, token):
		return int(token)


	def parse_attributes(self, token):
		return int(token, 16)


	def parse_arg_infos(self, arg_info_token, link_info_token):
		if not arg_info_token:
			return []
		arg_info_tokens = arg_info_token.split(",")
		link_info_tokens = link_info_token.split(",")

		arg_infos = []
		for i in range(0, len(arg_info_tokens)):
			arg_info_attributes_value = int(arg_info_tokens[i], 16)
			linkers = link_info_tokens[i].split("|")
			arg_infos.append(ArgInfo(arg_info_attributes_value, linkers))

		return arg_infos


	def get_arg_function(self, attributes):
		arg_function_name = "resolve_"
		if bool(attributes & Command.ATTRIBUTE_MOVEMENT):
			arg_function_name += "movement"
		elif bool(attributes & Command.ATTRIBUTE_SWITCHABLE):
			arg_function_name += "switchable"
		else:
			arg_function_name += "args"
		return self.argument_resolver.get_resolver_function(arg_function_name)


	def parse_handler_function(self, token):
		handler_function_name = "handle_" + token
		return self.command_handler.get_handler_function(handler_function_name)


	def get_vision_function(self, attributes, arg_infos):
		vision_function_name = "resolve_"
		if bool(attributes & Command.ATTRIBUTE_REQUIRES_VISION):
			if arg_infos:
				vision_function_name += "dark"
			else:
				vision_function_name += "light_and_dark"
		else:
			vision_function_name += "none"
		return self.vision_resolver.get_resolver_function(vision_function_name)


	def parse_command_names(self, token):
		command_names = token.split(",")
		return (command_names[0], command_names)


	def get_switches(self, token, attributes):
		if not bool(attributes & Command.ATTRIBUTE_SWITCHABLE):
			return None, None
		return token.split(",")


	def get_teleport_locations(self, token, attributes):
		teleport_locations = {}

		if bool(attributes & Command.ATTRIBUTE_TELEPORT):
			teleport_pair_tokens = token.split(",")
			for teleport_pair_token in teleport_pair_tokens:
				source, destination = self.get_teleport_location_ids(teleport_pair_token)
				teleport_locations[source] = destination

		return teleport_locations


	def get_teleport_location_ids(self, token):
		teleport_pair = token.split("|")
		source = int(teleport_pair[0])
		destination = int(teleport_pair[1])
		return source, destination


	def get(self, name):
		return self.commands.get(name)


	def create_command_list(self):
		result = []
		for command in set(self.commands.values()):
			if not command.is_secret():
				command_aliases = "/".join(sorted(command.aliases))
				result.append(command_aliases)

		return ", ".join(sorted(result))


	def list_commands(self):
		return self.command_list

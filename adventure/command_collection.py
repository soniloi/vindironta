from adventure.command import Command, MovementCommand, ArgumentCommand, ArglessCommand
from adventure.file_reader import FileReader

class CommandCollection:

	def __init__(self, reader, argument_resolver, command_handler):
		self.argument_resolver = argument_resolver
		self.command_handler = command_handler
		self.commands = {}
		line = reader.read_line()
		while not line.startswith("---"):
			self.parse_command(line)
			line = reader.read_line()

		self.command_list = self.create_command_list()


	def parse_command(self, line):
		tokens = line.split("\t")

		command_id = self.parse_command_id(tokens[0])
		command_attributes = self.parse_command_attributes(tokens[1])
		resolver_function = self.get_resolver_function(command_attributes)
		handler_function = self.parse_handler_function(tokens[2])

		if handler_function:
			(primary_command_name, command_names) = self.parse_command_names(tokens[3])
			command = self.create_command(
				command_id=command_id,
				attributes=command_attributes,
				resolver_function=resolver_function,
				handler_function=handler_function,
				primary=primary_command_name,
				aliases=command_names
			)
			for command_name in command_names:
				self.commands[command_name] = command


	def create_command(self, command_id, attributes, resolver_function, handler_function, primary, aliases):
		if attributes & Command.ATTRIBUTE_MOVEMENT != 0:
			return MovementCommand(
				command_id=command_id,
				attributes=attributes,
				resolver_function=resolver_function,
				handler_function=handler_function,
				primary=primary,
				aliases=aliases
			)

		elif attributes & Command.ATTRIBUTE_TAKES_ARG != 0:
			permissive = attributes & Command.ATTRIBUTE_ARG_OPTIONAL != 0
			return ArgumentCommand(
				command_id=command_id,
				attributes=attributes,
				resolver_function=resolver_function,
				handler_function=handler_function,
				primary=primary,
				aliases=aliases,
				permissive=permissive
			)

		return ArglessCommand(
			command_id=command_id,
			attributes=attributes,
			resolver_function=resolver_function,
			handler_function=handler_function,
			primary=primary,
			aliases=aliases
		)

	def parse_command_id(self, token):
		return int(token)


	def parse_command_attributes(self, token):
		return int(token, 16)


	def get_resolver_function(self, attributes):
		resolver_function_name = "execute"
		return self.argument_resolver.get_resolver_function(resolver_function_name)


	def parse_handler_function(self, token):
		handler_function_name = "handle_" + token
		return self.command_handler.get_handler_function(handler_function_name)


	def parse_command_names(self, token):
		command_names = token.split(",")
		return (command_names[0], command_names)


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

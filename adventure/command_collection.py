from adventure.command import Command, MovementCommand
from adventure.file_reader import FileReader

class CommandCollection:

	def __init__(self, reader, command_handler):
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
		command_function = self.parse_command_function(tokens[2])

		if command_function:
			(primary_command_name, command_names) = self.parse_command_names(tokens[3])
			command = self.create_command(
				command_id=command_id,
				attributes=command_attributes,
				function=command_function,
				primary=primary_command_name,
				aliases=command_names
			)
			for command_name in command_names:
				self.commands[command_name] = command


	def create_command(self, command_id, attributes, function, primary, aliases):
		if attributes & Command.ATTRIBUTE_MOVEMENT != 0:
			return MovementCommand(
				command_id=command_id,
				attributes=attributes,
				function=function,
				primary=primary,
				aliases=aliases
			)

		return Command(
			command_id=command_id,
			attributes=attributes,
			function=function,
			primary=primary,
			aliases=aliases
		)

	def parse_command_id(self, token):
		return int(token)


	def parse_command_attributes(self, token):
		return int(token, 16)


	def parse_command_function(self, token):
		command_function_name = "handle_" + token
		return self.command_handler.get_command_function(command_function_name)


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

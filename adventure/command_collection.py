from adventure.command import Command
from adventure.file_reader import FileReader

class CommandCollection:

	def __init__(self, reader, command_handler):
		self.command_handler = command_handler
		self.commands = {}
		line = reader.read_line()
		while not line.startswith("---"):
			self.create_command(line)
			line = reader.read_line()


	def create_command(self, line):
		tokens = line.split("\t")

		command_id = self.parse_command_id(tokens[0])
		command_attributes = self.parse_command_attributes(tokens[1])
		command_function = self.parse_command_function(tokens[2])

		if command_function:
			(primary_command_name, command_names) = self.parse_command_names(tokens[3])
			command = Command(command_id, command_attributes, command_function, primary_command_name)
			for command_name in command_names:
				self.commands[command_name] = command


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
		if name in self.commands:
			return self.commands[name]
		return None

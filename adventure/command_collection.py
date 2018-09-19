from adventure.command import Command
from adventure.file_reader import FileReader

class CommandCollection:

	def __init__(self, reader):
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
		return getattr(self, command_function_name, None)


	def parse_command_names(self, token):
		command_names = token.split(",")
		return (command_names[0], command_names)


	def get(self, name):
		if name in self.commands:
			return self.commands[name]
		return None


	def handle_look(self, player):
		return "You are %s." % player.location.get_full_description()


	def handle_score(self, player):
		return "Your current score is %s points" % player.score


	def handle_quit(self, player):
		player.playing = False
		return "Game has ended"

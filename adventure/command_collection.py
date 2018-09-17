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

		command_id = tokens[0]
		command_attributes = int(tokens[1], 16)
		command_function_name = "handle_" + tokens[2]
		command_function = getattr(self, command_function_name, None)

		if command_function:
			command_names = tokens[3].split(",")
			primary_command_name = command_names[0]

			command = Command(command_id, command_attributes, command_function, primary_command_name)

			for command_name in command_names:
				self.commands[command_name] = command


	def get(self, name):
		if name in self.commands:
			return self.commands[name]
		return None


	def handle_look(self, player):
		return "You cannot see at thing in this darkness"


	def handle_score(self, player):
		return "Your current score is %s points" % player.score


	def handle_quit(self, player):
		player.playing = False
		return "Game has ended"

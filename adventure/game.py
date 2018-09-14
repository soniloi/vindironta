from adventure.command import Command
from adventure.file_reader import FileReader

class Game:
 
	def __init__(self, filename=None):
		self.on = True

		# TODO: fix this
		if filename:
			with open(filename, "rb") as input_file:
				reader = FileReader(input_file)
				self.init_commands(reader)
				# TODO: read locations, items, strings


	def init_commands(self, reader):
		self.commands = {}
		line = reader.read_line()
		while line != "---":
			self.create_command(line)
			line = reader.read_line()


	def create_command(self, line):
		tokens = line.split("\t")

		command_id = tokens[0]
		command_attributes = int(tokens[1], 16)
		command_function_name = "handle_" + tokens[2]
		command_function = getattr(self, command_function_name, None)

		command_names = tokens[3].split(",")
		primary_command_name = command_names[0]

		command = Command(command_id, command_attributes, command_function, primary_command_name)

		for command_name in command_names:
			self.commands[command_name] = command


	def process_input(self, inputs):
		if not inputs:
			return ""

		command = inputs[0]
		command_function_name = "handle_" + command
		command_function = getattr(self, command_function_name, None)

		response = ""
		if command_function:
			response = command_function()

		return response


	def handle_look(self):
		return "You cannot see at thing in this darkness"


	def handle_score(self):
		return "Your current score is 17 points"


	def handle_quit(self):
		self.on = False
		return "Game has ended"

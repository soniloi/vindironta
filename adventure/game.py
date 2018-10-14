from adventure.argument_resolver import ArgumentResolver
from adventure.command_handler import CommandHandler
from adventure.data_collection import DataCollection
from adventure.file_reader import FileReader
from adventure.player import Player

class Game:
 
	def __init__(self, filename=None):
		self.on = True
		self.argument_resolver = ArgumentResolver()
		self.command_handler = CommandHandler()

		if filename:
			with open(filename, "rb") as input_file:
				reader = FileReader(input_file)
				self.init_data(reader)
				self.init_player()


	def init_data(self, reader):
		self.data = DataCollection(reader, self.argument_resolver, self.command_handler)
		self.commands = self.data.commands
		self.argument_resolver.init_data(self.data)
		self.command_handler.init_data(self.data)


	def init_player(self):
		self.player = Player(self.data.get_location(9))


	def process_input(self, line):
		tokens = line.split()
		response = ""

		if tokens:

			command = self.player.current_command
			self.player.current_command = None

			if command:
				command_arg = tokens[0]

			else:
				command = self.get_command_from_input(tokens)
				command_arg = self.get_command_arg(tokens)
				self.player.increment_instructions()

			if command:
				response = command.execute(self.player, command_arg)

		self.on = self.player.playing

		return response


	def get_command_from_input(self, tokens):
		command_name = tokens[0]
		command = self.commands.get(command_name)
		return command


	def get_command_arg(self, tokens):
		if len(tokens) > 1:
			return tokens[1]
		return None

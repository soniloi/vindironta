from adventure.argument_resolver import ArgumentResolver
from adventure.command_handler import CommandHandler
from adventure.data_collection import DataCollection
from adventure.file_reader import FileReader
from adventure.player import Player
from adventure.resolvers import Resolvers
from adventure.vision_resolver import VisionResolver

class Game:

	# TODO: decide where this should go
	PLAYER_START_LOCATION_ID = 9

	def __init__(self, filename=None):
		self.on = True
		self.argument_resolver = ArgumentResolver()
		self.command_handler = CommandHandler()
		self.vision_resolver = VisionResolver()

		if filename:
			with open(filename, "rb") as input_file:
				reader = FileReader(input_file)
				self.init_data(reader)
				self.init_player()


	def init_data(self, reader):
		resolvers = Resolvers(
			vision_resolver=self.vision_resolver,
			argument_resolver=self.argument_resolver,
			command_handler=self.command_handler
		)
		self.data = DataCollection(reader, resolvers)
		self.commands = self.data.commands
		self.argument_resolver.init_data(self.data)
		self.command_handler.init_data(self.data)
		self.vision_resolver.init_data(self.data)


	def init_player(self):
		self.player = Player(self.data.get_location(Game.PLAYER_START_LOCATION_ID))


	def process_input(self, line):
		tokens = line.split()
		if tokens:
			return self.process_tokens(tokens)
		return ""


	def process_tokens(self, tokens):

		response = ""
		if self.player.alive:
			response = self.process_tokens_as_command(tokens)

			if not self.player.alive:
				response += " " + self.data.get_response("describe_dead") + \
					" " + self.data.get_response("describe_reincarnation")

		else:
			response = self.process_tokens_as_reincarnation_answer(tokens)

		if self.player.playing and not self.player.alive:
			response += " " + self.data.get_response("request_reincarnation")

		self.on = self.player.playing

		return response


	def process_tokens_as_command(self, tokens):
		command = self.player.current_command
		self.player.current_command = None

		if command:
			command_args = tokens

		else:
			command = self.get_command_from_input(tokens)
			command_args = tokens[1:]
			self.player.increment_instructions()

		if command:
			return command.execute(self.player, command_args)
		return ""


	def get_command_from_input(self, tokens):
		return self.commands.get(tokens[0])


	def process_tokens_as_reincarnation_answer(self, tokens):
		answer = tokens[0]

		if self.data.matches_input("true", answer):
			self.process_reincarnation()
			return self.data.get_response("confirm_reincarnation")

		elif self.data.matches_input("false", answer):
			self.player.playing = False
			return self.data.get_response("confirm_quit")

		return self.data.get_response("reject_no_understand_selection")


	def process_reincarnation(self):
		self.player.alive = True
		self.player.location = self.data.get_location(Game.PLAYER_START_LOCATION_ID)
		self.player.previous_location = None

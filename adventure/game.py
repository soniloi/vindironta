import json

from adventure.argument_resolver import ArgumentResolver
from adventure.command_handler import CommandHandler
from adventure.command_runner import CommandRunner
from adventure.data_collection import DataCollection
from adventure.event_resolver import EventResolver
from adventure.file_reader import FileReader
from adventure.player import Player
from adventure.resolvers import Resolvers
from adventure.token_processor import TokenProcessor
from adventure.vision_resolver import VisionResolver

class Game:

	# TODO: decide where this should go
	PLAYER_INITIAL_LOCATION_ID = 9

	def __init__(self, filename=None):
		self.on = True
		self.argument_resolver = ArgumentResolver()
		self.command_handler = CommandHandler()
		self.vision_resolver = VisionResolver()
		self.event_resolver = EventResolver()

		if filename:
			with open(filename, "rb") as input_file:
				reader = FileReader(input_file)
				content = reader.get_content()
				json_content = json.loads(content)
				self.init_data(json_content)
				self.init_player()

				command_runner = CommandRunner()
				self.init_token_processor(self.data, command_runner)


	def init_data(self, content):
		resolvers = Resolvers(
			vision_resolver=self.vision_resolver,
			argument_resolver=self.argument_resolver,
			command_handler=self.command_handler,
			event_resolver=self.event_resolver,
		)
		self.data = DataCollection(content, resolvers)
		self.argument_resolver.init_data(self.data)
		self.command_handler.init_data(self.data)
		self.vision_resolver.init_data(self.data)
		self.event_resolver.init_data(self.data)


	def init_player(self):
		initial_location = self.data.get_location(Game.PLAYER_INITIAL_LOCATION_ID)
		default_inventory_template = self.data.get_default_inventory_template()
		inventory_templates = self.data.get_inventory_templates()
		self.player = Player(initial_location, default_inventory_template, inventory_templates)


	def init_token_processor(self, data, command_runner):
		self.token_processor = TokenProcessor(data, command_runner)


	def process_input(self, line):
		tokens = line.lower().split()
		if tokens:
			response = self.token_processor.process_tokens(self.player, tokens)
			self.on = self.player.is_playing()
			return response
		return ""

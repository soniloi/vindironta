import json

from adventure.argument_resolver import ArgumentResolver
from adventure.command_handler import CommandHandler
from adventure.command_runner import CommandRunner
from adventure.data_parser import DataParser
from adventure.event_resolver import EventResolver
from adventure.file_reader import FileReader
from adventure.player import Player
from adventure.resolvers import Resolvers
from adventure.token_processor import TokenProcessor
from adventure.vision_resolver import VisionResolver

class Game:

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
				self.init_data_and_player(json_content)

				command_runner = CommandRunner()
				self.init_token_processor(self.data, command_runner)


	def init_data_and_player(self, content):
		resolvers = Resolvers(
			vision_resolver=self.vision_resolver,
			argument_resolver=self.argument_resolver,
			command_handler=self.command_handler,
			event_resolver=self.event_resolver,
		)
		data_parser = DataParser()
		self.data, self.player = data_parser.parse(content, resolvers)

		self.argument_resolver.init_data(self.data)
		self.command_handler.init_data(self.data)
		self.vision_resolver.init_data(self.data)
		self.event_resolver.init_data(self.data)


	def init_token_processor(self, data, command_runner):
		self.token_processor = TokenProcessor(data, command_runner)


	def process_input(self, line):
		tokens = line.lower().split()
		if tokens:
			response = self.token_processor.process_tokens(self.player, tokens)
			self.on = self.player.is_playing()
			return response
		return ""

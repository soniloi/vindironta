from adventure.command_collection import CommandCollection
from adventure.command_handler import CommandHandler
from adventure.data_collection import DataCollection
from adventure.file_reader import FileReader
from adventure.item_collection import ItemCollection
from adventure.location_collection import LocationCollection
from adventure.player import Player
from adventure.text_collection import TextCollection

class Game:
 
	def __init__(self, filename=None):
		self.on = True
		self.command_handler = CommandHandler()

		if filename:
			with open(filename, "rb") as input_file:
				reader = FileReader(input_file)
				self.init_data(reader)
				self.init_player()


	def init_data(self, reader):
		self.command_collection = CommandCollection(reader, self.command_handler)
		location_collection = LocationCollection(reader)
		item_collection = ItemCollection(reader, location_collection)
		hint_text_collection = TextCollection(reader)
		explain_text_collection = TextCollection(reader)
		response_text_collection = TextCollection(reader)
		puzzle_text_collection = TextCollection(reader)

		self.data = DataCollection(
			commands=self.command_collection,
			locations=location_collection,
			items=item_collection,
			hints=hint_text_collection,
			explanations=explain_text_collection,
			responses=response_text_collection,
			puzzles=puzzle_text_collection
		)

		# TODO: Re-order file and pass through constructor?
		self.command_handler.init_data(self.data)


	def init_player(self):
		self.player = Player(self.data.locations.get(9))


	def process_input(self, line):
		tokens = line.split()
		response = ""

		if tokens:
			command_name = tokens[0]
			command_arg = self.get_arg(tokens)

			command = self.command_collection.get(command_name)
			if command:
				response = command.execute(self.player, command_arg)

		self.on = self.player.playing

		return response


	def get_arg(self, tokens):
		if len(tokens) > 1:
			return tokens[1]
		return None

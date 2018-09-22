from adventure.command_collection import CommandCollection
from adventure.command_handler import CommandHandler
from adventure.file_reader import FileReader
from adventure.item_collection import ItemCollection
from adventure.location_collection import LocationCollection
from adventure.player import Player

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
		self.location_collection = LocationCollection(reader)
		self.item_collection = ItemCollection(reader, self.location_collection)
		# TODO: Re-order file and pass through constructor
		self.command_handler.init_data(self.location_collection, self.item_collection)
		# TODO: read strings


	def init_player(self):
		self.player = Player(self.location_collection.get(9))


	def process_input(self, line):
		tokens = line.split()
		response = ""

		if tokens:
			command_name = tokens[0]
			command = self.command_collection.get(command_name)
			if command:
				response = command.execute(self.player)

		self.on = self.player.playing

		return response

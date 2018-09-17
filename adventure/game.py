from adventure.command_collection import CommandCollection
from adventure.file_reader import FileReader
from adventure.item_collection import ItemCollection
from adventure.location_collection import LocationCollection
from adventure.player import Player

class Game:
 
	def __init__(self, filename=None):
		self.on = True

		if filename:
			with open(filename, "rb") as input_file:
				reader = FileReader(input_file)
				self.init_data(reader)
				self.init_player()


	def init_data(self, reader):
		self.command_collection = CommandCollection(reader)
		self.location_collection = LocationCollection(reader)
		self.item_collection = ItemCollection(reader)
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
				response = command.execute()

		# TODO: remove
		if self.command_collection.quit_received:
			self.on = False

		return response

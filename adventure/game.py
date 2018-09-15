from adventure.command_collection import CommandCollection
from adventure.file_reader import FileReader

class Game:
 
	def __init__(self, filename=None):
		self.on = True

		if filename:
			with open(filename, "rb") as input_file:
				reader = FileReader(input_file)
				self.command_collection = CommandCollection(reader)
				# TODO: read locations, items, strings


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

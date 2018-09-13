from adventure import file_reader

class Game:
 
	def __init__(self, filename):
		self.init_data(filename)
		self.on = True


	def init_data(self, filename):
		with open(filename, "rb") as input_file:
			# TODO: read into objects
			reader = file_reader.FileReader(input_file)
			line = reader.read_line()
			print(line)


	def process_input(self, inputs):
		if not inputs:
			return ""

		command = inputs[0]
		response = ""

		if command == "look":
			response = self.handle_look()

		elif command == "score":
			response = self.handle_score()

		elif command == "quit":
			response = self.handle_quit()

		return response

	def handle_look(self):
		return "You cannot see at thing in this darkness"

	def handle_score(self):
		return "Your current score is 17 points"

	def handle_quit(self):
		self.on = False
		return "Game has ended"

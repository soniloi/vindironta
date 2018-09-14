from adventure import file_reader

class Game:
 
	def __init__(self, filename=None):
		self.on = True

		# TODO: fix this
		if filename:
			with open(filename, "rb") as input_file:
				# TODO: read into objects
				reader = file_reader.FileReader(input_file)
				line = reader.read_line()
				print(line)


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

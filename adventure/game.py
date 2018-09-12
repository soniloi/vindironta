class Game:
 
	def __init__(self, filename):
		# TODO: Read from file, using it to initialize data, player, etc.
		print(filename)
		self.on = True

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

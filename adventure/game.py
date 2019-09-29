from adventure.command_runner import CommandRunner
from adventure.token_processor import TokenProcessor

class Game:

	def __init__(self, data, player):
		self.data = data
		self.player = player
		self.running = True
		command_runner = CommandRunner(self.data)
		self.init_token_processor(self.data, command_runner)


	def init_token_processor(self, data, command_runner):
		self.token_processor = TokenProcessor(data, command_runner)


	def is_running(self):
		return self.running


	def get_start_message(self):
		return self.data.get_start_message()


	def process_input(self, line):
		tokens = line.lower().split()
		if tokens:
			response = self.token_processor.process_tokens(self.player, tokens)
			self.running = self.player.is_playing()
			return response
		return ""

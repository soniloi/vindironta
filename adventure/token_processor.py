class TokenProcessor:

	PLAYER_INITIAL_LOCATION_ID = 9

	def __init__(self, data):
		self.data = data
		self.commands = data.get_commands()


	def process_tokens(self, player, tokens):
		response = ""

		if player.is_alive():
			response = self.process_tokens_as_command(player, tokens)

			if not player.is_alive():
				response += " " + self.data.get_response("describe_dead") + \
					" " + self.data.get_response("describe_reincarnation")

		else:
			response = self.process_tokens_as_reincarnation_answer(player, tokens)

		if player.is_playing() and not player.is_alive():
			response += " " + self.data.get_response("request_reincarnation")

		return response


	def process_tokens_as_command(self, player, tokens):
		command = player.get_current_command()
		player.current_command = None
		command_args = tokens

		if not command:
			command = self.get_command_from_input(tokens)
			if command and not command.verb_is_first_arg():
				command_args = tokens[1:]
			player.increment_instructions()

		# TODO: deprecate this in favour of nouns-as-verbs
		if not command:
			command = self.commands.get("switch")

		if command:
			return command.execute(player, command_args)
		return ""


	def get_command_from_input(self, tokens):
		return self.commands.get(tokens[0])


	def process_tokens_as_reincarnation_answer(self, player, tokens):
		answer = tokens[0]

		if self.data.matches_input("true", answer):
			self.process_reincarnation(player)
			return self.data.get_response("confirm_reincarnation")

		elif self.data.matches_input("false", answer):
			player.set_playing(False)
			return self.data.get_response("confirm_quit")

		return self.data.get_response("reject_no_understand_selection")


	def process_reincarnation(self, player):
		player.set_alive(True)
		player.set_location(self.data.get_location(TokenProcessor.PLAYER_INITIAL_LOCATION_ID))
		player.set_previous_location(None)

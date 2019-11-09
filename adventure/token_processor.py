class TokenProcessor:

	def __init__(self, data, command_runner):
		self.data = data
		self.commands = data.get_commands()
		self.item_related_commands = data.get_item_related_commands()
		self.command_runner = command_runner


	def process_tokens(self, player, tokens):
		response = ""

		if player.is_alive():
			response = self.process_tokens_as_command(player, tokens)

		else:
			response = self.process_tokens_as_reincarnation_answer(player, tokens)

		if player.is_playing() and not player.is_alive():
			response += " " + self.data.get_response("request_reincarnation")

		if not response:
			response = self.data.get_response("reject_no_understand_instruction")

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

		if not command:
			command = self.item_related_commands.get(tokens[0])

		if not command:
			return ""

		return self.command_runner.run(command, player, command_args)


	def get_command_from_input(self, tokens):
		return self.commands.get_by_name(tokens[0])


	def process_tokens_as_reincarnation_answer(self, player, tokens):
		answer = tokens[0]

		if self.data.matches_input("true", answer):
			player.reincarnate()
			return self.data.get_response("confirm_reincarnation")

		elif self.data.matches_input("false", answer):
			player.set_playing(False)
			return self.data.get_response("confirm_quit")

		return self.data.get_response("reject_no_understand_selection")

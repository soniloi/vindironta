class CommandHandler:

	def init_data(self, data):
		self.data = data


	def get_command_function(self, command_function_name):
		return getattr(self, command_function_name, None)


	def get_response(self, response_key):
		return self.data.responses.get(response_key)


	def handle_drop(self, player, arg):
		#TODO: handle None arg

		template = ""
		content = ""

		item = self.data.items.get(arg)
		if not item:
			template = self.get_response("reject_unknown")

		else:
			content = item.shortname
			if not player.is_carrying(item):
				template = self.get_response("reject_not_holding")
			else:
				player.inventory.remove(item)
				player.location.insert(item)
				template = self.get_response("confirm_dropped")

		return template.format(content)


	def handle_inventory(self, player, arg):
		return player.inventory.get_contents_description()


	def handle_look(self, player, arg):
		return "You are %s." % player.location.get_full_description()


	def handle_quit(self, player, arg):
		player.playing = False
		return "Game has ended"


	def handle_score(self, player, arg):
		return "Your current score is %s points" % player.score


	def handle_take(self, player, arg):
		#TODO: handle None arg

		template = ""
		content = ""

		item = self.data.items.get(arg)
		if not item:
			template = self.get_response("reject_unknown")

		else:
			content = item.shortname
			if player.is_carrying(item):
				template = self.get_response("reject_already")

			elif not player.location.contains(item):
				template = self.get_response("reject_not_here")
			else:
				item.container.remove(item)
				player.inventory.insert(item)
				template = self.get_response("confirm_taken")

		return template.format(content)

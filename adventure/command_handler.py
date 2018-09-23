class CommandHandler:

	def init_data(self, data):
		self.data = data


	def get_command_function(self, command_function_name):
		return getattr(self, command_function_name, None)


	def handle_drop(self, player, arg):
		#TODO: handle None arg

		result = ""

		item = self.data.items.get(arg)
		if not item:
			result = "I do not know who or what that is."

		else:
			if not player.is_carrying(item):
				result = "You do not have the %s." % item.shortname
			else:
				player.inventory.remove(item)
				player.location.insert(item)
				result = "Dropped."

		return result


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

		result = ""

		item = self.data.items.get(arg)
		if not item:
			result = "I do not know who or what that is."

		else:
			if player.is_carrying(item):
				result = "You already have the %s." % item.shortname
			elif not player.location.contains(item):
				result = "I see no %s here." % item.shortname
			else:
				item.container.remove(item)
				player.inventory.insert(item)
				result = "Taken."

		return result

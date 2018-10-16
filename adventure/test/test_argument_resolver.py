import unittest
from unittest.mock import Mock

from adventure.argument_resolver import ArgumentResolver
from adventure.command import Command
from adventure.data_collection import DataCollection
from adventure.player import Player

class TestArgumentResolver(unittest.TestCase):

	def setUp(self):

		data = Mock()
		data.get_response.side_effect = self.responses_side_effect

		self.response_map = {
			"request_argless" : "Do not give an argument for this command.",
			"request_direct" : "What do you want to {0}?",
			"request_switch" : "Use the command \"{0}\" with either \"{1}\" or \"{2}\".",
		}

		self.resolver = ArgumentResolver()
		self.resolver.init_data(data)


	def responses_side_effect(self, *args):
		return self.response_map.get(args[0])


	def handler_function(self, player, arg):
		return "{0} success!", arg


	def test_resolve_movement_without_arg(self):
		command = Command(1, 0x9, None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_movement(command, None, "")

		self.assertEqual(("{0} success!", 1), response)


	def test_resolve_movement_with_arg(self):
		command = Command(1, 0x9, None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_movement(command, None, "test")

		self.assertEqual(("Do not give an argument for this command.", "test"), response)


	def test_resolve_switchable_without_arg(self):
		command = Command(1, 0x100, None, self.handler_function, None, "verbose", [], "no", "yes")

		response = self.resolver.resolve_switchable(command, None, "")

		self.assertEqual(("Use the command \"{0}\" with either \"{1}\" or \"{2}\".", ["verbose", "no", "yes"]), response)


	def test_resolve_switchable_with_invalid_arg(self):
		command = Command(1, 0x100, None, self.handler_function, None, "verbose", [], "no", "yes")

		response = self.resolver.resolve_switchable(command, None, "off")

		self.assertEqual(("Use the command \"{0}\" with either \"{1}\" or \"{2}\".", ["verbose", "no", "yes"]), response)


	def test_resolve_switchable_with_switch_arg(self):
		command = Command(1, 0x100, None, self.handler_function, None, "verbose", [], "no", "yes")

		response = self.resolver.resolve_switchable(command, None, "yes")

		self.assertEqual(("{0} success!", True), response)


	def test_resolve_argless_without_arg(self):
		command = Command(1, 0x9, None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_argless(command, None, "")

		self.assertEqual(("{0} success!", ""), response)


	def test_resolve_argless_with_arg(self):
		command = Command(1, 0x9, None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_argless(command, None, "test")

		self.assertEqual(("Do not give an argument for this command.", "test"), response)


	def test_resolve_single_arg_without_arg(self):
		command = Command(1, 0x9, None, self.handler_function, None, "take", [], None, None)
		player = Player(0)

		response = self.resolver.resolve_single_arg(command, player, "")

		self.assertEqual(("What do you want to {0}?", "take"), response)


	def test_resolve_single_arg_without_arg_permissive(self):
		command = Command(1, 0x89, None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_single_arg(command, None, "")

		self.assertEqual(("{0} success!", ""), response)


	def test_resolve_single_arg_with_arg(self):
		command = Command(1, 0x9, None, self.handler_function, None, "take", [], None, None)

		response = self.resolver.resolve_single_arg(command, None, "test")

		self.assertEqual(("{0} success!", "test"), response)


if __name__ == "__main__":
	unittest.main()

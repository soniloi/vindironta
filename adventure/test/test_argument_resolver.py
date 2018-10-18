import unittest
from unittest.mock import Mock

from adventure.argument_resolver import ArgumentResolver
from adventure.command import Command
from adventure.data_collection import DataCollection
from adventure.item import Item
from adventure.player import Player

class TestArgumentResolver(unittest.TestCase):

	def setUp(self):

		data = Mock()
		data.get_response.side_effect = self.responses_side_effect
		data.get_item.side_effect = self.items_side_effect

		self.book = Item(1105, 2, "book", "a book", "a book of fairytales", 2, "The Pied Piper")
		self.item_map = {
			"book" : self.book,
		}

		self.response_map = {
			"reject_carrying" : "You are carrying it.",
			"reject_not_here" : "It is not here.",
			"reject_not_holding" : "You are not holding it.",
			"reject_unknown" : "I do not know what that is.",
			"request_argless" : "Do not give an argument for this command.",
			"request_direct" : "What do you want to {0}?",
			"request_switch" : "Use the command \"{0}\" with either \"{1}\" or \"{2}\".",
		}

		self.resolver = ArgumentResolver()
		self.resolver.init_data(data)


	def items_side_effect(self, *args):
		return self.item_map.get(args[0])


	def responses_side_effect(self, *args):
		return self.response_map.get(args[0])


	def handler_function(self, player, arg):
		return "{0} success!", arg


	def test_resolve_movement_without_arg(self):
		command = Command(1, 0x4, None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_movement(command, None, "")

		self.assertEqual(("{0} success!", 1), response)


	def test_resolve_movement_with_arg(self):
		command = Command(1, 0x4, None, self.handler_function, None, "", [], None, None)

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
		command = Command(1, 0x0, None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_argless(command, None, "")

		self.assertEqual(("{0} success!", ""), response)


	def test_resolve_argless_with_arg(self):
		command = Command(1, 0x0, None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_argless(command, None, "test")

		self.assertEqual(("Do not give an argument for this command.", "test"), response)


	def test_resolve_single_arg_without_arg(self):
		command = Command(1, 0x209, None, self.handler_function, None, "take", [], None, None)
		player = Player(0)

		response = self.resolver.resolve_single_arg(command, player, "")

		self.assertEqual(("What do you want to {0}?", "take"), response)


	def test_resolve_single_arg_without_arg_permissive(self):
		command = Command(1, 0x89, None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_single_arg(command, None, "")

		self.assertEqual(("{0} success!", ""), response)


	def test_resolve_single_arg_with_non_item_arg(self):
		command = Command(1, 0x9, None, self.handler_function, None, "explain", [], None, None)

		response = self.resolver.resolve_single_arg(command, None, "test")

		self.assertEqual(("{0} success!", "test"), response)


	def test_resolve_single_arg_with_item_arg_unknown(self):
		command = Command(1, 0x209, None, self.handler_function, None, "take", [], None, None)

		response = self.resolver.resolve_single_arg(command, None, "test")

		self.assertEqual(("I do not know what that is.", "test"), response)


	def test_resolve_single_arg_with_item_arg_known_needs_inventory_only_and_not_in_inventory(self):
		command = Command(1, 0x20A, None, self.handler_function, None, "drop", [], None, None)
		player = Mock()
		player.is_carrying.return_value = False

		response = self.resolver.resolve_single_arg(command, player, "book")

		self.assertEqual(("You are not holding it.", "book"), response)


	def test_resolve_single_arg_with_item_arg_known_needs_location_only_and_player_carrying(self):
		command = Command(1, 0x20C, None, self.handler_function, None, "take", [], None, None)
		player = Mock()
		player.is_near_item.return_value = False
		player.is_carrying.return_value = True

		response = self.resolver.resolve_single_arg(command, player, "book")

		self.assertEqual(("You are carrying it.", "book"), response)


	def test_resolve_single_arg_with_item_arg_known_needs_inventory_or_location_only_and_player_not_near(self):
		command = Command(1, 0x20E, None, self.handler_function, None, "describe", [], None, None)
		player = Mock()
		player.has_or_is_near_item.return_value = False

		response = self.resolver.resolve_single_arg(command, player, "book")

		self.assertEqual(("It is not here.", "book"), response)


	def test_resolve_single_arg_with_item_arg_known_needs_inventory_or_location_only_and_player_is_near(self):
		command = Command(1, 0x20E, None, self.handler_function, None, "describe", [], None, None)
		player = Mock()
		player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_single_arg(command, player, "book")

		self.assertEqual(("{0} success!", self.book), response)


if __name__ == "__main__":
	unittest.main()

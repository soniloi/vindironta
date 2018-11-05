import unittest
from unittest.mock import Mock

from adventure.argument_resolver import ArgumentResolver
from adventure.command import ArgInfo, Command
from adventure.data_collection import DataCollection
from adventure.data_element import Labels
from adventure.item import Item, SwitchableItem, SwitchInfo
from adventure.player import Player

class TestArgumentResolver(unittest.TestCase):

	def setUp(self):

		data = Mock()
		data.get_response.side_effect = self.responses_side_effect
		data.get_item.side_effect = self.items_side_effect

		self.book = Item(1105, 2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper")
		lamp_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "off", "on")
		self.lamp = SwitchableItem(1043, 0x101A, Labels("lamp", "a lamp", "a small lamp"), 2, None, lamp_switching_info)
		self.item_map = {
			"book" : self.book,
			"lamp" : self.lamp,
		}

		self.response_map = {
			"reject_carrying" : "You are carrying it.",
			"reject_no_understand_instruction" : "I do not understand.",
			"reject_not_here" : "It is not here.",
			"reject_not_holding" : "You are not holding it.",
			"request_switch_item" : "Use \"{0} <{1}|{2}>\".",
			"reject_unknown" : "I do not know what that is.",
			"request_argless" : "Do not give an argument for this command.",
			"request_direct" : "What do you want to {0}?",
			"request_switch_command" : "Use the command \"{0}\" with either \"{1}\" or \"{2}\".",
		}

		self.resolver = ArgumentResolver()
		self.resolver.init_data(data)


	def items_side_effect(self, *args):
		return self.item_map.get(args[0])


	def responses_side_effect(self, *args):
		return self.response_map.get(args[0])


	def handler_function(self, player, arg, next_state=None):
		return "{0} success!", arg


	def test_resolve_movement_without_arg(self):
		command = Command(1, 0x40, [ArgInfo(0x0)], None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_movement(command, None, [])

		self.assertEqual(("{0} success!", 1), response)


	def test_resolve_movement_with_arg(self):
		command = Command(1, 0x40, [ArgInfo(0x1)], None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_movement(command, None, ["test"])

		self.assertEqual(("Do not give an argument for this command.", "test"), response)


	def test_resolve_switchable_without_arg(self):
		command = Command(1, 0x100, [ArgInfo(0x0)], None, self.handler_function, None, "verbose", [], "no", "yes")

		response = self.resolver.resolve_switchable(command, None, [""])

		self.assertEqual(("Use the command \"{0}\" with either \"{1}\" or \"{2}\".", ["verbose", "no", "yes"]), response)


	def test_resolve_switchable_with_invalid_arg(self):
		command = Command(1, 0x100, [ArgInfo(0x1)], None, self.handler_function, None, "verbose", [], "no", "yes")

		response = self.resolver.resolve_switchable(command, None, ["off"])

		self.assertEqual(("Use the command \"{0}\" with either \"{1}\" or \"{2}\".", ["verbose", "no", "yes"]), response)


	def test_resolve_switchable_with_switch_arg(self):
		command = Command(1, 0x100, [ArgInfo(0x1)], None, self.handler_function, None, "verbose", [], "no", "yes")

		response = self.resolver.resolve_switchable(command, None, ["yes"])

		self.assertEqual(("{0} success!", True), response)


	def test_resolve_argless_without_arg(self):
		command = Command(1, 0x0, [ArgInfo(0x0)], None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_argless(command, None, [])

		self.assertEqual(("{0} success!", None), response)


	def test_resolve_argless_with_arg(self):
		command = Command(1, 0x0, [ArgInfo(0x0)], None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_argless(command, None, ["test"])

		self.assertEqual(("Do not give an argument for this command.", "test"), response)


	def test_resolve_args_without_arg(self):
		command = Command(1, 0x9, [ArgInfo(0x1)], None, self.handler_function, None, "take", [], None, None)
		player = Player(0, 0)

		response = self.resolver.resolve_args(command, player, [])

		self.assertEqual(("What do you want to {0}?", "take"), response)


	def test_resolve_args_without_arg_permissive(self):
		command = Command(1, 0x89, [ArgInfo(0x0)], None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_args(command, None, [""])

		self.assertEqual(("{0} success!", ""), response)


	def test_resolve_args_with_non_item_arg(self):
		command = Command(1, 0x9, [ArgInfo(0x1)], None, self.handler_function, None, "explain", [], None, None)

		response = self.resolver.resolve_args(command, None, ["test"])

		self.assertEqual(("{0} success!", "test"), response)


	def test_resolve_args_with_item_arg_unknown(self):
		command = Command(1, 0x9, [ArgInfo(0x3)], None, self.handler_function, None, "take", [], None, None)

		response = self.resolver.resolve_args(command, None, ["test"])

		self.assertEqual(("I do not know what that is.", "test"), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_only_and_player_not_carrying(self):
		command = Command(1, 0x8, [ArgInfo(0xB)], None, self.handler_function, None, "drop", [], None, None)
		player = Mock()
		player.is_carrying.return_value = False

		response = self.resolver.resolve_args(command, player, ["book"])

		self.assertEqual(("You are not holding it.", "book"), response)


	def test_resolve_args_with_item_arg_known_needs_location_only_and_player_is_carrying(self):
		command = Command(1, 0x8, [ArgInfo(0x7)], None, self.handler_function, None, "take", [], None, None)
		player = Mock()
		player.is_carrying.return_value = True

		response = self.resolver.resolve_args(command, player, ["book"])

		self.assertEqual(("You are carrying it.", "book"), response)


	def test_resolve_args_with_item_arg_known_needs_location_only_and_player_not_near(self):
		command = Command(1, 0x8, [ArgInfo(0x7)], None, self.handler_function, None, "take", [], None, None)
		player = Mock()
		player.is_carrying.return_value = False
		player.is_near_item.return_value = False

		response = self.resolver.resolve_args(command, player, ["book"])

		self.assertEqual(("It is not here.", "book"), response)


	def test_resolve_args_with_item_arg_known_needs_location_only_and_player_is_near(self):
		command = Command(1, 0x8, [ArgInfo(0x7)], None, self.handler_function, None, "take", [], None, None)
		player = Mock()
		player.is_carrying.return_value = False
		player.is_near_item.return_value = True

		response = self.resolver.resolve_args(command, player, ["book"])

		self.assertEqual(("{0} success!", self.book), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_or_location_and_player_not_near(self):
		command = Command(1, 0x8, [ArgInfo(0xF)], None, self.handler_function, None, "describe", [], None, None)
		player = Mock()
		player.has_or_is_near_item.return_value = False

		response = self.resolver.resolve_args(command, player, ["book"])

		self.assertEqual(("It is not here.", "book"), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_or_location_and_player_is_near(self):
		command = Command(1, 0x8, [ArgInfo(0xF)], None, self.handler_function, None, "describe", [], None, None)
		player = Mock()
		player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, player, ["book"])

		self.assertEqual(("{0} success!", self.book), response)


	def test_resolve_args_switching_command_not_switchable_item(self):
		command = Command(1, 0x808, [ArgInfo(0xF)], None, self.handler_function, None, "turn", [], None, None)
		player = Mock()
		player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, player, ["book"])

		self.assertEqual(("I do not understand.", "book"), response)


	def test_resolve_args_switching_command_switchable_item_no_next_state(self):
		command = Command(1, 0x808, [ArgInfo(0xF)], None, self.handler_function, None, "turn", [], None, None)
		player = Mock()
		player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, player, ["lamp"])

		self.assertEqual(("Use \"{0} <{1}|{2}>\".", ["lamp", "off", "on"]), response)


	def test_resolve_args_switching_command_switchable_item_invalid_next_state(self):
		command = Command(1, 0x808, [ArgInfo(0xF)], None, self.handler_function, None, "turn", [], None, None)
		player = Mock()
		player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, player, ["lamp", "cinnamon"])

		self.assertEqual(("Use \"{0} <{1}|{2}>\".", ["lamp", "off", "on"]), response)


	def test_resolve_args_switching_command_switchable_item_valid_next_state(self):
		command = Command(1, 0x808, [ArgInfo(0xF)], None, self.handler_function, None, "turn", [], None, None)
		player = Mock()
		player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, player, ["lamp", "off"])

		self.assertEqual(("{0} success!", self.lamp), response)


if __name__ == "__main__":
	unittest.main()

import unittest
from unittest.mock import Mock

from adventure.argument_resolver import ArgumentResolver
from adventure.command import ArgInfo, Command
from adventure.data_collection import DataCollection
from adventure.data_element import Labels
from adventure.item import Item, ContainerItem, SwitchableItem, SwitchInfo

class TestArgumentResolver(unittest.TestCase):

	def setUp(self):

		data = Mock()
		data.get_response.side_effect = self.responses_side_effect
		data.get_item.side_effect = self.items_side_effect

		self.book = Item(1105, 0x2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper")
		self.box = ContainerItem(1106, 0x3, Labels("box", "a box", "a small box"), 3, None)
		lamp_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "off", "on")
		self.lamp = SwitchableItem(1043, 0x101A, Labels("lamp", "a lamp", "a small lamp"), 2, None, lamp_switching_info)
		self.salt = Item(1110, 0x102, Labels("salt", "some salt", "some salt"), 1, None)
		self.item_map = {
			"book" : self.book,
			"box" : self.box,
			"lamp" : self.lamp,
			"salt" : self.salt,
		}

		self.response_map = {
			"reject_carrying" : "You are carrying it.",
			"reject_no_understand_instruction" : "I do not understand.",
			"reject_not_here" : "It is not here.",
			"reject_not_holding" : "You are not holding it.",
			"request_switch_item" : "Use \"{0} <{1}|{2}>\".",
			"reject_unknown" : "I do not know what that is.",
			"request_addinfo" : "What do you want to {0}{1}?",
			"request_argless" : "Do not give an argument for this command.",
			"request_switch_command" : "Use the command \"{0}\" with either \"{1}\" or \"{2}\".",
		}

		self.resolver = ArgumentResolver()
		self.resolver.init_data(data)

		self.player = Mock()
		self.player.get_current_args.return_value = []


	def items_side_effect(self, *args):
		return self.item_map.get(args[0])


	def responses_side_effect(self, *args):
		return self.response_map.get(args[0])


	def handler_function(self, player, arg=None, next_state=None):
		return "{0} success!", arg


	def test_resolve_movement_without_arg(self):
		command = Command(1, 0x40, [ArgInfo(0x0)], None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_movement(command, self.player, [])

		self.assertEqual(("{0} success!", 1), response)


	def test_resolve_movement_with_arg(self):
		command = Command(1, 0x40, [ArgInfo(0x1)], None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_movement(command, self.player, ["test"])

		self.assertEqual(("Do not give an argument for this command.", "test"), response)


	def test_resolve_switchable_without_arg(self):
		command = Command(1, 0x100, [ArgInfo(0x0)], None, self.handler_function, None, "verbose", [], "no", "yes")

		response = self.resolver.resolve_switchable(command, self.player, [""])

		self.assertEqual(("Use the command \"{0}\" with either \"{1}\" or \"{2}\".", ["verbose", "no", "yes"]), response)


	def test_resolve_switchable_with_invalid_arg(self):
		command = Command(1, 0x100, [ArgInfo(0x1)], None, self.handler_function, None, "verbose", [], "no", "yes")

		response = self.resolver.resolve_switchable(command, self.player, ["off"])

		self.assertEqual(("Use the command \"{0}\" with either \"{1}\" or \"{2}\".", ["verbose", "no", "yes"]), response)


	def test_resolve_switchable_with_switch_arg(self):
		command = Command(1, 0x100, [ArgInfo(0x1)], None, self.handler_function, None, "verbose", [], "no", "yes")

		response = self.resolver.resolve_switchable(command, self.player, ["yes"])

		self.assertEqual(("{0} success!", True), response)


	def test_resolve_args_without_arg(self):
		command = Command(1, 0x9, [ArgInfo(0x1)], None, self.handler_function, None, "take", [], None, None)

		response = self.resolver.resolve_args(command, self.player, [])

		self.assertEqual(("What do you want to {0}{1}?", ["take", ""]), response)


	def test_resolve_args_without_arg_permissive(self):
		command = Command(1, 0x89, [ArgInfo(0x0)], None, self.handler_function, None, "", [], None, None)

		response = self.resolver.resolve_args(command, self.player, [""])

		self.assertEqual(("{0} success!", None), response)


	def test_resolve_args_with_non_item_arg(self):
		command = Command(1, 0x9, [ArgInfo(0x1)], None, self.handler_function, None, "explain", [], None, None)

		response = self.resolver.resolve_args(command, self.player, ["test"])

		self.assertEqual(("{0} success!", "test"), response)


	def test_resolve_args_with_item_arg_unknown(self):
		command = Command(1, 0x9, [ArgInfo(0x3)], None, self.handler_function, None, "take", [], None, None)

		response = self.resolver.resolve_args(command, self.player, ["test"])

		self.assertEqual(("I do not know what that is.", "test"), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_only_and_player_not_carrying(self):
		command = Command(1, 0x8, [ArgInfo(0xB)], None, self.handler_function, None, "drop", [], None, None)
		self.player.is_carrying.return_value = False

		response = self.resolver.resolve_args(command, self.player, ["book"])

		self.assertEqual(("You are not holding it.", "book"), response)


	def test_resolve_args_with_item_arg_known_needs_location_only_and_player_is_carrying(self):
		command = Command(1, 0x8, [ArgInfo(0x7)], None, self.handler_function, None, "take", [], None, None)
		self.player.is_carrying.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["book"])

		self.assertEqual(("You are carrying it.", "book"), response)


	def test_resolve_args_with_item_arg_known_needs_location_only_and_player_not_near(self):
		command = Command(1, 0x8, [ArgInfo(0x7)], None, self.handler_function, None, "take", [], None, None)
		self.player.is_carrying.return_value = False
		self.player.is_near_item.return_value = False

		response = self.resolver.resolve_args(command, self.player, ["book"])

		self.assertEqual(("It is not here.", "book"), response)


	def test_resolve_args_with_item_arg_known_needs_location_only_and_player_is_near(self):
		command = Command(1, 0x8, [ArgInfo(0x7)], None, self.handler_function, None, "take", [], None, None)
		self.player.is_carrying.return_value = False
		self.player.is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["book"])

		self.assertEqual(("{0} success!", self.book), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_or_location_and_player_not_near(self):
		command = Command(1, 0x8, [ArgInfo(0xF)], None, self.handler_function, None, "describe", [], None, None)
		self.player.has_or_is_near_item.return_value = False

		response = self.resolver.resolve_args(command, self.player, ["book"])

		self.assertEqual(("It is not here.", "book"), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_or_location_and_player_is_near(self):
		command = Command(1, 0x8, [ArgInfo(0xF)], None, self.handler_function, None, "describe", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["book"])

		self.assertEqual(("{0} success!", self.book), response)


	def test_resolve_args_multiple_items_all_valid(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF)], None, self.handler_function, None, "insert", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["book", "box"])

		self.assertEqual(("{0} success!", self.book), response)
		self.player.reset_current_command.assert_called_once()


	def test_resolve_args_multiple_items_second_invalid(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF)], None, self.handler_function, None, "insert", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["book", "blah"])

		self.assertEqual(("I do not know what that is.", "blah"), response)
		self.player.reset_current_command.assert_called_once()


	def test_resolve_args_multiple_missing_arg_without_link_info(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF)], None, self.handler_function, None, "insert", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["book"])

		self.assertEqual(("What do you want to {0}{1}?", ["insert", " book"]), response)
		self.player.reset_current_command.assert_not_called()


	def test_resolve_args_multiple_missing_arg_with_link_info_linker_implicit(self):
		arg_infos = [ArgInfo(0xF), ArgInfo(0xF, ["into", "in", "to"])]
		command = Command(1, 0x8, arg_infos, None, self.handler_function, None, "insert", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["book"])

		self.assertEqual(("What do you want to {0}{1}?", ["insert", " book into"]), response)
		self.player.reset_current_command.assert_not_called()


	def test_resolve_args_multiple_missing_arg_with_link_info_linker_explicit(self):
		arg_infos = [ArgInfo(0xF), ArgInfo(0xF, ["into", "in", "to"])]
		command = Command(1, 0x8, arg_infos, None, self.handler_function, None, "insert", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["book", "to"])

		self.assertEqual(("What do you want to {0}{1}?", ["insert", " book to"]), response)
		self.player.reset_current_command.assert_not_called()


	def test_resolve_args_multiple_missing_arg_with_link_info_three_args(self):
		arg_infos = [ArgInfo(0xF), ArgInfo(0xF, ["into", "in", "to"]), ArgInfo(0xB, ["using"])]
		command = Command(1, 0x8, arg_infos, None, self.handler_function, None, "scoop", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["salt", "box"])

		self.assertEqual(("What do you want to {0}{1}?", ["scoop", " salt into box using"]), response)
		self.player.reset_current_command.assert_not_called()


	def test_resolve_args_multiple_first_resolved(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF)], None, self.handler_function, None, "insert", [], None, None)
		self.player.get_current_args.return_value = [self.book]
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["box"])

		self.assertEqual(("{0} success!", self.book), response)


	def test_resolve_args_multiple_items_all_valid_with_invalid_linker(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF, ["into", "in"])], None, self.handler_function, None, "insert", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["book", "the", "box"])

		self.assertEqual(("I do not know what that is.", "the"), response)
		self.player.reset_current_command.assert_called_once()


	def test_resolve_args_multiple_items_all_valid_with_valid_linker(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF, ["into", "in"])], None, self.handler_function, None, "insert", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["book", "into", "box"])

		self.assertEqual(("{0} success!", self.book), response)
		self.player.reset_current_command.assert_called_once()


	def test_resolve_args_switching_command_not_switchable_item(self):
		command = Command(1, 0x808, [ArgInfo(0xF)], None, self.handler_function, None, "turn", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["book"])

		self.assertEqual(("I do not understand.", "book"), response)


	def test_resolve_args_switching_command_switchable_item_no_next_state(self):
		command = Command(1, 0x808, [ArgInfo(0xF)], None, self.handler_function, None, "turn", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["lamp"])

		self.assertEqual(("Use \"{0} <{1}|{2}>\".", ["lamp", "off", "on"]), response)


	def test_resolve_args_switching_command_switchable_item_invalid_next_state(self):
		command = Command(1, 0x808, [ArgInfo(0xF)], None, self.handler_function, None, "turn", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["lamp", "cinnamon"])

		self.assertEqual(("Use \"{0} <{1}|{2}>\".", ["lamp", "off", "on"]), response)


	def test_resolve_args_switching_command_switchable_item_valid_next_state(self):
		command = Command(1, 0x808, [ArgInfo(0xF), ArgInfo(0x0)], None, self.handler_function, None, "turn", [], None, None)
		self.player.has_or_is_near_item.return_value = True

		response = self.resolver.resolve_args(command, self.player, ["lamp", "off"])

		self.assertEqual(("{0} success!", self.lamp), response)


if __name__ == "__main__":
	unittest.main()

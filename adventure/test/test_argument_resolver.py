import unittest
from unittest.mock import Mock

from adventure.argument_resolver import ArgumentResolver
from adventure.command import ArgInfo, Command
from adventure.data_collection import DataCollection
from adventure.direction import Direction
from adventure.element import Labels
from adventure.item import Item, ContainerItem, SwitchableItem, SwitchInfo, SwitchTransition

class TestArgumentResolver(unittest.TestCase):

	def setUp(self):
		self.setup_data()
		self.setup_player()
		self.resolver = ArgumentResolver()
		self.resolver.init_data(self.data)


	def setup_data(self):
		self.data = Mock()
		self.setup_items()
		self.setup_responses()


	def setup_items(self):
		self.book = Item(1105, 0x2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper")
		self.box = ContainerItem(1106, 0x3, Labels("box", "a box", "a small box"), 3, None)
		lamp_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "off", "on")
		self.lamp = SwitchableItem(1043, 0x101A, Labels("lamp", "a lamp", "a small lamp"), 2, None, lamp_switching_info)
		self.salt = Item(1110, 0x102, Labels("salt", "some salt", "some salt"), 1, None)

		self.data.get_item_by_name.side_effect = lambda x: {
			"book" : self.book,
			"box" : self.box,
			"lamp" : self.lamp,
			"salt" : self.salt,
		}.get(x)


	def setup_responses(self):
		self.data.get_response.side_effect = lambda x: {
			"reject_carrying" : "You are carrying it.",
			"reject_no_back" : "I do not remember how you got here.",
			"reject_no_direction" : "You cannot go that way.",
			"reject_no_out" : "I cannot tell in from out here.",
			"reject_no_understand_instruction" : "I do not understand.",
			"reject_not_here" : "It is not here.",
			"reject_not_holding" : "You are not holding it.",
			"reject_nothing" : "Nothing happens.",
			"request_switch_item" : "Use \"{0} <{1}|{2}>\".",
			"reject_unknown" : "I do not know what that is.",
			"request_addinfo" : "What do you want to {0}{1}?",
			"request_argless" : "Do not give an argument for this command.",
			"request_switch_command" : "Use the command \"{0}\" with either \"{1}\" or \"{2}\".",
		}.get(x)


	def setup_player(self):
		self.player = Mock()
		self.player.get_current_args.return_value = []


	def test_resolve_teleport_with_arg(self):
		teleport_info = {23 : 24, 26 : 23}
		command = Command(1, 0x12, [], [], [""], {}, teleport_info)

		response = self.resolver.resolve_teleport(command, self.player, "test")

		self.assertEqual((False, "Do not give an argument for this command.", ["test"], []), response)


	def test_resolve_teleport_without_matching_source(self):
		teleport_info = {23 : 24, 26 : 23}
		self.player.get_location_id.return_value = 1
		command = Command(1, 0x12, [], [], [""], {}, teleport_info)

		response = self.resolver.resolve_teleport(command, self.player)

		self.assertEqual((False, "Nothing happens.", [None], []), response)


	def test_resolve_teleport_with_matching_source(self):
		teleport_info = {23 : 24, 26 : 23}
		self.player.get_location_id.return_value = 26
		destination = Mock()
		self.data.get_location.return_value = destination
		command = Command(1, 0x12, [], [], [""], {}, teleport_info)

		response = self.resolver.resolve_teleport(command, self.player)

		self.assertEqual((True, "", [], [destination]), response)


	def test_resolve_movement_with_arg(self):
		command = Command(1, 0x40, [ArgInfo(0x1)], [], [""], {}, {})

		response = self.resolver.resolve_movement(command, self.player, "test")

		self.assertEqual((False, "Do not give an argument for this command.", ["test"], []), response)


	def test_resolve_movement_back_without_destination(self):
		command = Command(5, 0x40, [ArgInfo(0x0)], [], [""], {}, {})
		self.player.get_previous_location.return_value = None

		response = self.resolver.resolve_movement(command, self.player)

		self.assertEqual((False, "I do not remember how you got here.", [Direction.BACK], []), response)


	def test_resolve_movement_back_with_destination(self):
		command = Command(5, 0x40, [ArgInfo(0x0)], [], [""], {}, {})
		proposed_location = Mock()
		self.player.get_previous_location.return_value = proposed_location

		response = self.resolver.resolve_movement(command, self.player)

		self.assertEqual((True, "", [], [proposed_location]), response)


	def test_resolve_movement_out_without_destination(self):
		command = Command(37, 0x40, [ArgInfo(0x0)], [], [""], {}, {})
		self.player.get_adjacent_location.return_value = None

		response = self.resolver.resolve_movement(command, self.player)

		self.assertEqual((False, "I cannot tell in from out here.", [Direction.OUT], []), response)


	def test_resolve_movement_out_with_destination(self):
		command = Command(37, 0x40, [ArgInfo(0x0)], [], [""], {}, {})
		proposed_location = Mock()
		self.player.get_adjacent_location.return_value = proposed_location

		response = self.resolver.resolve_movement(command, self.player)

		self.assertEqual((True, "", [], [proposed_location]), response)


	def test_resolve_movement_non_back_non_out_without_destination(self):
		command = Command(34, 0x40, [ArgInfo(0x0)], [], [""], {}, {})
		self.player.get_adjacent_location.return_value = None

		response = self.resolver.resolve_movement(command, self.player)

		self.assertEqual((False, "You cannot go that way.", [Direction.NORTH], []), response)


	def test_resolve_movement_non_back_non_out_with_destination(self):
		command = Command(34, 0x40, [ArgInfo(0x0)], [], [""], {}, {})
		proposed_location = Mock()
		self.player.get_adjacent_location.return_value = proposed_location

		response = self.resolver.resolve_movement(command, self.player)

		self.assertEqual((True, "", [], [proposed_location]), response)


	def test_resolve_switchable_without_arg(self):
		switch_info = {"no" : False, "yes" : True}
		command = Command(1, 0x100, [ArgInfo(0x0)], [], ["verbose"], switch_info, {})

		response = self.resolver.resolve_switchable(command, self.player)

		self.assertEqual((False, "Use the command \"{0}\" with either \"{1}\" or \"{2}\".", ["verbose", "no", "yes"], []), response)


	def test_resolve_switchable_with_invalid_arg(self):
		switch_info = {"no" : False, "yes" : True}
		command = Command(1, 0x100, [ArgInfo(0x1)], [], ["verbose"], switch_info, {})

		response = self.resolver.resolve_switchable(command, self.player, "off")

		self.assertEqual((False, "Use the command \"{0}\" with either \"{1}\" or \"{2}\".", ["verbose", "no", "yes"], []), response)


	def test_resolve_switchable_with_switch_arg(self):
		switch_info = {"no" : False, "yes" : True}
		command = Command(1, 0x100, [ArgInfo(0x1)], [], ["verbose"], switch_info, {})

		response = self.resolver.resolve_switchable(command, self.player, "yes")

		self.assertEqual((True, "", [], [True]), response)


	def test_resolve_args_without_arg(self):
		command = Command(1, 0x9, [ArgInfo(0x1)], [], ["take"], {}, {})

		response = self.resolver.resolve_args(command, self.player)

		self.assertEqual((False, "What do you want to {0}{1}?", ["take", ""], []), response)


	def test_resolve_args_without_arg_permissive(self):
		command = Command(1, 0x89, [ArgInfo(0x0)], [], [""], {}, {})

		response = self.resolver.resolve_args(command, self.player)

		self.assertEqual((True, "", [], []), response)


	def test_resolve_args_with_non_item_arg(self):
		command = Command(1, 0x9, [ArgInfo(0x1)], [], ["explain"], {}, {})

		response = self.resolver.resolve_args(command, self.player, "test")

		self.assertEqual((True, "", [], ["test"]), response)


	def test_resolve_args_with_item_arg_unknown(self):
		command = Command(1, 0x9, [ArgInfo(0x3)], [], ["take"], {}, {})

		response = self.resolver.resolve_args(command, self.player, "test")

		self.assertEqual((False, "I do not know what that is.", ["test"], []), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_only_and_player_not_carrying(self):
		command = Command(1, 0x8, [ArgInfo(0xB)], [], ["drop"], {}, {})
		self.player.get_carried_item.return_value = None
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((False, "You are not holding it.", ["book"], []), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_only_and_player_is_carrying(self):
		command = Command(1, 0x8, [ArgInfo(0xB)], [], ["drop"], {}, {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((True, "", [], [self.book]), response)


	def test_resolve_args_with_item_arg_known_needs_location_only_and_player_is_carrying(self):
		command = Command(1, 0x8, [ArgInfo(0x7)], [], ["take"], {}, {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((False, "You are carrying it.", ["book"], []), response)


	def test_resolve_args_with_item_arg_known_needs_location_only_and_player_not_near(self):
		command = Command(1, 0x8, [ArgInfo(0x7)], [], ["take"], {}, {})
		self.player.get_carried_item.return_value = None
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((False, "It is not here.", ["book"], []), response)


	def test_resolve_args_with_item_arg_known_needs_location_only_and_player_is_near(self):
		command = Command(1, 0x8, [ArgInfo(0x7)], [], ["take"], {}, {})
		self.player.get_carried_item.return_value = None
		self.player.get_nearby_item.return_value = self.book

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((True, "", [], [self.book]), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_or_location_and_player_not_near(self):
		command = Command(1, 0x8, [ArgInfo(0xF)], [], ["describe"], {}, {})
		self.player.get_carried_item.return_value = None
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((False, "It is not here.", ["book"], []), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_or_location_and_player_is_carrying(self):
		command = Command(1, 0x8, [ArgInfo(0xF)], [], ["describe"], {}, {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((True, "", [], [self.book]), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_or_location_and_player_is_near(self):
		command = Command(1, 0x8, [ArgInfo(0xF)], [], ["describe"], {}, {})
		self.player.get_carried_item.return_value = None
		self.player.get_nearby_item.return_value = self.book

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((True, "", [], [self.book]), response)


	def test_resolve_args_multiple_items_all_valid(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF)], [], ["insert"], {}, {})
		self.player.get_carried_item.side_effect = [self.book, self.box]
		self.player.get_nearby_item.side_effect = [None, None]

		response = self.resolver.resolve_args(command, self.player, "book", "box")

		self.assertEqual((True, "", [], [self.book, self.box]), response)
		self.player.reset_current_command.assert_called_once()


	def test_resolve_args_multiple_items_second_invalid(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF)], [], ["insert"], {}, {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book", "blah")

		self.assertEqual((False, "I do not know what that is.", ["blah"], []), response)
		self.player.reset_current_command.assert_called_once()


	def test_resolve_args_multiple_missing_arg_without_link_info(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF)], [], ["insert"], {}, {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((False, "What do you want to {0}{1}?", ["insert", " book"], []), response)
		self.player.reset_current_command.assert_not_called()


	def test_resolve_args_multiple_missing_arg_with_link_info_linker_implicit(self):
		arg_infos = [ArgInfo(0xF), ArgInfo(0xF, ["into", "in", "to"])]
		command = Command(1, 0x8, arg_infos, [], ["insert"], {}, {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((False, "What do you want to {0}{1}?", ["insert", " book into"], []), response)
		self.player.reset_current_command.assert_not_called()


	def test_resolve_args_multiple_missing_arg_with_link_info_linker_explicit(self):
		arg_infos = [ArgInfo(0xF), ArgInfo(0xF, ["into", "in", "to"])]
		command = Command(1, 0x8, arg_infos, [], ["insert"], {}, {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book", "to")

		self.assertEqual((False, "What do you want to {0}{1}?", ["insert", " book to"], []), response)
		self.player.reset_current_command.assert_not_called()


	def test_resolve_args_multiple_permissive_with_linker_explicit(self):
		command = Command(1, 0x9, [ArgInfo(0x7), ArgInfo(0xA, ["in"])], [], ["take"], {}, {})
		self.player.get_carried_item.return_value = None
		self.player.get_nearby_item.return_value = self.book

		response = self.resolver.resolve_args(command, self.player, "book", "in")

		self.assertEqual((False, "What do you want to {0}{1}?", ["take", " book in"], []), response)


	def test_resolve_args_multiple_missing_arg_with_link_info_three_args(self):
		arg_infos = [ArgInfo(0xF), ArgInfo(0xF, ["into", "in", "to"]), ArgInfo(0xB, ["using"])]
		command = Command(1, 0x8, arg_infos, [], ["scoop"], {}, {})
		self.player.get_carried_item.side_effect = [self.salt, self.box]
		self.player.get_nearby_item.side_effect = [None, None]

		response = self.resolver.resolve_args(command, self.player, "salt", "box")

		self.assertEqual((False, "What do you want to {0}{1}?", ["scoop", " salt into box using"], []), response)
		self.player.reset_current_command.assert_not_called()


	def test_resolve_args_multiple_first_resolved(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF)], [], ["insert"], {}, {})
		self.player.get_current_args.return_value = [self.book]
		self.player.get_carried_item.return_value = self.box
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "box")

		self.assertEqual((True, "", [], [self.book, self.box]), response)


	def test_resolve_args_multiple_items_all_valid_with_invalid_linker(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF, ["into", "in"])], [], ["insert"], {}, {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book", "the", "box")

		self.assertEqual((False, "I do not know what that is.", ["the"], []), response)
		self.player.reset_current_command.assert_called_once()


	def test_resolve_args_multiple_items_all_valid_with_valid_linker(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF, ["into", "in"])], [], ["insert"], {}, {})
		self.player.get_carried_item.side_effect = [self.book, self.box]
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book", "into", "box")

		self.assertEqual((True, "", [], [self.book, self.box]), response)
		self.player.reset_current_command.assert_called_once()


	def test_resolve_args_switching_command_not_switchable_item(self):
		command = Command(1, 0x208, [ArgInfo(0xF)], [], ["turn"], {}, {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_switching(command, self.player, "book")

		self.assertEqual((False, "I do not understand.", ["book"], []), response)


	def test_resolve_args_switching_command_switchable_item_no_next_state(self):
		command = Command(1, 0x208, [ArgInfo(0xF)], [], ["turn"], {}, {})
		self.player.get_carried_item.return_value = self.lamp
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_switching(command, self.player, "lamp")

		self.assertEqual((False, "Use \"{0} <{1}|{2}>\".", ["lamp", "off", "on"], []), response)


	def test_resolve_args_switching_command_switchable_item_invalid_next_state(self):
		command = Command(1, 0x208, [ArgInfo(0xF)], [], ["turn"], {}, {})
		self.player.get_carried_item.return_value = self.lamp
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_switching(command, self.player, "lamp", "cinnamon")

		self.assertEqual((False, "Use \"{0} <{1}|{2}>\".", ["lamp", "off", "on"], []), response)


	def test_resolve_args_switching_command_switchable_item_valid_next_state(self):
		command = Command(1, 0x208, [ArgInfo(0xF), ArgInfo(0x0)], [], ["turn"], {}, {})
		self.player.get_carried_item.return_value = self.lamp
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_switching(command, self.player, "lamp", "off")

		self.assertEqual((True, "", [], [self.lamp, SwitchTransition.OFF]), response)


if __name__ == "__main__":
	unittest.main()

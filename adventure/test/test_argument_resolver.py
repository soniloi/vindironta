import unittest
from unittest.mock import Mock

from adventure.argument_resolver import ArgumentResolver
from adventure.command import ArgInfo, Command
from adventure.data_collection import DataCollection
from adventure.direction import Direction
from adventure.element import Labels
from adventure.item import Item, ContainerItem, SwitchableItem, SwitchInfo, SwitchTransition
from adventure.location import Location

class TestArgumentResolver(unittest.TestCase):

	def setUp(self):
		self.setup_data()
		self.setup_player()
		self.resolver = ArgumentResolver()
		self.resolver.init_data(self.data)


	def setup_data(self):
		self.data = Mock()
		self.setup_locations()
		self.setup_items()


	def setup_locations(self):
		self.beach_location = Location(13, 0x603, Labels("Beach", "on a beach", " of black sand"))
		self.lighthouse_location = Location(12, 0x603, Labels("Lighthouse", "at a lighthouse", " by the sea."))


	def setup_items(self):
		self.book = Item(1105, 0x2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper", {})
		self.box = ContainerItem(1106, 0x3, Labels("box", "a box", "a small box"), 3, None, {})
		lamp_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "off", "on")
		self.lamp = SwitchableItem(1043, 0x101A, Labels("lamp", "a lamp", "a small lamp"), 2, None, {}, lamp_switching_info)
		self.salt = Item(1110, 0x102, Labels("salt", "some salt", "some salt"), 1, None, {})

		self.data.get_item_list_by_name.side_effect = lambda x: {
			"book" : [self.book],
			"box" : [self.box],
			"lamp" : [self.lamp],
			"salt" : [self.salt],
		}.get(x)


	def setup_player(self):
		self.player = Mock()
		self.player.get_current_args.return_value = []


	def test_resolve_teleport_with_arg(self):
		command = Command(1, 0x12, [], [], [""], {})
		command.teleport_info[6] = self.lighthouse_location
		command.teleport_info[7] = self.beach_location

		response = self.resolver.resolve_teleport(command, self.player, "test")

		self.assertEqual((False, ["request_argless"], ["test"], []), response)


	def test_resolve_teleport_without_matching_source(self):
		self.player.get_location_id.return_value = 1
		command = Command(1, 0x12, [], [], [""], {})
		command.teleport_info[6] = self.lighthouse_location
		command.teleport_info[7] = self.beach_location

		response = self.resolver.resolve_teleport(command, self.player)

		self.assertEqual((False, ["reject_nothing"], [None], []), response)


	def test_resolve_teleport_with_matching_source(self):
		self.player.get_location_id.return_value = 6
		command = Command(1, 0x12, [], [], [""], {})
		command.teleport_info[6] = self.lighthouse_location
		command.teleport_info[7] = self.beach_location

		response = self.resolver.resolve_teleport(command, self.player)

		self.assertEqual((True, [], [], [self.lighthouse_location]), response)


	def test_resolve_movement_with_arg(self):
		command = Command(1, 0x40, [ArgInfo(0x1)], [], [""], {})

		response = self.resolver.resolve_movement(command, self.player, "test")

		self.assertEqual((False, ["request_argless"], ["test"], []), response)


	def test_resolve_movement_back_without_destination(self):
		command = Command(5, 0x40, [ArgInfo(0x0)], [], [""], {})
		self.player.get_previous_location.return_value = None

		response = self.resolver.resolve_movement(command, self.player)

		self.assertEqual((False, ["reject_movement_no_back"], [Direction.BACK], []), response)


	def test_resolve_movement_back_with_destination(self):
		command = Command(5, 0x40, [ArgInfo(0x0)], [], [""], {})
		proposed_location = Mock()
		self.player.get_previous_location.return_value = proposed_location

		response = self.resolver.resolve_movement(command, self.player)

		self.assertEqual((True, [], [], [Direction.BACK, proposed_location]), response)


	def test_resolve_movement_out_without_destination(self):
		command = Command(37, 0x40, [ArgInfo(0x0)], [], [""], {})
		self.player.get_adjacent_location.return_value = None

		response = self.resolver.resolve_movement(command, self.player)

		self.assertEqual((False, ["reject_movement_no_out"], [Direction.OUT], []), response)


	def test_resolve_movement_out_with_destination(self):
		command = Command(37, 0x40, [ArgInfo(0x0)], [], [""], {})
		proposed_location = Mock()
		self.player.get_adjacent_location.return_value = proposed_location

		response = self.resolver.resolve_movement(command, self.player)

		self.assertEqual((True, [], [], [Direction.OUT, proposed_location]), response)


	def test_resolve_movement_non_back_non_out_without_destination(self):
		command = Command(34, 0x40, [ArgInfo(0x0)], [], [""], {})
		self.player.get_adjacent_location.return_value = None

		response = self.resolver.resolve_movement(command, self.player)

		self.assertEqual((False, ["reject_movement_no_direction"], [Direction.NORTH], []), response)


	def test_resolve_movement_non_back_non_out_with_destination(self):
		command = Command(34, 0x40, [ArgInfo(0x0)], [], [""], {})
		proposed_location = Mock()
		self.player.get_adjacent_location.return_value = proposed_location

		response = self.resolver.resolve_movement(command, self.player)

		self.assertEqual((True, [], [], [Direction.NORTH, proposed_location]), response)


	def test_resolve_switchable_without_arg(self):
		switch_info = {"no" : False, "yes" : True}
		command = Command(1, 0x100, [ArgInfo(0x0)], [], ["verbose"], switch_info)

		response = self.resolver.resolve_switchable(command, self.player)

		self.assertEqual((False, ["request_switch_command"], ["verbose", "no", "yes"], []), response)


	def test_resolve_switchable_with_invalid_arg(self):
		switch_info = {"no" : False, "yes" : True}
		command = Command(1, 0x100, [ArgInfo(0x1)], [], ["verbose"], switch_info)

		response = self.resolver.resolve_switchable(command, self.player, "off")

		self.assertEqual((False, ["request_switch_command"], ["verbose", "no", "yes"], []), response)


	def test_resolve_switchable_with_switch_arg(self):
		switch_info = {"no" : False, "yes" : True}
		command = Command(1, 0x100, [ArgInfo(0x1)], [], ["verbose"], switch_info)

		response = self.resolver.resolve_switchable(command, self.player, "yes")

		self.assertEqual((True, [], [], [True]), response)


	def test_resolve_args_without_arg(self):
		command = Command(1, 0x9, [ArgInfo(0x1)], [], ["take"], {})

		response = self.resolver.resolve_args(command, self.player)

		self.assertEqual((False, ["request_addinfo"], ["take", ""], []), response)


	def test_resolve_args_without_arg_permissive(self):
		command = Command(1, 0x89, [ArgInfo(0x0)], [], [""], {})

		response = self.resolver.resolve_args(command, self.player)

		self.assertEqual((True, [], [], []), response)


	def test_resolve_args_with_non_item_arg(self):
		command = Command(1, 0x9, [ArgInfo(0x1)], [], ["explain"], {})

		response = self.resolver.resolve_args(command, self.player, "test")

		self.assertEqual((True, [], [], ["test"]), response)


	def test_resolve_args_with_item_arg_unknown(self):
		command = Command(1, 0x9, [ArgInfo(0x3)], [], ["take"], {})

		response = self.resolver.resolve_args(command, self.player, "test")

		self.assertEqual((False, ["reject_unknown"], ["test"], []), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_only_and_player_not_carrying(self):
		command = Command(1, 0x8, [ArgInfo(0xB)], [], ["drop"], {})
		self.player.get_carried_item.return_value = None
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((False, ["reject_not_holding"], ["book"], []), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_only_and_player_is_carrying(self):
		command = Command(1, 0x8, [ArgInfo(0xB)], [], ["drop"], {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((True, [], [], [self.book]), response)


	def test_resolve_args_with_item_arg_known_needs_location_only_and_player_is_carrying(self):
		command = Command(1, 0x8, [ArgInfo(0x7)], [], ["take"], {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((False, ["reject_carrying"], ["take", "book"], []), response)


	def test_resolve_args_with_item_arg_known_needs_location_only_and_player_not_near(self):
		command = Command(1, 0x8, [ArgInfo(0x7)], [], ["take"], {})
		self.player.get_carried_item.return_value = None
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((False, ["reject_not_here"], ["book"], []), response)


	def test_resolve_args_with_item_arg_known_needs_location_only_and_player_is_near(self):
		command = Command(1, 0x8, [ArgInfo(0x7)], [], ["take"], {})
		self.player.get_carried_item.return_value = None
		self.player.get_nearby_item.return_value = self.book

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((True, [], [], [self.book]), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_or_location_and_player_not_near(self):
		command = Command(1, 0x8, [ArgInfo(0xF)], [], ["describe"], {})
		self.player.get_carried_item.return_value = None
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((False, ["reject_not_here"], ["book"], []), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_or_location_and_player_is_carrying(self):
		command = Command(1, 0x8, [ArgInfo(0xF)], [], ["describe"], {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((True, [], [], [self.book]), response)


	def test_resolve_args_with_item_arg_known_needs_inventory_or_location_and_player_is_near(self):
		command = Command(1, 0x8, [ArgInfo(0xF)], [], ["describe"], {})
		self.player.get_carried_item.return_value = None
		self.player.get_nearby_item.return_value = self.book

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((True, [], [], [self.book]), response)


	def test_resolve_args_multiple_items_all_valid(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF)], [], ["insert"], {})
		self.player.get_carried_item.side_effect = [self.book, self.box]
		self.player.get_nearby_item.side_effect = [None, None]

		response = self.resolver.resolve_args(command, self.player, "book", "box")

		self.assertEqual((True, [], [], [self.book, self.box]), response)
		self.player.reset_current_command.assert_called_once()


	def test_resolve_args_multiple_items_second_invalid(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF)], [], ["insert"], {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book", "blah")

		self.assertEqual((False, ["reject_unknown"], ["blah"], []), response)
		self.player.reset_current_command.assert_called_once()


	def test_resolve_args_multiple_missing_arg_without_link_info(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF)], [], ["insert"], {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((False, ["request_addinfo"], ["insert", " book"], []), response)
		self.player.reset_current_command.assert_not_called()


	def test_resolve_args_multiple_missing_arg_with_link_info_linker_implicit(self):
		arg_infos = [ArgInfo(0xF), ArgInfo(0xF, ["into", "in", "to"])]
		command = Command(1, 0x8, arg_infos, [], ["insert"], {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book")

		self.assertEqual((False, ["request_addinfo"], ["insert", " book into"], []), response)
		self.player.reset_current_command.assert_not_called()


	def test_resolve_args_multiple_missing_arg_with_link_info_linker_explicit(self):
		arg_infos = [ArgInfo(0xF), ArgInfo(0xF, ["into", "in", "to"])]
		command = Command(1, 0x8, arg_infos, [], ["insert"], {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book", "to")

		self.assertEqual((False, ["request_addinfo"], ["insert", " book to"], []), response)
		self.player.reset_current_command.assert_not_called()


	def test_resolve_args_multiple_permissive_with_linker_explicit(self):
		command = Command(1, 0x9, [ArgInfo(0x7), ArgInfo(0xA, ["in"])], [], ["take"], {})
		self.player.get_carried_item.return_value = None
		self.player.get_nearby_item.return_value = self.book

		response = self.resolver.resolve_args(command, self.player, "book", "in")

		self.assertEqual((False, ["request_addinfo"], ["take", " book in"], []), response)


	def test_resolve_args_multiple_missing_arg_with_link_info_three_args(self):
		arg_infos = [ArgInfo(0xF), ArgInfo(0xF, ["into", "in", "to"]), ArgInfo(0xB, ["using"])]
		command = Command(1, 0x8, arg_infos, [], ["scoop"], {})
		self.player.get_carried_item.side_effect = [self.salt, self.box]
		self.player.get_nearby_item.side_effect = [None, None]

		response = self.resolver.resolve_args(command, self.player, "salt", "box")

		self.assertEqual((False, ["request_addinfo"], ["scoop", " salt into box using"], []), response)
		self.player.reset_current_command.assert_not_called()


	def test_resolve_args_multiple_first_resolved(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF)], [], ["insert"], {})
		self.player.get_current_args.return_value = [self.book]
		self.player.get_carried_item.return_value = self.box
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "box")

		self.assertEqual((True, [], [], [self.book, self.box]), response)


	def test_resolve_args_multiple_items_all_valid_with_invalid_linker(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF, ["into", "in"])], [], ["insert"], {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book", "the", "box")

		self.assertEqual((False, ["reject_unknown"], ["the"], []), response)
		self.player.reset_current_command.assert_called_once()


	def test_resolve_args_multiple_items_all_valid_with_valid_linker(self):
		command = Command(1, 0x8, [ArgInfo(0xF), ArgInfo(0xF, ["into", "in"])], [], ["insert"], {})
		self.player.get_carried_item.side_effect = [self.book, self.box]
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_args(command, self.player, "book", "into", "box")

		self.assertEqual((True, [], [], [self.book, self.box]), response)
		self.player.reset_current_command.assert_called_once()


	def test_resolve_args_switching_command_not_switchable_item(self):
		command = Command(1, 0x208, [ArgInfo(0xF)], [], ["turn"], {})
		self.player.get_carried_item.return_value = self.book
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_switching(command, self.player, "book")

		self.assertEqual((False, ["reject_no_understand_instruction"], ["book"], []), response)


	def test_resolve_args_switching_command_switchable_item_no_next_state(self):
		command = Command(1, 0x208, [ArgInfo(0xF)], [], ["turn"], {})
		self.player.get_carried_item.return_value = self.lamp
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_switching(command, self.player, "lamp")

		self.assertEqual((False, ["request_switch_item"], ["lamp", "off", "on"], []), response)


	def test_resolve_args_switching_command_switchable_item_invalid_next_state(self):
		command = Command(1, 0x208, [ArgInfo(0xF)], [], ["turn"], {})
		self.player.get_carried_item.return_value = self.lamp
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_switching(command, self.player, "lamp", "cinnamon")

		self.assertEqual((False, ["request_switch_item"], ["lamp", "off", "on"], []), response)


	def test_resolve_args_switching_command_switchable_item_valid_next_state(self):
		command = Command(1, 0x208, [ArgInfo(0xF), ArgInfo(0x0)], [], ["turn"], {})
		self.player.get_carried_item.return_value = self.lamp
		self.player.get_nearby_item.return_value = None

		response = self.resolver.resolve_switching(command, self.player, "lamp", "off")

		self.assertEqual((True, [], [], [self.lamp, SwitchTransition.OFF]), response)


if __name__ == "__main__":
	unittest.main()

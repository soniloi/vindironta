import unittest
from unittest.mock import Mock

from adventure.command import Command
from adventure.command_handler import CommandHandler
from adventure.direction import Direction
from adventure.item import Item
from adventure.location import Location
from adventure.player import Player

class TestCommandHandler(unittest.TestCase):

	def setUp(self):
		self.setup_data()
		self.setup_locations()
		self.setup_items()
		self.setup_texts()
		self.setup_player()

		self.handler = CommandHandler()
		self.handler.init_data(self.data)


	def setup_data(self):
		self.data = Mock()
		self.data.list_commands.side_effect = self.list_commands_side_effect
		self.data.get_location.side_effect = self.locations_side_effect
		self.data.get_item.side_effect = self.items_side_effect
		self.data.get_hint.side_effect = self.hints_side_effect
		self.data.get_explanation.side_effect = self.explanations_side_effect
		self.data.get_response.side_effect = self.responses_side_effect


	def setup_locations(self):
		self.beach_location = Location(13, 0x1, "Beach", "on a beach", " of black sand")
		self.lighthouse_location = Location(12, 0x1, "Lighthouse", "at a lighthouse", " by the sea.")
		self.mine_location = Location(11, 0x0, "Mines", "in the mines", ". There are dark passages everywhere.")
		self.sun_location = Location(10, 0x11, "Sun", "in the sun", ". It is hot.")

		self.location_map = {
			11 : self.mine_location,
			12 : self.lighthouse_location,
			13 : self.beach_location,
		}


	def setup_items(self):
		self.book = Item(1105, 2, "book", "a book", "a book of fairytales", 2, "The Pied Piper")
		self.lamp = Item(1043, 0x101A, "lamp", "a lamp", "a small lamp", 2, None)
		self.kohlrabi = Item(1042, 0x2002, "kohlrabi", "some kohlrabi", "some kohlrabi, a cabbage cultivar", 3, None)
		self.desk = Item(1000, 0x0, "desk", "a desk", "a large mahogany desk", 6, None)
		self.heavy_item = Item(1001, 0x0, "heavy", "a heavy item", "a dummy heavy item", 15, None)
		self.obstruction = Item(1002, 0x4, "obstruction", "an obstruction", "an obstruction blocking you", 8, None)
		self.mobile_obstruction = Item(1003, 0x6, "mobile_obstruction", "a mobile obstruction", "a mobile obstruction", 5, None)

		self.item_map = {
			"book" : self.book,
			"desk" : self.desk,
			"heavy" : self.heavy_item,
			"kohlrabi" : self.kohlrabi,
			"lamp" : self.lamp,
			"mobile_obstruction" : self.mobile_obstruction,
		}


	def setup_texts(self):
		self.hint_map = {
			"default" : "I have no hint.",
			"magic" : "abrakadabra",
		}

		self.explanation_map = {
			"default" : "I have no explanation.",
			"spaize" : "Spaize is space-maize.",
		}

		self.response_map = {
			"confirm_dropped" : "Dropped.",
			"confirm_look" : "You are {0}.",
			"confirm_quit" : "OK.",
			"confirm_taken" : "Taken.",
			"confirm_verbose_off" : "Verbose off.",
			"confirm_verbose_on" : "Verbose on.",
			"describe_commands" : "I know these commands: {0}.",
			"describe_help" : "Welcome and good luck.",
			"describe_item" : "It is {0}.",
			"describe_location" : "You are {0}.",
			"describe_node" : "You are at node {0}.",
			"describe_score" : "Current score: {0} point(s). Instructions entered: {1}.",
			"describe_writing" : "It reads {0}.",
			"list_inventory_nonempty" : "You have: {0}.",
			"list_inventory_empty" : "You have nothing.",
			"list_location" : " Nearby: {1}.",
			"reject_already" : "You already have the {0}.",
			"reject_climb" : "Use \"up\" or \"down\".",
			"reject_excess_light" : "It is too bright.",
			"reject_go" : "Use a compass point.",
			"reject_no_direction" : "You cannot go that way.",
			"reject_no_light" : "It is too dark.",
			"reject_no_back" : "I do not remember how you got here.",
			"reject_no_node" : "There is no such node id.",
			"reject_no_out" : "I cannot tell in from out here.",
			"reject_no_writing" : "There is no writing.",
			"reject_not_here" : "There is no {0} here.",
			"reject_not_holding" : "You do not have the {0}.",
			"reject_not_portable" : "You cannot take that.",
			"reject_obstruction_known" : "You are blocked by {0}.",
			"reject_obstruction_unknown" : "You are blocked by something here.",
			"reject_too_full" : "That is too large to carry.",
			"reject_unknown" : "I do not know what that is.",
		}


	def setup_player(self):
		self.player = Player(self.lighthouse_location)
		self.player.instructions = 7


	def list_commands_side_effect(self, *args):
		return "look, ne"


	def locations_side_effect(self, *args):
		return self.location_map.get(args[0])


	def items_side_effect(self, *args):
		return self.item_map.get(args[0])


	def hints_side_effect(self, *args):
		return self.hint_map.get(args[0])


	def explanations_side_effect(self, *args):
		return self.explanation_map.get(args[0])


	def responses_side_effect(self, *args):
		return self.response_map.get(args[0])


	def test_handle_climb(self):
		response = self.handler.handle_climb(self.player, "tree")

		self.assertEqual(("Use \"up\" or \"down\".", ""), response)


	def test_handle_commands(self):
		response = self.handler.handle_commands(self.player, "")

		self.assertEqual(("I know these commands: {0}.", "look, ne"), response)


	def test_handle_describe_unknown(self):
		response = self.handler.handle_describe(self.player, "biscuit")

		self.assertEqual(("I do not know what that is.", "biscuit"), response)


	def test_handle_describe_known_absent(self):
		response = self.handler.handle_describe(self.player, "book")

		self.assertEqual(("There is no {0} here.", "book"), response)


	def test_handle_describe_known_in_inventory(self):
		self.player.inventory.insert(self.lamp)

		response = self.handler.handle_describe(self.player, "lamp")

		self.assertEqual(("It is {0}.", "a small lamp"), response)


	def test_handle_describe_known_at_location(self):
		self.player.location.insert(self.lamp)

		response = self.handler.handle_describe(self.player, "lamp")

		self.assertEqual(("It is {0}.", "a small lamp"), response)


	def test_handle_drop_unknown(self):
		response = self.handler.handle_drop(self.player, "biscuit")

		self.assertEqual(("I do not know what that is.", "biscuit"), response)


	def test_handle_drop_known_not_in_inventory(self):
		response = self.handler.handle_drop(self.player, "book")

		self.assertEqual(("You do not have the {0}.", "book"), response)
		self.assertFalse(self.player.is_carrying(self.book))


	def test_handle_drop_known_in_inventory(self):
		self.player.inventory.insert(self.lamp)

		response = self.handler.handle_drop(self.player, "lamp")

		self.assertEqual(("Dropped.", "lamp"), response)
		self.assertFalse(self.player.is_carrying(self.lamp))


	def test_handle_explain_default(self):
		response = self.handler.handle_explain(self.player, "dreams")

		self.assertEqual(("I have no explanation.", "dreams"), response)


	def test_handle_explain_non_default(self):
		response = self.handler.handle_explain(self.player, "spaize")

		self.assertEqual(("Spaize is space-maize.", "spaize"), response)


	def test_handle_go_without_destination(self):
		response = self.handler.handle_go(self.player, 34)

		self.assertEqual(("You cannot go that way.", ""), response)
		self.assertIs(self.lighthouse_location, self.player.location)
		self.assertIsNone(self.player.previous_location)


	def test_handle_go_with_destination(self):
		self.player.location.directions[Direction.SOUTH] = self.beach_location
		self.beach_location.directions[Direction.NORTH] = self.player.location

		response = self.handler.handle_go(self.player, 52)

		self.assertEqual(("You are {0}.", ["on a beach of black sand", ""]), response)
		self.assertIs(self.beach_location, self.player.location)
		self.assertIs(self.lighthouse_location, self.player.previous_location)
		self.assertTrue(self.beach_location.seen)


	def test_handle_go_with_destination_again(self):
		self.player.location.directions[Direction.SOUTH] = self.beach_location
		self.beach_location.directions[Direction.NORTH] = self.lighthouse_location

		self.handler.handle_go(self.player, 52)
		self.handler.handle_go(self.player, 34)
		response = self.handler.handle_go(self.player, 52)

		self.assertEqual(("You are {0}.", ["on a beach", ""]), response)
		self.assertIs(self.beach_location, self.player.location)
		self.assertIs(self.lighthouse_location, self.player.previous_location)
		self.assertTrue(self.beach_location.seen)
		self.assertTrue(self.lighthouse_location.seen)


	def test_handle_go_with_destination_no_light(self):
		self.player.location.directions[Direction.DOWN] = self.mine_location
		self.mine_location.directions[Direction.UP] = self.player.location

		response = self.handler.handle_go(self.player, 13)

		self.assertEqual(("It is too dark.", ""), response)
		self.assertIs(self.mine_location, self.player.location)
		self.assertIs(self.lighthouse_location, self.player.previous_location)
		self.assertFalse(self.mine_location.seen)


	def test_handle_go_with_destination_excess_light_carrying_light(self):
		self.player.location.directions[Direction.UP] = self.sun_location
		self.sun_location.directions[Direction.DOWN] = self.player.location
		self.player.inventory.insert(self.lamp)

		response = self.handler.handle_go(self.player, 60)

		self.assertEqual(("It is too bright.", ""), response)
		self.assertIs(self.sun_location, self.player.location)
		self.assertIs(self.lighthouse_location, self.player.previous_location)


	def test_handle_go_with_destination_excess_light_not_carrying_light(self):
		self.player.location.directions[Direction.UP] = self.sun_location
		self.sun_location.directions[Direction.DOWN] = self.player.location

		response = self.handler.handle_go(self.player, 60)

		self.assertEqual(("You are {0}.", ["in the sun. It is hot.", ""]), response)
		self.assertIs(self.sun_location, self.player.location)
		self.assertIs(self.lighthouse_location, self.player.previous_location)


	def test_handle_go_back_without_destination(self):
		response = self.handler.handle_go(self.player, 5)

		self.assertEqual(("I do not remember how you got here.", ""), response)
		self.assertIs(self.lighthouse_location, self.player.location)
		self.assertIsNone(self.player.previous_location)


	def test_handle_go_back_with_destination(self):
		self.player.previous_location = self.beach_location
		self.beach_location.directions[Direction.SOUTH] = self.player.location

		response = self.handler.handle_go(self.player, 5)

		self.assertEqual(("You are {0}.", ["on a beach of black sand", ""]), response)
		self.assertIs(self.beach_location, self.player.location)
		self.assertIs(self.lighthouse_location, self.player.previous_location)


	def test_handle_go_back_with_destination_one_way(self):
		self.player.previous_location = self.beach_location

		response = self.handler.handle_go(self.player, 5)

		self.assertEqual(("You are {0}.", ["on a beach of black sand", ""]), response)
		self.assertIs(self.beach_location, self.player.location)
		self.assertIsNone(self.player.previous_location)


	def test_handle_go_out_without_destination(self):
		response = self.handler.handle_go(self.player, 37)

		self.assertEqual(("I cannot tell in from out here.", ""), response)
		self.assertIs(self.lighthouse_location, self.player.location)
		self.assertIsNone(self.player.previous_location)


	def test_handle_go_without_destination_with_obstruction(self):
		self.player.location.insert(self.obstruction)

		response = self.handler.handle_go(self.player, 34)

		self.assertEqual(("You cannot go that way.", ""), response)
		self.assertIs(self.lighthouse_location, self.player.location)
		self.assertIsNone(self.player.previous_location)


	def test_handle_go_with_destination_with_obstruction(self):
		self.player.location.insert(self.obstruction)
		self.player.location.directions[Direction.SOUTH] = self.beach_location

		response = self.handler.handle_go(self.player, 52)

		self.assertEqual(("You are blocked by {0}.", "an obstruction"), response)


	def test_handle_go_with_destination_with_obstruction_no_light(self):
		self.player.location = self.mine_location
		self.player.location.insert(self.obstruction)
		self.player.location.directions[Direction.EAST] = self.beach_location

		response = self.handler.handle_go(self.player, 16)

		self.assertEqual(("You are blocked by something here.", ""), response)


	def test_handle_go_back_with_destination_with_obstruction(self):
		self.player.location.insert(self.obstruction)
		self.player.previous_location = self.beach_location
		self.beach_location.directions[Direction.NORTH] = self.player.location

		response = self.handler.handle_go(self.player, 5)

		self.assertEqual(("You are {0}.", ["on a beach of black sand", ""]), response)
		self.assertIs(self.beach_location, self.player.location)
		self.assertIs(self.lighthouse_location, self.player.previous_location)


	def test_handle_go_with_obstruction_to_previous_location(self):
		self.beach_location.insert(self.obstruction)
		self.player.location.directions[Direction.SOUTH] = self.beach_location
		self.beach_location.directions[Direction.NORTH] = self.lighthouse_location

		self.handler.handle_go(self.player, 52)
		response = self.handler.handle_go(self.player, 34)

		self.assertEqual(("You are {0}.", ["at a lighthouse by the sea.", ""]), response)
		self.assertIs(self.lighthouse_location, self.player.location)
		self.assertIs(self.beach_location, self.player.previous_location)


	def test_handle_go_disambiguate(self):
		response = self.handler.handle_go_disambiguate(self.player, "east")

		self.assertEqual(("Use a compass point.", ""), response)


	def test_handle_help(self):
		response = self.handler.handle_help(self.player, "")

		self.assertEqual(("Welcome and good luck.", ""), response)
		self.assertEqual(6, self.player.instructions)


	def test_handle_hint_default(self):
		response = self.handler.handle_hint(self.player, "cat")

		self.assertEqual(("I have no hint.", "cat"), response)


	def test_handle_hint_non_default(self):
		response = self.handler.handle_hint(self.player, "magic")

		self.assertEqual(("abrakadabra", "magic"), response)


	def test_handle_inventory_empty(self):
		response = self.handler.handle_inventory(self.player, "")

		self.assertEqual(("You have nothing.", ""), response)


	def test_handle_inventory_nonempty(self):
		self.player.inventory.insert(self.book)

		response = self.handler.handle_inventory(self.player, "")

		self.assertEqual(("You have: {0}.", "\n\ta book"), response)


	def test_handle_look_no_items(self):
		response = self.handler.handle_look(self.player, "")

		self.assertEqual(("You are {0}.", ["at a lighthouse by the sea.", ""]), response)


	def test_handle_look_with_items(self):
		self.player.location.insert(self.lamp)

		response = self.handler.handle_look(self.player, "")

		self.assertEqual(("You are {0}. Nearby: {1}.",
			["at a lighthouse by the sea.", "\n\ta lamp"]), response)


	def test_handle_node_no_arg(self):
		response = self.handler.handle_node(self.player, "")

		self.assertEqual(("You are at node {0}.", 12), response)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_node_arg_invalid(self):
		response = self.handler.handle_node(self.player, "abc")

		self.assertEqual(("You are {0}.", ["at a lighthouse by the sea.", ""]), response)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_node_arg_out_of_range(self):
		response = self.handler.handle_node(self.player, 61)

		self.assertEqual(("There is no such node id.", ""), response)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_node_arg_valid(self):
		response = self.handler.handle_node(self.player, 12)

		self.assertEqual(("You are {0}.", ["at a lighthouse by the sea.", ""]), response)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_node_arg_valid_no_light(self):
		response = self.handler.handle_node(self.player, 11)

		self.assertEqual(("It is too dark.", ""), response)
		self.assertIs(self.mine_location, self.player.location)


	def test_handle_quit(self):
		response = self.handler.handle_quit(self.player, "")

		self.assertEqual(("OK.", ""), response)
		self.assertEqual(6, self.player.instructions)
		self.assertFalse(self.player.playing)


	def test_handle_read_no_writing(self):
		self.player.inventory.insert(self.lamp)

		response = self.handler.handle_read(self.player, "lamp")

		self.assertEqual(("There is no writing.", "lamp"), response)


	def test_handle_read_with_writing(self):
		self.player.inventory.insert(self.book)

		response = self.handler.handle_read(self.player, "book")

		self.assertEqual(("It reads {0}.", "The Pied Piper"), response)


	def test_handle_score(self):
		response = self.handler.handle_score(self.player, "")

		self.assertEqual(("Current score: {0} point(s). Instructions entered: {1}.", [0, 6]), response)
		self.assertEqual(6, self.player.instructions)


	def test_handle_take_unknown(self):
		response = self.handler.handle_take(self.player, "biscuit")

		self.assertEqual(("I do not know what that is.", "biscuit"), response)


	def test_handle_take_known_in_inventory(self):
		self.player.inventory.insert(self.lamp)

		response = self.handler.handle_take(self.player, "lamp")

		self.assertEqual(("You already have the {0}.", "lamp"), response)
		self.assertTrue(self.player.is_carrying(self.lamp))


	def test_handle_take_known_absent(self):
		response = self.handler.handle_take(self.player, "kohlrabi")

		self.assertEqual(("There is no {0} here.", "kohlrabi"), response)
		self.assertFalse(self.player.is_carrying(self.kohlrabi))


	def test_handle_take_known_not_mobile(self):
		self.player.location.insert(self.desk)

		response = self.handler.handle_take(self.player, "desk")

		self.assertEqual(("You cannot take that.", "desk"), response)
		self.assertFalse(self.player.is_carrying(self.desk))
		self.assertTrue(self.player.location.contains(self.desk))


	def test_handle_take_known_obstruction(self):
		self.player.location.insert(self.mobile_obstruction)

		response = self.handler.handle_take(self.player, "mobile_obstruction")

		self.assertEqual(("You cannot take that.", "mobile_obstruction"), response)
		self.assertFalse(self.player.is_carrying(self.mobile_obstruction))
		self.assertTrue(self.player.location.contains(self.mobile_obstruction))


	def test_handle_take_known_over_capacity(self):
		self.player.location.insert(self.book)
		self.player.inventory.insert(self.heavy_item)

		response = self.handler.handle_take(self.player, "book")

		self.assertEqual(("That is too large to carry.", "book"), response)
		self.assertFalse(self.player.is_carrying(self.book))
		self.assertTrue(self.player.location.contains(self.book))


	def test_handle_take_known_at_location(self):
		self.player.location.insert(self.book)

		response = self.handler.handle_take(self.player, "book")

		self.assertEqual(("Taken.", "book"), response)
		self.assertTrue(self.player.is_carrying(self.book))
		self.assertFalse(self.player.location.contains(self.book))


	def test_handle_verbose_off(self):
		self.player.verbose = True

		response = self.handler.handle_verbose(self.player, False)

		self.assertFalse(self.player.verbose)
		self.assertEqual(("Verbose off.", ""), response)


	def test_handle_verbose_on(self):
		self.player.verbose = False

		response = self.handler.handle_verbose(self.player, True)

		self.assertTrue(self.player.verbose)
		self.assertEqual(("Verbose on.", ""), response)


	def test_handle_yank_known_at_location(self):
		self.player.location.insert(self.book)

		response = self.handler.handle_yank(self.player, "book")

		self.assertEqual(("Taken.", "book"), response)
		self.assertTrue(self.player.is_carrying(self.book))
		self.assertFalse(self.lighthouse_location.contains(self.book))


	def test_handle_yank_known_not_at_location(self):
		self.mine_location.insert(self.book)

		response = self.handler.handle_yank(self.player, "book")

		self.assertEqual(("Taken.", "book"), response)
		self.assertTrue(self.player.is_carrying(self.book))
		self.assertFalse(self.mine_location.contains(self.book))


if __name__ == "__main__":
	unittest.main()

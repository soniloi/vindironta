import unittest
from unittest.mock import Mock
from unittest.mock import patch

from adventure.command_handler import CommandHandler
from adventure.data_collection import DataCollection
from adventure.direction import Direction
from adventure import item_collection
from adventure.item import Item
from adventure.location import Location
from adventure.player import Player
from adventure import text_collection

class TestCommandHandler(unittest.TestCase):

	def setUp(self):

		self.handler = CommandHandler()

		location_collection_mock = Mock()
		location_collection_mock.get.side_effect = self.locations_side_effect

		item_collection_mock = Mock()
		item_collection_mock.get.side_effect = self.item_side_effect

		explanations_mock = Mock()
		explanations_mock.get.side_effect = self.explanations_side_effect

		responses_mock = Mock()
		responses_mock.get.side_effect = self.responses_side_effect

		self.data = DataCollection(
			locations=location_collection_mock,
			items=item_collection_mock,
			hints=None,
			explanations=explanations_mock,
			responses=responses_mock,
			puzzles=None,
		)
		self.handler.init_data(self.data)

		self.mine_location = Location(11, 0, "Mines", "in the mines", ". There are dark passages everywhere")
		self.lighthouse_location = Location(12, 0, "Lighthouse", "at a lighthouse", " by the sea")
		self.player = Player(self.mine_location)
		self.book = Item(1105, 2, "book", "a book", "a book of fairytales", 2, "The Pied Piper")
		self.lamp = Item(1043, 0x101A, "lamp", "a lamp", "a small lamp", 2, None)
		self.kohlrabi = Item(1042, 0x2002, "kohlrabi", "some kohlrabi", "some kohlrabi, a cabbage cultivar", 3, None)
		self.desk = Item(1000, 0x0, "desk", "a desk", "a large mahogany desk", 6, None)

		self.location_map = {
			11 : self.mine_location,
			12 : self.lighthouse_location,
		}

		self.item_map = {
			"book" : self.book,
			"desk" : self.desk,
			"kohlrabi" : self.kohlrabi,
			"lamp" : self.lamp,
		}

		self.explanation_map = {
			"default" : "I have no explanation for that.",
			"spaize" : "Spaize is space-maize.",
		}

		self.response_map = {
			"confirm_dropped" : "Dropped.",
			"confirm_look" : "You are {0}.",
			"confirm_quit" : "OK.",
			"confirm_taken" : "Taken.",
			"describe_item" : "It is {0}.",
			"describe_location" : "You are {0}.",
			"describe_node" : "You are at node {0}.",
			"describe_score" : "Your current score is {0} point(s).",
			"list_inventory_nonempty" : "You currently have the following: {0}.",
			"list_inventory_empty" : "You are not carrying anything.",
			"list_location" : " The following items are nearby: {1}.",
			"reject_already" : "You already have the {0}.",
			"reject_no_direction" : "You cannot go that way.",
			"reject_no_back" : "I do not remember how you got here.",
			"reject_no_node" : "There is no such node id.",
			"reject_no_out" : "I cannot tell in from out here.",
			"reject_not_here" : "There is no {0} here.",
			"reject_not_holding" : "You do not have the {0}.",
			"reject_not_portable" : "You cannot take that.",
			"reject_unknown" : "I do not know who or what that is.",
		}


	def get_value_or_none(self, data_map, key):
		if key in data_map:
			return data_map[key]
		return None


	def locations_side_effect(self, *args):
		return self.get_value_or_none(self.location_map, args[0])


	def item_side_effect(self, *args):
		return self.get_value_or_none(self.item_map, args[0])


	def explanations_side_effect(self, *args):
		return self.get_value_or_none(self.explanation_map, args[0])


	def responses_side_effect(self, *args):
		return self.get_value_or_none(self.response_map, args[0])


	def test_handle_describe_unknown(self):
		response = self.handler.handle_describe(self.player, "biscuit")

		self.assertEqual(("I do not know who or what that is.", "biscuit"), response)


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

		self.assertEqual(("I do not know who or what that is.", "biscuit"), response)


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

		self.assertEqual(("I have no explanation for that.", "dreams"), response)


	def test_handle_explain_non_default(self):
		response = self.handler.handle_explain(self.player, "spaize")

		self.assertEqual(("Spaize is space-maize.", "spaize"), response)


	def test_handle_go_without_destination(self):
		response = self.handler.handle_go(self.player, 34)

		self.assertEqual(("You cannot go that way.", ""), response)
		self.assertIs(self.mine_location, self.player.location)
		self.assertIsNone(self.player.previous_location)


	def test_handle_go_with_destination(self):
		new_location = Location(12, 0, "Lighthouse", "at a lighthouse", " by the sea")
		self.mine_location.directions[Direction.SOUTH] = self.lighthouse_location

		response = self.handler.handle_go(self.player, 52)

		self.assertEqual(("You are {0}.", ["at a lighthouse by the sea", ""]), response)
		self.assertIs(self.lighthouse_location, self.player.location)
		self.assertIs(self.mine_location, self.player.previous_location)


	def test_handle_go_back_without_destination(self):
		response = self.handler.handle_go(self.player, 5)

		self.assertEqual(("I do not remember how you got here.", ""), response)
		self.assertIs(self.mine_location, self.player.location)
		self.assertIsNone(self.player.previous_location)


	def test_handle_go_back_with_destination(self):
		self.player.previous_location = self.lighthouse_location

		response = self.handler.handle_go(self.player, 5)

		self.assertEqual(("You are {0}.", ["at a lighthouse by the sea", ""]), response)
		self.assertIs(self.lighthouse_location, self.player.location)
		self.assertIs(self.mine_location, self.player.previous_location)


	def test_handle_go_out_without_destination(self):
		response = self.handler.handle_go(self.player, 37)

		self.assertEqual(("I cannot tell in from out here.", ""), response)
		self.assertIs(self.mine_location, self.player.location)
		self.assertIsNone(self.player.previous_location)


	def test_handle_inventory_empty(self):
		response = self.handler.handle_inventory(self.player, "")

		self.assertEqual(("You are not carrying anything.", ""), response)


	def test_handle_inventory_nonempty(self):
		self.player.inventory.insert(self.book)

		response = self.handler.handle_inventory(self.player, "")

		self.assertEqual(("You currently have the following: {0}.", "\n\ta book"), response)


	def test_handle_look_no_items(self):
		response = self.handler.handle_look(self.player, "")

		self.assertEqual(("You are {0}.", ["in the mines. There are dark passages everywhere", ""]), response)


	def test_handle_look_with_items(self):
		self.mine_location.insert(self.lamp)

		response = self.handler.handle_look(self.player, "")

		self.assertEqual(("You are {0}. The following items are nearby: {1}.",
			["in the mines. There are dark passages everywhere", "\n\ta lamp"]), response)


	def test_handle_node_no_arg(self):
		response = self.handler.handle_node(self.player, "")

		self.assertEqual(("You are at node {0}.", 11), response)


	def test_handle_node_arg_invalid(self):
		response = self.handler.handle_node(self.player, "abc")

		self.assertEqual(("You are {0}.", ["in the mines. There are dark passages everywhere", ""]), response)
		self.assertIs(self.mine_location, self.player.location)


	def test_handle_node_arg_out_of_range(self):
		response = self.handler.handle_node(self.player, 61)

		self.assertEqual(("There is no such node id.", ""), response)
		self.assertIs(self.mine_location, self.player.location)


	def test_handle_node_arg_valid(self):
		response = self.handler.handle_node(self.player, 12)

		self.assertEqual(("You are {0}.", ["at a lighthouse by the sea", ""]), response)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_quit(self):
		response = self.handler.handle_quit(self.player, "")

		self.assertEqual(("OK.", ""), response)
		self.assertFalse(self.player.playing)


	def test_handle_score(self):
		response = self.handler.handle_score(self.player, "")

		self.assertEqual(("Your current score is {0} point(s).", 0), response)


	def test_handle_take_unknown(self):
		response = self.handler.handle_take(self.player, "biscuit")

		self.assertEqual(("I do not know who or what that is.", "biscuit"), response)


	def test_handle_take_known_in_inventory(self):
		self.player.inventory.insert(self.lamp)

		response = self.handler.handle_take(self.player, "lamp")

		self.assertEqual(("You already have the {0}.", "lamp"), response)
		self.assertTrue(self.player.is_carrying(self.lamp))


	def test_handle_take_known_absent(self):
		response = self.handler.handle_take(self.player, "kohlrabi")

		self.assertEqual(("There is no {0} here.", "kohlrabi"), response)
		self.assertFalse(self.player.is_carrying(self.kohlrabi))


	def test_handle_take_known_not_portable(self):
		self.mine_location.insert(self.desk)

		response = self.handler.handle_take(self.player, "desk")

		self.assertEqual(("You cannot take that.", "desk"), response)
		self.assertFalse(self.player.is_carrying(self.desk))


	def test_handle_take_known_at_location(self):
		self.mine_location.insert(self.book)

		response = self.handler.handle_take(self.player, "book")

		self.assertEqual(("Taken.", "book"), response)
		self.assertTrue(self.player.is_carrying(self.book))


if __name__ == "__main__":
	unittest.main()

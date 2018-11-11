import unittest
from unittest.mock import Mock

from adventure.command import Command
from adventure.command_handler import CommandHandler
from adventure.data_element import Labels
from adventure.direction import Direction
from adventure.inventory import Inventory
from adventure.item import Item, ContainerItem, SwitchableItem, SwitchInfo, SwitchTransition, WearableItem
from adventure.location import Location
from adventure.player import Player

class TestCommandHandler(unittest.TestCase):

	def setUp(self):
		self.setup_data()
		self.setup_inventories()
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
		self.data.get_hint.side_effect = self.hints_side_effect
		self.data.get_explanation.side_effect = self.explanations_side_effect
		self.data.get_response.side_effect = self.responses_side_effect


	def setup_inventories(self):
		self.default_inventory = Inventory(0, 0x1, 13)


	def setup_locations(self):
		self.beach_location = Location(13, 0x1, Labels("Beach", "on a beach", " of black sand"))
		self.lighthouse_location = Location(12, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.mine_location = Location(11, 0x0, Labels("Mines", "in the mines", ". There are dark passages everywhere."))
		self.sun_location = Location(10, 0x11, Labels("Sun", "in the sun", ". It is hot."))
		self.cave_location = Location(9, 0x0, Labels("Cave", "in a cave", ". It is dark"))
		self.item_start_location = Location(0, 0x0, Labels("Start", "at the start", ", where items start out."))

		self.location_map = {
			11 : self.mine_location,
			12 : self.lighthouse_location,
			13 : self.beach_location,
		}


	def setup_items(self):
		self.book = Item(1105, 2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper")
		lamp_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "off", "on")
		self.lamp = SwitchableItem(1043, 0x101A, Labels("lamp", "a lamp", "a small lamp"), 2, None, lamp_switching_info)
		self.lamp.switched_element = self.lamp
		self.kohlrabi = Item(1042, 0x2002, Labels("kohlrabi", "some kohlrabi", "some kohlrabi, a cabbage cultivar"), 3, None)
		self.desk = Item(1000, 0x20000, Labels("desk", "a desk", "a large mahogany desk"), 6, None)
		self.heavy_item = Item(1001, 0x0, Labels("heavy", "a heavy item", "a dummy heavy item"), 15, None)
		self.obstruction = Item(1002, 0x4, Labels("obstruction", "an obstruction", "an obstruction blocking you"), 8, None)
		self.mobile_obstruction = Item(1003, 0x6, Labels("mobile_obstruction", "a mobile obstruction", "a mobile obstruction"), 5, None)
		self.basket = ContainerItem(1107, 0x3, Labels("basket", "a basket", "a large basket"), 6, None)
		self.suit = WearableItem(1046, 0x402, Labels("suit", "a suit", "a space-suit"), 2, None, Item.ATTRIBUTE_GIVES_AIR)
		self.bottle = ContainerItem(1108, 0x203, Labels("bottle", "a bottle", "a small bottle"), 2, None)
		self.water = Item(1109, 0x102, Labels("water", "some water", "some water"), 1, None)

		self.item_start_location.insert(self.book)
		self.item_start_location.insert(self.lamp)
		self.item_start_location.insert(self.heavy_item)
		self.item_start_location.insert(self.basket)
		self.item_start_location.insert(self.suit)
		self.item_start_location.insert(self.bottle)


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
			"confirm_emptied" : "You take the {0} out of the {1}.",
			"confirm_look" : "You are {0}.",
			"confirm_ok" : "OK.",
			"confirm_poured" : "You pour the liquid away.",
			"confirm_quit" : "OK.",
			"confirm_taken" : "Taken.",
			"confirm_immune_off" : "Immune off.",
			"confirm_immune_on" : "Immune on.",
			"confirm_verbose_off" : "Verbose off.",
			"confirm_verbose_on" : "Verbose on.",
			"confirm_wearing" : "You are wearing the {0}.",
			"death_darkness" : "You fall to your death in the darkness.",
			"describe_commands" : "I know these commands: {0}.",
			"describe_help" : "Welcome and good luck.",
			"describe_item" : "It is {0}.",
			"describe_item_switch" : " It is {1}.",
			"describe_locate" : "The {0} is at {1} ({2}).",
			"describe_location" : "You are {0}.",
			"describe_node" : "You are at node {0}.",
			"describe_score" : "Current score: {0} point(s). Instructions entered: {1}.",
			"describe_switch_item" : "The {0} is now {1}.",
			"describe_writing" : "It reads {0}.",
			"list_inventory_nonempty" : "You have: {0}.",
			"list_inventory_empty" : "You have nothing.",
			"list_location" : " Nearby: {1}.",
			"reject_already_empty" : "It is already empty.",
			"reject_already_switched" : "The {0} is already {1}.",
			"reject_already_wearing" : "You are already wearing the {0}.",
			"reject_climb" : "Use \"up\" or \"down\".",
			"reject_excess_light" : "It is too bright.",
			"reject_go" : "Use a compass point.",
			"reject_no_direction" : "You cannot go that way.",
			"reject_no_light" : "It is too dark.",
			"reject_no_back" : "I do not remember how you got here.",
			"reject_no_know_how" : "I do not know how.",
			"reject_no_node" : "There is no such node id.",
			"reject_no_out" : "I cannot tell in from out here.",
			"reject_no_writing" : "There is no writing.",
			"reject_not_container" : "That is not a container.",
			"reject_not_liquid" : "That is not a liquid.",
			"reject_not_portable" : "You cannot take that.",
			"reject_not_wearable" : "You cannot wear the {0}.",
			"reject_obstruction_known" : "You are blocked by {0}.",
			"reject_obstruction_unknown" : "You are blocked by something here.",
			"reject_take_liquid" : "You cannot take a liquid.",
			"reject_too_full" : "That is too large to carry.",
		}


	def setup_player(self):
		self.player = Player(self.lighthouse_location, self.default_inventory)
		self.player.instructions = 7


	def list_commands_side_effect(self, *args):
		return "look, ne"


	def locations_side_effect(self, *args):
		return self.location_map.get(args[0])


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
		response = self.handler.handle_commands(self.player)

		self.assertEqual(("I know these commands: {0}.", "look, ne"), response)


	def test_handle_describe_in_inventory(self):
		self.player.take_item(self.book)

		response = self.handler.handle_describe(self.player, self.book)

		self.assertEqual(("It is {0}.", "a book of fairytales"), response)


	def test_handle_describe_at_location(self):
		self.player.location.insert(self.book)

		response = self.handler.handle_describe(self.player, self.lamp)

		self.assertEqual(("It is {0}. It is {1}.", ["a small lamp", "on"]), response)


	def test_handle_drop_non_wearable(self):
		self.player.take_item(self.lamp)

		response = self.handler.handle_drop(self.player, self.lamp)

		self.assertEqual(("Dropped.", "lamp"), response)
		self.assertFalse(self.player.is_carrying(self.lamp))
		self.assertTrue(self.player.is_near_item(self.lamp))


	def test_handle_drop_wearable(self):
		self.player.take_item(self.suit)
		self.suit.being_worn = True

		response = self.handler.handle_drop(self.player, self.suit)

		self.assertEqual(("Dropped.", "suit"), response)
		self.assertFalse(self.player.is_carrying(self.suit))
		self.assertTrue(self.player.is_near_item(self.suit))
		self.assertFalse(self.suit.being_worn)


	def test_handle_drop_from_inside_container(self):
		self.basket.insert(self.book)
		self.player.take_item(self.basket)

		response = self.handler.handle_drop(self.player, self.book)

		self.assertEqual(("Dropped.", "book"), response)
		self.assertFalse(self.player.is_carrying(self.book))
		self.assertTrue(self.player.is_near_item(self.book))


	def test_handle_drop_liquid(self):
		self.bottle.insert(self.water)
		self.player.take_item(self.bottle)

		response = self.handler.handle_drop(self.player, self.water)

		self.assertEqual(("You pour the liquid away.", ["water", "bottle"]), response)
		self.assertFalse(self.player.is_carrying(self.water))
		self.assertFalse(self.player.is_near_item(self.water))


	def test_handle_empty_non_container(self):
		self.player.take_item(self.book)

		response = self.handler.handle_empty(self.player, self.book)

		self.assertEqual(("That is not a container.", "book"), response)


	def test_handle_empty_already_empty(self):
		self.player.take_item(self.basket)

		response = self.handler.handle_empty(self.player, self.basket)

		self.assertEqual(("It is already empty.", "basket"), response)
		self.assertFalse(self.basket.has_items())


	def test_handle_empty_liquid(self):
		self.bottle.insert(self.water)
		self.player.take_item(self.bottle)

		response = self.handler.handle_empty(self.player, self.bottle)

		self.assertEqual(("You pour the liquid away.", ["water", "bottle"]), response)
		self.assertFalse(self.bottle.contains(self.water))
		self.assertFalse(self.player.is_carrying(self.water))
		self.assertFalse(self.player.is_near_item(self.water))


	def test_handle_empty_solid_in_inventory(self):
		self.basket.insert(self.book)
		self.player.take_item(self.basket)

		response = self.handler.handle_empty(self.player, self.basket)

		self.assertEqual(("You take the {0} out of the {1}.", ["book", "basket"]), response)
		self.assertFalse(self.basket.contains(self.book))
		self.assertTrue(self.player.is_carrying(self.book))
		self.assertFalse(self.player.is_near_item(self.book))


	def test_handle_empty_solid_at_location(self):
		self.basket.insert(self.book)
		self.player.location.insert(self.basket)

		response = self.handler.handle_empty(self.player, self.basket)

		self.assertEqual(("You take the {0} out of the {1}.", ["book", "basket"]), response)
		self.assertFalse(self.basket.contains(self.book))
		self.assertFalse(self.player.is_carrying(self.book))
		self.assertTrue(self.player.is_near_item(self.book))


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
		self.player.take_item(self.lamp)

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


	def test_handle_go_from_light_to_light(self):
		self.player.location = self.beach_location
		self.player.location.directions[Direction.EAST] = self.lighthouse_location

		response = self.handler.handle_go(self.player, 16)

		self.assertEqual(("You are {0}.", ["at a lighthouse by the sea.", ""]), response)
		self.assertTrue(self.player.playing)


	def test_handle_go_from_dark_to_light(self):
		self.player.location = self.beach_location
		self.player.location.directions[Direction.EAST] = self.mine_location

		response = self.handler.handle_go(self.player, 16)

		self.assertEqual(("It is too dark.", ""), response)
		self.assertTrue(self.player.playing)


	def test_handle_go_from_dark_to_light(self):
		self.player.location = self.mine_location
		self.player.location.directions[Direction.EAST] = self.beach_location

		response = self.handler.handle_go(self.player, 16)

		self.assertEqual(("You are {0}.", ["on a beach of black sand", ""]), response)
		self.assertTrue(self.player.playing)


	def test_handle_go_from_dark_to_dark_not_carrying_light_immune_off(self):
		self.player.location = self.mine_location
		self.player.location.directions[Direction.EAST] = self.cave_location
		self.player.take_item(self.book)

		response = self.handler.handle_go(self.player, 16)

		self.assertEqual(("You fall to your death in the darkness.", ""), response)
		self.assertFalse(self.player.alive)
		self.assertFalse(self.player.holding_items())
		self.assertEqual(self.mine_location, self.book.container)


	def test_handle_go_from_dark_to_dark_not_carrying_light_immune_on(self):
		self.player.location = self.mine_location
		self.player.location.directions[Direction.EAST] = self.cave_location
		self.player.immune = True

		response = self.handler.handle_go(self.player, 16)

		self.assertEqual(("It is too dark.", ""), response)
		self.assertTrue(self.player.alive)


	def test_handle_go_from_dark_to_dark_carrying_light(self):
		self.player.location = self.mine_location
		self.player.location.directions[Direction.EAST] = self.cave_location
		self.player.take_item(self.lamp)

		response = self.handler.handle_go(self.player, 16)

		self.assertEqual(("You are {0}.", ["in a cave. It is dark", ""]), response)
		self.assertTrue(self.player.playing)


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


	def test_handle_immune_off(self):
		self.player.immune = True

		response = self.handler.handle_immune(self.player, False)

		self.assertFalse(self.player.immune)
		self.assertEqual(("Immune off.", ""), response)


	def test_handle_immune_on(self):
		response = self.handler.handle_immune(self.player, True)

		self.assertTrue(self.player.immune)
		self.assertEqual(("Immune on.", ""), response)


	def test_handle_inventory_empty(self):
		response = self.handler.handle_inventory(self.player)

		self.assertEqual(("You have nothing.", ""), response)


	def test_handle_inventory_nonempty(self):
		self.player.take_item(self.book)

		response = self.handler.handle_inventory(self.player)

		self.assertEqual(("You have: {0}.", "\n\ta book"), response)


	def test_handle_locate_at_location(self):
		self.player.location.insert(self.book)

		response = self.handler.handle_locate(self.player, self.book)

		self.assertEqual(("The {0} is at {1} ({2}).", ["book", 12, "at a lighthouse"]), response)


	def test_handle_locate_in_item(self):
		self.basket.insert(self.book)

		response = self.handler.handle_locate(self.player, self.book)

		self.assertEqual(("The {0} is at {1} ({2}).", ["book", 1107, "a basket"]), response)


	def test_handle_locate_in_inventory(self):
		self.player.take_item(self.book)

		response = self.handler.handle_locate(self.player, self.book)

		self.assertEqual(("The {0} is at {1} ({2}).", ["book", 0, "inventory"]), response)


	def test_handle_look_no_items(self):
		response = self.handler.handle_look(self.player)

		self.assertEqual(("You are {0}.", ["at a lighthouse by the sea.", ""]), response)


	def test_handle_look_with_item(self):
		self.player.location.insert(self.book)

		response = self.handler.handle_look(self.player)

		self.assertEqual(("You are {0}. Nearby: {1}.",
			["at a lighthouse by the sea.", "\n\ta book"]), response)


	def test_handle_look_with_silent_item(self):
		self.player.location.insert(self.desk)

		response = self.handler.handle_look(self.player)

		self.assertEqual(("You are {0}.", ["at a lighthouse by the sea.", ""]), response)


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


	def test_pour_non_liquid(self):
		self.player.take_item(self.book)

		response = self.handler.handle_pour(self.player, self.book)

		self.assertEqual(("That is not a liquid.", "book"), response)


	def test_handle_pour_liquid(self):
		self.bottle.insert(self.water)
		self.player.take_item(self.bottle)

		response = self.handler.handle_pour(self.player, self.water)

		self.assertEqual(("You pour the liquid away.", ["water", "bottle"]), response)
		self.assertFalse(self.bottle.contains(self.water))
		self.assertFalse(self.player.is_near_item(self.water))


	def test_handle_quit(self):
		response = self.handler.handle_quit(self.player)

		self.assertEqual(("OK.", ""), response)
		self.assertEqual(6, self.player.instructions)
		self.assertFalse(self.player.playing)


	def test_handle_read_no_writing(self):
		self.player.take_item(self.lamp)

		response = self.handler.handle_read(self.player, self.lamp)

		self.assertEqual(("There is no writing.", "lamp"), response)


	def test_handle_read_with_writing(self):
		self.player.take_item(self.book)

		response = self.handler.handle_read(self.player, self.book)

		self.assertEqual(("It reads {0}.", "The Pied Piper"), response)


	def test_handle_score(self):
		response = self.handler.handle_score(self.player)

		self.assertEqual(("Current score: {0} point(s). Instructions entered: {1}.", [0, 6]), response)
		self.assertEqual(6, self.player.instructions)


	def test_handle_switch_off_to_off(self):
		self.lamp.switch_off()

		response = self.handler.handle_switch(self.player, self.lamp, SwitchTransition.OFF)

		self.assertEqual(("The {0} is already {1}.", ["lamp", "off"]), response)
		self.assertFalse(self.lamp.is_on())


	def test_handle_switch_off_to_on(self):
		self.lamp.switch_off()

		response = self.handler.handle_switch(self.player, self.lamp, SwitchTransition.ON)

		self.assertEqual(("The {0} is now {1}.", ["lamp", "on"]), response)
		self.assertTrue(self.lamp.is_on())


	def test_handle_switch_on_to_off(self):
		self.lamp.switch_on()

		response = self.handler.handle_switch(self.player, self.lamp, SwitchTransition.OFF)

		self.assertEqual(("The {0} is now {1}.", ["lamp", "off"]), response)
		self.assertFalse(self.lamp.is_on())


	def test_handle_switch_on_to_on(self):
		self.lamp.switch_on()

		response = self.handler.handle_switch(self.player, self.lamp, SwitchTransition.ON)

		self.assertEqual(("The {0} is already {1}.", ["lamp", "on"]), response)
		self.assertTrue(self.lamp.is_on())


	def test_handle_take_not_mobile(self):
		self.player.location.insert(self.desk)

		response = self.handler.handle_take(self.player, self.desk)

		self.assertEqual(("You cannot take that.", "desk"), response)
		self.assertFalse(self.player.is_carrying(self.desk))
		self.assertTrue(self.player.is_near_item(self.desk))


	def test_handle_take_obstruction(self):
		self.player.location.insert(self.mobile_obstruction)

		response = self.handler.handle_take(self.player, self.mobile_obstruction)

		self.assertEqual(("You cannot take that.", "mobile_obstruction"), response)
		self.assertFalse(self.player.is_carrying(self.mobile_obstruction))
		self.assertTrue(self.player.is_near_item(self.mobile_obstruction))


	def test_handle_take_over_capacity(self):
		self.player.location.insert(self.book)
		self.player.take_item(self.heavy_item)

		response = self.handler.handle_take(self.player, self.book)

		self.assertEqual(("That is too large to carry.", "book"), response)
		self.assertFalse(self.player.is_carrying(self.book))
		self.assertTrue(self.player.is_near_item(self.book))


	def test_handle_take_at_location(self):
		self.player.location.insert(self.book)

		response = self.handler.handle_take(self.player, self.book)

		self.assertEqual(("Taken.", "book"), response)
		self.assertTrue(self.player.is_carrying(self.book))
		self.assertFalse(self.player.is_near_item(self.book))


	def test_handle_take_liquid(self):
		self.bottle.insert(self.water)
		self.player.location.insert(self.bottle)

		response = self.handler.handle_take(self.player, self.water)

		self.assertEqual(("You cannot take a liquid.", "water"), response)
		self.assertFalse(self.player.is_carrying(self.water))
		self.assertTrue(self.player.is_near_item(self.water))


	def test_handle_toggle_non_switchable_item(self):
		response = self.handler.handle_toggle(self.player, self.book)

		self.assertEqual(("I do not know how.", "book"), response)


	def test_handle_toggle_off_to_on(self):
		self.lamp.attributes &= ~0x10

		response = self.handler.handle_toggle(self.player, self.lamp)

		self.assertEqual(("The {0} is now {1}.", ["lamp", "on"]), response)
		self.assertTrue(self.lamp.is_on())


	def test_handle_toggle_on_to_off(self):
		self.lamp.attributes |= 0x10

		response = self.handler.handle_toggle(self.player, self.lamp)

		self.assertEqual(("The {0} is now {1}.", ["lamp", "off"]), response)
		self.assertFalse(self.lamp.is_on())


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


	def test_handle_wear_not_wearable(self):
		response = self.handler.handle_wear(self.player, self.lamp)

		self.assertEqual(("You cannot wear the {0}.", "lamp"), response)


	def test_handle_wear_wearable_already_wearing(self):
		self.suit.being_worn = True

		response = self.handler.handle_wear(self.player, self.suit)

		self.assertEqual(("You are already wearing the {0}.", "suit"), response)


	def test_handle_wear_wearable_not_already_wearing(self):
		self.player.location.insert(self.suit)
		self.suit.being_worn = False

		response = self.handler.handle_wear(self.player, self.suit)

		self.assertEqual(("You are wearing the {0}.", "suit"), response)


if __name__ == "__main__":
	unittest.main()

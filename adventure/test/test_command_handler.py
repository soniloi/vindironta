import unittest
from unittest.mock import Mock

from adventure.command_handler import CommandHandler
from adventure.direction import Direction
from adventure.element import Labels
from adventure.inventory import Inventory
from adventure.item import Item, ContainerItem, SentientItem, SwitchableItem, SwitchInfo, SwitchTransition, WearableItem
from adventure.location import Location
from adventure.player import Player

class TestCommandHandler(unittest.TestCase):

	def setUp(self):
		self.setup_data()

		self.setup_player()

		self.command = Mock()
		self.handler = CommandHandler()
		self.handler.init_data(self.data)


	def setup_data(self):
		self.data = Mock()
		self.setup_commands()
		self.setup_inventories()
		self.setup_locations()
		self.setup_items()
		self.setup_texts()


	def setup_commands(self):
		self.data.list_commands.return_value = "look, ne"


	def setup_inventories(self):
		self.default_inventory = Inventory(0, 0x1, Labels("Main Inventory", "in the main inventory", ", where items live usually."), 13)


	def setup_locations(self):
		self.beach_location = Location(13, 0x1, Labels("Beach", "on a beach", " of black sand"))
		self.lighthouse_location = Location(12, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.mine_location = Location(11, 0x0, Labels("Mines", "in the mines", ". There are dark passages everywhere."))
		self.sun_location = Location(10, 0x11, Labels("Sun", "in the sun", ". It is hot."))
		self.cave_location = Location(9, 0x0, Labels("Cave", "in a cave", ". It is dark"))
		self.item_start_location = Location(0, 0x0, Labels("Start", "at the start", ", where items start out."))

		self.data.get_location.side_effect = lambda x: {
			11 : self.mine_location,
			12 : self.lighthouse_location,
			13 : self.beach_location,
		}.get(x)


	def setup_items(self):
		self.book = Item(1105, 2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper")
		lamp_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "off", "on")
		self.lamp = SwitchableItem(1043, 0x101A, Labels("lamp", "a lamp", "a small lamp"), 2, None, lamp_switching_info)
		self.lamp.switched_element = self.lamp
		self.kohlrabi = Item(1042, 0x2002, Labels("kohlrabi", "some kohlrabi", "some kohlrabi, a cabbage cultivar"), 3, None)
		self.desk = Item(1000, 0x20000, Labels("desk", "a desk", "a large mahogany desk"), 6, None)
		self.heavy_item = Item(1001, 0x2, Labels("heavy", "a heavy item", "a dummy heavy item"), 15, None)
		self.obstruction = Item(1002, 0x4, Labels("obstruction", "an obstruction", "an obstruction blocking you"), 8, None)
		self.mobile_obstruction = Item(1003, 0x6, Labels("mobile_obstruction", "a mobile obstruction", "a mobile obstruction"), 5, None)
		self.basket = ContainerItem(1107, 0x3, Labels("basket", "a basket", "a large basket"), 6, None)
		self.suit = WearableItem(1046, 0x402, Labels("suit", "a suit", "a space-suit"), 2, None, Item.ATTRIBUTE_GIVES_AIR)
		self.bottle = ContainerItem(1108, 0x203, Labels("bottle", "a bottle", "a small bottle"), 3, None)
		self.cat = SentientItem(1047, 0x80003, Labels("cat", "a cat", "a black cat"), 3, None)
		self.bread = Item(1109, 0x2002, Labels("bread", "some bread", "a loaf of bread"), 2, None)
		self.water = Item(1110, 0x22902, Labels("water", "some water", "some water"), 1, None)


	def setup_texts(self):
		self.data.get_hint.side_effect = lambda x: {
			"default" : "I have no hint.",
			"magic" : "abrakadabra",
		}.get(x)

		self.data.get_explanation.side_effect = lambda x: {
			"default" : "I have no explanation.",
			"spaize" : "Spaize is space-maize.",
		}.get(x)

		self.data.get_response.side_effect = lambda x: {
			"confirm_consume" : "You consume the {0}.",
			"confirm_dropped" : "Dropped.",
			"confirm_emptied_liquid" : "You pour the {1} out of the {0}.",
			"confirm_emptied_solid" : "You take the {1} out of the {0}.",
			"confirm_feed" : "You feed the {0} to the {1}.",
			"confirm_given" : "Given.",
			"confirm_inserted" : "Inserted.",
			"confirm_look" : "You are {0}.",
			"confirm_ok" : "OK.",
			"confirm_poured_no_destination" : "You pour the liquid away.",
			"confirm_poured_with_destination" : "You pour the liquid onto the {1}.",
			"confirm_quit" : "OK.",
			"confirm_say_audience" : "You say {0} to the {1}.",
			"confirm_say_no_audience" : "You say {0}.",
			"confirm_say_no_sentient_audience" : "You say {0} at the {1}.",
			"confirm_taken" : "Taken.",
			"confirm_immune_off" : "Immune off.",
			"confirm_immune_on" : "Immune on.",
			"confirm_verbose_off" : "Verbose off.",
			"confirm_verbose_on" : "Verbose on.",
			"confirm_wearing" : "You are wearing the {0}.",
			"describe_commands" : "I know these commands: {0}.",
			"describe_help" : "Welcome and good luck.",
			"describe_item" : "It is {0}.",
			"describe_item_switch" : " It is {1}.",
			"describe_locate_copies" : "Copies at {2}.",
			"describe_locate_primary" : "The {0} is at {1}. ",
			"describe_location" : "You are {0}.",
			"describe_node" : "You are at node {0}.",
			"describe_score" : "Current score: {0} points. Maximum score: {1} points. Instructions entered: {2}.",
			"describe_switch_item" : "The {0} is now {1}.",
			"describe_writing" : "It reads {0}.",
			"list_inventory_nonempty" : "You have: {0}.",
			"list_inventory_empty" : "You have nothing.",
			"list_location" : " Nearby: {1}.",
			"reject_already_contained" : "The {0} is already in the {1}.",
			"reject_already_empty" : "It is already empty.",
			"reject_already_switched" : "The {0} is already {1}.",
			"reject_already_wearing" : "You are already wearing the {0}.",
			"reject_climb" : "Use \"up\" or \"down\".",
			"reject_container_self" : "You cannot insert the {0} into itself.",
			"reject_container_size" : "The {1} is not big enough.",
			"reject_drink_solid" : "You cannot drink a solid.",
			"reject_eat_liquid" : "You cannot eat a liquid.",
			"reject_give_inanimate" : "You cannot give to an inanimate object.",
			"reject_give_liquid" : "You cannot give a liquid.",
			"reject_go" : "Use a compass point.",
			"reject_insert_liquid" : "The {1} cannot hold liquids.",
			"reject_insert_solid" : "The {1} cannot hold solids.",
			"reject_no_light" : "It is too dark.",
			"reject_no_know_how" : "I do not know how.",
			"reject_no_node" : "There is no such node id.",
			"reject_no_writing" : "There is no writing.",
			"reject_not_container" : "That is not a container.",
			"reject_not_empty" : "There is already something in that container.",
			"reject_not_liquid" : "That is not a liquid.",
			"reject_not_consumable" : "You cannot consume that.",
			"reject_not_portable" : "You cannot move that.",
			"reject_not_wearable" : "You cannot wear the {0}.",
			"reject_obstruction_known" : "You are blocked by {0}.",
			"reject_obstruction_unknown" : "You are blocked by something here.",
			"reject_take_animate" : "You cannot take anything from the {1}.",
			"reject_take_liquid" : "You cannot take a liquid.",
			"reject_too_full" : "That is too large to carry.",
		}.get(x)


	def setup_player(self):
		self.player = Player(9000, 0x3, self.lighthouse_location, self.default_inventory)
		self.player.instructions = 7


	def test_handle_climb(self):
		success, template, content_args, next_args = self.handler.handle_climb(self.command, self.player, "tree")

		self.assertFalse(success)
		self.assertEqual("Use \"up\" or \"down\".", template)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)


	def test_handle_commands(self):
		success, template, content_args, next_args = self.handler.handle_commands(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual("I know these commands: {0}.", template)
		self.assertEqual(["look, ne"], content_args)
		self.assertEqual([], next_args)


	def test_handle_consume_non_edible(self):
		self.item_start_location.add(self.book)

		success, template, content_args, next_args = self.handler.handle_consume(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual("You cannot consume that.", template)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.book in self.item_start_location.items.values())


	def test_handle_consume_edible(self):
		self.item_start_location.add(self.bread)

		success, template, content_args, next_args = self.handler.handle_consume(self.command, self.player, self.bread)

		self.assertTrue(success)
		self.assertEqual("You consume the {0}.", template)
		self.assertEqual([self.bread], content_args)
		self.assertEqual([self.bread], next_args)
		self.assertFalse(self.bread in self.item_start_location.items.values())
		self.assertFalse(self.item_start_location in self.bread.containers)


	def test_handle_describe_in_inventory(self):
		self.player.get_inventory().add(self.book)

		success, template, content_args, next_args = self.handler.handle_describe(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual("It is {0}.", template)
		self.assertEqual(["a book of fairytales"], content_args)
		self.assertEqual([self.book], next_args)


	def test_handle_describe_at_location(self):
		self.player.location.add(self.book)

		success, template, content_args, next_args = self.handler.handle_describe(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual("It is {0}. It is {1}.", template)
		self.assertEqual(["a small lamp", "on"], content_args)
		self.assertEqual([self.lamp], next_args)


	def test_handle_drink_solid(self):
		self.item_start_location.add(self.bread)

		success, template, content_args, next_args = self.handler.handle_drink(self.command, self.player, self.bread)

		self.assertFalse(success)
		self.assertEqual("You cannot drink a solid.", template)
		self.assertEqual([self.bread], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.bread in self.item_start_location.items.values())


	def test_handle_drink_liquid(self):
		self.bottle.add(self.water)

		success, template, content_args, next_args = self.handler.handle_drink(self.command, self.player, self.water)

		self.assertTrue(success)
		self.assertEqual("You consume the {0}.", template)
		self.assertEqual([self.water], content_args)
		self.assertEqual([self.water], next_args)
		self.assertFalse(self.water in self.bottle.items.values())


	def test_handle_drop_non_wearable(self):
		self.player.get_inventory().add(self.lamp)

		success, template, content_args, next_args = self.handler.handle_drop(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual("Dropped.", template)
		self.assertEqual([self.lamp], content_args)
		self.assertEqual([self.lamp], next_args)
		self.assertFalse(self.lamp in self.default_inventory.items.values())
		self.assertTrue(self.lamp in self.player.location.items.values())


	def test_handle_drop_wearable(self):
		self.player.get_inventory().add(self.suit)
		self.suit.being_worn = True

		success, template, content_args, next_args = self.handler.handle_drop(self.command, self.player, self.suit)

		self.assertTrue(success)
		self.assertEqual("Dropped.", template)
		self.assertEqual([self.suit], content_args)
		self.assertEqual([self.suit], next_args)
		self.assertFalse(self.suit in self.player.get_inventory().items.values())
		self.assertTrue(self.suit in self.player.location.items.values())
		self.assertFalse(self.suit.being_worn)


	def test_handle_drop_from_inside_container(self):
		self.basket.add(self.book)
		self.player.get_inventory().add(self.basket)

		success, template, content_args, next_args = self.handler.handle_drop(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual("Dropped.", template)
		self.assertEqual([self.book], content_args)
		self.assertEqual([self.book], next_args)
		self.assertFalse(self.book in self.player.get_inventory().items.values())
		self.assertTrue(self.book in self.player.location.items.values())


	def test_handle_drop_liquid(self):
		self.bottle.add(self.water)
		self.player.get_inventory().add(self.bottle)

		success, template, content_args, next_args = self.handler.handle_drop(self.command, self.player, self.water)

		self.assertTrue(success)
		self.assertEqual("You pour the liquid away.", template)
		self.assertEqual([self.water, self.bottle], content_args)
		self.assertEqual([self.water], next_args)
		self.assertFalse(self.water in self.bottle.items.values())
		self.assertFalse(self.water in self.player.location.items.values())
		self.assertFalse(self.bottle in self.water.containers)


	def test_handle_eat_liquid(self):
		self.item_start_location.add(self.water)

		success, template, content_args, next_args = self.handler.handle_eat(self.command, self.player, self.water)

		self.assertFalse(success)
		self.assertEqual("You cannot eat a liquid.", template)
		self.assertEqual([self.water], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.water in self.item_start_location.items.values())


	def test_handle_eat_solid(self):
		success, template, content_args, next_args = self.handler.handle_eat(self.command, self.player, self.bread)

		self.assertTrue(success)
		self.assertEqual("You consume the {0}.", template)
		self.assertEqual([self.bread], content_args)
		self.assertEqual([self.bread], next_args)
		self.assertFalse(self.bread in self.item_start_location.items.values())


	def test_handle_empty_non_container(self):
		self.player.get_inventory().add(self.book)

		success, template, content_args, next_args = self.handler.handle_empty(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual("That is not a container.", template)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)


	def test_handle_empty_already_empty(self):
		self.player.get_inventory().add(self.basket)

		success, template, content_args, next_args = self.handler.handle_empty(self.command, self.player, self.basket)

		self.assertFalse(success)
		self.assertEqual("It is already empty.", template)
		self.assertEqual([self.basket], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.basket.has_items())


	def test_handle_empty_liquid(self):
		self.bottle.add(self.water)
		self.player.get_inventory().add(self.bottle)

		success, template, content_args, next_args = self.handler.handle_empty(self.command, self.player, self.bottle)

		self.assertTrue(success)
		self.assertEqual("You pour the {1} out of the {0}.", template)
		self.assertEqual([self.bottle, self.water], content_args)
		self.assertEqual([self.bottle], next_args)
		self.assertFalse(self.water in self.bottle.items.values())
		self.assertFalse(self.water in self.player.location.items.values())
		self.assertFalse(self.bottle in self.water.containers)


	def test_handle_empty_solid_in_inventory(self):
		self.basket.add(self.book)
		self.player.get_inventory().add(self.basket)

		success, template, content_args, next_args = self.handler.handle_empty(self.command, self.player, self.basket)

		self.assertTrue(success)
		self.assertEqual("You take the {1} out of the {0}.", template)
		self.assertEqual([self.basket, self.book], content_args)
		self.assertEqual([self.basket], next_args)
		self.assertFalse(self.book in self.basket.items.values())
		self.assertTrue(self.book in self.player.get_inventory().items.values())
		self.assertFalse(self.book in self.player.location.items.values())


	def test_handle_empty_solid_at_location(self):
		self.basket.add(self.book)
		self.player.location.add(self.basket)

		success, template, content_args, next_args = self.handler.handle_empty(self.command, self.player, self.basket)

		self.assertTrue(success)
		self.assertEqual("You take the {1} out of the {0}.", template)
		self.assertEqual([self.basket, self.book], content_args)
		self.assertEqual([self.basket], next_args)
		self.assertFalse(self.book in self.basket.items.values())
		self.assertFalse(self.book in self.player.get_inventory().items.values())
		self.assertTrue(self.book in self.player.location.items.values())


	def test_handle_explain_default(self):
		success, template, content_args, next_args = self.handler.handle_explain(self.command, self.player, "dreams")

		self.assertFalse(success)
		self.assertEqual("I have no explanation.", template)
		self.assertEqual(["dreams"], content_args)
		self.assertEqual([], next_args)


	def test_handle_explain_non_default(self):
		success, template, content_args, next_args = self.handler.handle_explain(self.command, self.player, "spaize")

		self.assertTrue(success)
		self.assertEqual("Spaize is space-maize.", template)
		self.assertEqual(["spaize"], content_args)
		self.assertEqual(["spaize"], next_args)


	def test_feed_non_sentient(self):
		success, template, content_args, next_args = self.handler.handle_feed(self.command, self.player, self.bread, self.book)

		self.assertFalse(success)
		self.assertEqual("You cannot give to an inanimate object.", template)
		self.assertEqual([self.bread, self.book], content_args)
		self.assertEqual([], next_args)


	def test_feed_non_edible(self):
		success, template, content_args, next_args = self.handler.handle_feed(self.command, self.player, self.book, self.cat)

		self.assertFalse(success)
		self.assertEqual("You cannot consume that.", template)
		self.assertEqual([self.book, self.cat], content_args)
		self.assertEqual([], next_args)


	def test_feed_valid(self):
		success, template, content_args, next_args = self.handler.handle_feed(self.command, self.player, self.bread, self.cat)

		self.assertTrue(success)
		self.assertEqual("You feed the {0} to the {1}.", template)
		self.assertEqual([self.bread, self.cat], content_args)
		self.assertEqual([self.bread, self.cat], next_args)


	def test_handle_give_non_sentient_recipient(self):
		self.player.get_inventory().add(self.book)

		success, template, content_args, next_args = self.handler.handle_give(self.command, self.player, self.book, self.lamp)

		self.assertFalse(success)
		self.assertEqual("You cannot give to an inanimate object.", template)
		self.assertEqual([self.book, self.lamp], content_args)
		self.assertEqual([], next_args)


	def test_handle_give_liquid_item(self):
		self.bottle.add(self.water)
		self.player.get_inventory().add(self.bottle)

		success, template, content_args, next_args = self.handler.handle_give(self.command, self.player, self.water, self.cat)

		self.assertFalse(success)
		self.assertEqual("You cannot give a liquid.", template)
		self.assertEqual([self.water, self.cat], content_args)
		self.assertEqual([], next_args)


	def test_handle_give_valid(self):
		self.player.get_inventory().add(self.book)

		success, template, content_args, next_args = self.handler.handle_give(self.command, self.player, self.book, self.cat)

		self.assertTrue(success)
		self.assertEqual("Given.", template)
		self.assertEqual([self.book, self.cat], content_args)
		self.assertEqual([self.book, self.cat], next_args)
		self.assertFalse(self.book in self.player.get_inventory().items.values())
		self.assertFalse(self.player.get_inventory() in self.book.containers)


	def test_handle_go_with_obstruction(self):
		self.player.location.add(self.obstruction)
		self.player.location.directions[Direction.SOUTH] = self.beach_location

		success, template, content_args, next_args = self.handler.handle_go(self.command, self.player, self.beach_location)

		self.assertFalse(success)
		self.assertEqual("You are blocked by {0}.", template)
		self.assertEqual(["an obstruction"], content_args)
		self.assertEqual([], next_args)


	def test_handle_go_with_obstruction_no_light(self):
		self.player.location = self.mine_location
		self.player.location.add(self.obstruction)
		self.player.location.directions[Direction.EAST] = self.beach_location

		success, template, content_args, next_args = self.handler.handle_go(self.command, self.player, self.beach_location)

		self.assertFalse(success)
		self.assertEqual("You are blocked by something here.", template)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)


	def test_handle_go_with_obstruction_to_previous_location(self):
		self.beach_location.add(self.obstruction)
		self.player.location.directions[Direction.SOUTH] = self.beach_location
		self.beach_location.directions[Direction.NORTH] = self.lighthouse_location

		self.handler.handle_go(self.command, self.player, self.beach_location)
		success, template, content_args, next_args = self.handler.handle_go(self.command, self.player, self.lighthouse_location)

		self.assertTrue(success)
		self.assertEqual("", template)
		self.assertEqual([], content_args)
		self.assertEqual([self.lighthouse_location, self.beach_location], next_args)
		self.assertIs(self.lighthouse_location, self.player.location)
		self.assertIs(self.beach_location, self.player.previous_location)


	def test_handle_go_without_obstruction_two_way(self):
		self.player.location.directions[Direction.SOUTH] = self.beach_location
		self.beach_location.directions[Direction.NORTH] = self.player.location

		success, template, content_args, next_args = self.handler.handle_go(self.command, self.player, self.beach_location)

		self.assertTrue(success)
		self.assertEqual("", template)
		self.assertEqual([], content_args)
		self.assertEqual([self.beach_location, self.lighthouse_location], next_args)
		self.assertIs(self.beach_location, self.player.location)
		self.assertIs(self.lighthouse_location, self.player.previous_location)


	def test_handle_go_without_obstruction_one_way(self):
		self.player.location.directions[Direction.SOUTH] = self.beach_location

		success, template, content_args, next_args = self.handler.handle_go(self.command, self.player, self.beach_location)

		self.assertTrue(success)
		self.assertEqual("", template)
		self.assertEqual([], content_args)
		self.assertEqual([self.beach_location, self.lighthouse_location], next_args)
		self.assertIs(self.beach_location, self.player.location)
		self.assertIs(None, self.player.previous_location)


	def test_handle_go_disambiguate(self):
		success, template, content_args, next_args = self.handler.handle_go_disambiguate(self.command, self.player, "east")

		self.assertFalse(success)
		self.assertEqual("Use a compass point.", template)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)


	def test_handle_help(self):
		success, template, content_args, next_args = self.handler.handle_help(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual("Welcome and good luck.", template)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.assertEqual(6, self.player.instructions)


	def test_handle_hint_default(self):
		success, template, content_args, next_args = self.handler.handle_hint(self.command, self.player, "cat")

		self.assertFalse(success)
		self.assertEqual("I have no hint.", template)
		self.assertEqual(["cat"], content_args)
		self.assertEqual([], next_args)


	def test_handle_hint_non_default(self):
		success, template, content_args, next_args = self.handler.handle_hint(self.command, self.player, "magic")

		self.assertTrue(success)
		self.assertEqual("abrakadabra", template)
		self.assertEqual(["magic"], content_args)
		self.assertEqual(["magic"], next_args)


	def test_handle_immune_off(self):
		self.player.set_immune(True)

		success, template, content_args, next_args = self.handler.handle_immune(self.command, self.player, False)

		self.assertTrue(success)
		self.assertEqual("Immune off.", template)
		self.assertEqual([False], content_args)
		self.assertEqual([False], next_args)
		self.assertFalse(self.player.is_immune())


	def test_handle_immune_on(self):
		success, template, content_args, next_args = self.handler.handle_immune(self.command, self.player, True)

		self.assertTrue(success)
		self.assertEqual("Immune on.", template)
		self.assertEqual([True], content_args)
		self.assertEqual([True], next_args)
		self.assertTrue(self.player.is_immune())


	def test_handle_insert_into_non_container(self):
		success, template, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.book, self.lamp)

		self.assertFalse(success)
		self.assertEqual("That is not a container.", template)
		self.assertEqual([self.book, self.lamp], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_container_into_self(self):
		success, template, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.basket, self.basket)

		self.assertFalse(success)
		self.assertEqual("You cannot insert the {0} into itself.", template)
		self.assertEqual([self.basket, self.basket], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_already_inserted(self):
		self.basket.add(self.book)

		success, template, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.book, self.basket)

		self.assertFalse(success)
		self.assertEqual("The {0} is already in the {1}.", template)
		self.assertEqual([self.book, self.basket], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_non_portable(self):
		success, template, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.desk, self.basket)

		self.assertFalse(success)
		self.assertEqual("You cannot move that.", template)
		self.assertEqual([self.desk, self.basket], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_liquid_into_solid_container(self):
		self.item_start_location.add(self.water)

		success, template, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.water, self.basket)

		self.assertFalse(success)
		self.assertEqual("The {1} cannot hold liquids.", template)
		self.assertEqual([self.water, self.basket], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_solid_into_liquid_container(self):
		success, template, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.book, self.bottle)

		self.assertFalse(success)
		self.assertEqual("The {1} cannot hold solids.", template)
		self.assertEqual([self.book, self.bottle], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_container_not_empty(self):
		self.basket.add(self.lamp)

		success, template, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.book, self.basket)

		self.assertFalse(success)
		self.assertEqual("There is already something in that container.", template)
		self.assertEqual([self.book, self.basket], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_container_too_small(self):
		success, template, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.heavy_item, self.basket)

		self.assertFalse(success)
		self.assertEqual("The {1} is not big enough.", template)
		self.assertEqual([self.heavy_item, self.basket], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_valid_non_copyable(self):
		success, template, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.book, self.basket)

		self.assertTrue(success)
		self.assertEqual("Inserted.", template)
		self.assertEqual([self.book, self.basket], content_args)
		self.assertFalse(self.book.data_id in self.item_start_location.items)
		self.assertTrue(self.book.data_id in self.basket.items)
		self.assertIs(self.book, self.basket.items[self.book.data_id])
		self.assertEqual([self.book, self.basket], next_args)


	def test_handle_insert_valid_copyable(self):
		self.item_start_location.add(self.water)

		success, template, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.water, self.bottle)

		self.assertTrue(success)
		self.assertEqual("Inserted.", template)
		self.assertEqual([self.water, self.bottle], content_args)
		self.assertEqual([self.water, self.bottle], next_args)
		self.assertTrue(self.water.data_id in self.item_start_location.items)
		self.assertIs(self.water, self.item_start_location.items[self.water.data_id])
		self.assertTrue(self.water.data_id in self.bottle.items)
		self.assertIsNot(self.water, self.bottle.items[self.water.data_id])


	def test_handle_inventory_empty(self):
		success, template, content_args, next_args = self.handler.handle_inventory(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual("You have nothing.", template)
		self.assertEqual([""], content_args)
		self.assertEqual([], next_args)


	def test_handle_inventory_nonempty(self):
		self.player.get_inventory().add(self.book)

		success, template, content_args, next_args = self.handler.handle_inventory(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual("You have: {0}.", template)
		self.assertEqual(["\n\ta book"], content_args)
		self.assertEqual([], next_args)


	def test_handle_locate_at_location(self):
		self.player.location.add(self.book)

		success, template, content_args, next_args = self.handler.handle_locate(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual("The {0} is at {1}. ", template)
		self.assertEqual(["book", "['12:at a lighthouse']"], content_args)
		self.assertEqual([self.book], next_args)


	def test_handle_locate_in_item(self):
		self.basket.add(self.book)

		success, template, content_args, next_args = self.handler.handle_locate(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual("The {0} is at {1}. ", template)
		self.assertEqual(["book", "['1107:a basket']"], content_args)
		self.assertEqual([self.book], next_args)


	def test_handle_locate_in_inventory(self):
		self.player.get_inventory().add(self.book)

		success, template, content_args, next_args = self.handler.handle_locate(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual("The {0} is at {1}. ", template)
		self.assertEqual(["book", "['0:in the main inventory']"], content_args)
		self.assertEqual([self.book], next_args)


	def test_handle_locate_with_copies(self):
		self.player.location.add(self.water)
		self.bottle.insert(self.water)

		success, template, content_args, next_args = self.handler.handle_locate(self.command, self.player, self.water)

		self.assertTrue(success)
		self.assertEqual("The {0} is at {1}. Copies at {2}.", template)
		self.assertEqual(["water", "['12:at a lighthouse']", "['1108:a bottle']"], content_args)
		self.assertEqual([self.water], next_args)


	def test_handle_look_no_items(self):
		success, template, content_args, next_args = self.handler.handle_look(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual("You are {0}.", template)
		self.assertEqual(["at a lighthouse by the sea.", ""], content_args)
		self.assertEqual([], next_args)


	def test_handle_look_with_item(self):
		self.player.location.add(self.book)

		success, template, content_args, next_args = self.handler.handle_look(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual("You are {0}. Nearby: {1}.", template)
		self.assertEqual(["at a lighthouse by the sea.", "\n\ta book"], content_args)
		self.assertEqual([], next_args)


	def test_handle_look_with_silent_item(self):
		self.player.location.add(self.desk)

		success, template, content_args, next_args = self.handler.handle_look(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual("You are {0}.", template)
		self.assertEqual(["at a lighthouse by the sea.", ""], content_args)
		self.assertEqual([], next_args)


	def test_handle_node_no_arg(self):
		success, template, content_args, next_args = self.handler.handle_node(self.command, self.player)

		self.assertFalse(success)
		self.assertEqual("You are at node {0}.", template)
		self.assertEqual([12], content_args)
		self.assertEqual([], next_args)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_node_arg_invalid(self):
		success, template, content_args, next_args = self.handler.handle_node(self.command, self.player, "abc")

		self.assertFalse(success)
		self.assertEqual("There is no such node id.", template)
		self.assertEqual(["abc"], content_args)
		self.assertEqual([], next_args)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_node_arg_out_of_range(self):
		success, template, content_args, next_args = self.handler.handle_node(self.command, self.player, "61")

		self.assertFalse(success)
		self.assertEqual("There is no such node id.", template)
		self.assertEqual(["61"], content_args)
		self.assertEqual([], next_args)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_node_arg_valid(self):
		success, template, content_args, next_args = self.handler.handle_node(self.command, self.player, "13")

		self.assertTrue(success)
		self.assertEqual("", template)
		self.assertEqual([], content_args)
		self.assertEqual([self.beach_location, self.lighthouse_location], next_args)
		self.assertIs(self.beach_location, self.player.location)


	def test_handle_pick(self):
		self.player.location.add(self.book)

		success, template, content_args, next_args = self.handler.handle_pick(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual("Taken.", template)
		self.assertEqual([self.book], content_args)
		self.assertEqual([self.book], next_args)
		self.assertTrue(self.book in self.player.get_inventory().items.values())
		self.assertFalse(self.book in self.player.location.items.values())


	def test_pour_non_liquid(self):
		self.player.get_inventory().add(self.book)

		success, template, content_args, next_args = self.handler.handle_pour(self.command, self.player, self.book, self.lamp)

		self.assertFalse(success)
		self.assertEqual("That is not a liquid.", template)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)


	def test_handle_pour_liquid(self):
		self.bottle.add(self.water)
		self.player.get_inventory().add(self.bottle)

		success, template, content_args, next_args = self.handler.handle_pour(self.command, self.player, self.water, self.lamp)

		self.assertTrue(success)
		self.assertEqual("You pour the liquid onto the {1}.", template)
		self.assertEqual([self.water, self.lamp, self.bottle], content_args)
		self.assertEqual([self.water, self.lamp], next_args)
		self.assertFalse(self.water in self.bottle.items.values())
		self.assertFalse(self.water in self.player.location.items.values())


	def test_handle_quit(self):
		success, template, content_args, next_args = self.handler.handle_quit(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual("OK.", template)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.assertEqual(6, self.player.instructions)
		self.assertFalse(self.player.is_playing())


	def test_handle_read_no_writing(self):
		self.player.get_inventory().add(self.lamp)

		success, template, content_args, next_args = self.handler.handle_read(self.command, self.player, self.lamp)

		self.assertFalse(success)
		self.assertEqual("There is no writing.", template)
		self.assertEqual([self.lamp], content_args)
		self.assertEqual([], next_args)


	def test_handle_read_with_writing(self):
		self.player.get_inventory().add(self.book)

		success, template, content_args, next_args = self.handler.handle_read(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual("It reads {0}.", template)
		self.assertEqual(["The Pied Piper"], content_args)
		self.assertEqual([self.book], next_args)


	def test_handle_say_no_audience(self):
		success, template, content_args, next_args = self.handler.handle_say(self.command, self.player, "hello")

		self.assertTrue(success)
		self.assertEqual("You say {0}.", template)
		self.assertEqual(["hello"], content_args)
		self.assertEqual(["hello"], next_args)


	def test_handle_say_no_sentient_audience(self):
		success, template, content_args, next_args = self.handler.handle_say(self.command, self.player, "hello", self.book)

		self.assertTrue(success)
		self.assertEqual("You say {0} at the {1}.", template)
		self.assertEqual(["hello", self.book], content_args)
		self.assertEqual(["hello", self.book], next_args)


	def test_handle_say_with_sentient_audience(self):
		success, template, content_args, next_args = self.handler.handle_say(self.command, self.player, "hello", self.cat)

		self.assertTrue(success)
		self.assertEqual("You say {0} to the {1}.", template)
		self.assertEqual(["hello", self.cat], content_args)
		self.assertEqual(["hello", self.cat], next_args)


	def test_handle_score_zero(self):
		self.data.get_puzzle_count.return_value = 17

		success, template, content_args, next_args = self.handler.handle_score(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual("Current score: {0} points. Maximum score: {1} points. Instructions entered: {2}.", template)
		self.assertEqual([0, 119, 6], content_args)
		self.assertEqual([], next_args)
		self.assertEqual(6, self.player.instructions)


	def test_handle_score_with_puzzles_solved(self):
		self.data.get_puzzle_count.return_value = 17
		self.player.solve_puzzle(Mock())
		self.player.solve_puzzle(Mock())

		success, template, content_args, next_args = self.handler.handle_score(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual("Current score: {0} points. Maximum score: {1} points. Instructions entered: {2}.", template)
		self.assertEqual([14, 119, 6], content_args)
		self.assertEqual([], next_args)
		self.assertEqual(6, self.player.instructions)


	def test_handle_set(self):
		self.player.get_inventory().add(self.lamp)

		success, template, content_args, next_args = self.handler.handle_set(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual("Dropped.", template)
		self.assertEqual([self.lamp], content_args)
		self.assertEqual([self.lamp], next_args)
		self.assertFalse(self.lamp in self.player.get_inventory().items.values())
		self.assertTrue(self.lamp in self.player.location.items.values())


	def test_handle_switch_off_to_off(self):
		self.lamp.switch_off()

		success, template, content_args, next_args = self.handler.handle_switch(self.command, self.player, self.lamp, SwitchTransition.OFF)

		self.assertFalse(success)
		self.assertEqual("The {0} is already {1}.", template)
		self.assertEqual([self.lamp, "off"], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.lamp.is_on())


	def test_handle_switch_off_to_on(self):
		self.lamp.switch_off()

		success, template, content_args, next_args = self.handler.handle_switch(self.command, self.player, self.lamp, SwitchTransition.ON)

		self.assertTrue(success)
		self.assertEqual("The {0} is now {1}.", template)
		self.assertEqual([self.lamp, "on"], content_args)
		self.assertEqual([self.lamp, SwitchTransition.ON], next_args)
		self.assertTrue(self.lamp.is_on())


	def test_handle_switch_on_to_off(self):
		self.lamp.switch_on()

		success, template, content_args, next_args = self.handler.handle_switch(self.command, self.player, self.lamp, SwitchTransition.OFF)

		self.assertTrue(success)
		self.assertEqual("The {0} is now {1}.", template)
		self.assertEqual([self.lamp, "off"], content_args)
		self.assertEqual([self.lamp, SwitchTransition.OFF], next_args)
		self.assertFalse(self.lamp.is_on())


	def test_handle_switch_on_to_on(self):
		self.lamp.switch_on()

		success, template, content_args, next_args = self.handler.handle_switch(self.command, self.player, self.lamp, SwitchTransition.ON)

		self.assertFalse(success)
		self.assertEqual("The {0} is already {1}.", template)
		self.assertEqual([self.lamp, "on"], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.lamp.is_on())


	def test_handle_take_from_sentient_simple(self):
		self.cat.add(self.book)

		success, template, content_args, next_args = self.handler.handle_take(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual("You cannot take anything from the {1}.", template)
		self.assertEqual([self.book, self.cat], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.book in self.player.get_inventory().items.values())
		self.assertTrue(self.book in self.cat.items.values())


	def test_handle_take_from_sentient_nested(self):
		self.basket.add(self.book)
		self.cat.add(self.basket)

		success, template, content_args, next_args = self.handler.handle_take(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual("You cannot take anything from the {1}.", template)
		self.assertEqual([self.book, self.cat], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.book in self.player.get_inventory().items.values())
		self.assertTrue(self.basket in self.cat.items.values())
		self.assertTrue(self.book in self.basket.items.values())


	def test_handle_take_not_portable(self):
		self.player.location.add(self.desk)

		success, template, content_args, next_args = self.handler.handle_take(self.command, self.player, self.desk)

		self.assertFalse(success)
		self.assertEqual("You cannot move that.", template)
		self.assertEqual([self.desk], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.desk in self.player.get_inventory().items.values())
		self.assertTrue(self.desk in self.player.location.items.values())


	def test_handle_take_obstruction(self):
		self.player.location.add(self.mobile_obstruction)

		success, template, content_args, next_args = self.handler.handle_take(self.command, self.player, self.mobile_obstruction)

		self.assertFalse(success)
		self.assertEqual("You cannot move that.", template)
		self.assertEqual([self.mobile_obstruction], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.mobile_obstruction in self.player.get_inventory().items.values())
		self.assertTrue(self.mobile_obstruction in self.player.location.items.values())


	def test_handle_take_over_capacity(self):
		self.player.location.add(self.book)
		self.player.get_inventory().add(self.heavy_item)

		success, template, content_args, next_args = self.handler.handle_take(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual("That is too large to carry.", template)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.book in self.player.get_inventory().items.values())
		self.assertTrue(self.book in self.player.location.items.values())


	def test_handle_take_at_location(self):
		self.player.location.add(self.book)

		success, template, content_args, next_args = self.handler.handle_take(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual("Taken.", template)
		self.assertEqual([self.book], content_args)
		self.assertEqual([self.book], next_args)
		self.assertTrue(self.book in self.player.get_inventory().items.values())
		self.assertFalse(self.book in self.player.location.items.values())


	def test_handle_take_liquid(self):
		self.player.location.add(self.water)

		success, template, content_args, next_args = self.handler.handle_take(self.command, self.player, self.water)

		self.assertFalse(success)
		self.assertEqual("You cannot take a liquid.", template)
		self.assertEqual([self.water], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.water in self.player.get_inventory().items.values())
		self.assertTrue(self.water in self.player.location.items.values())


	def test_handle_take_multi_arg(self):
		self.player.location.add(self.book)
		self.player.get_inventory().add(self.basket)

		success, template, content_args, next_args = self.handler.handle_take(self.command, self.player, self.book, self.basket)

		self.assertTrue(success)
		self.assertEqual("Inserted.", template)
		self.assertEqual([self.book, self.basket], content_args)
		self.assertEqual([self.book, self.basket], next_args)
		self.assertTrue(self.book in self.basket.items.values())


	def test_handle_teleport(self):
		success, template, content_args, next_args = self.handler.handle_teleport(self.command, self.player, self.beach_location)

		self.assertTrue(success)
		self.assertEqual("", template)
		self.assertEqual([], content_args)
		self.assertEqual([self.beach_location, self.lighthouse_location], next_args)
		self.assertIs(self.beach_location, self.player.location)
		self.assertIs(None, self.player.previous_location)


	def test_handle_toggle_non_switchable_item(self):
		success, template, content_args, next_args = self.handler.handle_toggle(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual("I do not know how.", template)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)


	def test_handle_toggle_off_to_on(self):
		self.lamp.attributes &= ~0x10

		success, template, content_args, next_args = self.handler.handle_toggle(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual("The {0} is now {1}.", template)
		self.assertEqual([self.lamp, "on"], content_args)
		self.assertEqual([self.lamp, SwitchTransition.TOGGLE], next_args)
		self.assertTrue(self.lamp.is_on())


	def test_handle_toggle_on_to_off(self):
		self.lamp.attributes |= 0x10

		success, template, content_args, next_args = self.handler.handle_toggle(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual("The {0} is now {1}.", template)
		self.assertEqual([self.lamp, "off"], content_args)
		self.assertEqual([self.lamp, SwitchTransition.TOGGLE], next_args)
		self.assertFalse(self.lamp.is_on())


	def test_handle_verbose_off(self):
		self.player.set_verbose(True)

		success, template, content_args, next_args = self.handler.handle_verbose(self.command, self.player, False)

		self.assertTrue(success)
		self.assertEqual("Verbose off.", template)
		self.assertEqual([False], content_args)
		self.assertEqual([False], next_args)
		self.assertFalse(self.player.is_verbose())


	def test_handle_verbose_on(self):
		self.player.set_verbose(False)

		success, template, content_args, next_args = self.handler.handle_verbose(self.command, self.player, True)

		self.assertTrue(success)
		self.assertEqual("Verbose on.", template)
		self.assertEqual([True], content_args)
		self.assertEqual([True], next_args)
		self.assertTrue(self.player.is_verbose())


	def test_handle_wear_not_wearable(self):
		success, template, content_args, next_args = self.handler.handle_wear(self.command, self.player, self.lamp)

		self.assertFalse(success)
		self.assertEqual("You cannot wear the {0}.", template)
		self.assertEqual([self.lamp], content_args)
		self.assertEqual([], next_args)


	def test_handle_wear_wearable_already_wearing(self):
		self.suit.being_worn = True

		success, template, content_args, next_args = self.handler.handle_wear(self.command, self.player, self.suit)

		self.assertFalse(success)
		self.assertEqual("You are already wearing the {0}.", template)
		self.assertEqual([self.suit], content_args)
		self.assertEqual([], next_args)


	def test_handle_wear_wearable_not_already_wearing(self):
		self.player.location.add(self.suit)
		self.suit.being_worn = False

		success, template, content_args, next_args = self.handler.handle_wear(self.command, self.player, self.suit)

		self.assertTrue(success)
		self.assertEqual("You are wearing the {0}.", template)
		self.assertEqual([self.suit], content_args)
		self.assertEqual([self.suit], next_args)


if __name__ == "__main__":
	unittest.main()

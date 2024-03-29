import unittest
from unittest.mock import Mock

from adventure.command import Command
from adventure.command_handler import CommandHandler
from adventure.direction import Direction
from adventure.element import Labels
from adventure.inventory import Inventory
from adventure.item import Item, ContainerItem, SentientItem, SwitchableItem, SwitchInfo, SwitchTransition, UsableItem, Transformation
from adventure.location import Location
from adventure.player import Player

class TestCommandHandler(unittest.TestCase):

	def setUp(self):
		self.setup_data()
		self.setup_player()
		self.command = Command(0, 0x0, 0x0, [], [""],  {})
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
		self.data.get_smash_command_id.return_value = 37


	def setup_inventories(self):
		self.default_inventory = Inventory(0, 0x1, Labels("Main Inventory", "in the main inventory", ", where items live usually."), 13)


	def setup_locations(self):
		self.beach_location = Location(13, 0x603, Labels("Beach", "on a beach", " of black sand"))
		self.lighthouse_location = Location(12, 0x603, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.mine_location = Location(11, 0x602, Labels("Mines", "in the mines", ". There are dark passages everywhere."))
		self.sun_location = Location(10, 0x613, Labels("Sun", "in the sun", ". It is hot."))
		self.cave_location = Location(9, 0x402, Labels("Cave", "in a cave", ". It is dark"))
		self.airless_location = Location(8, 0x400, Labels("Airless", "in an airless room", ". There is no air here"))
		self.water_location = Location(8, 0xA02, Labels("River", "on a river", ". it moves fast"))
		self.item_start_location = Location(0, 0x602, Labels("Start", "at the start", ", where items start out."))

		self.data.get_location.side_effect = lambda x: {
			11 : self.mine_location,
			12 : self.lighthouse_location,
			13 : self.beach_location,
		}.get(x)


	def setup_items(self):
		self.book = Item(1105, 2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper", {})
		lamp_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "off", "on")
		self.lamp = SwitchableItem(1043, 0x101A, Labels("lamp", "a lamp", "a small lamp"), 2, None, {}, lamp_switching_info)
		self.lamp.switched_element = self.lamp
		self.kohlrabi = Item(1042, 0x2002, Labels("kohlrabi", "some kohlrabi", "some kohlrabi, a cabbage cultivar"), 3, None, {})
		self.desk = Item(1000, 0x20000, Labels("desk", "a desk", "a large mahogany desk"), 6, None, {})
		self.heavy_item = Item(1001, 0x2, Labels("heavy", "a heavy item", "a dummy heavy item"), 13, None, {})
		self.obstruction = Item(1002, 0x4, Labels("obstruction", "an obstruction", "an obstruction blocking you"), 8, None, {})
		self.mobile_obstruction = Item(1003, 0x6, Labels("mobile_obstruction", "a mobile obstruction", "a mobile obstruction"), 5, None, {})
		self.basket = ContainerItem(1107, 0x3, Labels("basket", "a basket", "a large basket"), 6, None, {})
		self.suit = UsableItem(1046, 0x402, Labels("suit", "a suit", "a space-suit"), 2, None, {}, Item.ATTRIBUTE_GIVES_AIR)
		self.shards = Item(1114, 0x2, Labels("shards", "some shards", "some glass shards"), 1, None, {})
		self.bottle = ContainerItem(1108, 0x4203, Labels("bottle", "a bottle", "a small glass bottle"), 3, None, {})
		self.bottle.transformations[37] = Transformation(replacement=self.shards, tool=None, material=None)
		self.cat = SentientItem(1047, 0x80003, Labels("cat", "a cat", "a black cat"), 3, None, {})
		self.bread = Item(1109, 0x2002, Labels("bread", "some bread", "a loaf of bread"), 2, None, {})
		self.water = Item(1110, 0x22902, Labels("water", "some water", "some water"), 1, None, {})
		self.raft = UsableItem(1118, 0x10000, Labels("raft", "a raft", "a rickety raft"), 6, None, {}, Item.ATTRIBUTE_GIVES_LAND)
		self.boat = UsableItem(1119, 0x10000, Labels("boat", "a boat", "a wooden boat"), 6, None, {}, Item.ATTRIBUTE_GIVES_LAND)

		self.ash = Item(1112, 0x0, Labels("ash", "some ash", "some black ash"), 1, None, {})
		self.matches = Item(1113, 0x200000, Labels("matches", "some matches", "a box of matches"), 2, None, {})
		self.paper = Item(1111, 0x100000, Labels("paper", "some paper", "some old paper"), 1, None, {})
		self.paper.transformations[6] = Transformation(replacement=self.ash, tool=self.matches, material=None)

		self.dust = Item(1115, 0x2, Labels("dust", "some dust", "some grey dust"), 1, None, {})
		self.rock = Item(1116, 0x1000, Labels("rock", "a rock", "a large rock"), 15, None, {})
		self.rock.transformations[37] = Transformation(replacement=self.dust, tool=None, material=None)

		self.tray = ContainerItem(1117, 0x4003, Labels("tray", "a tray", "a glass tray"), 4, None, {})
		self.tray.transformations[37] = Transformation(replacement=self.shards, tool=None, material=None)

		self.timber = Item(1120, 0x2, Labels("plank", "a plank of timber", "a small plank of timber"), 3, None, {})
		self.axe = Item(1121, 0x400002, Labels("axe", "an axe", "a small axe"), 3, None, {})
		self.log = Item(1122, 0x0, Labels("log", "a log of wood", "a large log of wood"), 6, None, {})
		self.log.transformations[78] = Transformation(replacement=self.timber, tool=self.axe, material=None)

		self.rope = Item(1123, 0x2, Labels("rope", "some rope", "a small length of rope"), 2, None, {})
		self.log.transformations[57] = Transformation(replacement=self.raft, tool=None, material=self.rope)


	def setup_texts(self):
		self.data.get_hint.side_effect = lambda x: {
			"default" : "I have no hint.",
			"magic" : "abrakadabra",
		}.get(x)

		self.data.get_explanation.side_effect = lambda x: {
			"default" : "I have no explanation.",
			"spaize" : "Spaize is space-maize.",
		}.get(x)


	def setup_player(self):
		self.player = Player(9000, 0x3, self.lighthouse_location, self.lighthouse_location, self.lighthouse_location, self.cave_location, self.default_inventory)
		self.player.instructions = 7


	def test_handle_burn_not_burnable(self):
		self.item_start_location.add(self.water)

		success, template_keys, content_args, next_args = self.handler.handle_burn(self.command, self.player, self.water)

		self.assertFalse(success)
		self.assertEqual(["reject_not_burnable"], template_keys)
		self.assertEqual([self.water], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.water in self.item_start_location.items)


	def test_handle_burn_burnable_no_burning_tool(self):
		burn_command = Command(6, 0x9, 0x0, [], ["burn"], {})
		self.item_start_location.insert(self.paper)

		success, template_keys, content_args, next_args = self.handler.handle_burn(burn_command, self.player, self.paper)

		self.assertFalse(success)
		self.assertEqual(["reject_no_tool"], template_keys)
		self.assertEqual([self.paper, "burn"], content_args)
		self.assertTrue(self.paper in self.item_start_location.items)


	def test_handle_burn_burnable_with_burning_tool(self):
		burn_command = Command(6, 0x9, 0x0, [], ["burn"], {})
		self.item_start_location.insert(self.paper)
		self.player.get_inventory().add(self.matches)

		success, template_keys, content_args, next_args = self.handler.handle_burn(burn_command, self.player, self.paper)

		self.assertTrue(success)
		self.assertEqual(["confirm_burn"], template_keys)
		self.assertEqual([self.paper, "some ash"], content_args)
		self.assertEqual([self.paper], next_args)
		self.assertFalse(self.paper in self.item_start_location.items)
		self.assertTrue(self.ash in self.item_start_location.items)


	def test_handle_chop_not_choppable(self):
		self.item_start_location.add(self.water)

		success, template_keys, content_args, next_args = self.handler.handle_chop(self.command, self.player, self.water)

		self.assertFalse(success)
		self.assertEqual(["reject_not_choppable"], template_keys)
		self.assertEqual([self.water], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.water in self.item_start_location.items)


	def test_handle_chop_choppable_no_chopping_tool(self):
		chop_command = Command(78, 0x0, 0x0, [], ["chop"], {})
		self.item_start_location.add(self.log)

		success, template_keys, content_args, next_args = self.handler.handle_chop(chop_command, self.player, self.log)

		self.assertFalse(success)
		self.assertEqual(["reject_no_tool"], template_keys)
		self.assertEqual([self.log, "chop"], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.log in self.item_start_location.items)


	def test_handle_chop_choppable_with_chopping_tool(self):
		chop_command = Command(78, 0x0, 0x0, [], ["chop"], {})
		self.item_start_location.add(self.log)
		self.player.get_inventory().add(self.axe)

		success, template_keys, content_args, next_args = self.handler.handle_chop(chop_command, self.player, self.log)

		self.assertTrue(success)
		self.assertEqual(["confirm_chop"], template_keys)
		self.assertEqual([self.log, "a plank of timber"], content_args)
		self.assertEqual([self.log], next_args)
		self.assertFalse(self.log in self.item_start_location.items)
		self.assertTrue(self.timber in self.item_start_location.items)


	def test_handle_climb(self):
		success, template_keys, content_args, next_args = self.handler.handle_climb(self.command, self.player, "tree")

		self.assertFalse(success)
		self.assertEqual(["reject_climb"], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)


	def test_handle_commands(self):
		success, template_keys, content_args, next_args = self.handler.handle_commands(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual(["describe_commands"], template_keys)
		self.assertEqual(["look, ne"], content_args)
		self.assertEqual([], next_args)


	def test_handle_consume_non_edible(self):
		self.item_start_location.add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_consume(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual(["reject_not_consumable"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.book in self.item_start_location.items)


	def test_handle_consume_edible(self):
		self.item_start_location.add(self.bread)

		success, template_keys, content_args, next_args = self.handler.handle_consume(self.command, self.player, self.bread)

		self.assertTrue(success)
		self.assertEqual(["confirm_consume"], template_keys)
		self.assertEqual([self.bread], content_args)
		self.assertEqual([self.bread], next_args)
		self.assertFalse(self.bread in self.item_start_location.items)
		self.assertFalse(self.item_start_location in self.bread.containers)


	def test_handle_describe_in_inventory(self):
		self.player.get_inventory().add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_describe(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual(["describe_item"], template_keys)
		self.assertEqual(["a book of fairytales"], content_args)
		self.assertEqual([self.book], next_args)


	def test_handle_describe_at_location(self):
		self.player.location.add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_describe(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual(["describe_item", "describe_item_switch"], template_keys)
		self.assertEqual(["a small lamp", "on"], content_args)
		self.assertEqual([self.lamp], next_args)


	def test_handle_disembark_not_sailable(self):
		success, template_keys, content_args, next_args = self.handler.handle_disembark(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual(["reject_not_sailable"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)


	def test_handle_disembark_not_sailing(self):
		success, template_keys, content_args, next_args = self.handler.handle_disembark(self.command, self.player, self.raft)

		self.assertFalse(success)
		self.assertEqual(["reject_not_sailing"], template_keys)
		self.assertEqual([self.raft], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.raft.being_used)


	def test_handle_disembark_success(self):
		self.raft.being_used = True

		success, template_keys, content_args, next_args = self.handler.handle_disembark(self.command, self.player, self.raft)

		self.assertTrue(success)
		self.assertEqual(["confirm_disembark"], template_keys)
		self.assertEqual([self.raft], content_args)
		self.assertEqual([self.raft], next_args)
		self.assertFalse(self.raft.being_used)


	def test_handle_drink_solid(self):
		self.item_start_location.add(self.bread)

		success, template_keys, content_args, next_args = self.handler.handle_drink(self.command, self.player, self.bread)

		self.assertFalse(success)
		self.assertEqual(["reject_drink_solid"], template_keys)
		self.assertEqual([self.bread], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.bread in self.item_start_location.items)


	def test_handle_drink_liquid(self):
		self.bottle.add(self.water)

		success, template_keys, content_args, next_args = self.handler.handle_drink(self.command, self.player, self.water)

		self.assertTrue(success)
		self.assertEqual(["confirm_consume"], template_keys)
		self.assertEqual([self.water], content_args)
		self.assertEqual([self.water], next_args)
		self.assertFalse(self.water in self.bottle.items)


	def test_handle_drop_non_wearable(self):
		self.player.get_inventory().add(self.lamp)

		success, template_keys, content_args, next_args = self.handler.handle_drop(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual(["confirm_dropped"], template_keys)
		self.assertEqual([self.lamp], content_args)
		self.assertEqual([self.lamp], next_args)
		self.assertFalse(self.lamp in self.default_inventory.items)
		self.assertTrue(self.lamp in self.player.location.items)


	def test_handle_drop_wearable(self):
		self.player.get_inventory().add(self.suit)
		self.suit.being_used = True

		success, template_keys, content_args, next_args = self.handler.handle_drop(self.command, self.player, self.suit)

		self.assertTrue(success)
		self.assertEqual(["confirm_dropped"], template_keys)
		self.assertEqual([self.suit], content_args)
		self.assertEqual([self.suit], next_args)
		self.assertFalse(self.suit in self.player.get_inventory().items)
		self.assertTrue(self.suit in self.player.location.items)
		self.assertFalse(self.suit.being_used)


	def test_handle_drop_from_inside_container(self):
		self.basket.add(self.book)
		self.player.get_inventory().add(self.basket)

		success, template_keys, content_args, next_args = self.handler.handle_drop(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual(["confirm_dropped"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([self.book], next_args)
		self.assertFalse(self.book in self.player.get_inventory().items)
		self.assertTrue(self.book in self.player.location.items)


	def test_handle_drop_liquid(self):
		self.bottle.add(self.water)
		self.player.get_inventory().add(self.bottle)

		success, template_keys, content_args, next_args = self.handler.handle_drop(self.command, self.player, self.water)

		self.assertTrue(success)
		self.assertEqual(["confirm_poured_no_destination"], template_keys)
		self.assertEqual([self.water, self.bottle], content_args)
		self.assertEqual([self.water], next_args)
		self.assertFalse(self.water in self.bottle.items)
		self.assertFalse(self.water in self.player.location.items)
		self.assertFalse(self.bottle in self.water.containers)


	def test_handle_drop_at_location_with_no_floor_non_fragile(self):
		self.player.location = self.cave_location
		self.cave_location.directions[Direction.DOWN] = self.mine_location
		self.player.get_inventory().add(self.lamp)

		success, template_keys, content_args, next_args = self.handler.handle_drop(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual(["confirm_dropped", "describe_item_falling"], template_keys)
		self.assertEqual([self.lamp], content_args)
		self.assertEqual([self.lamp], next_args)
		self.assertFalse(self.lamp in self.default_inventory.items)
		self.assertTrue(self.lamp in self.mine_location.items)


	def test_handle_drop_at_location_with_no_floor_fragile_empty(self):
		self.player.location = self.cave_location
		self.cave_location.directions[Direction.DOWN] = self.mine_location
		self.player.get_inventory().add(self.bottle)

		success, template_keys, content_args, next_args = self.handler.handle_drop(self.command, self.player, self.bottle)

		self.assertTrue(success)
		self.assertEqual(["confirm_dropped", "describe_item_falling", "describe_item_smash_hear"], template_keys)
		self.assertEqual([self.bottle, self.shards], content_args)
		self.assertEqual([self.bottle], next_args)
		self.assertFalse(self.bottle in self.default_inventory.items)
		self.assertFalse(self.bottle in self.mine_location.items)
		self.assertTrue(self.shards in self.mine_location.items)


	def test_handle_drop_at_location_with_no_floor_fragile_non_empty(self):
		self.player.location = self.cave_location
		self.cave_location.directions[Direction.DOWN] = self.mine_location
		self.tray.add(self.book)
		self.player.get_inventory().add(self.tray)

		success, template_keys, content_args, next_args = self.handler.handle_drop(self.command, self.player, self.tray)

		self.assertTrue(success)
		self.assertEqual(["confirm_dropped", "describe_item_falling", "describe_item_smash_hear", "describe_item_smash_release_solid"], template_keys)
		self.assertEqual([self.tray, self.shards, self.book], content_args)
		self.assertEqual([self.tray], next_args)
		self.assertFalse(self.tray in self.default_inventory.items)
		self.assertFalse(self.tray in self.mine_location.items)
		self.assertTrue(self.shards in self.mine_location.items)
		self.assertTrue(self.book in self.mine_location.items)


	def test_handle_drop_at_location_with_no_land(self):
		self.player.location = self.water_location
		self.player.get_inventory().add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_drop(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual(["confirm_dropped", "describe_item_sink"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([self.book], next_args)
		self.assertFalse(self.book in self.default_inventory.items)
		self.assertFalse(self.book in self.water_location.items)


	def test_handle_eat_liquid(self):
		self.item_start_location.add(self.water)

		success, template_keys, content_args, next_args = self.handler.handle_eat(self.command, self.player, self.water)

		self.assertFalse(success)
		self.assertEqual(["reject_eat_liquid"], template_keys)
		self.assertEqual([self.water], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.water in self.item_start_location.items)


	def test_handle_eat_solid(self):
		success, template_keys, content_args, next_args = self.handler.handle_eat(self.command, self.player, self.bread)

		self.assertTrue(success)
		self.assertEqual(["confirm_consume"], template_keys)
		self.assertEqual([self.bread], content_args)
		self.assertEqual([self.bread], next_args)
		self.assertFalse(self.bread in self.item_start_location.items)


	def test_handle_empty_non_container(self):
		self.player.get_inventory().add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_empty(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual(["reject_not_container"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)


	def test_handle_empty_already_empty(self):
		self.player.get_inventory().add(self.basket)

		success, template_keys, content_args, next_args = self.handler.handle_empty(self.command, self.player, self.basket)

		self.assertFalse(success)
		self.assertEqual(["reject_already_empty"], template_keys)
		self.assertEqual([self.basket], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.basket.has_items())


	def test_handle_empty_liquid(self):
		self.bottle.add(self.water)
		self.player.get_inventory().add(self.bottle)

		success, template_keys, content_args, next_args = self.handler.handle_empty(self.command, self.player, self.bottle)

		self.assertTrue(success)
		self.assertEqual(["confirm_emptied_liquid"], template_keys)
		self.assertEqual([self.bottle, self.water], content_args)
		self.assertEqual([self.bottle], next_args)
		self.assertFalse(self.water in self.bottle.items)
		self.assertFalse(self.water in self.player.location.items)
		self.assertFalse(self.bottle in self.water.containers)


	def test_handle_empty_solid_in_inventory(self):
		self.basket.add(self.book)
		self.player.get_inventory().add(self.basket)

		success, template_keys, content_args, next_args = self.handler.handle_empty(self.command, self.player, self.basket)

		self.assertTrue(success)
		self.assertEqual(["confirm_emptied_solid"], template_keys)
		self.assertEqual([self.basket, self.book], content_args)
		self.assertEqual([self.basket], next_args)
		self.assertFalse(self.book in self.basket.items)
		self.assertTrue(self.book in self.player.get_inventory().items)
		self.assertFalse(self.book in self.player.location.items)


	def test_handle_empty_solid_at_location(self):
		self.basket.add(self.book)
		self.player.location.add(self.basket)

		success, template_keys, content_args, next_args = self.handler.handle_empty(self.command, self.player, self.basket)

		self.assertTrue(success)
		self.assertEqual(["confirm_emptied_solid"], template_keys)
		self.assertEqual([self.basket, self.book], content_args)
		self.assertEqual([self.basket], next_args)
		self.assertFalse(self.book in self.basket.items)
		self.assertFalse(self.book in self.player.get_inventory().items)
		self.assertTrue(self.book in self.player.location.items)


	def test_handle_explain_default(self):
		success, template_keys, content_args, next_args = self.handler.handle_explain(self.command, self.player, "dreams")

		self.assertFalse(success)
		self.assertEqual(["I have no explanation."], template_keys)
		self.assertEqual(["dreams"], content_args)
		self.assertEqual([], next_args)


	def test_handle_explain_non_default(self):
		success, template_keys, content_args, next_args = self.handler.handle_explain(self.command, self.player, "spaize")

		self.assertTrue(success)
		self.assertEqual(["Spaize is space-maize."], template_keys)
		self.assertEqual(["spaize"], content_args)
		self.assertEqual(["spaize"], next_args)


	def test_feed_non_sentient(self):
		success, template_keys, content_args, next_args = self.handler.handle_feed(self.command, self.player, self.bread, self.book)

		self.assertFalse(success)
		self.assertEqual(["reject_give_inanimate"], template_keys)
		self.assertEqual([self.bread, self.book], content_args)
		self.assertEqual([], next_args)


	def test_feed_non_edible(self):
		success, template_keys, content_args, next_args = self.handler.handle_feed(self.command, self.player, self.book, self.cat)

		self.assertFalse(success)
		self.assertEqual(["reject_not_consumable"], template_keys)
		self.assertEqual([self.book, self.cat], content_args)
		self.assertEqual([], next_args)


	def test_feed_valid(self):
		success, template_keys, content_args, next_args = self.handler.handle_feed(self.command, self.player, self.bread, self.cat)

		self.assertTrue(success)
		self.assertEqual(["confirm_feed"], template_keys)
		self.assertEqual([self.bread, self.cat], content_args)
		self.assertEqual([self.bread, self.cat], next_args)


	def test_handle_free(self):
		self.player.get_inventory().add(self.lamp)

		success, template_keys, content_args, next_args = self.handler.handle_free(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual(["confirm_dropped"], template_keys)
		self.assertEqual([self.lamp], content_args)
		self.assertEqual([self.lamp], next_args)
		self.assertFalse(self.lamp in self.default_inventory.items)
		self.assertTrue(self.lamp in self.player.location.items)


	def test_handle_give_non_sentient_recipient(self):
		self.player.get_inventory().add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_give(self.command, self.player, self.book, self.lamp)

		self.assertFalse(success)
		self.assertEqual(["reject_give_inanimate"], template_keys)
		self.assertEqual([self.book, self.lamp], content_args)
		self.assertEqual([], next_args)


	def test_handle_give_liquid_item(self):
		self.bottle.add(self.water)
		self.player.get_inventory().add(self.bottle)

		success, template_keys, content_args, next_args = self.handler.handle_give(self.command, self.player, self.water, self.cat)

		self.assertFalse(success)
		self.assertEqual(["reject_give_liquid"], template_keys)
		self.assertEqual([self.water, self.cat], content_args)
		self.assertEqual([], next_args)


	def test_handle_give_valid(self):
		self.player.get_inventory().add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_give(self.command, self.player, self.book, self.cat)

		self.assertTrue(success)
		self.assertEqual(["confirm_given"], template_keys)
		self.assertEqual([self.book, self.cat], content_args)
		self.assertEqual([self.book, self.cat], next_args)
		self.assertFalse(self.book in self.player.get_inventory().items)
		self.assertFalse(self.player.get_inventory() in self.book.containers)


	def test_handle_go_with_obstruction(self):
		self.player.location.add(self.obstruction)
		self.player.location.directions[Direction.SOUTH] = self.beach_location

		success, template_keys, content_args, next_args = self.handler.handle_go(self.command, self.player, Direction.SOUTH, self.beach_location)

		self.assertFalse(success)
		self.assertEqual(["reject_obstruction_known"], template_keys)
		self.assertEqual(["an obstruction"], content_args)
		self.assertEqual([], next_args)


	def test_handle_go_with_obstruction_no_light(self):
		self.player.location = self.mine_location
		self.player.location.add(self.obstruction)
		self.player.location.directions[Direction.EAST] = self.beach_location

		success, template_keys, content_args, next_args = self.handler.handle_go(self.command, self.player, Direction.EAST, self.beach_location)

		self.assertFalse(success)
		self.assertEqual(["reject_obstruction_unknown"], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)


	def test_handle_go_with_obstruction_to_previous_location(self):
		self.beach_location.add(self.obstruction)
		self.player.location.directions[Direction.SOUTH] = self.beach_location
		self.beach_location.directions[Direction.NORTH] = self.lighthouse_location

		self.handler.handle_go(self.command, self.player, Direction.SOUTH, self.beach_location)
		success, template_keys, content_args, next_args = self.handler.handle_go(self.command, self.player, Direction.NORTH, self.lighthouse_location)

		self.assertTrue(success)
		self.assertEqual([], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([self.lighthouse_location, self.beach_location], next_args)
		self.assertIs(self.lighthouse_location, self.player.location)
		self.assertIs(self.beach_location, self.player.previous_location)


	def test_handle_go_without_obstruction_two_way(self):
		self.player.location.directions[Direction.SOUTH] = self.beach_location
		self.beach_location.directions[Direction.NORTH] = self.player.location

		success, template_keys, content_args, next_args = self.handler.handle_go(self.command, self.player, Direction.SOUTH, self.beach_location)

		self.assertTrue(success)
		self.assertEqual([], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([self.beach_location, self.lighthouse_location], next_args)
		self.assertIs(self.beach_location, self.player.location)
		self.assertIs(self.lighthouse_location, self.player.previous_location)


	def test_handle_go_without_obstruction_one_way(self):
		self.player.location.directions[Direction.SOUTH] = self.beach_location

		success, template_keys, content_args, next_args = self.handler.handle_go(self.command, self.player, Direction.SOUTH, self.beach_location)

		self.assertTrue(success)
		self.assertEqual([], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([self.beach_location, self.lighthouse_location], next_args)
		self.assertIs(self.beach_location, self.player.location)
		self.assertIs(None, self.player.previous_location)


	def test_handle_go_without_air_at_destination_not_immune(self):
		self.player.location.directions[Direction.SOUTH] = self.airless_location

		success, template_keys, content_args, next_args = self.handler.handle_go(self.command, self.player, Direction.SOUTH, self.airless_location)

		self.assertFalse(success)
		self.assertEqual(["reject_movement_no_air"], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_go_without_air_at_destination_immune(self):
		self.player.set_immune(True)
		self.player.location.directions[Direction.SOUTH] = self.airless_location

		success, template_keys, content_args, next_args = self.handler.handle_go(self.command, self.player, Direction.SOUTH, self.airless_location)

		self.assertTrue(success)
		self.assertEqual([], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([self.airless_location, self.lighthouse_location], next_args)
		self.assertIs(self.airless_location, self.player.location)


	def test_handle_go_without_land_at_destination_not_immune(self):
		self.player.location.directions[Direction.SOUTH] = self.water_location

		success, template_keys, content_args, next_args = self.handler.handle_go(self.command, self.player, Direction.SOUTH, self.water_location)

		self.assertFalse(success)
		self.assertEqual(["reject_movement_no_land"], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_go_without_land_at_destination_immune(self):
		self.player.set_immune(True)
		self.player.location.directions[Direction.SOUTH] = self.water_location

		success, template_keys, content_args, next_args = self.handler.handle_go(self.command, self.player, Direction.SOUTH, self.water_location)

		self.assertTrue(success)
		self.assertEqual([], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([self.water_location, self.lighthouse_location], next_args)
		self.assertIs(self.water_location, self.player.location)


	def test_handle_go_down_without_floor_not_immune(self):
		self.player.location = self.cave_location
		self.cave_location.directions[Direction.DOWN] = self.mine_location

		success, template_keys, content_args, next_args = self.handler.handle_go(self.command, self.player, Direction.DOWN, self.mine_location)

		self.assertFalse(success)
		self.assertEqual(["reject_movement_no_floor"], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.assertIs(self.cave_location, self.player.location)


	def test_handle_go_down_without_floor_immune(self):
		self.player.set_immune(True)
		self.player.location = self.cave_location
		self.cave_location.directions[Direction.DOWN] = self.mine_location

		success, template_keys, content_args, next_args = self.handler.handle_go(self.command, self.player, Direction.DOWN, self.mine_location)

		self.assertTrue(success)
		self.assertEqual([], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([self.mine_location, self.cave_location], next_args)
		self.assertIs(self.mine_location, self.player.location)


	def test_handle_go_sail_without_water(self):
		self.player.location = self.water_location
		self.default_inventory.insert(self.raft)
		self.raft.being_used = True

		success, template_keys, content_args, next_args = self.handler.handle_go(self.command, self.player, Direction.EAST, self.lighthouse_location)

		self.assertFalse(success)
		self.assertEqual(["reject_movement_no_water"], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.assertIs(self.water_location, self.player.location)


	def test_handle_go_disambiguate(self):
		success, template_keys, content_args, next_args = self.handler.handle_go_disambiguate(self.command, self.player, "east")

		self.assertFalse(success)
		self.assertEqual(["reject_go"], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)


	def test_handle_help(self):
		success, template_keys, content_args, next_args = self.handler.handle_help(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual(["describe_help"], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.assertEqual(6, self.player.instructions)


	def test_handle_hint_default(self):
		success, template_keys, content_args, next_args = self.handler.handle_hint(self.command, self.player, "cat")

		self.assertFalse(success)
		self.assertEqual(["I have no hint."], template_keys)
		self.assertEqual(["cat"], content_args)
		self.assertEqual([], next_args)


	def test_handle_hint_non_default(self):
		success, template_keys, content_args, next_args = self.handler.handle_hint(self.command, self.player, "magic")

		self.assertTrue(success)
		self.assertEqual(["abrakadabra"], template_keys)
		self.assertEqual(["magic"], content_args)
		self.assertEqual(["magic"], next_args)


	def test_handle_immune_off(self):
		self.player.set_immune(True)

		success, template_keys, content_args, next_args = self.handler.handle_immune(self.command, self.player, False)

		self.assertTrue(success)
		self.assertEqual(["confirm_immune_off"], template_keys)
		self.assertEqual([False], content_args)
		self.assertEqual([False], next_args)
		self.assertFalse(self.player.is_immune())


	def test_handle_immune_on(self):
		success, template_keys, content_args, next_args = self.handler.handle_immune(self.command, self.player, True)

		self.assertTrue(success)
		self.assertEqual(["confirm_immune_on"], template_keys)
		self.assertEqual([True], content_args)
		self.assertEqual([True], next_args)
		self.assertTrue(self.player.is_immune())


	def test_handle_insert_into_non_container(self):
		success, template_keys, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.book, self.lamp)

		self.assertFalse(success)
		self.assertEqual(["reject_not_container"], template_keys)
		self.assertEqual([self.book, self.lamp], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_container_into_self(self):
		success, template_keys, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.basket, self.basket)

		self.assertFalse(success)
		self.assertEqual(["reject_container_self"], template_keys)
		self.assertEqual([self.basket, self.basket], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_already_inserted(self):
		self.basket.add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.book, self.basket)

		self.assertFalse(success)
		self.assertEqual(["reject_already_contained"], template_keys)
		self.assertEqual([self.book, self.basket], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_non_portable(self):
		success, template_keys, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.desk, self.basket)

		self.assertFalse(success)
		self.assertEqual(["reject_not_portable"], template_keys)
		self.assertEqual([self.desk, self.basket], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_liquid_into_solid_container(self):
		self.item_start_location.add(self.water)

		success, template_keys, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.water, self.basket)

		self.assertFalse(success)
		self.assertEqual(["reject_insert_liquid"], template_keys)
		self.assertEqual([self.water, self.basket], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_solid_into_liquid_container(self):
		success, template_keys, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.book, self.bottle)

		self.assertFalse(success)
		self.assertEqual(["reject_insert_solid"], template_keys)
		self.assertEqual([self.book, self.bottle], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_container_not_empty(self):
		self.basket.add(self.lamp)

		success, template_keys, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.book, self.basket)

		self.assertFalse(success)
		self.assertEqual(["reject_not_empty"], template_keys)
		self.assertEqual([self.book, self.basket], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_container_too_small(self):
		success, template_keys, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.heavy_item, self.basket)

		self.assertFalse(success)
		self.assertEqual(["reject_container_size"], template_keys)
		self.assertEqual([self.heavy_item, self.basket], content_args)
		self.assertEqual([], next_args)


	def test_handle_insert_valid_non_copyable(self):
		success, template_keys, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.book, self.basket)

		self.assertTrue(success)
		self.assertEqual(["confirm_insert_solid"], template_keys)
		self.assertEqual([self.book, self.basket], content_args)
		self.assertFalse(self.book in self.item_start_location.items)
		self.assertTrue(self.book in self.basket.items)
		self.assertEqual([self.book, self.basket], next_args)


	def test_handle_insert_valid_copyable(self):
		self.item_start_location.add(self.water)

		success, template_keys, content_args, next_args = self.handler.handle_insert(self.command, self.player, self.water, self.bottle)

		self.assertTrue(success)
		self.assertEqual(["confirm_insert_liquid"], template_keys)
		self.assertEqual([self.water, self.bottle], content_args)
		self.assertEqual([self.water, self.bottle], next_args)
		self.assertTrue(self.water in self.item_start_location.items)
		self.assertFalse(self.water in self.bottle.items)
		bottle_water = self.bottle.get_allow_copy(self.water)
		self.assertTrue(bottle_water in self.bottle.items)
		self.assertIsNot(self.water, bottle_water)
		self.assertIs(self.water, bottle_water.copied_from)
		self.assertTrue(bottle_water in self.water.copied_to)


	def test_handle_inventory_empty(self):
		success, template_keys, content_args, next_args = self.handler.handle_inventory(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual(["list_inventory_empty"], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)


	def test_handle_inventory_nonempty(self):
		self.player.get_inventory().add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_inventory(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual(["list_inventory_nonempty"], template_keys)
		self.assertEqual(["\n\ta book"], content_args)
		self.assertEqual([], next_args)


	def test_handle_locate_at_location(self):
		self.player.location.add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_locate(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual(["describe_locate_primary"], template_keys)
		self.assertEqual(["book", "['12:at a lighthouse']"], content_args)
		self.assertEqual([self.book], next_args)


	def test_handle_locate_in_item(self):
		self.basket.add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_locate(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual(["describe_locate_primary"], template_keys)
		self.assertEqual(["book", "['1107:a basket']"], content_args)
		self.assertEqual([self.book], next_args)


	def test_handle_locate_in_inventory(self):
		self.player.get_inventory().add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_locate(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual(["describe_locate_primary"], template_keys)
		self.assertEqual(["book", "['0:in the main inventory']"], content_args)
		self.assertEqual([self.book], next_args)


	def test_handle_locate_with_copies(self):
		self.player.location.add(self.water)
		self.bottle.insert(self.water)

		success, template_keys, content_args, next_args = self.handler.handle_locate(self.command, self.player, self.water)

		self.assertTrue(success)
		self.assertEqual(["describe_locate_primary", "describe_locate_copies"], template_keys)
		self.assertEqual(["water", "['12:at a lighthouse']", "['1108:a bottle']"], content_args)
		self.assertEqual([self.water], next_args)


	def test_handle_look_no_items(self):
		success, template_keys, content_args, next_args = self.handler.handle_look(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual(["describe_location"], template_keys)
		self.assertEqual(["at a lighthouse by the sea.", ""], content_args)
		self.assertEqual([], next_args)


	def test_handle_look_with_item(self):
		self.player.location.add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_look(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual(["describe_location", "list_location"], template_keys)
		self.assertEqual(["at a lighthouse by the sea.", "\n\ta book"], content_args)
		self.assertEqual([], next_args)


	def test_handle_look_with_silent_item(self):
		self.player.location.add(self.desk)

		success, template_keys, content_args, next_args = self.handler.handle_look(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual(["describe_location"], template_keys)
		self.assertEqual(["at a lighthouse by the sea.", ""], content_args)
		self.assertEqual([], next_args)


	def test_handle_node_no_arg(self):
		success, template_keys, content_args, next_args = self.handler.handle_node(self.command, self.player)

		self.assertFalse(success)
		self.assertEqual(["describe_node"], template_keys)
		self.assertEqual([12], content_args)
		self.assertEqual([], next_args)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_node_arg_invalid(self):
		success, template_keys, content_args, next_args = self.handler.handle_node(self.command, self.player, "abc")

		self.assertFalse(success)
		self.assertEqual(["reject_no_node"], template_keys)
		self.assertEqual(["abc"], content_args)
		self.assertEqual([], next_args)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_node_arg_out_of_range(self):
		success, template_keys, content_args, next_args = self.handler.handle_node(self.command, self.player, "61")

		self.assertFalse(success)
		self.assertEqual(["reject_no_node"], template_keys)
		self.assertEqual(["61"], content_args)
		self.assertEqual([], next_args)
		self.assertIs(self.lighthouse_location, self.player.location)


	def test_handle_node_arg_valid(self):
		success, template_keys, content_args, next_args = self.handler.handle_node(self.command, self.player, "13")

		self.assertTrue(success)
		self.assertEqual([], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([self.beach_location, self.lighthouse_location], next_args)
		self.assertIs(self.beach_location, self.player.location)


	def test_handle_pick(self):
		self.player.location.add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_pick(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual(["confirm_taken"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([self.book], next_args)
		self.assertTrue(self.book in self.player.get_inventory().items)
		self.assertFalse(self.book in self.player.location.items)


	def test_pour_non_liquid(self):
		self.player.get_inventory().add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_pour(self.command, self.player, self.book, self.lamp)

		self.assertFalse(success)
		self.assertEqual(["reject_not_liquid"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)


	def test_handle_pour_liquid(self):
		self.bottle.add(self.water)
		self.player.get_inventory().add(self.bottle)

		success, template_keys, content_args, next_args = self.handler.handle_pour(self.command, self.player, self.water, self.lamp)

		self.assertTrue(success)
		self.assertEqual(["confirm_poured_with_destination"], template_keys)
		self.assertEqual([self.water, self.lamp, self.bottle], content_args)
		self.assertEqual([self.water, self.lamp], next_args)
		self.assertFalse(self.water in self.bottle.items)
		self.assertFalse(self.water in self.player.location.items)


	def test_handle_quit(self):
		success, template_keys, content_args, next_args = self.handler.handle_quit(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual(["confirm_quit"], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)
		self.assertEqual(6, self.player.instructions)
		self.assertFalse(self.player.is_playing())


	def test_handle_read_no_writing(self):
		self.player.get_inventory().add(self.lamp)

		success, template_keys, content_args, next_args = self.handler.handle_read(self.command, self.player, self.lamp)

		self.assertFalse(success)
		self.assertEqual(["reject_no_writing"], template_keys)
		self.assertEqual([self.lamp], content_args)
		self.assertEqual([], next_args)


	def test_handle_read_with_writing(self):
		self.player.get_inventory().add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_read(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual(["describe_writing"], template_keys)
		self.assertEqual(["The Pied Piper"], content_args)
		self.assertEqual([self.book], next_args)


	def test_handle_remove_not_wearable(self):
		success, template_keys, content_args, next_args = self.handler.handle_remove(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual(["reject_not_wearing"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)


	def test_handle_remove_not_being_worn(self):
		self.suit.being_used = False

		success, template_keys, content_args, next_args = self.handler.handle_remove(self.command, self.player, self.suit)

		self.assertFalse(success)
		self.assertEqual(["reject_not_wearing"], template_keys)
		self.assertEqual([self.suit], content_args)
		self.assertEqual([], next_args)


	def test_handle_remove_over_capacity(self):
		self.suit.being_used = True
		self.player.get_inventory().add(self.heavy_item)

		success, template_keys, content_args, next_args = self.handler.handle_remove(self.command, self.player, self.suit)

		self.assertFalse(success)
		self.assertEqual(["reject_too_full_not_worn"], template_keys)
		self.assertEqual([self.suit], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.suit.being_used)


	def test_handle_remove_success(self):
		self.suit.being_used = True

		success, template_keys, content_args, next_args = self.handler.handle_remove(self.command, self.player, self.suit)

		self.assertTrue(success)
		self.assertEqual(["confirm_remove"], template_keys)
		self.assertEqual([self.suit], content_args)
		self.assertEqual([self.suit], next_args)


	def test_handle_sail_not_sailable(self):
		success, template_keys, content_args, next_args = self.handler.handle_sail(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual(["reject_not_sailable"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)


	def test_handle_sail_no_water(self):
		success, template_keys, content_args, next_args = self.handler.handle_sail(self.command, self.player, self.raft)

		self.assertFalse(success)
		self.assertEqual(["reject_no_water_sail"], template_keys)
		self.assertEqual([self.raft], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.raft.being_used)


	def test_handle_sail_already_sailing_item(self):
		self.player.location = self.water_location
		self.raft.being_used = True

		success, template_keys, content_args, next_args = self.handler.handle_sail(self.command, self.player, self.raft)

		self.assertFalse(success)
		self.assertEqual(["reject_already_sailing_item"], template_keys)
		self.assertEqual([self.raft], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.raft.being_used)


	def test_handle_sail_already_sailing(self):
		self.player.location = self.water_location
		self.default_inventory.insert(self.boat)
		self.boat.being_used = True

		success, template_keys, content_args, next_args = self.handler.handle_sail(self.command, self.player, self.raft)

		self.assertFalse(success)
		self.assertEqual(["reject_already_sailing"], template_keys)
		self.assertEqual([self.raft], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.raft.being_used)


	def test_handle_sail_success(self):
		self.player.location = self.water_location

		success, template_keys, content_args, next_args = self.handler.handle_sail(self.command, self.player, self.raft)

		self.assertTrue(success)
		self.assertEqual(["confirm_sail"], template_keys)
		self.assertEqual([self.raft], content_args)
		self.assertEqual([self.raft], next_args)
		self.assertTrue(self.raft.being_used)


	def test_handle_say_no_audience(self):
		success, template_keys, content_args, next_args = self.handler.handle_say(self.command, self.player, "hello")

		self.assertTrue(success)
		self.assertEqual(["confirm_say_no_audience"], template_keys)
		self.assertEqual(["hello"], content_args)
		self.assertEqual(["hello"], next_args)


	def test_handle_say_no_sentient_audience(self):
		success, template_keys, content_args, next_args = self.handler.handle_say(self.command, self.player, "hello", self.book)

		self.assertTrue(success)
		self.assertEqual(["confirm_say_no_sentient_audience"], template_keys)
		self.assertEqual(["hello", self.book], content_args)
		self.assertEqual(["hello", self.book], next_args)


	def test_handle_say_with_sentient_audience(self):
		success, template_keys, content_args, next_args = self.handler.handle_say(self.command, self.player, "hello", self.cat)

		self.assertTrue(success)
		self.assertEqual(["confirm_say_audience"], template_keys)
		self.assertEqual(["hello", self.cat], content_args)
		self.assertEqual(["hello", self.cat], next_args)


	def test_handle_score_zero(self):
		self.data.get_puzzle_count.return_value = 17
		self.data.get_collectible_count.return_value = 29

		success, template_keys, content_args, next_args = self.handler.handle_score(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual(["describe_score"], template_keys)
		self.assertEqual([0, 264, 6], content_args)
		self.assertEqual([], next_args)
		self.assertEqual(6, self.player.instructions)


	def test_handle_score_with_puzzles_solved(self):
		self.data.get_puzzle_count.return_value = 17
		self.data.get_collectible_count.return_value = 29
		self.player.solve_puzzle(Mock())
		self.player.solve_puzzle(Mock())

		success, template_keys, content_args, next_args = self.handler.handle_score(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual(["describe_score"], template_keys)
		self.assertEqual([14, 264, 6], content_args)
		self.assertEqual([], next_args)
		self.assertEqual(6, self.player.instructions)


	def test_handle_score_with_collectibles_solved(self):
		self.data.get_puzzle_count.return_value = 17
		self.data.get_collectible_count.return_value = 29
		self.cave_location.insert(Item(2222, 0x8002, Labels("nugget", "a gold nugget", "; it is shiny"), 2, None, {}))
		self.cave_location.insert(Item(2223, 0x8002, Labels("medal", "a silver medal", "; it is beautiful"), 2, None, {}))
		self.cave_location.insert(Item(2224, 0x8002, Labels("statue", "a bronze statue", "; it is heavy"), 2, None, {}))

		success, template_keys, content_args, next_args = self.handler.handle_score(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual(["describe_score"], template_keys)
		self.assertEqual([15, 264, 6], content_args)
		self.assertEqual([], next_args)
		self.assertEqual(6, self.player.instructions)


	def test_handle_score_with_puzzles_and_collectibles_solved(self):
		self.data.get_puzzle_count.return_value = 17
		self.data.get_collectible_count.return_value = 29
		self.player.solve_puzzle(Mock())
		self.player.solve_puzzle(Mock())
		self.cave_location.insert(Item(2222, 0x8002, Labels("nugget", "a gold nugget", "; it is shiny"), 2, None, {}))
		self.cave_location.insert(Item(2223, 0x8002, Labels("medal", "a silver medal", "; it is beautiful"), 2, None, {}))
		self.cave_location.insert(Item(2224, 0x8002, Labels("statue", "a bronze statue", "; it is heavy"), 2, None, {}))

		success, template_keys, content_args, next_args = self.handler.handle_score(self.command, self.player)

		self.assertTrue(success)
		self.assertEqual(["describe_score"], template_keys)
		self.assertEqual([29, 264, 6], content_args)
		self.assertEqual([], next_args)
		self.assertEqual(6, self.player.instructions)


	def test_handle_set(self):
		self.player.get_inventory().add(self.lamp)

		success, template_keys, content_args, next_args = self.handler.handle_set(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual(["confirm_dropped"], template_keys)
		self.assertEqual([self.lamp], content_args)
		self.assertEqual([self.lamp], next_args)
		self.assertFalse(self.lamp in self.player.get_inventory().items)
		self.assertTrue(self.lamp in self.player.location.items)


	def test_handle_smash_not_smashable(self):
		self.item_start_location.insert(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_smash(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual(["reject_not_smashable"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.book in self.item_start_location.items)


	def test_handle_smash_smashable_not_strong_item(self):
		smash_command = Command(37, 0x9, 0x0, [], [""],  {})
		self.item_start_location.insert(self.bottle)

		success, template_keys, content_args, next_args = self.handler.handle_smash(smash_command, self.player, self.bottle)

		self.assertTrue(success)
		self.assertEqual(["confirm_smash"], template_keys)
		self.assertEqual([self.bottle, "some shards"], content_args)
		self.assertEqual([self.bottle], next_args)
		self.assertFalse(self.bottle in self.item_start_location.items)
		self.assertTrue(self.shards in self.item_start_location.items)


	def test_handle_smash_smashable_strong_item_not_strong_player(self):
		smash_command = Command(37, 0x9, 0x0, [], [""],  {})
		self.item_start_location.insert(self.rock)

		success, template_keys, content_args, next_args = self.handler.handle_smash(smash_command, self.player, self.rock)

		self.assertFalse(success)
		self.assertEqual(["reject_not_strong"], template_keys)
		self.assertTrue(self.rock in self.item_start_location.items)


	def test_handle_smash_smashable_strong_item_strong_player(self):
		smash_command = Command(37, 0x9, 0x0, [], [""],  {})
		self.item_start_location.insert(self.rock)
		self.player.set_strong(True)

		success, template_keys, content_args, next_args = self.handler.handle_smash(smash_command, self.player, self.rock)

		self.assertTrue(success)
		self.assertEqual(["confirm_smash"], template_keys)
		self.assertEqual([self.rock, "some dust"], content_args)
		self.assertEqual([self.rock], next_args)
		self.assertFalse(self.rock in self.item_start_location.items)
		self.assertTrue(self.dust in self.item_start_location.items)


	def test_handle_switch_off_to_off(self):
		self.lamp.switch_off()

		success, template_keys, content_args, next_args = self.handler.handle_switch(self.command, self.player, self.lamp, SwitchTransition.OFF)

		self.assertFalse(success)
		self.assertEqual(["reject_already_switched"], template_keys)
		self.assertEqual([self.lamp, "off"], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.lamp.is_on())


	def test_handle_swim(self):
		success, template_keys, content_args, next_args = self.handler.handle_swim(self.command, self.player)

		self.assertFalse(success)
		self.assertEqual(["reject_no_know_swim"], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([], next_args)


	def test_handle_switch_off_to_on(self):
		self.lamp.switch_off()

		success, template_keys, content_args, next_args = self.handler.handle_switch(self.command, self.player, self.lamp, SwitchTransition.ON)

		self.assertTrue(success)
		self.assertEqual(["describe_switch_item"], template_keys)
		self.assertEqual([self.lamp, "on"], content_args)
		self.assertEqual([self.lamp, SwitchTransition.ON], next_args)
		self.assertTrue(self.lamp.is_on())


	def test_handle_switch_on_to_off(self):
		self.lamp.switch_on()

		success, template_keys, content_args, next_args = self.handler.handle_switch(self.command, self.player, self.lamp, SwitchTransition.OFF)

		self.assertTrue(success)
		self.assertEqual(["describe_switch_item"], template_keys)
		self.assertEqual([self.lamp, "off"], content_args)
		self.assertEqual([self.lamp, SwitchTransition.OFF], next_args)
		self.assertFalse(self.lamp.is_on())


	def test_handle_switch_on_to_on(self):
		self.lamp.switch_on()

		success, template_keys, content_args, next_args = self.handler.handle_switch(self.command, self.player, self.lamp, SwitchTransition.ON)

		self.assertFalse(success)
		self.assertEqual(["reject_already_switched"], template_keys)
		self.assertEqual([self.lamp, "on"], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.lamp.is_on())


	def test_handle_take_from_sentient_simple(self):
		self.cat.add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_take(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual(["reject_take_animate"], template_keys)
		self.assertEqual([self.book, self.cat], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.book in self.player.get_inventory().items)
		self.assertTrue(self.book in self.cat.items)


	def test_handle_take_from_sentient_nested(self):
		self.basket.add(self.book)
		self.cat.add(self.basket)

		success, template_keys, content_args, next_args = self.handler.handle_take(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual(["reject_take_animate"], template_keys)
		self.assertEqual([self.book, self.cat], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.book in self.player.get_inventory().items)
		self.assertTrue(self.basket in self.cat.items)
		self.assertTrue(self.book in self.basket.items)


	def test_handle_take_not_portable(self):
		self.player.location.add(self.desk)

		success, template_keys, content_args, next_args = self.handler.handle_take(self.command, self.player, self.desk)

		self.assertFalse(success)
		self.assertEqual(["reject_not_portable"], template_keys)
		self.assertEqual([self.desk], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.desk in self.player.get_inventory().items)
		self.assertTrue(self.desk in self.player.location.items)


	def test_handle_take_obstruction(self):
		self.player.location.add(self.mobile_obstruction)

		success, template_keys, content_args, next_args = self.handler.handle_take(self.command, self.player, self.mobile_obstruction)

		self.assertFalse(success)
		self.assertEqual(["reject_not_portable"], template_keys)
		self.assertEqual([self.mobile_obstruction], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.mobile_obstruction in self.player.get_inventory().items)
		self.assertTrue(self.mobile_obstruction in self.player.location.items)


	def test_handle_take_over_capacity(self):
		self.player.location.add(self.book)
		self.player.get_inventory().add(self.heavy_item)

		success, template_keys, content_args, next_args = self.handler.handle_take(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual(["reject_too_full"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.book in self.player.get_inventory().items)
		self.assertTrue(self.book in self.player.location.items)


	def test_handle_take_at_location(self):
		self.player.location.add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_take(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual(["confirm_taken"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([self.book], next_args)
		self.assertTrue(self.book in self.player.get_inventory().items)
		self.assertFalse(self.book in self.player.location.items)


	def test_handle_take_liquid(self):
		self.player.location.add(self.water)

		success, template_keys, content_args, next_args = self.handler.handle_take(self.command, self.player, self.water)

		self.assertFalse(success)
		self.assertEqual(["reject_take_liquid"], template_keys)
		self.assertEqual([self.water], content_args)
		self.assertEqual([], next_args)
		self.assertFalse(self.water in self.player.get_inventory().items)
		self.assertTrue(self.water in self.player.location.items)


	def test_handle_take_multi_arg(self):
		self.player.location.add(self.book)
		self.player.get_inventory().add(self.basket)

		success, template_keys, content_args, next_args = self.handler.handle_take(self.command, self.player, self.book, self.basket)

		self.assertTrue(success)
		self.assertEqual(["confirm_insert_solid"], template_keys)
		self.assertEqual([self.book, self.basket], content_args)
		self.assertEqual([self.book, self.basket], next_args)
		self.assertTrue(self.book in self.basket.items)


	def test_handle_teleport(self):
		success, template_keys, content_args, next_args = self.handler.handle_teleport(self.command, self.player, self.beach_location)

		self.assertTrue(success)
		self.assertEqual([], template_keys)
		self.assertEqual([], content_args)
		self.assertEqual([self.beach_location, self.lighthouse_location], next_args)
		self.assertIs(self.beach_location, self.player.location)
		self.assertIs(None, self.player.previous_location)


	def test_handle_throw_liquid(self):
		self.bottle.add(self.water)
		self.player.get_inventory().add(self.bottle)

		success, template_keys, content_args, next_args = self.handler.handle_throw(self.command, self.player, self.water)

		self.assertFalse(success)
		self.assertEqual(["reject_throw_liquid"], template_keys)
		self.assertEqual([self.water], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.water in self.bottle.items)
		self.assertFalse(self.water in self.player.location.items)


	def test_handle_throw_with_floor_non_fragile(self):
		self.player.get_inventory().add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_throw(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual(["confirm_throw"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([self.book], next_args)
		self.assertFalse(self.book in self.default_inventory.items)
		self.assertTrue(self.book in self.player.location.items)


	def test_handle_throw_with_floor_fragile(self):
		self.player.get_inventory().add(self.bottle)

		success, template_keys, content_args, next_args = self.handler.handle_throw(self.command, self.player, self.bottle)

		self.assertTrue(success)
		self.assertEqual(["confirm_throw", "describe_item_smash_see"], template_keys)
		self.assertEqual([self.bottle, self.shards], content_args)
		self.assertEqual([self.bottle], next_args)
		self.assertFalse(self.bottle in self.default_inventory.items)
		self.assertFalse(self.bottle in self.player.location.items)
		self.assertTrue(self.shards in self.player.location.items)


	def test_handle_throw_without_floor_non_fragile(self):
		self.player.location = self.cave_location
		self.cave_location.directions[Direction.DOWN] = self.mine_location
		self.player.get_inventory().add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_throw(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual(["confirm_throw", "describe_item_falling"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([self.book], next_args)
		self.assertFalse(self.book in self.default_inventory.items)
		self.assertFalse(self.book in self.cave_location.items)
		self.assertTrue(self.book in self.mine_location.items)


	def test_handle_throw_without_floor_fragile(self):
		self.player.location = self.cave_location
		self.cave_location.directions[Direction.DOWN] = self.mine_location
		self.player.get_inventory().add(self.bottle)

		success, template_keys, content_args, next_args = self.handler.handle_throw(self.command, self.player, self.bottle)

		self.assertTrue(success)
		self.assertEqual(["confirm_throw", "describe_item_falling", "describe_item_smash_hear"], template_keys)
		self.assertEqual([self.bottle, self.shards], content_args)
		self.assertEqual([self.bottle], next_args)
		self.assertFalse(self.bottle in self.default_inventory.items)
		self.assertFalse(self.bottle in self.cave_location.items)
		self.assertFalse(self.shards in self.cave_location.items)
		self.assertTrue(self.shards in self.mine_location.items)


	def test_handle_throw_fragile_liquid_container(self):
		self.bottle.add(self.water)
		self.player.get_inventory().add(self.bottle)

		success, template_keys, content_args, next_args = self.handler.handle_throw(self.command, self.player, self.bottle)

		self.assertTrue(success)
		self.assertEqual(["confirm_throw", "describe_item_smash_see", "describe_item_smash_release_liquid"], template_keys)
		self.assertEqual([self.bottle, self.shards, self.water], content_args)
		self.assertEqual([self.bottle], next_args)
		self.assertFalse(self.bottle in self.default_inventory.items)
		self.assertFalse(self.bottle in self.player.location.items)
		self.assertTrue(self.shards in self.player.location.items)


	def test_handle_throw_fragile_solid_container(self):
		self.tray.insert(self.book)
		self.player.get_inventory().insert(self.tray)

		success, template_keys, content_args, next_args = self.handler.handle_throw(self.command, self.player, self.tray)

		self.assertTrue(success)
		self.assertEqual(["confirm_throw", "describe_item_smash_see", "describe_item_smash_release_solid"], template_keys)
		self.assertEqual([self.tray, self.shards, self.book], content_args)
		self.assertEqual([self.tray], next_args)
		self.assertFalse(self.tray in self.default_inventory.items)
		self.assertFalse(self.tray in self.player.location.items)
		self.assertTrue(self.shards in self.player.location.items)


	def test_handle_throw_fragile_container_empty(self):
		self.player.get_inventory().insert(self.tray)

		success, template_keys, content_args, next_args = self.handler.handle_throw(self.command, self.player, self.tray)

		self.assertTrue(success)
		self.assertEqual(["confirm_throw", "describe_item_smash_see"], template_keys)
		self.assertEqual([self.tray, self.shards], content_args)
		self.assertEqual([self.tray], next_args)
		self.assertFalse(self.tray in self.default_inventory.items)
		self.assertFalse(self.tray in self.player.location.items)
		self.assertTrue(self.shards in self.player.location.items)


	def test_handle_throw_at_location_with_no_land(self):
		self.player.location = self.water_location
		self.player.get_inventory().add(self.book)

		success, template_keys, content_args, next_args = self.handler.handle_throw(self.command, self.player, self.book)

		self.assertTrue(success)
		self.assertEqual(["confirm_throw", "describe_item_sink"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([self.book], next_args)
		self.assertFalse(self.book in self.default_inventory.items)
		self.assertFalse(self.book in self.water_location.items)


	def test_handle_tie_not_tyable(self):
		self.item_start_location.add(self.water)

		success, template_keys, content_args, next_args = self.handler.handle_tie(self.command, self.player, self.water)

		self.assertFalse(success)
		self.assertEqual(["reject_not_tyable"], template_keys)
		self.assertEqual([self.water], content_args)
		self.assertEqual([], next_args)
		self.assertTrue(self.water in self.item_start_location.items)


	def test_handle_tie_tyable_no_tying_material(self):
		tie_command = Command(57, 0x9, 0x0, [], ["tie"], {})
		self.item_start_location.insert(self.log)

		success, template_keys, content_args, next_args = self.handler.handle_tie(tie_command, self.player, self.log)

		self.assertFalse(success)
		self.assertEqual(["reject_no_material"], template_keys)
		self.assertEqual([self.log, "tie", "some rope"], content_args)
		self.assertTrue(self.log in self.item_start_location.items)


	def test_handle_tie_tyable_with_tying_material(self):
		tie_command = Command(57, 0x9, 0x0, [], ["tie"], {})
		self.item_start_location.insert(self.log)
		self.player.get_inventory().add(self.rope)

		success, template_keys, content_args, next_args = self.handler.handle_tie(tie_command, self.player, self.log)

		self.assertTrue(success)
		self.assertEqual(["confirm_tie"], template_keys)
		self.assertEqual([self.log, "a raft"], content_args)
		self.assertEqual([self.log], next_args)
		self.assertFalse(self.log in self.item_start_location.items)
		self.assertTrue(self.raft in self.item_start_location.items)


	def test_handle_toggle_non_switchable_item(self):
		success, template_keys, content_args, next_args = self.handler.handle_toggle(self.command, self.player, self.book)

		self.assertFalse(success)
		self.assertEqual(["reject_no_know_how"], template_keys)
		self.assertEqual([self.book], content_args)
		self.assertEqual([], next_args)


	def test_handle_toggle_off_to_on(self):
		self.lamp.attributes &= ~0x10

		success, template_keys, content_args, next_args = self.handler.handle_toggle(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual(["describe_switch_item"], template_keys)
		self.assertEqual([self.lamp, "on"], content_args)
		self.assertEqual([self.lamp, SwitchTransition.TOGGLE], next_args)
		self.assertTrue(self.lamp.is_on())


	def test_handle_toggle_on_to_off(self):
		self.lamp.attributes |= 0x10

		success, template_keys, content_args, next_args = self.handler.handle_toggle(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual(["describe_switch_item"], template_keys)
		self.assertEqual([self.lamp, "off"], content_args)
		self.assertEqual([self.lamp, SwitchTransition.TOGGLE], next_args)
		self.assertFalse(self.lamp.is_on())


	def test_handle_verbose_off(self):
		self.player.set_verbose(True)

		success, template_keys, content_args, next_args = self.handler.handle_verbose(self.command, self.player, False)

		self.assertTrue(success)
		self.assertEqual(["confirm_verbose_off"], template_keys)
		self.assertEqual([False], content_args)
		self.assertEqual([False], next_args)
		self.assertFalse(self.player.is_verbose())


	def test_handle_verbose_on(self):
		self.player.set_verbose(False)

		success, template_keys, content_args, next_args = self.handler.handle_verbose(self.command, self.player, True)

		self.assertTrue(success)
		self.assertEqual(["confirm_verbose_on"], template_keys)
		self.assertEqual([True], content_args)
		self.assertEqual([True], next_args)
		self.assertTrue(self.player.is_verbose())


	def test_handle_wave(self):
		success, template_keys, content_args, next_args = self.handler.handle_wave(self.command, self.player, self.lamp)

		self.assertTrue(success)
		self.assertEqual(["confirm_wave"], template_keys)
		self.assertEqual([self.lamp], content_args)
		self.assertEqual([self.lamp], next_args)


	def test_handle_wear_not_wearable(self):
		success, template_keys, content_args, next_args = self.handler.handle_wear(self.command, self.player, self.lamp)

		self.assertFalse(success)
		self.assertEqual(["reject_not_wearable"], template_keys)
		self.assertEqual([self.lamp], content_args)
		self.assertEqual([], next_args)


	def test_handle_wear_wearable_already_wearing(self):
		self.suit.being_used = True

		success, template_keys, content_args, next_args = self.handler.handle_wear(self.command, self.player, self.suit)

		self.assertFalse(success)
		self.assertEqual(["reject_already_wearing"], template_keys)
		self.assertEqual([self.suit], content_args)
		self.assertEqual([], next_args)


	def test_handle_wear_wearable_not_already_wearing(self):
		self.player.location.add(self.suit)
		self.suit.being_used = False

		success, template_keys, content_args, next_args = self.handler.handle_wear(self.command, self.player, self.suit)

		self.assertTrue(success)
		self.assertEqual(["confirm_wearing"], template_keys)
		self.assertEqual([self.suit], content_args)
		self.assertEqual([self.suit], next_args)


if __name__ == "__main__":
	unittest.main()

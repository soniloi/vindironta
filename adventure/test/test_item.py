from copy import copy
import unittest

from adventure.command import Command
from adventure.element import Labels
from adventure.inventory import Inventory
from adventure.item import Item, ContainerItem, ListTemplateType, SentientItem, SwitchableItem, SwitchInfo, UsableItem
from adventure.location import Location

class TestItem(unittest.TestCase):

	def setUp(self):
		self.book = Item(1105, 0x2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper", {}, None)
		self.desk = Item(1106, 0x20000, Labels("desk", "a desk", "a large mahogany desk"), 6, None, {}, None)

		basket_list_templates = {ListTemplateType.DEFAULT : "{0} (being lugged)"}
		self.basket = ContainerItem(1107, 0x3, Labels("basket", "a basket", "a large basket"), 6, basket_list_templates, None, "{0} (being lugged)")
		self.box = ContainerItem(1108, 0x3, Labels("box", "a box", "a small box"), 3, None, {}, None)

		lamp_list_templates = {ListTemplateType.DEFAULT : "{0} ({1})"}
		lamp_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "off", "on")
		self.lamp = SwitchableItem(1043, 0x100A, Labels("lamp", "a lamp", "a small lamp"), 2, None, lamp_list_templates, "{0} ({1})", lamp_switching_info)

		button_list_templates = {ListTemplateType.DEFAULT : "{0} ({1})"}
		button_switching_info = SwitchInfo(Item.ATTRIBUTE_GIVES_LIGHT, "up", "down")
		self.button = SwitchableItem(1044, 0x8, Labels("button", "a button", "a red button", [". It is dark", ". It is glowing"]), 2, None, button_list_templates, "{0} ({1})", button_switching_info)

		lever_list_templates = {ListTemplateType.DEFAULT : "{0} ({1})"}
		lever_switching_info = SwitchInfo(Location.ATTRIBUTE_GIVES_LIGHT, "down", "up")
		self.lever = SwitchableItem(1045, 0x8, Labels("lever", "a lever", "a mysterious lever"), 2, None, lever_list_templates, "{0} ({1})", lever_switching_info)

		suit_list_templates = {ListTemplateType.USING : "{0} (being worn)"}
		self.suit = UsableItem(1046, 0x402, Labels("suit", "a suit", "a space-suit"), 2, None, suit_list_templates, None, "{0} (being worn)", Item.ATTRIBUTE_GIVES_AIR)

		self.cat = SentientItem(1047, 0x80002, Labels("cat", "a cat", "a black cat"), 3, None, {}, None)
		self.water = Item(1109, 0x22902, Labels("water", "some water", "some water", [". It is cold", ". It is hot"]), 1, None, {}, None)
		self.mine_location = Location(11, 0x0, Labels("Mines", "in the mines", ". There are dark passages everywhere."))
		self.inventory = Inventory(0, 0x1, Labels("Main Inventory", "in the main inventory", ", where items live usually."), 100)

		self.steam = Item(1117, 0x2, Labels("steam", "some steam", "some hot steam"), 1, None, {}, None)
		self.water.transformations[98] = self.steam


	def test_copy(self):
		water_copy = copy(self.water)
		self.assertEqual(self.water.data_id, water_copy.data_id)
		self.assertEqual(self.water.shortname, water_copy.shortname)
		self.assertEqual(self.water.longname, water_copy.longname)
		self.assertEqual(self.water.description, water_copy.description)
		self.assertEqual(self.water.extended_descriptions, water_copy.extended_descriptions)
		self.assertFalse(water_copy.is_copyable())
		self.assertIs(self.steam, water_copy.transformations[98])
		self.assertIs(self.water, water_copy.copied_from)
		self.assertTrue(water_copy in self.water.copied_to)


	def test_get_original_not_copied(self):
		self.assertEqual(self.book, self.book.get_original())


	def test_get_original_copied_once(self):
		water_copy = copy(self.water)

		self.assertEqual(self.water, water_copy.get_original())


	def test_get_original_copied_twice(self):
		water_copy = copy(self.water)
		water_copy_copy = copy(water_copy)

		self.assertEqual(self.water, water_copy_copy.get_original())


	def test_break_open_non_container(self):
		self.assertIsNone(self.lamp.break_open())


	def test_get_list_name_simple(self):
		self.assertEqual("\n\ta book", self.book.get_list_name())


	def test_get_list_name_simple_indented(self):
		self.assertEqual("\n\t\t\ta book", self.book.get_list_name(3))


	def test_get_full_description_without_extended_descriptions(self):
		self.assertEqual(["a book of fairytales"], self.book.get_full_description())


	def test_get_full_description_with_extended_descriptions(self):
		self.assertEqual(["some water. It is cold"], self.water.get_full_description())


	def test_get_non_silent_list_name_simple_silent_item(self):
		self.assertEqual("", self.desk.get_non_silent_list_name())


	def test_get_non_silent_list_name_simple_non_silent_item(self):
		self.assertEqual("\n\ta book", self.book.get_non_silent_list_name())


	def test_break_open_container(self):
		self.box.insert(self.book)

		self.assertEqual(self.book, self.box.break_open())


	def test_get_list_name_container_empty(self):
		self.assertEqual("\n\ta basket (being lugged) (---)", self.basket.get_list_name())


	def test_get_list_name_container_nonempty(self):
		self.box.insert(self.book)

		self.assertEqual("\n\ta box (being lugged) +\n\t\ta book", self.box.get_list_name())


	def test_get_list_name_container_nonempty_multi(self):
		self.basket.insert(self.box)
		self.box.insert(self.book)

		self.assertEqual("\n\ta basket (being lugged) +\n\t\ta box +\n\t\t\ta book", self.basket.get_list_name())


	def test_contains_simple(self):
		self.assertFalse(self.desk.contains(self.book))


	def test_contains_container_empty(self):
		self.assertFalse(self.basket.contains(self.book))


	def test_contains_container_nonempty_single(self):
		self.box.insert(self.book)

		self.assertTrue(self.box.contains(self.book))


	def test_contains_container_nonempty_multi(self):
		self.basket.insert(self.box)
		self.box.insert(self.book)

		self.assertTrue(self.basket.contains(self.box))
		self.assertTrue(self.box.contains(self.book))
		self.assertTrue(self.basket.contains(self.book))


	def test_get_allow_copy_single(self):
		book_copy = copy(self.book)
		self.box.insert(book_copy)

		self.assertFalse(self.box.contains(self.book))
		self.assertEqual(book_copy, self.box.get_allow_copy(self.book))


	def test_get_allow_copy_multi(self):
		book_copy = copy(self.book)
		self.box.insert(book_copy)
		self.basket.insert(self.box)

		self.assertFalse(self.basket.contains(self.book))
		self.assertEqual(book_copy, self.basket.get_allow_copy(self.book))


	def test_get_outermost_container_location(self):
		self.mine_location.insert(self.book)

		self.assertEqual(self.mine_location, self.book.get_outermost_container())


	def test_get_outermost_container_inventory(self):
		self.inventory.insert(self.book)

		self.assertEqual(self.inventory, self.book.get_outermost_container())


	def test_get_outermost_container_multi(self):
		self.mine_location.insert(self.basket)
		self.basket.insert(self.box)
		self.box.insert(self.book)

		self.assertEqual(self.mine_location, self.book.get_outermost_container())


	def test_get_list_name_sentient(self):
		self.assertEqual("\n\ta cat", self.cat.get_list_name())


	def test_get_list_name_container_nonempty(self):
		self.cat.insert(self.book)

		self.assertEqual("\n\ta cat +\n\t\ta book", self.cat.get_list_name())


	def test_switch_on_self(self):
		self.lamp.switched_element = self.lamp

		self.lamp.switch_on()

		self.assertTrue(self.lamp.gives_light())


	def test_switch_off_self(self):
		self.lamp.switched_element = self.lamp

		self.lamp.switch_off()

		self.assertFalse(self.lamp.gives_light())


	def test_switch_on_other_item(self):
		self.button.switched_element = self.lamp

		self.button.switch_on()

		self.assertTrue(self.lamp.gives_light())


	def test_switch_off_other_item(self):
		self.button.switched_element = self.lamp

		self.button.switch_off()

		self.assertFalse(self.lamp.gives_light())


	def test_switch_on_other_location(self):
		self.lever.switched_element = self.mine_location

		self.lever.switch_on()

		self.assertTrue(self.mine_location.gives_light())


	def test_switch_off_other_location(self):
		self.lever.switched_element = self.mine_location

		self.lever.switch_off()

		self.assertFalse(self.mine_location.gives_light())


	def test_get_list_name_switchable_off(self):
		self.lamp.switched_element = self.lamp
		self.lamp.switch_off()

		self.assertEqual("\n\ta lamp (off)", self.lamp.get_list_name())


	def test_get_list_name_switchable_on(self):
		self.lever.switched_element = self.mine_location
		self.lever.switch_on()

		self.assertEqual("\n\ta lever (up)", self.lever.get_list_name())


	def test_get_full_description_switchable_without_extended_descriptions(self):
		self.lamp.switched_element = self.lamp
		self.lamp.switch_off()

		self.assertEqual(["a small lamp", "off"], self.lamp.get_full_description())


	def test_get_full_description_switchable_with_extended_descriptions(self):
		self.button.switched_element = self.lamp
		self.button.switch_off()

		self.assertEqual(["a red button. It is dark", "up"], self.button.get_full_description())


	def test_has_attribute_wearable_not_being_used(self):
		self.suit.being_used = False

		self.assertFalse(self.suit.gives_air())


	def test_has_attribute_wearable_being_used(self):
		self.suit.being_used = True

		self.assertTrue(self.suit.gives_air())


	def test_list_name_wearable_not_being_used(self):
		self.suit.being_used = False

		self.assertEqual("\n\ta suit", self.suit.get_list_name())


	def test_list_name_wearable_being_used(self):
		self.suit.being_used = True

		self.assertEqual("\n\ta suit (being worn)", self.suit.get_list_name())


if __name__ == "__main__":
	unittest.main()

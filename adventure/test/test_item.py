import unittest

from adventure.item import Item, ContainerItem, SwitchableItem
from adventure.location import Location

class TestItem(unittest.TestCase):

	def setUp(self):
		self.book = Item(1105, 0x2, "book", "a book", "a book of fairytales", 2, "The Pied Piper")
		self.desk = Item(1106, 0x20000, "desk", "a desk", "a large mahogany desk", 6, None)
		self.basket = ContainerItem(1107, 0x3, "basket", "a basket", "a large basket", 6, None)
		self.box = ContainerItem(1108, 0x3, "box", "a box", "a small box", 3, None)
		self.lamp = SwitchableItem(1043, 0x100A, "lamp", "a lamp", "a small lamp", 2, None, Item.ATTRIBUTE_GIVES_LIGHT)
		self.button = SwitchableItem(1044, 0x8, "button", "a button", "a red button", 2, None, Item.ATTRIBUTE_GIVES_LIGHT)
		self.lever = SwitchableItem(1045, 0x8, "lever", "a lever", "a mysterious lever", 2, None, Location.ATTRIBUTE_GIVES_LIGHT)
		self.mine_location = Location(11, 0x0, "Mines", "in the mines", ". There are dark passages everywhere.")


	def test_get_list_name_simple(self):
		self.assertEqual("\n\ta book", self.book.get_list_name())


	def test_get_list_name_simple_indented(self):
		self.assertEqual("\n\t\t\ta book", self.book.get_list_name(3))


	def test_get_non_silent_list_name_simple_silent_item(self):
		self.assertEqual("", self.desk.get_non_silent_list_name())


	def test_get_non_silent_list_name_simple_non_silent_item(self):
		self.assertEqual("\n\ta book", self.book.get_non_silent_list_name())


	def test_get_list_name_container_empty(self):
		self.assertEqual("\n\ta basket (---)", self.basket.get_list_name())


	def test_get_list_name_container_nonempty(self):
		self.box.insert(self.book)

		self.assertEqual("\n\ta box +\n\t\ta book", self.box.get_list_name())


	def test_get_list_name_container_nonempty_multi(self):
		self.basket.insert(self.box)
		self.box.insert(self.book)

		self.assertEqual("\n\ta basket +\n\t\ta box +\n\t\t\ta book", self.basket.get_list_name())


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


	def test_switch_on_other_location(self):
		self.lever.switched_element = self.mine_location

		self.lever.switch_off()

		self.assertFalse(self.mine_location.gives_light())


	def test_get_list_name_switchable_off(self):
		self.lamp.switched_element = self.lamp
		self.lamp.switch_off()

		self.assertEqual("\n\ta lamp (-)", self.lamp.get_list_name())


	def test_get_list_name_switchable_on(self):
		self.lever.switched_element = self.mine_location
		self.lever.switch_on()

		self.assertEqual("\n\ta lever (+)", self.lever.get_list_name())


if __name__ == "__main__":
	unittest.main()

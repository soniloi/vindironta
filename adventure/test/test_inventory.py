import unittest

from adventure.element import Labels
from adventure.item import Item, ContainerItem, UsableItem
from adventure.inventory import Inventory
from adventure.location import Location

class TestInventory(unittest.TestCase):

	def setUp(self):

		self.inventory = Inventory(0, 0x1, Labels("Main Inventory", "in the main inventory", ", where items live usually."), 3)
		self.book = Item(1105, 0x2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper")
		self.lamp = Item(1043, 0x10101A, Labels("lamp", "a lamp", "a small lamp"), 2, None)
		self.coin = Item(1000, 0x2, Labels("coin", "a coin", "a silver coin"), 1, None)
		self.medal = Item(1001, 0x2, Labels("medal", "a medal", "a gold medal"), 1, None)
		self.suit = UsableItem(1046, 0x402, Labels("suit", "a suit", "a space-suit"), 2, None, {}, None, None, Item.ATTRIBUTE_GIVES_AIR)
		self.water = Item(1109, 0x22902, Labels("water", "some water", "some water"), 1, None)
		self.basket = ContainerItem(1107, 0x3, Labels("basket", "a basket", "a large basket"), 6, None)
		self.non_essential_drop_location = Location(12, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.essential_drop_location = Location(9, 0x0, Labels("Cave", "in a cave", ". It is dark"))


	def test_insert_non_copyable(self):
		self.inventory.insert(self.book)

		self.assertTrue(self.inventory.contains(self.book))


	def test_insert_copyable(self):
		self.inventory.insert(self.water)

		self.assertFalse(self.inventory.contains(self.water))
		water_copy = self.inventory.get_allow_copy(self.water)
		self.assertTrue(water_copy)
		self.assertEqual(self.water.data_id, water_copy.data_id)
		self.assertIs(self.water, water_copy.copied_from)
		self.assertTrue(water_copy in self.water.copied_to)


	def test_can_accommodate_below_capacity(self):
		self.assertTrue(self.inventory.can_accommodate(self.book))


	def test_can_accommodate_to_capacity(self):
		self.inventory.insert(self.book)

		self.assertTrue(self.inventory.can_accommodate(self.coin))


	def test_can_accommodate_at_capacity(self):
		self.inventory.insert(self.book)
		self.inventory.insert(self.medal)

		self.assertFalse(self.inventory.can_accommodate(self.coin))


	def test_can_accommodate_above_capacity_non_wearable(self):
		self.inventory.insert(self.book)

		self.assertFalse(self.inventory.can_accommodate(self.lamp))


	def test_can_accommodate_above_capacity_wearable_not_being_used(self):
		self.inventory.insert(self.suit)
		self.suit.being_used = False

		self.assertFalse(self.inventory.can_accommodate(self.lamp))


	def test_can_accommodate_above_capacity_wearable_being_used(self):
		self.inventory.insert(self.suit)
		self.suit.being_used = True

		self.assertTrue(self.inventory.can_accommodate(self.lamp))


	def test_drop_all_items_none(self):
		self.inventory.drop_all_items(self.non_essential_drop_location, self.essential_drop_location)

		self.assertFalse(self.inventory.has_items())
		self.assertFalse(self.non_essential_drop_location.has_items())
		self.assertFalse(self.essential_drop_location.has_items())


	def test_drop_all_items_single(self):
		self.inventory.insert(self.book)

		self.inventory.drop_all_items(self.non_essential_drop_location, self.essential_drop_location)

		self.assertFalse(self.inventory.has_items())
		self.assertTrue(self.non_essential_drop_location.contains(self.book))
		self.assertFalse(self.essential_drop_location.has_items())


	def test_drop_all_items_multiple_with_only_non_essential(self):
		self.inventory.insert(self.coin)
		self.inventory.insert(self.medal)
		self.inventory.insert(self.book)

		self.inventory.drop_all_items(self.non_essential_drop_location, self.essential_drop_location)

		self.assertFalse(self.inventory.has_items())
		self.assertTrue(self.non_essential_drop_location.contains(self.coin))
		self.assertTrue(self.non_essential_drop_location.contains(self.medal))
		self.assertTrue(self.non_essential_drop_location.contains(self.book))
		self.assertFalse(self.essential_drop_location.has_items())


	def test_drop_all_items_multiple_with_essential_item_simple(self):
		self.inventory.insert(self.book)
		self.inventory.insert(self.lamp)

		self.inventory.drop_all_items(self.non_essential_drop_location, self.essential_drop_location)

		self.assertFalse(self.inventory.has_items())
		self.assertTrue(self.non_essential_drop_location.contains(self.book))
		self.assertFalse(self.non_essential_drop_location.contains(self.lamp))
		self.assertTrue(self.essential_drop_location.has_items())
		self.assertFalse(self.essential_drop_location.contains(self.book))
		self.assertTrue(self.essential_drop_location.contains(self.lamp))


	def test_drop_all_items_multiple_with_essential_item_nested(self):
		self.basket.insert(self.lamp)
		self.inventory.insert(self.basket)

		self.inventory.drop_all_items(self.non_essential_drop_location, self.essential_drop_location)

		self.assertFalse(self.inventory.has_items())
		self.assertFalse(self.non_essential_drop_location.has_items())
		self.assertTrue(self.essential_drop_location.has_items())
		self.assertFalse(self.lamp in self.essential_drop_location.items)
		self.assertTrue(self.basket in self.essential_drop_location.items)
		self.assertTrue(self.basket.contains(self.lamp))


if __name__ == "__main__":
	unittest.main()

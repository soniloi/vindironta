from copy import copy

import unittest

from adventure.data_element import Labels
from adventure.direction import Direction
from adventure.item import Item, ContainerItem
from adventure.location import Location

class TestLocation(unittest.TestCase):

	def setUp(self):
		self.location = Location(11, 0, Labels("Mines", "in the mines", ". There are dark passages everywhere"))
		self.other_location = Location(12, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))

		self.book = Item(1105, 2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper")
		self.desk = Item(1000, 0x20000, Labels("desk", "a desk", "a large mahogany desk"), 6, None)
		self.obstruction = Item(1000, 0x4, Labels("obstruction", "an obstruction", "an obstruction blocking you"), 8, None)
		self.basket = ContainerItem(1107, 0x3, Labels("basket", "a basket", "a large basket"), 6, None)
		self.box = ContainerItem(1108, 0x3, Labels("box", "a box", "a small box"), 3, None)


	def test_contains_simple(self):
		self.location.insert(self.book)

		self.assertEqual(1, len(self.book.containers))
		self.assertTrue(self.location in self.book.containers)
		self.assertTrue(self.location.contains(self.book))


	def test_contains_container_single(self):
		self.box.insert(self.book)
		self.location.insert(self.box)

		self.assertTrue(self.location.contains(self.box))


	def test_contains_container_multi(self):
		self.basket.insert(self.box)
		self.box.insert(self.book)
		self.location.insert(self.basket)

		self.assertTrue(self.location.contains(self.book))


	def test_contains_allow_copy_simple(self):
		book_copy = copy(self.book)
		self.location.add(book_copy)

		self.assertFalse(self.location.contains(self.book))
		self.assertTrue(self.location.contains_allow_copy(self.book))


	def test_contains_allow_copy_container(self):
		book_copy = copy(self.book)
		self.box.insert(book_copy)
		self.location.insert(self.box)

		self.assertFalse(self.location.contains(self.book))
		self.assertTrue(self.location.contains_allow_copy(self.book))


	def test_get_arrival_description_not_seen_not_verbose(self):
		description = self.location.get_arrival_description(False)

		self.assertEqual(["in the mines. There are dark passages everywhere", ""], description)


	def test_get_arrival_description_not_seen_verbose(self):
		description = self.location.get_arrival_description(True)

		self.assertEqual(["in the mines. There are dark passages everywhere", ""], description)


	def test_get_arrival_description_seen_not_verbose(self):
		self.location.seen = True

		description = self.location.get_arrival_description(False)

		self.assertEqual(["in the mines", ""], description)


	def test_get_arrival_description_seen_verbose(self):
		self.location.seen = True

		description = self.location.get_arrival_description(True)

		self.assertEqual(["in the mines. There are dark passages everywhere", ""], description)


	def test_get_full_description_non_silent(self):
		self.location.seen = True
		self.location.insert(self.book)

		description = self.location.get_full_description()

		self.assertEqual(["in the mines. There are dark passages everywhere", "\n\ta book"], description)


	def test_get_full_description_silent(self):
		self.location.seen = True
		self.location.insert(self.desk)

		description = self.location.get_full_description()

		self.assertEqual(["in the mines. There are dark passages everywhere", ""], description)


	def test_get_obstructions(self):
		self.location.insert(self.book)
		self.location.insert(self.obstruction)

		obstructions = self.location.get_obstructions()

		self.assertEqual(1, len(obstructions))
		self.assertIs(self.obstruction, obstructions[0])


	def test_can_reach_no_ways(self):
		self.assertFalse(self.location.can_reach(self.other_location))


	def test_can_reach_one_way(self):
		self.location.directions[Direction.SOUTH] = self.other_location

		self.assertTrue(self.location.can_reach(self.other_location))


	def test_can_reach_multiple_ways(self):
		self.location.directions[Direction.SOUTH] = self.other_location
		self.location.directions[Direction.NORTHEAST] = self.other_location
		self.location.directions[Direction.DOWN] = self.other_location

		self.assertTrue(self.location.can_reach(self.other_location))


if __name__ == "__main__":
	unittest.main()

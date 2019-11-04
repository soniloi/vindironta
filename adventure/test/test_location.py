from copy import copy
import unittest

from adventure.direction import Direction
from adventure.element import Labels
from adventure.item import Item, ContainerItem
from adventure.location import Location

class TestLocation(unittest.TestCase):

	def setUp(self):
		extended_descriptions = [". The walls are dark and cold", ". The walls are glowing"]
		self.lighthouse_location = Location(12, 0x1, Labels("Lighthouse", "at a lighthouse", " by the sea."))
		self.mine_location = Location(11, 0x0, Labels("Mines", "in the mines", ". There are dark passages everywhere", extended_descriptions))
		self.lower_mine_location = Location(10, 0x200, Labels("Lower mines", "in the lower mines", ". This is the bottom of the mines", extended_descriptions))

		self.book = Item(1105, 2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper", {})
		self.desk = Item(1000, 0x20000, Labels("desk", "a desk", "a large mahogany desk"), 6, None, {})
		self.obstruction = Item(1000, 0x4, Labels("obstruction", "an obstruction", "an obstruction blocking you"), 8, None, {})
		self.basket = ContainerItem(1107, 0x3, Labels("basket", "a basket", "a large basket"), 6, None, {})
		self.box = ContainerItem(1108, 0x3, Labels("box", "a box", "a small box"), 3, None, {})


	def test_contains_simple(self):
		self.mine_location.insert(self.book)

		self.assertEqual(1, len(self.book.containers))
		self.assertTrue(self.mine_location in self.book.containers)
		self.assertTrue(self.mine_location.contains(self.book))


	def test_contains_container_single(self):
		self.box.insert(self.book)
		self.mine_location.insert(self.box)

		self.assertTrue(self.mine_location.contains(self.box))


	def test_contains_container_multi(self):
		self.basket.insert(self.box)
		self.box.insert(self.book)
		self.mine_location.insert(self.basket)

		self.assertTrue(self.mine_location.contains(self.book))


	def test_get_allow_copy_simple(self):
		book_copy = copy(self.book)
		self.mine_location.add(book_copy)

		self.assertFalse(self.mine_location.contains(self.book))
		self.assertEqual(book_copy, self.mine_location.get_allow_copy(self.book))


	def test_get_allow_copy_container(self):
		book_copy = copy(self.book)
		self.box.insert(book_copy)
		self.mine_location.insert(self.box)

		self.assertFalse(self.mine_location.contains(self.book))
		self.assertEqual(book_copy, self.mine_location.get_allow_copy(self.book))


	def test_get_arrival_description_not_seen_not_verbose(self):
		description = self.mine_location.get_arrival_description(False)

		self.assertEqual(["in the mines. There are dark passages everywhere. The walls are dark and cold", ""], description)


	def test_get_arrival_description_not_seen_verbose(self):
		description = self.mine_location.get_arrival_description(True)

		self.assertEqual(["in the mines. There are dark passages everywhere. The walls are dark and cold", ""], description)


	def test_get_arrival_description_seen_not_verbose(self):
		self.mine_location.seen = True

		description = self.mine_location.get_arrival_description(False)

		self.assertEqual(["in the mines", ""], description)


	def test_get_arrival_description_seen_verbose(self):
		self.mine_location.seen = True

		description = self.mine_location.get_arrival_description(True)

		self.assertEqual(["in the mines. There are dark passages everywhere. The walls are dark and cold", ""], description)


	def test_get_full_description_non_silent(self):
		self.mine_location.seen = True
		self.mine_location.insert(self.book)

		description = self.mine_location.get_full_description()

		self.assertEqual(["in the mines. There are dark passages everywhere. The walls are dark and cold", "\n\ta book"], description)


	def test_get_full_description_silent(self):
		self.mine_location.seen = True
		self.mine_location.insert(self.desk)

		description = self.mine_location.get_full_description()

		self.assertEqual(["in the mines. There are dark passages everywhere. The walls are dark and cold", ""], description)


	def test_get_drop_location_has_floor(self):
		self.assertIs(self.lower_mine_location, self.lower_mine_location.get_drop_location())


	def test_get_drop_location_one_below_has_floor(self):
		self.mine_location.directions[Direction.DOWN] = self.lower_mine_location

		self.assertIs(self.lower_mine_location, self.mine_location.get_drop_location())


	def test_get_drop_location_two_below_has_floor(self):
		self.lighthouse_location.directions[Direction.DOWN] = self.mine_location
		self.mine_location.directions[Direction.DOWN] = self.lower_mine_location

		self.assertIs(self.lower_mine_location, self.lighthouse_location.get_drop_location())


	def test_get_obstructions(self):
		self.mine_location.insert(self.book)
		self.mine_location.insert(self.obstruction)

		obstructions = self.mine_location.get_obstructions()

		self.assertEqual(1, len(obstructions))
		self.assertIs(self.obstruction, obstructions[0])


	def test_can_reach_no_ways(self):
		self.assertFalse(self.mine_location.can_reach(self.lighthouse_location))


	def test_can_reach_one_way(self):
		self.mine_location.directions[Direction.SOUTH] = self.lighthouse_location

		self.assertTrue(self.mine_location.can_reach(self.lighthouse_location))


	def test_can_reach_multiple_ways(self):
		self.mine_location.directions[Direction.SOUTH] = self.lighthouse_location
		self.mine_location.directions[Direction.NORTHEAST] = self.lighthouse_location
		self.mine_location.directions[Direction.DOWN] = self.lighthouse_location

		self.assertTrue(self.mine_location.can_reach(self.lighthouse_location))


	def test_gives_tether_with_gravity_with_ceiling(self):
		self.mine_location.set_attribute(Location.ATTRIBUTE_GIVES_GRAVITY)
		self.mine_location.set_attribute(Location.ATTRIBUTE_HAS_CEILING)

		self.assertTrue(self.mine_location.gives_tether())


	def test_gives_tether_with_gravity_without_ceiling(self):
		self.mine_location.set_attribute(Location.ATTRIBUTE_GIVES_GRAVITY)
		self.mine_location.unset_attribute(Location.ATTRIBUTE_HAS_CEILING)

		self.assertTrue(self.mine_location.gives_tether())


	def test_gives_tether_without_gravity_with_ceiling(self):
		self.mine_location.unset_attribute(Location.ATTRIBUTE_GIVES_GRAVITY)
		self.mine_location.set_attribute(Location.ATTRIBUTE_HAS_CEILING)

		self.assertTrue(self.mine_location.gives_tether())


	def test_gives_tether_without_gravity_without_ceiling_with_location_above_that_gives_tether(self):
		self.mine_location.unset_attribute(Location.ATTRIBUTE_GIVES_GRAVITY)
		self.mine_location.unset_attribute(Location.ATTRIBUTE_HAS_CEILING)
		self.mine_location.directions[Direction.UP] = self.lighthouse_location
		self.lighthouse_location.set_attribute(Location.ATTRIBUTE_GIVES_GRAVITY)
		self.lighthouse_location.set_attribute(Location.ATTRIBUTE_HAS_CEILING)

		self.assertTrue(self.mine_location.gives_tether())


	def test_gives_tether_without_gravity_without_ceiling_with_location_above_that_gives_no_tether(self):
		self.mine_location.unset_attribute(Location.ATTRIBUTE_GIVES_GRAVITY)
		self.mine_location.unset_attribute(Location.ATTRIBUTE_HAS_CEILING)
		self.mine_location.directions[Direction.UP] = self.lighthouse_location
		self.lighthouse_location.unset_attribute(Location.ATTRIBUTE_GIVES_GRAVITY)
		self.lighthouse_location.unset_attribute(Location.ATTRIBUTE_HAS_CEILING)

		self.assertFalse(self.mine_location.gives_tether())


	def test_gives_tether_without_gravity_without_ceiling_without_location_above(self):
		self.mine_location.unset_attribute(Location.ATTRIBUTE_GIVES_GRAVITY)
		self.mine_location.unset_attribute(Location.ATTRIBUTE_HAS_CEILING)

		self.assertFalse(self.mine_location.gives_tether())


if __name__ == "__main__":
	unittest.main()

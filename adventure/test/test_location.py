import unittest

from adventure.item import Item
from adventure.location import Location

class TestLocation(unittest.TestCase):

	def setUp(self):
		self.location = Location(11, 0, "Mines", "in the mines", ". There are dark passages everywhere")
		self.book = Item(1105, 2, "book", "a book", "a book of fairytales", 2, "The Pied Piper")
		self.desk = Item(1000, 0x20000, "desk", "a desk", "a large mahogany desk", 6, None)
		self.obstruction = Item(1000, 0x4, "obstruction", "an obstruction", "an obstruction blocking you", 8, None)


	def test_insert(self):
		self.location.insert(self.book)

		self.assertEqual(self.location, self.book.container)
		self.assertTrue(self.location.contains(self.book))


	def test_get_arrival_description_not_visited(self):
		description = self.location.get_arrival_description()

		self.assertEqual(["in the mines. There are dark passages everywhere", ""], description)


	def test_get_arrival_description_visited(self):
		self.location.visited = True

		description = self.location.get_arrival_description()

		self.assertEqual(["in the mines", ""], description)


	def test_get_full_description_non_silent(self):
		self.location.visited = True
		self.location.insert(self.book)

		description = self.location.get_full_description()

		self.assertEqual(["in the mines", "\n\ta book"], self.location.get_arrival_description())


	def test_get_full_description_silent(self):
		self.location.visited = True
		self.location.insert(self.desk)

		description = self.location.get_full_description()

		self.assertEqual(["in the mines", ""], self.location.get_arrival_description())


	def test_get_obstructions(self):
		self.location.insert(self.book)
		self.location.insert(self.obstruction)

		obstructions = self.location.get_obstructions()

		self.assertEqual(1, len(obstructions))
		self.assertIs(self.obstruction, obstructions[0])


if __name__ == "__main__":
	unittest.main()

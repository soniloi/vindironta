import unittest

from adventure.item import Item
from adventure.location import Location

class TestLocation(unittest.TestCase):

	def setUp(self):
		self.location = Location(11, 0, "Mines", "in the mines", ". There are dark passages everywhere")


	def test_insert(self):
		book = Item(1105, 2, "book", "a book", "a book of fairytales", 2, "The Pied Piper")

		self.location.insert(book)

		self.assertEqual(self.location, book.container)
		self.assertTrue(self.location.contains(book))


	def test_get_arrival_description_not_visited(self):
		self.assertEqual(["in the mines. There are dark passages everywhere", ""], self.location.get_arrival_description())


	def test_get_arrival_description_visited(self):
		self.location.visited = True
		self.assertEqual(["in the mines", ""], self.location.get_arrival_description())


if __name__ == "__main__":
	unittest.main()

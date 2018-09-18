import unittest
from unittest.mock import Mock
from unittest.mock import patch

from adventure.item_collection import ItemCollection
from adventure import file_reader
from adventure import location_collection

class TestItemCollection(unittest.TestCase):

	def setUp(self):
		with patch(file_reader.__name__ + ".FileReader") as reader_mock, \
			patch(location_collection.__name__ + ".LocationCollection") as location_collection_mock:
			reader_mock_instance = reader_mock.return_value
			reader_mock_instance.read_line.side_effect = [
				"1042\t2002\t27\t3\tkohlrabi,cabbage\tsome kohlrabi\tsome kohlrabi, or Brassica oleracea var. gongylodes, a cabbage cultivar\t0",
				"1076\t22802\t1007\t1\twater\twater\tRiver Amethyst water. It is cold and clear\t0",
				"1105\t2\t80\t2\tbook\ta book\ta book of fairytales in English. It is open on a particular page\tThe Pied Piper of Hamelin",
				"---",
			]

			location_collection_mock_instance = location_collection_mock.return_value
			location_collection_mock_instance.get.side_effect = self.location_side_effect
			self.kohlrabi_initial_location = Mock()
			self.book_initial_location = Mock()
			self.location_map = {
				27 : self.kohlrabi_initial_location,
				80 : self.book_initial_location,
			}

			self.collection = ItemCollection(reader_mock_instance, location_collection_mock_instance)


	def location_side_effect(self, *args):
		location_id = int(args[0])
		if location_id in self.location_map:
			return self.location_map[location_id]
		return None


	def test_init(self):
		self.assertEqual(4, len(self.collection.items))
		self.assertTrue("book" in self.collection.items)
		self.assertTrue("cabbage" in self.collection.items)
		self.assertTrue("kohlrabi" in self.collection.items)

		book = self.collection.items["book"]
		self.assertEqual(0x2, book.attributes)
		self.assertEqual(self.book_initial_location, book.location)
		self.assertEqual(2, book.size)
		self.assertEqual("book", book.shortname)
		self.assertEqual("a book", book.longname)
		self.assertEqual("a book of fairytales in English. It is open on a particular page", book.description)
		self.assertEqual("The Pied Piper of Hamelin", book.writing)

		kohlrabi = self.collection.items["kohlrabi"]
		self.assertEqual(0x2002, kohlrabi.attributes)
		self.assertEqual(self.kohlrabi_initial_location, kohlrabi.location)
		self.assertEqual("kohlrabi", kohlrabi.shortname)
		self.assertIsNone(kohlrabi.writing)

		cabbage = self.collection.items["cabbage"]
		self.assertIs(kohlrabi, cabbage)
		self.assertIsNot(kohlrabi, book)

		water = self.collection.items["water"]
		self.assertIsNone(water.location)


if __name__ == "__main__":
	unittest.main()

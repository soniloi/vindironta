import unittest
from unittest.mock import patch

from adventure.item_collection import ItemCollection
from adventure import file_reader

class TestItemCollection(unittest.TestCase):

	def setUp(self):
		with patch(file_reader.__name__ + ".FileReader") as reader_mock:
			reader_mock_instance = reader_mock.return_value
			reader_mock_instance.read_line.side_effect = [
				"1042\t2002\t27\t3\tkohlrabi,cabbage\tsome kohlrabi\tsome kohlrabi, or Brassica oleracea var. gongylodes, a cabbage cultivar\t0",
				"1105\t2\t80\t2\tbook\ta book\ta book of fairytales in English. It is open on a particular page\tThe Pied Piper of Hamelin",
				"---",
			]

			self.collection = ItemCollection(reader_mock_instance)


	def test_init(self):
		self.assertEqual(3, len(self.collection.items))
		self.assertTrue("book" in self.collection.items)
		self.assertTrue("cabbage" in self.collection.items)
		self.assertTrue("kohlrabi" in self.collection.items)

		book = self.collection.items["book"]
		self.assertEqual(0x2, book.attributes)
		self.assertEqual(2, book.size)
		self.assertEqual("book", book.shortname)
		self.assertEqual("a book", book.longname)
		self.assertEqual("a book of fairytales in English. It is open on a particular page", book.description)
		self.assertEqual("The Pied Piper of Hamelin", book.writing)

		kohlrabi = self.collection.items["kohlrabi"]
		self.assertEqual(0x2002, kohlrabi.attributes)
		self.assertEqual("kohlrabi", kohlrabi.shortname)
		self.assertIsNone(kohlrabi.writing)

		cabbage = self.collection.items["cabbage"]
		self.assertIs(kohlrabi, cabbage)
		self.assertIsNot(kohlrabi, book)


if __name__ == "__main__":
	unittest.main()

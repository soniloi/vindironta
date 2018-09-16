import unittest
from unittest.mock import patch

from adventure.item_collection import ItemCollection
from adventure import file_reader

class TestItemCollection(unittest.TestCase):

	def setUp(self):
		with patch(file_reader.__name__ + ".FileReader") as reader_mock:
			reader_mock_instance = reader_mock.return_value
			reader_mock_instance.read_line.side_effect = [
				"1043\t0101A\t34\t3\tlamp\ta lamp\ta small hand-held lamp; I cannot determine its power source\t0",
				"1105\t2\t80\t2\tbook\ta book\ta book of fairytales in English. It is open on a particular page\tThe Pied Piper of Hamelin",
				"---",
			]

			self.collection = ItemCollection(reader_mock_instance)


	def test_init(self):
		self.assertEqual(2, len(self.collection.items))
		self.assertTrue("lamp" in self.collection.items)
		self.assertTrue("book" in self.collection.items)

		lamp = self.collection.items["lamp"]
		self.assertEqual(0x0101A, lamp.attributes)
		self.assertEqual("lamp", lamp.shortname)
		self.assertEqual("a lamp", lamp.longname)
		self.assertEqual("a small hand-held lamp; I cannot determine its power source", lamp.description)

		book = self.collection.items["book"]
		self.assertIsNot(lamp, book)


if __name__ == "__main__":
	unittest.main()

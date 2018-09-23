import unittest
from unittest.mock import patch

from adventure import file_reader
from adventure.text_collection import TextCollection

class TestTextCollection(unittest.TestCase):

	def setUp(self):
		with patch(file_reader.__name__ + ".FileReader") as reader_mock:
			reader_mock_instance = reader_mock.return_value
			reader_mock_instance.read_line.side_effect = [
				"inventory\tThis command lists the items you are carrying.",
				"lamp\tThe lamp can be turned on with the \"light\" command and turned off with the \"quench\" command.",
				"---",
			]
			self.collection = TextCollection(reader_mock_instance)


	def test_init(self):
		self.assertEqual(2, len(self.collection.texts))
		self.assertTrue("inventory" in self.collection.texts)
		self.assertTrue("lamp" in self.collection.texts)
		self.assertEqual("This command lists the items you are carrying.", self.collection.texts["inventory"])
		self.assertEqual("The lamp can be turned on with the \"light\" command and turned off with the \"quench\" command.", self.collection.texts["lamp"])


if __name__ == "__main__":
	unittest.main()

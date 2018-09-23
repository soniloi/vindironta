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
				"reject_not_here\tThere is no $0 here.",
				"confirm_insert\tYou insert the $0 into the $1.",
				"---",
			]
			self.collection = TextCollection(reader_mock_instance)


	def test_init(self):
		self.assertEqual(3, len(self.collection.texts))
		self.assertTrue("inventory" in self.collection.texts)
		self.assertTrue("reject_not_here" in self.collection.texts)
		self.assertEqual("This command lists the items you are carrying.", self.collection.texts["inventory"])
		self.assertEqual("There is no {0} here.", self.collection.texts["reject_not_here"])
		self.assertEqual("You insert the {0} into the {1}.", self.collection.texts["confirm_insert"])


if __name__ == "__main__":
	unittest.main()

import json
import unittest

from adventure.text_parser import TextParser

class TestTextParser(unittest.TestCase):

	def setUp(self):
		pass


	def test_parse(self):
		text_inputs = json.loads(
			"{ \
				\"inventory\": \"This command lists the items you are carrying.\", \
				\"reject_not_here\": \"There is no $0 here.\", \
				\"confirm_insert\": \"You insert the $0 into the $1.\" \
			}"
		)

		self.collection = TextParser().parse(text_inputs)

		self.assertEqual(3, len(self.collection.texts))
		self.assertTrue("inventory" in self.collection.texts)
		self.assertTrue("reject_not_here" in self.collection.texts)
		self.assertEqual("This command lists the items you are carrying.", self.collection.get("inventory"))
		self.assertEqual("There is no {0} here.", self.collection.get("reject_not_here"))
		self.assertEqual("You insert the {0} into the {1}.", self.collection.get("confirm_insert"))
		self.assertEqual("", self.collection.get("unknown"))


if __name__ == "__main__":
	unittest.main()

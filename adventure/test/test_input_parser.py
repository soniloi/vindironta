import json
import unittest

from adventure.input_parser import InputParser

class TestInputParser(unittest.TestCase):

	def setUp(self):
		pass


	def test_single_input_key(self):
		input_inputs = json.loads("{\"no\":[\"no\"]}")

		collection = InputParser().parse(input_inputs)

		self.assertEqual(1, len(collection.inputs))
		self.assertEqual("no", collection.inputs["no"])


	def test_multi_input_key(self):
		input_inputs = json.loads("{\"no\":[\"no\",\"n\",\"false\"], \
			\"yes\":[\"yes\",\"y\",\"true\",\"absolutely\"]}")

		collection = InputParser().parse(input_inputs)

		self.assertEqual(7, len(collection.inputs))
		self.assertEqual("no", collection.inputs["no"])
		self.assertEqual("no", collection.inputs["n"])
		self.assertEqual("no", collection.inputs["false"])
		self.assertEqual("yes", collection.inputs["yes"])
		self.assertEqual("yes", collection.inputs["y"])
		self.assertEqual("yes", collection.inputs["true"])
		self.assertEqual("yes", collection.inputs["absolutely"])


if __name__ == "__main__":
	unittest.main()

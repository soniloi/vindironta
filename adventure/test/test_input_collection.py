import json
import unittest

from adventure.input_collection import InputCollection

class TestInputCollection(unittest.TestCase):

	def setUp(self):
		pass


	def test_single_input_key(self):
		input_inputs = json.loads("{\"no\":[\"no\"]}")

		collection = InputCollection(input_inputs)

		self.assertEqual(1, len(collection.inputs))
		self.assertTrue("no" in collection.inputs)

		no_inputs = collection.inputs["no"]
		self.assertEqual(1, len(no_inputs))
		self.assertTrue("no" in no_inputs)


	def test_multi_input_key(self):
		input_inputs = json.loads("{\"no\":[\"no\",\"n\",\"false\"], \
			\"yes\":[\"yes\",\"y\",\"true\",\"absolutely\"]}")

		collection = InputCollection(input_inputs)

		self.assertEqual(2, len(collection.inputs))
		self.assertTrue("no" in collection.inputs)
		self.assertTrue("yes" in collection.inputs)

		no_inputs = collection.inputs["no"]
		self.assertEqual(3, len(no_inputs))
		self.assertTrue("no" in no_inputs)
		self.assertTrue("n" in no_inputs)
		self.assertTrue("false" in no_inputs)

		yes_inputs = collection.inputs["yes"]
		self.assertEqual(4, len(yes_inputs))
		self.assertTrue("yes" in yes_inputs)
		self.assertTrue("y" in yes_inputs)
		self.assertTrue("true" in yes_inputs)
		self.assertTrue("absolutely" in yes_inputs)


if __name__ == "__main__":
	unittest.main()

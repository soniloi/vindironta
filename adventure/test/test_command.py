import unittest

from adventure.command import Command
from adventure.data_element import Labels
from adventure.item import Item

class TestCommand(unittest.TestCase):

	def setUp(self):
		self.command_movement = Command(1, 0x49, 0x0, [self.arg_function_movement, self.vision_function],
			self.handler_function, "", [],  {}, {})
		self.command_non_movement = Command(1, 0x9, 0x0, [self.arg_function_non_movement, self.vision_function],
			self.handler_function, "", [],  {}, {})
		self.command_unsuccessful = Command(1, 0x9, 0x0, [self.arg_function_unsuccessful, self.vision_function],
			self.handler_function, "", [], {}, {})


	def arg_function_movement(self, command, player, *args):
		return True, "", [command.data_id]


	def arg_function_non_movement(self, command, player, *args):
		return True, "", args


	def arg_function_unsuccessful(self, command, player, *args):
		return False, "reason template", args


	def handler_function(self, command, player, *arg):
		return True, ("{0} success!", list(arg))


	def vision_function(self, command, player, *arg):
		return True, "", list(arg)


	def test_has_attribute_set(self):
		self.assertTrue(self.command_non_movement.has_attribute(0x8))


	def test_has_attribute_not_set(self):
		self.assertFalse(self.command_non_movement.has_attribute(0x4))


	def test_execute_movement(self):
		result = self.command_movement.execute(None, ["test"])

		self.assertEqual("1 success!", result)


	def test_execute_non_movement(self):
		result = self.command_non_movement.execute(None, ["test"])

		self.assertEqual("test success!", result)


	def test_execute_item_args(self):
		book = Item(1105, 2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper")

		result = self.command_non_movement.execute(None, [book])

		self.assertEqual("book success!", result)


	def test_execute_unsuccessful(self):
		result = self.command_unsuccessful.execute(None, ["test"])

		self.assertEqual("reason template", result)


if __name__ == "__main__":
	unittest.main()

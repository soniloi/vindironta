import unittest

from adventure.command import Command

class TestCommand(unittest.TestCase):

	def setUp(self):
		self.command_movement = Command(1, 0x49, 0x0, self.arg_function_movement, self.handler_function,
			self.vision_function, "", [],  {}, {})
		self.command_non_movement = Command(1, 0x9, 0x0, self.arg_function_non_movement, self.handler_function,
			self.vision_function, "", [],  {}, {})


	def arg_function_movement(self, command, player, args):
		return True, (player, [command.data_id])


	def arg_function_non_movement(self, command, player, args):
		return True, (player, args)


	def handler_function(self, player, arg):
		return "{0} success!", [arg]


	def vision_function(self, command, player, arg):
		return True, (player, arg)


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


if __name__ == "__main__":
	unittest.main()

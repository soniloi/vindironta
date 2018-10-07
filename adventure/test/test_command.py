import unittest

from adventure.command import Command

class TestCommand(unittest.TestCase):

	def setUp(self):
		self.command_singular = Command(1, 0x9, self.resolver_function_non_movement, self.handler_function_singular, "", [], False)
		self.command_movement = Command(1, 0x49, self.resolver_function_movement, self.handler_function_singular, "", [], False)
		self.command_list = Command(1, 0x9, self.resolver_function_non_movement, self.handler_function_list, "", [], False)


	def resolver_function_movement(self, command, player, arg):
		arg = command.command_id
		return command.handler_function(player, arg)


	def resolver_function_non_movement(self, command, player, arg):
		return command.handler_function(player, arg)


	def handler_function_singular(self, player, arg):
		return "{0} success!", arg


	def handler_function_list(self, player, arg):
		return "{0} success!", [arg]


	def test_has_attribute_set(self):
		self.assertTrue(self.command_singular.has_attribute(0x8))


	def test_has_attribute_not_set(self):
		self.assertFalse(self.command_singular.has_attribute(0x4))


	def test_execute_singular_non_movement(self):
		result = self.command_singular.execute(None, "test")

		self.assertEqual("test success!", result)


	def test_execute_singular_movement(self):
		result = self.command_movement.execute(None, "test")

		self.assertEqual("1 success!", result)


	def test_execute_list(self):
		result = self.command_list.execute(None, "test")

		self.assertEqual("test success!", result)


if __name__ == "__main__":
	unittest.main()

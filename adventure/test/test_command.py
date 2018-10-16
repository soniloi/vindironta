import unittest

from adventure.command import Command

class TestCommand(unittest.TestCase):

	def setUp(self):
		self.command_singular = Command(1, 0x9, self.arg_function_non_movement, self.handler_function_singular,
			self.vision_function, "", [],  None, None)
		self.command_movement = Command(1, 0x49, self.arg_function_movement, self.handler_function_singular,
			self.vision_function, "", [],  None, None)
		self.command_switchable = Command(1, 0x100, self.arg_function_non_movement, self.handler_function_singular,
			self.vision_function, "", [],  "off", "on")
		self.command_list = Command(1, 0x9, self.arg_function_non_movement, self.handler_function_list,
			self.vision_function, "", [],  None, None)


	def arg_function_movement(self, command, player, arg):
		arg = command.command_id
		return command.handler_function(player, arg)


	def arg_function_non_movement(self, command, player, arg):
		return command.handler_function(player, arg)


	def handler_function_singular(self, player, arg):
		return "{0} success!", arg


	def handler_function_list(self, player, arg):
		return "{0} success!", [arg]


	def vision_function(self, command, player, arg):
		return command.arg_function(command, player, arg)


	def test_init(self):
		self.assertFalse(self.command_singular.transitions)
		self.assertFalse(self.command_movement.transitions)
		self.assertFalse(self.command_list.transitions)
		self.assertIn("off", self.command_switchable.transitions)
		self.assertIn("on", self.command_switchable.transitions)
		self.assertFalse(self.command_switchable.transitions["off"])
		self.assertTrue(self.command_switchable.transitions["on"])


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

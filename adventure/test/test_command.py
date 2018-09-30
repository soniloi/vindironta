import unittest

from adventure.command import Command

class TestCommand(unittest.TestCase):

	def setUp(self):
		self.command_singular = Command(1, 0x9, self.command_function_singular, "", [])
		self.command_list = Command(1, 0x9, self.command_function_list, "", [])


	def command_function_singular(self, player, arg):
		return "{0} success!", arg


	def command_function_list(self, player, arg):
		return "{0} success!", [arg]


	def test_has_attribute_set(self):
		self.assertTrue(self.command_singular.has_attribute(0x8))


	def test_has_attribute_not_set(self):
		self.assertFalse(self.command_singular.has_attribute(0x4))


	def test_execute_singular_non_movement(self):
		result = self.command_singular.execute(None, "test")

		self.assertEqual("test success!", result)


	def test_execute_singular_movement(self):
		self.command_singular.attributes |= 0x40

		result = self.command_singular.execute(None, "test")

		self.assertEqual("1 success!", result)


	def test_execute_list(self):
		result = self.command_list.execute(None, "test")

		self.assertEqual("test success!", result)


if __name__ == "__main__":
	unittest.main()

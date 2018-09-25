import unittest

from adventure.command import Command

class TestCommand(unittest.TestCase):

	def setUp(self):
		self.command = Command(1, 0x9, self.command_function, "")


	def command_function(self, player, arg):
		return "{0} success!", arg


	def test_has_attribute_set(self):
		self.assertTrue(self.command.has_attribute(0x8))


	def test_has_attribute_not_set(self):
		self.assertFalse(self.command.has_attribute(0x4))


	def test_execute(self):
		result = self.command.execute(None, "test")

		self.assertEqual("test success!", result)


if __name__ == "__main__":
	unittest.main()

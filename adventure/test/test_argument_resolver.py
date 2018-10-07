import unittest

from adventure.argument_resolver import ArgumentResolver
from adventure.command import Command
from adventure.data_collection import DataCollection

class TestArgumentResolver(unittest.TestCase):

	def setUp(self):

		self.resolver = ArgumentResolver()
		self.data = DataCollection(
			commands=None,
			locations=None,
			items=None,
			hints=None,
			explanations=None,
			responses=None,
			puzzles=None,
		)
		self.resolver.init_data(self.data)


	def handler_function(self, player, arg):
		return "{0} success!", arg


	def test_resolve_movement(self):
		command = Command(1, 0x9, None, self.handler_function, "", [])

		response = self.resolver.resolve_movement(command, None, "test")

		self.assertEqual(("{0} success!", 1), response)


	def test_resolve_non_movement(self):
		command = Command(1, 0x9, None, self.handler_function, "", [])

		response = self.resolver.resolve_non_movement(command, None, "test")

		self.assertEqual(("{0} success!", "test"), response)


if __name__ == "__main__":
	unittest.main()

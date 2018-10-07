import unittest
from unittest.mock import Mock

from adventure.argument_resolver import ArgumentResolver
from adventure.command import Command
from adventure.data_collection import DataCollection

class TestArgumentResolver(unittest.TestCase):

	def setUp(self):

		self.resolver = ArgumentResolver()

		responses_mock = Mock()
		responses_mock.get.side_effect = self.responses_side_effect

		self.data = DataCollection(
			commands=None,
			locations=None,
			items=None,
			hints=None,
			explanations=None,
			responses=responses_mock,
			puzzles=None,
		)
		self.resolver.init_data(self.data)

		self.response_map = {
			"request_argless" : "Do not give an argument for this command.",
		}

	def responses_side_effect(self, *args):
		return self.response_map.get(args[0])


	def handler_function(self, player, arg):
		return "{0} success!", arg


	def test_resolve_movement(self):
		command = Command(1, 0x9, None, self.handler_function, "", [], False)

		response = self.resolver.resolve_movement(command, None, "test")

		self.assertEqual(("{0} success!", 1), response)


	def test_resolve_argless(self):
		command = Command(1, 0x9, None, self.handler_function, "", [], False)

		response = self.resolver.resolve_argless(command, None, "test")

		self.assertEqual(("Do not give an argument for this command.", "test"), response)


	def test_resolve_single_arg(self):
		command = Command(1, 0x9, None, self.handler_function, "", [], False)

		response = self.resolver.resolve_single_arg(command, None, "test")

		self.assertEqual(("{0} success!", "test"), response)


if __name__ == "__main__":
	unittest.main()

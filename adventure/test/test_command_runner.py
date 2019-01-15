import unittest

from adventure.command import Command
from adventure.command_runner import CommandRunner
from adventure.element import Labels
from adventure.item import Item

class TestCommandRunner(unittest.TestCase):

	def setUp(self):
		self.runner = CommandRunner()


	def arg_function_movement(self, command, player, *args):
		return True, [], [], [command.data_id]


	def arg_function_non_movement(self, command, player, *args):
		return True, [], [], args


	def arg_function_unsuccessful(self, command, player, *args):
		return False, ["reason template"], args, []


	def handler_function(self, command, player, *arg):
		return True, ["{0} success!"], list(arg), list(arg)


	def vision_function(self, command, player, *arg):
		return True, [], [], list(arg)


	def test_run_movement(self):
		resolver_functions = [self.arg_function_movement, self.vision_function, self.handler_function]
		command_movement = Command(1, 0x49, 0x0, resolver_functions, [""],  {}, {})

		result = self.runner.run(command_movement, None, ["test"])

		self.assertEqual("1 success!", result)


	def test_run_non_movement(self):
		resolver_functions = [self.arg_function_non_movement, self.vision_function, self.handler_function]
		command_non_movement = Command(1, 0x9, 0x0, resolver_functions, [""],  {}, {})

		result = self.runner.run(command_non_movement, None, ["test"])

		self.assertEqual("test success!", result)


	def test_run_item_args(self):
		resolver_functions = [self.arg_function_non_movement, self.vision_function, self.handler_function]
		command_non_movement = Command(1, 0x9, 0x0, resolver_functions, [""],  {}, {})
		book = Item(1105, 2, Labels("book", "a book", "a book of fairytales"), 2, "The Pied Piper")

		result = self.runner.run(command_non_movement, None, [book])

		self.assertEqual("book success!", result)


	def test_run_unsuccessful(self):
		resolver_functions = [self.arg_function_unsuccessful, self.vision_function, self.handler_function]
		command_unsuccessful = Command(1, 0x9, 0x0, resolver_functions, [""], {}, {})

		result = self.runner.run(command_unsuccessful, None, ["test"])

		self.assertEqual("reason template", result)


if __name__ == "__main__":
	unittest.main()

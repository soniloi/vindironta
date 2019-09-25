import unittest

from adventure.validation import Severity, ValidationMessage

class TestValidation(unittest.TestCase):

	def test_get_formatted_message(self):
		message = ValidationMessage(Severity.ERROR, "Invalid input: {0}.", ("abc",))

		self.assertEqual("ERROR Invalid input: abc.", message.get_formatted_message())


if __name__ == "__main__":
	unittest.main()

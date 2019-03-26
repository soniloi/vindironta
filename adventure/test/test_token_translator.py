import unittest

from adventure.token_translator import TokenTranslator

class TestTokenTranslator(unittest.TestCase):

	def setUp(self):
		pass


	def test_translate_substitution_tokens_single(self):
		self.assertEqual("{0}", TokenTranslator.translate_substitution_tokens("$0"))


	def test_translate_substitution_tokens_multiple_adjacent(self):
		self.assertEqual("{0}{1}", TokenTranslator.translate_substitution_tokens("$0$1"))


	def test_translate_substitution_tokens_multiple_non_adjacent(self):
		self.assertEqual(" {0} abc {1}   ", TokenTranslator.translate_substitution_tokens(" $0 abc $1   "))


if __name__ == "__main__":
	unittest.main()

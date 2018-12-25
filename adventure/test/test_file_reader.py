import io
import unittest

from adventure import file_reader

class TestFileReader(unittest.TestCase):

	def test_empty(self):
		input_stream = io.BytesIO(bytes([]))
		reader = file_reader.FileReader(input_stream)

		self.assertFalse(reader.content)


	def test_with_newlines(self):
		input_bytes = bytes([134, 118, 150, 206, 166, 166, 38, 80, 70, 134, 206, 150, 54, 4, 198, 150, 118, 118, 134, 182, 246, 118, 80])
		input_stream = io.BytesIO(input_bytes)
		reader = file_reader.FileReader(input_stream)

		self.assertEqual("aniseed\nbasil cinnamon\n", reader.content)


	def test_with_quotes(self):
		input_bytes = bytes([134, 118, 150, 206, 166, 166, 38, 4, 68, 70, 134, 206, 150, 54, 68, 4, 198, 150, 118, 118, 134, 182, 246, 118])
		input_stream = io.BytesIO(input_bytes)
		reader = file_reader.FileReader(input_stream)

		self.assertEqual("aniseed \"basil\" cinnamon", reader.content)


if __name__ == "__main__":
  unittest.main()

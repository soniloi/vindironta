import io
import unittest

from adventure import file_reader

class TestFileReader(unittest.TestCase):

	def test_read_line_empty(self):
		input_stream = io.BytesIO(bytes([]))
		reader = file_reader.FileReader(input_stream)

		line = reader.read_line()
		self.assertTrue(reader.eof())
		self.assertFalse(line)


	def test_read_line_not_empty(self):
		input_bytes = bytes([134, 118, 150, 206, 166, 166, 38, 80, 70, 134, 206, 150, 54, 4, 198, 150, 118, 118, 134, 182, 246, 118, 80])
		input_stream = io.BytesIO(input_bytes)
		reader = file_reader.FileReader(input_stream)

		line1 = reader.read_line()
		self.assertFalse(reader.eof())
		self.assertEqual("aniseed", line1)

		line2 = reader.read_line()
		self.assertTrue(reader.eof())
		self.assertEqual("basil cinnamon", line2)


if __name__ == "__main__":
  unittest.main()

import io
import unittest

from adventure import file_reader

class TestFileReader(unittest.TestCase):

	def setUp(self):
		input_bytes = bytes([134, 118, 150, 206, 166, 166, 38, 80, 70, 134, 206, 150, 54, 4, 198, 150, 118, 118, 134, 182, 246, 118, 80])
		input_stream = io.BytesIO(input_bytes)
		self.reader = file_reader.FileReader(input_stream)

	def test_read_line(self):
		line1 = self.reader.read_line()
		self.assertEqual("aniseed", line1)
		line2 = self.reader.read_line()
		self.assertEqual("basil cinnamon", line2)

if __name__ == "__main__":
  unittest.main()

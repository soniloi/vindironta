class FileReader:

	BITS_PER_BYTE = 8
	NEW_LINE = ord('\n')

	def __init__(self, input_file):
		self.input_bytes = input_file.read()
		self.index = 0


	def read_line(self):

		output_bytes = []
		output_byte = -1

		while not self.eof() and output_byte != FileReader.NEW_LINE:

			input_byte = self.input_bytes[self.index]
			output_byte = self.reverse_bits(input_byte)

			if output_byte != FileReader.NEW_LINE:
				output_bytes.append(output_byte)

			self.index += 1

		return "".join(map(chr, output_bytes))


	def eof(self):
		return self.index >= len(self.input_bytes)


	def reverse_bits(self, input_byte):
		output_byte = 0

		for i in range(FileReader.BITS_PER_BYTE):
			bit = (input_byte & (1 << i)) != 0
			output_byte += (bit << (FileReader.BITS_PER_BYTE-1-i))

		return output_byte

class FileReader:

	BITS_PER_BYTE = 8

	def __init__(self, input_file):
		self.content = self.flip_bytes(input_file)


	def get_content(self):
		return self.content


	def flip_bytes(self, input_file):

		flipped_bytes = []

		for input_line in input_file:
			input_bytes = list(input_line)
			for input_byte in input_bytes:
				flipped_byte = self.reverse_bits(input_byte)
				flipped_bytes.append(flipped_byte)

		return "".join(map(chr, flipped_bytes))


	def reverse_bits(self, input_byte):
		output_byte = 0

		for i in range(FileReader.BITS_PER_BYTE):
			bit = (input_byte & (1 << i)) != 0
			output_byte += (bit << (FileReader.BITS_PER_BYTE-1-i))

		return output_byte

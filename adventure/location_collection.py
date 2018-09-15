from adventure.location import Location
from adventure.file_reader import FileReader

class LocationCollection:

	def __init__(self, reader):
		self.locations = {}

		line = reader.read_line()
		while line != "---":
			self.create_location(line)
			line = reader.read_line()

		# TODO: cross-referencing


	def create_location(self, line):
		tokens = line.split("\t")

		location_id = int(tokens[0])
		location_attributes = int(tokens[11], 16)
		location_shortname = tokens[12]
		location_longname = tokens[13]
		location_description = tokens[14]

		self.locations[location_id] = Location(location_id, location_attributes, location_shortname, location_longname,
			location_description)

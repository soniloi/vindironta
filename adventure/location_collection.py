class LocationCollection:

	def __init__(self, locations):
		self.locations = locations


	def get(self, location_id):
		return self.locations.get(location_id)

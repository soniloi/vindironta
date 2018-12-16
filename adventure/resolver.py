class Resolver:

	def init_data(self, data):
		self.data = data


	def get_resolver_function(self, resolver_function_name):
		return getattr(self, resolver_function_name, None)


	def get_response(self, response_key):
		return self.data.get_response(response_key)

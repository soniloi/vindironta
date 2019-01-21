from adventure.item import Item

class CommandRunner():

	def __init__(self, data):
		self.data = data


	def run(self, command, player, args):
		template_keys = []
		content_args = []
		next_args = args

		for resolver_function in command.resolver_functions:
			success, resolved_template_keys, current_content_args, next_args = resolver_function(command, player, *next_args)

			if resolved_template_keys:
				template_keys += resolved_template_keys
				content_args += current_content_args

			if not success:
				break

		return self.format_response(template_keys, content_args)


	def format_response(self, template_keys, tokens):
		templates = [self.data.get_response(template_key) for template_key in template_keys]
		template = " ".join(templates)
		contents = []

		for token in tokens:
			token_content = token
			if isinstance(token, Item):
				token_content = token.shortname
			contents.append(token_content)

		return template.format(*contents)

from adventure.item import Item

class CommandRunner():

	def run(self, command, player, args):
		templates = []

		for resolver_function in command.resolver_functions:
			success, resolved_template, args = resolver_function(command, player, *args)

			if resolved_template:
				templates.append(resolved_template)

			if not success:
				return self.format_response(templates, args)

		return self.format_response(templates, args)


	def format_response(self, templates, tokens):
		template = " ".join(templates)
		contents = []

		for token in tokens:
			token_content = token
			if isinstance(token, Item):
				token_content = token.shortname
			contents.append(token_content)

		return template.format(*contents)

from adventure.item import Item

class CommandRunner():

	def run(self, command, player, args):
		templates = []
		content_args = []
		next_args = args

		for resolver_function in command.resolver_functions:
			success, resolved_template, current_content_args, next_args = resolver_function(command, player, *next_args)

			if resolved_template:
				templates.append(resolved_template)
				content_args += current_content_args

			if not success:
				break

		return self.format_response(templates, content_args)


	def format_response(self, templates, tokens):
		template = " ".join(templates)
		contents = []

		for token in tokens:
			token_content = token
			if isinstance(token, Item):
				token_content = token.shortname
			contents.append(token_content)

		return template.format(*contents)

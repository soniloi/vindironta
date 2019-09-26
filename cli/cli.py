import sys

from adventure import game

RESET_COLOUR = "\x1b[0m"
INPUT_COLOUR = "\x1b[0m"
OUTPUT_COLOUR = "\x1b[32m"
PROMPT = "> "
RESPONSE_FORMAT = OUTPUT_COLOUR + PROMPT + "{0}\n"


class Cli:

	def run(self, game, output=sys.stdout, input=sys.stdin):
		output.write(self.format_response(game.get_start_message()))

		while(game.is_running()):
			output.write(INPUT_COLOUR + PROMPT)
			output.flush()
			request = input.readline()
			response = game.process_input(request).rstrip()
			if response:
				output.write(self.format_response(response))

		output.write(RESET_COLOUR)


	def format_response(self, response):
		return RESPONSE_FORMAT.format(response)


if __name__ == '__main__':
	if len(sys.argv) != 2:
		print("Usage: {0} <filename>".format(sys.argv[0]))
		sys.exit(1)

	current_game = game.Game(sys.argv[1])

	cli = Cli()
	cli.run(current_game)

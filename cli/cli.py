import sys

from adventure import game

RESET_COLOUR = "\x1b[0m"
INPUT_COLOUR = "\x1b[0m"
OUTPUT_COLOUR = "\x1b[32m"
PROMPT = "> "
RESPONSE_FORMAT = OUTPUT_COLOUR + PROMPT + "{0}"

def format_response(response):
	return RESPONSE_FORMAT.format(response)


if __name__ == '__main__':
	if len(sys.argv) != 2:
		print("Usage: {0} <filename>".format(sys.argv[0]))
		sys.exit(1)

	current_game = game.Game(sys.argv[1])
	print(format_response(current_game.get_start_message()))

	while(current_game.on):
		request = input(INPUT_COLOUR + PROMPT)
		response = current_game.process_input(request).rstrip()
		if response:
			print(format_response(response))

	print(RESET_COLOUR)

from adventure import game

RESET_COLOUR = "\x1b[0m"
INPUT_COLOUR = "\x1b[0m"
OUTPUT_COLOUR = "\x1b[32m"
PROMPT = "> "

if __name__ == '__main__':
	current_game = game.Game("datafile/rucesse.dat")

	while(current_game.on):
		request = input(INPUT_COLOUR + PROMPT)
		response = current_game.process_input(request).rstrip()
		if response:
			response_str = OUTPUT_COLOUR + PROMPT + response
			print(response_str)

	print(RESET_COLOUR)

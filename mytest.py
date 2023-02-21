import GameFiles as game


run = True
while True:
    game.display()
    source = input("Source: ")
    dest = input("Destination: ")
    game.move(source, dest)

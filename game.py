"""
Tried to keep true to the PEP-8 good code practices.
The comments are pretty verbose, but I try to explain my reasoning fully in
them. All questions are welcome either through Facebook event page, on Facebook
direct message or at jastrzebskib (at) gmail (dot) com.

Things that could be modified if you want to play with the code a bit and want
to actually learn something by doing it:
* instead of dying by running into the wall, wrap the snake around
* make the game go faster if you get to a certain score
* make it so that the fruit cannot be spawned "in" snake
* add different kinds of fruit (more points, less points, are only temporary,
  make game go slower)
* make the game ask you if you want to play another round after dying
* save the scores to a .txt file in the same folder
* corollary to the previous one: at the end of the game display top10/top20/we
  scores
* corollary to both previous points: add the functionality to add your name to
  the high score that you have earned at the end of the game
"""

# Necessary imports; using from module import * imports all of the methods of 
# that module in such a way, that we don't have to call the functions in the 
# format module.method - just method. It is generally a bad practice (since you
# always end up importing a lot of unnecessary things); in PyGame usage of
# "from pygame.locals import *" is very widespread, since the module contains
# a vast amount of functionality.
import pygame
from pygame.locals import *
from sys import exit
from random import randrange

# Colour constants (constants are by convention written in ALL CAPS; 
# technically they can be changed, it just signifies that they shouldn't). They
# could also be easily stored in the Game class.
BLACK = (0, 0, 0,)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
SUBTITLE_YELLOW = (250, 250, 60)

class Game(object):

    """
    To be honest, the whole game could have been done without using a class.
    We're practicing pretty bad form using only one class here, due to the
    Single Responsibility Principle - basically, a single class should be
    responsible for one thing.

    This one isn't - it has the event loop and keeps the state of the game
    (which would be enough for one class, really), but it also does spawn and
    move the snake, as well as spawns the fruit (both should be done by
    separate classes).

    For extra credit: separate the whole thing into three classes :)
    """

    # I'm personally not a fan of a __init__ not taking any arguments, but in
    # this situation it kinda makes sense, so let's run with this.
    def __init__(self):
        # Gotta do some PyGame things before we get to the logic.
        pygame.init()
        flag = DOUBLEBUF
        self.surface = pygame.display.set_mode((800, 600), flag)
        pygame.display.set_caption("Yet Another Snake!")
        # Fonts, along with setting PyGame up for rendering the text; Courier,
        # because monospace fonts make it easier to place them on the screen.
        pygame.font.init()
        self.font = pygame.font.SysFont("Courier", 16, False, False)
        self.largefont = pygame.font.SysFont("Courier", 48, True, False)
        # Set initial game state.
        self.score = 0
        self.grid_width = 20
        self.grid_height = 20
        self.snake = [(400, 300), (400, 320), (400, 340)]
        self.direction = "up"
        self.gamestate = 1
        # Create first fruit and start the event loop, which is basically the
        # actual game.
        self.spawn_fruit()
        self.loop()

    # Function will be called in each "frame" of the event loop; we ask PyGame
    # to draw each segment of our snake.
    def draw_snake(self):
        for pos in self.snake:
            pygame.draw.rect(self.surface, GREEN,
                            (pos[0], pos[1],
                            self.grid_width, self.grid_height), 1)

    # Function will be called in each "frame"; moves snake's head in the 
    # current direction and (if we haven't eaten a fruit) removes the last 
    # segment of the snake.
    def move_snake(self):
        if self.direction == "left":
            former_head = self.snake[0]
            new_head = (former_head[0]-20, former_head[1])
            self.snake.insert(0, new_head)
        if self.direction == "right":
            former_head = self.snake[0]
            new_head = (former_head[0]+20, former_head[1])
            self.snake.insert(0, new_head)
        if self.direction == "up":
            former_head = self.snake[0]
            new_head = (former_head[0], former_head[1]-20)
            self.snake.insert(0, new_head)
        if self.direction == "down":
            former_head = self.snake[0]
            new_head = (former_head[0], former_head[1]+20)
            self.snake.insert(0, new_head)
        # I think this is pretty neat; we call for function that returns True
        # iff we have just eaten a fruit. Could use del self.snake[:-1] here,
        # but pop is nicer.
        if not self.eat_fruit():
            self.snake.pop()

    # Is (indirectly) called in each "frame"; checks if we are out of bounds.
    # Since x and y coordinates actually describe the top, left-hand corner of
    # the item we want to draw, 800 would be out of the screen to the right and
    # 600 - out of the screen to the bottom.
    def check_borders_hit(self):
        if self.snake[0][0] < 0:
            self.gamestate = 20
        if self.snake[0][0] > 780:
            self.gamestate = 0
        if self.snake[0][1] < 0:
            self.gamestate = 0
        if self.snake[0][1] > 580:
            self.gamestate = 0

    # Is (indirectly) called in each "frame". This one is pretty neat, since in
    # the beginning, it looked like this:
    #
    # def check_snake_hit(self):
    #     headless_snake = self.snake
    #     del headless_snake[0]
    #     for pos in headless_snake:
    #         if self.snake[0] == pos:
    #             self.gamestate = 0
    #
    # it didn't work, because headless_snake actually stored reference to
    # self.snake instead of it's values, so when I called del headless_snake[0]
    # it also removed the first element of self.snake.
    # Due to this, we had to fill the headless_snake with the values using the
    # for loop and then remove the first item (head) from it.
    # Main functionality is trivial: check if any part of the snake has the 
    # same position as the head; if it does, it means you're dead.
    def check_snake_hit(self):
        headless_snake = []
        for pos in self.snake:
            headless_snake.append(pos)
        del headless_snake[0]
        for pos in headless_snake:
            if self.snake[0] == pos:
                self.gamestate = 0

    # Is directly called in each "frame".
    # Yes, I made a function just to call two other functions. Why?
    # I am a huge proponent of keeping the event loop tidy, so I'd rather keep
    # all the things that check if we have already died in one place 
    # (especially since we might add more death conditions in the future).
    # The more readable the event loop is, the less issues you will encounter
    # when adding more functionality to the game.
    def check_dead(self):
        self.check_borders_hit()
        self.check_snake_hit()

    # Is called during the __init__() and each time a fruit is eaten. Positions
    # the fruit randomly on the screen (800 would be out of the screen to the
    # right, 600 to the bottom since x and y coordinates are actually of the
    # top, left-hand corner of the item we want to draw).
    def spawn_fruit(self):
        pos_x = randrange(0, 780, 20)
        pos_y = randrange(0, 580, 20)
        self.fruit = (pos_x, pos_y)

    # Is called in each "frame".
    def draw_fruit(self):
        pygame.draw.rect(self.surface, RED,
                        (self.fruit[0], self.fruit[1],
                        self.grid_width, self.grid_height))

    # Is called in each frame by self.move_snake(). Checks if head is in the
    # same position as the fruit. If yes, increments the score by 10 and 
    # returns True, so that self.move_snake() knows not to remove the last item
    # of the self.snake.
    def eat_fruit(self):
        if self.snake[0] == self.fruit:
            self.score += 10
            self.spawn_fruit()
            return True

    # Is called in each "frame".
    def draw_score(self):
        score_string = "Score: " + str(self.score)
        score_text = self.font.render(score_string, True, SUBTITLE_YELLOW)
        self.surface.blit(score_text, (5, 5))
        
    # Currently there is no way to win, so...
    def game_over(self):
        # "Clear" the screen.
        self.surface.fill(BLACK)
        lose_text = self.largefont.render("u ded, h4h4", True, RED)
        # Tell the rendered text where it will go on the screen.
        self.surface.blit(lose_text, (240, 200))
        # Make all the changes above actually display on the screen.
        pygame.display.update()
        pygame.time.wait(2000)

    # Is called in each "frame". We check if player exit the game and if any 
    # keys were pressed.
    def get_player_input(self):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and \
                                    event.key == K_ESCAPE):
                self.gamestate = 0
                # Pressing an arrow key changes the direction we're going in...
                # unless you wanted to revert in place - it doesn't allow that.
            if event.type == KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not self.direction == "right":
                        self.direction = "left"
                if event.key == pygame.K_RIGHT:
                    if not self.direction == "left":
                        self.direction = "right"
                if event.key == pygame.K_UP:
                    if not self.direction == "down":
                        self.direction = "up"
                if event.key == pygame.K_DOWN:
                    if not self.direction == "up":
                        self.direction = "down"

    # The main event loop - where the magic happens, indents get messed up and
    # you cuss a lot if you mess something up and it was not kept tidy.
    def loop(self):
        while self.gamestate==1:
            # Check if player closes the game or pressed arrow keys.
            self.get_player_input()
            # Fill the screen with black colour (if not for this function, it
            # would seem as if the snake got longer by 1 square in each "frame"
            # because the "tail" part was already drawn and flipped to the
            # screen.
            self.surface.fill(BLACK)
            self.move_snake()
            # We move first, draw later; if the order is reversed, snake gets
            # drawn first and then moves, which makes it a bit harder to e.g.
            # turn next to the walls.
            self.draw_score()
            self.draw_fruit()
            self.draw_snake()
            self.check_dead()
            # Move all the things that we have drawn to the screen.
            pygame.display.update()
            # Can be made slower/faster by increasing/decreasing the wait. I'm
            # old, so I went with a pretty slow game, 40 gives 20-25 FPS.
            pygame.time.wait(100)

        # After the player's inevitable demise.
        self.game_over()

# Let's go!
if __name__ == '__main__':
   Game()

# We're IDLE friendly.
pygame.quit()

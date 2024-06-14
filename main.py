
import pygame
from rendering_engine import RenderingEngine
from lighting_mc import *
from controller import Controller
import minigames

CAST_BTN_KEY = pygame.K_k
LEFT_BTN_KEY = pygame.K_a
RIGHT_BTN_KEY = pygame.K_f

FISH_CLOCK_FULL = 20

class Game:

    def __init__(self) -> None:
        pygame.mixer.pre_init(44100)
        pygame.init()
        pygame.display.init()

        self.lighting = LightingMC()

        self.screen: pygame.Surface = pygame.display.set_mode((640, 360), pygame.FULLSCREEN | pygame.SCALED | pygame.NOFRAME, 0, 0, 0)
        pygame.display.set_caption("Placeholder Title", "Placeholder Title")
        pygame.mouse.set_visible(False)
        self.rendering_engine = RenderingEngine(self.screen)
        self.controller = Controller(0)

        self.clock = pygame.Clock()
        self.delta = 0

        self.running: bool = False

        self.high_scores: list[float] = []
        self.score = 0
        self.fish_clock = FISH_CLOCK_FULL
        self.game_clock = 180
        self.scene = 2
        self.game_end_reason = ""

        self.current_frame = None

    def main_loop(self) -> None:
        self.running = True
        #pygame.mixer.music.load("assets/bgm_game.wav")
        #pygame.mixer.music.play(loops=1000000)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    raise KeyboardInterrupt
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    raise KeyboardInterrupt

            self.rendering_engine.update(self.scene, self.score, self.fish_clock, self.game_clock, self.game_end_reason, self.high_scores, self.current_frame)
            self.lighting.update()

            match self.scene:
                case 0:
                    self.update_game()
                case 1:
                    self.update_end_screen()
                case 2:
                    self.update_menu()
                
            self.delta = self.clock.tick(60)/1000

    def update_game(self):
        # update timers (mario seconds :D)
        self.fish_clock -= self.delta*1.666666
        self.game_clock -= self.delta*1.666666

        if self.fish_clock < 0.005: # 0.005 is the last value which would round to 0.01 and thus show to the player
            self.game_end_reason = "Fish clock ran out!"
            self.scene = 1
            self.current_frame = None
        if self.game_clock < 0.005: # 0.005 is the last value which would round to 0.01 and thus show to the player
            self.game_end_reason = "You ran out of time!"
            self.scene = 1
            self.current_frame = None

        if (self.controller.get_button(self.controller.a) or pygame.key.get_just_pressed()[CAST_BTN_KEY]) and not self.current_frame and self.rendering_engine.scene_transfer_stage == 0:
            self.current_frame = minigames.DemoMinigame(self, self.rendering_engine, self.lighting)
        
        if self.current_frame:
            result = self.current_frame.update(self.controller, pygame.key.get_pressed(), self.delta)
            if isinstance(result, float):
                if result:
                    self.fish_clock = FISH_CLOCK_FULL
                    self.score += result
                self.current_frame = None
        
        self.score = round(self.score, 2)

    def update_end_screen(self):
        if self.controller.get_button(self.controller.b) or pygame.key.get_just_pressed()[CAST_BTN_KEY]:
            self.scene = 2

    def update_menu(self):
        if self.controller.get_button(self.controller.a) or pygame.key.get_just_pressed()[CAST_BTN_KEY]:
            self.scene = 0
            self.game_clock = 180
            self.fish_clock = FISH_CLOCK_FULL
        
if __name__ == "__main__":
    while True:
        try:
            game = Game()
            game.lighting.set_mode(FAST_FLASH)
            #game.lighting.bulk_add_sequenced_callbacks([None, None, None, None, None, ALL_OFF])
            game.main_loop()
        except KeyboardInterrupt:
            print(f"[main] caught keyboardinterrupt, closing...")
            break
        except Exception as e:
            print(f"[main] caught exception {e}, restarting game silently...")
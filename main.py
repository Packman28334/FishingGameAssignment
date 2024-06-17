
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
        pygame.display.set_caption("Untitled Fishing Game", "Untitled Fishing Game")
        pygame.mouse.set_visible(False)
        self.rendering_engine = RenderingEngine(self.screen, self.lighting)
        self.controller = Controller(0)

        self.clock = pygame.Clock()
        self.delta = 0

        self.running: bool = False

        self.high_scores: list[tuple[str, float, str]] = [] # name, weight, difficulty
        self.score = 0
        self.fish_clock = FISH_CLOCK_FULL
        self.game_clock = 180
        self.scene = 2
        self.game_end_reason = ""

        self.current_frame = None
        self.difficulty = 0

        with open("names.txt", "r") as f:
            self.names_list = f.readlines()
        self.names_list = [name.rstrip("\n") for name in self.names_list]
        self.chosen_name_idx = 0
        try:
            with open("high_scores.txt", "r") as f:
                for line in f.readlines():
                    split_line = line.split(" | ")
                    self.high_scores.append((split_line[0], float(split_line[1]), split_line[2]))
        except FileNotFoundError:
            pass

    def main_loop(self) -> None:
        self.running = True
        #pygame.mixer.music.load("assets/bgm_game.wav")
        #pygame.mixer.music.play(loops=1000000)
        while self.running:
            self.controller.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    raise KeyboardInterrupt
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    raise KeyboardInterrupt

            self.rendering_engine.update(self.scene, self.score, self.fish_clock, self.game_clock, self.game_end_reason, self.high_scores, self.current_frame, self.difficulty, self.controller.nintendo_mode, self.names_list, self.chosen_name_idx) # i'm sorry
            self.lighting.update()

            match self.rendering_engine._last_scene if self.rendering_engine.scene_transfer_stage == 1 else self.scene:
                case 0:
                    self.update_game()
                case 1:
                    self.update_end_screen()
                case 2:
                    self.update_menu()
                case 3:
                    self.update_tutorial_screen()
                case 4:
                    self.update_difficulty_selector()
                case 5:
                    self.update_minigame_tutorial()
                case 6:
                    self.update_name_selector()

            self.delta = self.clock.tick(60)/1000

    def attempt_to_change_scene(self, scene: int):
        if self.rendering_engine.scene_transfer_stage == 0:
            self.scene = scene
            self.current_frame = None
    
    def update_high_scores(self):
        difficulty_name = "Unknown"
        match self.difficulty:
            case 0:
                difficulty_name = "Common"
            case 1:
                difficulty_name = "Uncommon"
            case 2:
                difficulty_name = "Rare"
        highest_score = 0
        highest_score_idx = -1
        for idx, score in enumerate(self.high_scores):
            if score[0] == self.names_list[self.chosen_name_idx]:
                if score[1] > highest_score:
                    highest_score = score[1]
                    highest_score_idx = idx
                else:
                    self.high_scores.remove(score)
        if self.score > highest_score:
            self.high_scores.append((self.names_list[self.chosen_name_idx], round(self.score, 1), difficulty_name))
            if highest_score_idx != -1:
                self.high_scores.pop(highest_score_idx)
        self.high_scores.sort(reverse=True, key=lambda val: val[1])
        out = ""
        for score in self.high_scores:
            out += f"{score[0]} | {score[1]} | {score[2]}\n"
        out = out.rstrip("\n")
        with open("high_scores.txt", "w") as f:
            f.write(out)

    def update_game(self):
        # update timers (mario seconds :D)
        self.fish_clock -= self.delta*1.666666
        self.game_clock -= self.delta*1.666666

        if self.fish_clock < 0.005: # 0.005 is the last value which would round to 0.01 and thus show to the player
            self.game_end_reason = "Fish clock ran out!"
            self.attempt_to_change_scene(6)
        if self.game_clock < 0.005: # 0.005 is the last value which would round to 0.01 and thus show to the player
            self.game_end_reason = "You ran out of time!"
            self.attempt_to_change_scene(6)

        if (self.controller.get_proceed_button(just_pressed=True) or pygame.key.get_just_pressed()[CAST_BTN_KEY]) and not self.current_frame and self.rendering_engine.scene_transfer_stage == 0:
            match self.difficulty:
                case -1:
                    self.current_frame = minigames.DemoMinigame(self, self.rendering_engine, self.lighting)
                case 0:
                    self.current_frame = minigames.CommonMinigame(self, self.rendering_engine, self.lighting)
                case 1:
                    self.current_frame = minigames.UncommonMinigame(self, self.rendering_engine, self.lighting)
                case 2:
                    self.current_frame = minigames.RareMinigame(self, self.rendering_engine, self.lighting)
            self.lighting.set_mode(FAST_FLASH)

        if self.current_frame:
            result = self.current_frame.update(self.controller, pygame.key.get_pressed(), self.delta)
            if isinstance(result, float):
                if result:
                    self.fish_clock = FISH_CLOCK_FULL
                    self.score += result
                self.current_frame = None
                self.lighting.set_mode(FAST_CYCLE)
        
        self.score = round(pygame.math.clamp(self.score, 0, 1000000000), 1)

    def update_end_screen(self):
        self.difficulty = 0
        self.chosen_name_idx = 0
        if self.controller.get_proceed_button(just_pressed=True) or pygame.key.get_just_pressed()[CAST_BTN_KEY]:
            self.attempt_to_change_scene(2)

    def update_menu(self):
        if self.controller.get_proceed_button(just_pressed=True) or pygame.key.get_just_pressed()[CAST_BTN_KEY]:
            self.attempt_to_change_scene(3)
        if self.controller.get_button(self.controller.select, just_pressed=True):
            self.controller.nintendo_mode = not self.controller.nintendo_mode

    def update_tutorial_screen(self):
        if self.controller.get_proceed_button(just_pressed=True) or pygame.key.get_just_pressed()[CAST_BTN_KEY]:
            self.attempt_to_change_scene(4)

    def update_difficulty_selector(self):
        #print(self.controller.get_direction(self.controller.left_stick)[1])
        if self.controller.get_dpad_as_btn(just_pressed=True)[0]:
            self.difficulty -= 1
        elif self.controller.get_dpad_as_btn(just_pressed=True)[1]:
            self.difficulty += 1
        self.difficulty = pygame.math.clamp(self.difficulty, 0, 2)
        if self.controller.get_proceed_button(just_pressed=True) or pygame.key.get_just_pressed()[CAST_BTN_KEY]:
            self.attempt_to_change_scene(5)

    def update_minigame_tutorial(self):
        if self.controller.get_proceed_button(just_pressed=True) or pygame.key.get_just_pressed()[CAST_BTN_KEY]:
            self.score = 0
            self.game_clock = 180
            self.fish_clock = FISH_CLOCK_FULL
            self.attempt_to_change_scene(0)

    def update_name_selector(self):
        if self.controller.get_proceed_button(just_pressed=True):
            self.update_high_scores()
            self.attempt_to_change_scene(1)
        if self.controller.get_dpad_as_btn(just_pressed=True)[2]:
            self.chosen_name_idx -= 1
        if self.controller.get_dpad_as_btn(just_pressed=True)[3]:
            self.chosen_name_idx += 1
        self.chosen_name_idx = pygame.math.clamp(self.chosen_name_idx, 0, len(self.names_list)-1)

if __name__ == "__main__":
    while True:
        try:
            game = Game()
            game.lighting.set_mode(MENU_MUSIC_FLASH)
            #game.lighting.bulk_add_sequenced_callbacks([None, None, None, None, None, ALL_OFF])
            game.main_loop()
        except KeyboardInterrupt:
            print(f"[main] caught keyboardinterrupt, closing...")
            break
        except Exception as e:
            print(f"[main] caught exception {e}, restarting game silently...")
    game.lighting.set_mode(ALL_OFF)
    game.lighting.update()
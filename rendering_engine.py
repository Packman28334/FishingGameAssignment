
import pygame
from math import sin
from dataclasses import dataclass, field
import os
from random import choice, randint
import datetime
from minigames import BaseMinigame

BG_COLOR = pygame.Color("#2962ff")

@dataclass
class PersistentTexture:
    x: float
    y: float
    vx: float
    vy: float
    texture: pygame.Surface
    ttl: int = 120

@dataclass
class FancyText:
    x: float
    y: float
    text: str
    _curr_text: str = ""
    color: pygame.Color = field(default_factory=lambda: pygame.Color(255, 255, 255, 255))
    bg_color: pygame.Color | None = None
    sine_wave: float = 0
    _sine_incrementer: float = 0
    frames_per_character: int = 0
    _frame_incrementer: int = 0
    flashing_red_interval: int = -1
    _flashing_red: int = 0
    align: int = 0
    small_font: bool = False

class RenderingEngine:

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen: pygame.Surface = screen
        self.surface: pygame.Surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    
        self.persistent_textures: list[PersistentTexture] = []
        self.fancy_texts: list[FancyText] = []

        self.font = pygame.font.Font("assets/vt323.ttf", 48)
        self.small_font = pygame.font.Font("assets/vt323.ttf", 24)

        self.background = pygame.image.load("assets/background.png").convert()

        self.weight_texture = pygame.image.load("assets/weight.png").convert_alpha()
        self.clock_texture = pygame.image.load("assets/clock.png").convert_alpha()
        self.cloud_texture = pygame.image.load("assets/cloud.png").convert_alpha()

        self.fish_textures = [pygame.transform.scale(pygame.image.load("assets/fish/"+file).convert_alpha(), (64, 64)) for file in os.listdir("assets/fish") if file == file.removesuffix(".old")]
        self.default_fish_texture = choice(self.fish_textures)

        self.black_screen = pygame.Surface(self.screen.get_rect().size)
        pygame.draw.rect(self.black_screen, pygame.Color(0, 0, 0), self.screen.get_rect())
        self.black_screen.set_alpha(0)
        self.black_screen_alpha = 0

        self.subsurface_bg = pygame.Surface((520, 240))
        self.subsurface_bg.fill(pygame.Color(0, 0, 0))

        self.scene_transfer_stage = 0
        self._last_scene = 2
        self.prepare_main_menu(False)

    def draw_persistent_texture(self, texture: PersistentTexture):
        self.surface.blit(texture.texture, (texture.x, texture.y))
        texture.x += texture.vx
        texture.y += texture.vy
        texture.ttl -= 1
        if texture.ttl == 0:
            self.persistent_textures.remove(texture)

    def draw_fancy_text(self, text: FancyText):
        draw_text = text._curr_text if text.frames_per_character else text.text
        draw_color = pygame.Color(255, 0, 0) if text._flashing_red > text.flashing_red_interval and text.flashing_red_interval > 0 else text.color
        if text.small_font:
            drawn = self.small_font.render(draw_text, False, draw_color, text.bg_color)
        else:
            drawn = self.font.render(draw_text, True, draw_color, text.bg_color)
        drawn_rect = drawn.get_rect()
        match text.align:
            case 0:
                drawn_rect.x, drawn_rect.y = text.x, text.y
            case 1:
                drawn_rect.centerx, drawn_rect.y = text.x, text.y
            case 2:
                drawn_rect.topright = (text.x, text.y)
        self.surface.blit(drawn, (drawn_rect.x, drawn_rect.y))
        text._frame_incrementer += 1
        text._flashing_red += 1
        if text._flashing_red > text.flashing_red_interval*2:
            text._flashing_red = 0
        text._sine_incrementer += text.sine_wave
        if text.sine_wave:
            text.y += sin(text._sine_incrementer)/2
        if text._curr_text != text.text and text.frames_per_character != 0:
            if text._frame_incrementer % text.frames_per_character == 0:
                text._curr_text += text.text[len(text._curr_text)]

    def update(self, scene: int, score: float, fish_clock: float, main_clock: float, end_reason: str, high_scores: list, frame: BaseMinigame | None, difficulty: int, nintendo_mode: bool, names_list: list[str], chosen_name_idx: int) -> None:
        #self.screen.fill(pygame.Color(0, 0, 0, 255))
        self.screen.blit(self.background, (0, 0))

        match self.scene_transfer_stage:
            case 0:
                pass
            case 1:
                self.black_screen_alpha += 5
                self.black_screen.set_alpha(self.black_screen_alpha)
                if self.black_screen_alpha == 255:
                    self.scene_transfer_stage = 2
                    self.persistent_textures = []
                    self.fancy_texts = []
                    self._last_scene = scene
                    match scene:
                        case 0:
                            self.prepare_game()
                        case 1:
                            self.prepare_end_menu()
                        case 2:
                            self.prepare_main_menu(nintendo_mode)
                        case 3:
                            self.prepare_tutorial_screen()
                        case 4:
                            self.prepare_difficulty_selector()
                        case 5:
                            self.prepare_minigame_tutorial(difficulty)
                        case 6:
                            self.prepare_name_selector(names_list)
            case 2:
                self.black_screen_alpha -= 5
                self.black_screen.set_alpha(self.black_screen_alpha)
                if self.black_screen_alpha == 0:
                    self.scene_transfer_stage = 0

        self.surface.fill(pygame.Color(0, 0, 0, 0))

        if scene != self._last_scene and self.scene_transfer_stage == 0:
            self.scene_transfer_stage = 1

        active_scene = self._last_scene if self.scene_transfer_stage == 1 else scene

        match active_scene:
            case 0:
                self.render_game(score, fish_clock, main_clock)
            case 1:
                self.render_end_menu(score, end_reason, high_scores)
            case 2:
                self.render_main_menu(nintendo_mode, high_scores)
            case 3:
                self.render_tutorial_screen()
            case 4:
                self.render_difficulty_selector(difficulty)
            case 5:
                self.render_minigame_tutorial(difficulty)
            case 6:
                self.render_name_selector(names_list, chosen_name_idx)
            case _:
                self.draw_fancy_text(FancyText(320, 150, "SCENE NOT FOUND ERROR", align=1))

        for persistent_texture in self.persistent_textures:
            self.draw_persistent_texture(persistent_texture)
        for fancy_text in self.fancy_texts:
            self.draw_fancy_text(fancy_text)

        self.screen.blit(self.surface, (0, 0))

        if frame:
            match active_scene:
                case 1:
                    y_offset = 30
                case 2:
                    y_offset = 20
                case _:
                    y_offset = 0
            self.screen.blit(self.subsurface_bg, (60, 60+y_offset))
            self.screen.blit(frame.render(pygame.Surface((510, 230))), (65, 65+y_offset))

        if self.black_screen_alpha != 0:
            self.screen.blit(self.black_screen, (0, 0))
        pygame.display.flip()

    def prepare_game(self):
        self.fancy_texts.append(FancyText(80, 10, "FISH CLOCK: 15.00"))
        self.fancy_texts.append(FancyText(570, 300, "3:00", align=2))
        self.fancy_texts.append(FancyText(80, 300, "0 lbs"))
        for i in range(randint(1, 5)):
            self.persistent_textures.append(PersistentTexture(randint(0, 640), randint(0, 150), randint(-2, 2)/10, 0, self.cloud_texture, 10000))
        #pygame.mixer.music.stop()
        #pygame.mixer.music.unload()
        #pygame.mixer.music.load("assets/bgm_game.wav")
        #pygame.mixer.music.play(1000000)
    
    def prepare_end_menu(self):
        self.fancy_texts.append(FancyText(320, 10, "Game Over", align=1))
        self.fancy_texts.append(FancyText(320, 55, "You Failed | Final Weight: 0 lbs", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 330, "Press A to return to main menu", align=1, small_font=True))
        for i in range(10):
            self.fancy_texts.append(FancyText(320, 100+(i*20), f"{i+1} | N/A | 0.0 lbs", align=1, small_font=True))

    def prepare_main_menu(self, nintendo_mode: bool):
        self.fancy_texts.append(FancyText(320, 20, "Fishing Game", align=1))
        for i in range(3):
            self.fancy_texts.append(FancyText(320, 120+(i*25), f"{i+1} | N/A | 0.0 lbs", align=1, small_font=True))
        layout = "Nintendo (BAYX)" if nintendo_mode else "Xbox (ABXY)"
        self.fancy_texts.append(FancyText(320, 240, "Current button layout: "+layout, align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 270, "Press BACK to change.", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 290, "Press A to play", align=1))
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load("assets/bgm_menu.wav")
        pygame.mixer.music.play(1000000)

    def prepare_tutorial_screen(self):
        self.fancy_texts.append(FancyText(320, 20, "How To Play", align=1))
        self.fancy_texts.append(FancyText(320, 80, "To begin, press A.", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 100, "Press A to play a minigame.", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 130, "By sucessfully playing minigames, you can catch fish.", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 160, "The top 3 people on the leaderboard for fish by weight", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 180, "at the end of the day can win a prize!", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 250, "The game ends when either the Fish or Game clocks run out.", align=1, small_font=True, color=(255, 0, 0)))
        self.fancy_texts.append(FancyText(320, 280, "Press A to continue...", align=1))

        #pygame.mixer.music.stop()
        #pygame.mixer.music.unload()

    def prepare_difficulty_selector(self):
        self.fancy_texts.append(FancyText(320, 20, "Choose Difficulty", align=1))
        self.fancy_texts.append(FancyText(320, 80, "> Common <", align=1))
        self.fancy_texts.append(FancyText(320, 120, "Uncommon", align=1))
        self.fancy_texts.append(FancyText(320, 160, "Rare", align=1))
        
        self.fancy_texts.append(FancyText(320, 260, "Easy to play, but doesn't give many rewards.", align=1, small_font=True))

        self.fancy_texts.append(FancyText(320, 300, "Press A to continue...", align=1))

        #pygame.mixer.music.stop()
        #pygame.mixer.music.unload()

    def prepare_minigame_tutorial(self, difficulty: int):
        difficulties = ["Common", "Uncommon", "Rare"]
        self.fancy_texts.append(FancyText(320, 20, "How To Play: "+difficulties[difficulty], align=1))
        match difficulty:
            case 0:
                self.fancy_texts.append(FancyText(320, 70, "Using the A button, keep the bar over the fish.", align=1, small_font=True))
                self.fancy_texts.append(FancyText(320, 100, "Don't let the bar fill up with red!", align=1, small_font=True))
            case 1:
                self.fancy_texts.append(FancyText(320, 70, "Use the left joystick or D-Pad to keep the circle over the dot.", align=1, small_font=True))
                self.fancy_texts.append(FancyText(320, 100, "Don't let the bar fill up with red!", align=1, small_font=True))
            case 2:
                self.fancy_texts.append(FancyText(320, 70, "Use the left joystick or D-Pad to keep the circle over", align=1, small_font=True))
                self.fancy_texts.append(FancyText(320, 90, "the dot AT ALL TIMES.", align=1, small_font=True))
                self.fancy_texts.append(FancyText(320, 130, "While the circle is over the dot, press the next ", align=1, small_font=True))
                self.fancy_texts.append(FancyText(320, 150, "button in the sequence. Only push buttons while the circle", align=1, small_font=True))
                self.fancy_texts.append(FancyText(320, 170, "is over the dot, and make sure you press the right buttons!", align=1, small_font=True))
                self.fancy_texts.append(FancyText(320, 200, "Make any mistake, and move back in the sequence.", align=1, small_font=True, color=(255, 0, 0)))
                self.fancy_texts.append(FancyText(320, 220, "Make a mistake with none of the sequence completed,", align=1, small_font=True, color=(255, 0, 0)))
                self.fancy_texts.append(FancyText(320, 240, "and you lose fish.", align=1, small_font=True, color=(255, 0, 0)))

        self.fancy_texts.append(FancyText(320, 300, "Press A to play!", align=1))

        #pygame.mixer.music.stop()
        #pygame.mixer.music.unload()
    
    def prepare_name_selector(self, names_list: list[str]):
        self.fancy_texts.append(FancyText(320, 20, "Select Your Name", align=1))
        self.fancy_texts.append(FancyText(320, 150, names_list[0], align=1))
        self.fancy_texts.append(FancyText(320, 270, "Use D-Pad left/right", align=1))
        self.fancy_texts.append(FancyText(320, 310, "Press A to select", align=1))
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load("assets/bgm_end.wav")
        pygame.mixer.music.play(1000000)

    def render_game(self, score: float, fish_clock: float, main_clock: float):
        #self.screen.blit(self.background, (0, 0))

        self.surface.blit(self.default_fish_texture, (10, 7))
        #self.surface.blit(self.font.render(f"FISH CLOCK: {str(round(fish_clock, 2))}", False, (255, 255, 255)), (80, 15))
        self.fancy_texts[0].text = f"FISH CLOCK: {str(max(round(fish_clock, 2), 0))}"
        if fish_clock < 5:
            self.fancy_texts[0].flashing_red_interval = 20
        else:
            self.fancy_texts[0].flashing_red_interval = 0

        #self.surface.blit(self.font.render(main_clock_str, False, (255, 255, 255)), (100, 100))
        self.surface.blit(self.clock_texture, (555, 275))
        self.fancy_texts[1].text = str(datetime.timedelta(seconds=max(main_clock, 0))).lstrip("00:")[:-7]
        if main_clock < 5:
            self.fancy_texts[1].flashing_red_interval = 10
        elif main_clock < 15:
            self.fancy_texts[1].flashing_red_interval = 20
        elif main_clock < 30:
            self.fancy_texts[1].flashing_red_interval = 30
        elif main_clock < 45:
            self.fancy_texts[1].flashing_red_interval = 60

        self.surface.blit(self.weight_texture, (10, 295))
        self.fancy_texts[2].text = f"{str(score)} lbs"

    def render_end_menu(self, score: float, end_reason: str, high_scores: list):
        #self.screen.blit(self.background, (0, 0))
        self.fancy_texts[1].text = f"{end_reason} | Final Weight: {score} lbs"
        for i in range(3, 13):
            idx = i-3
            try:
                self.fancy_texts[i].text = f"{idx+1} | {high_scores[idx][0]} | {high_scores[idx][1]} lbs"
            except IndexError:
                pass

    def render_main_menu(self, nintendo_mode: bool, high_scores: list):
        for i in range(1, 4):
            idx = i-1
            try:
                self.fancy_texts[i].text = f"{idx+1} | {high_scores[idx][0]} | {high_scores[idx][1]} lbs"
            except IndexError:
                pass
        self.fancy_texts[4].text = f"Current button layout: {"Nintendo (BAYX)" if nintendo_mode else "Xbox (ABXY)"}"

    def render_tutorial_screen(self):
        pass

    def render_difficulty_selector(self, difficulty: int):
        for idx, text in enumerate(self.fancy_texts):
            text.text = text.text.lstrip("> ").rstrip(" <")
            if idx == difficulty+1:
                text.text = f"> {text.text} <"
        
        match difficulty:
            case 0:
                self.fancy_texts[4].text = "Easy to play, but doesn't give many rewards."
            case 1:
                self.fancy_texts[4].text = "Just like the common minigame, but in two dimensions."
            case 2:
                self.fancy_texts[4].text = "An unholy mix of Common and Uncommon. I'm sorry."

    def render_minigame_tutorial(self, difficulty: int):
        pass

    def render_name_selector(self, names_list: list[str], chosen_name_idx: int):
        self.fancy_texts[1].text = names_list[chosen_name_idx]
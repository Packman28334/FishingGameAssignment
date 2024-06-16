
import pygame
from math import sin
from dataclasses import dataclass, field
import os
from random import choice, randint
import datetime
from minigames import BaseMinigame

BG_COLOR = pygame.Color("#2962ff")

HIGH_SCORES_ENABLED = False

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
        self.prepare_main_menu()

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

    def update(self, scene: int, score: float, fish_clock: float, main_clock: float, end_reason: str, high_scores: list, frame: BaseMinigame | None) -> None:
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
                            self.prepare_main_menu()
                        case 3:
                            self.prepare_tutorial_screen()
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
                self.render_main_menu()
            case 3:
                self.render_tutorial_screen()
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
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load("assets/bgm_game.wav")
        pygame.mixer.music.play(1000000)
    
    def prepare_end_menu(self):
        self.fancy_texts.append(FancyText(320, 10, "Game Over", align=1))
        self.fancy_texts.append(FancyText(320, 55, "You Failed | Final Weight: 0 lbs", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 330, "Press B to return to main menu", align=1, small_font=True))
        if HIGH_SCORES_ENABLED:
            for i in range(10):
                self.fancy_texts.append(FancyText(320, 100+(i*20), f"{i+1} | N/A | 0.0 lbs", align=1, small_font=True))
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load("assets/bgm_end.wav")
        pygame.mixer.music.play(1000000)

    def prepare_main_menu(self):
        self.fancy_texts.append(FancyText(320, 20, "Fishing Game", align=1))
        self.fancy_texts.append(FancyText(320, 300, "Press A to play", align=1))
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load("assets/bgm_menu.wav")
        pygame.mixer.music.play(1000000)

    def prepare_tutorial_screen(self):
        self.fancy_texts.append(FancyText(320, 20, "How To Play", align=1))
        self.fancy_texts.append(FancyText(320, 80, "To begin, press A.", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 110, "Move your character left and right with the arrow buttons", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 130, "to catch fish.", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 160, "When the circle changes color, press A again", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 180, "to catch the fish.", align=1, small_font=True))
        self.fancy_texts.append(FancyText(320, 210, "Don't let the fish fall off the screen, and don't", align=1, small_font=True, color=(255, 0, 0)))
        self.fancy_texts.append(FancyText(320, 230, "press A without a fish in range!", align=1, small_font=True, color=(255, 0, 0)))
        self.fancy_texts.append(FancyText(320, 260, "The game ends when either the Fish or Game clocks run out.", align=1, small_font=True, color=(255, 0, 0)))
        self.fancy_texts.append(FancyText(320, 280, "Ready? Press A to begin!", align=1))
        self.fancy_texts.append(FancyText(320, 330, "PRE-ALPHA DEMO BUILD - not representative of final version", align=1, small_font=True))

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

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

    def render_main_menu(self):
        pass

    def render_tutorial_screen(self):
        pass
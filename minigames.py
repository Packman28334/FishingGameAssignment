
from controller import Controller
from pygame import Surface, K_a, K_f, K_k
from pygame.math import clamp
from pygame.draw import circle
from pygame import Rect
from random import randint, choice

CAST_KEY = K_k
LEFT_KEY = K_a
RIGHT_KEY = K_f

DEMO_SPEED = 150

class BaseMinigame:

    def __init__(self, game, rendering_engine, lighting_mc) -> None:
        self.game = game
        self.rendering_engine = rendering_engine
        self.lighting_mc = lighting_mc

    def update(self, controller: Controller, keys: list, delta_time: float) -> bool | None:
        return None

    def render(self, surface: Surface) -> Surface:
        return surface
    

class DemoMinigame(BaseMinigame):

    def __init__(self, game, rendering_engine, lighting_mc) -> None:
        self.player_x = 255
        self.fish = []
        self.game = game
        self.rendering_engine = rendering_engine
        self.lighting_mc = lighting_mc
        self.first_frame = True
        self.previous_inputs = [False, False, False]
        self.n_fish = randint(1, 4)

    def update(self, controller: Controller, keys: list, delta_time: float) -> float | None:
        if controller.get_dpad_as_btn()[2] or keys[LEFT_KEY]:
            self.player_x -= DEMO_SPEED * delta_time
        elif controller.get_dpad_as_btn()[3] or keys[RIGHT_KEY]:
            self.player_x += DEMO_SPEED * delta_time
        
        self.player_x = clamp(self.player_x, 0, 510)

        if len(self.fish) < self.n_fish:
            self.fish.append([randint(0, 510), 0, choice(self.rendering_engine.fish_textures), randint(10, 500)/10, False])

        player_collision_rect = Rect(self.player_x, 184, 32, 32)

        collision_detected = None
        for fish in self.fish:
            if fish[1] > 235:
                self.fish.remove(fish)
                return 0.0
            fish[1] += 50 * delta_time
            fish_rect = Rect(fish[0], fish[1], 64, 64)
            if player_collision_rect.colliderect(fish_rect):
                fish[4] = True
                collision_detected = self.fish.index(fish)
            else:
                fish[4] = False

        if (controller.get_button(controller.a) or keys[CAST_KEY]) and not self.first_frame and not self.previous_inputs[0]:
            if collision_detected != None:
                return self.fish[collision_detected][3]
            else:
                return 0.0

        self.first_frame = False
        self.previous_inputs = [controller.get_button(controller.a) or keys[CAST_KEY], controller.get_dpad_as_btn()[2] or keys[LEFT_KEY], controller.get_dpad_as_btn()[3] or keys[RIGHT_KEY]]

    def render(self, surface: Surface) -> Surface:
        #surface.fill("#2962ff")
        surface.fill("#0099ff")

        colliding_with_fish = False
        for fish in self.fish:
            if fish[4]:
                colliding_with_fish = True

        circle(surface, "#000066" if colliding_with_fish else "#0000cc", (self.player_x, 184), 16)

        for fish in self.fish:
            surface.blit(fish[2], (fish[0], fish[1]))

        return surface
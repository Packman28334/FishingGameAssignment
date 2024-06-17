
from controller import Controller
from pygame import Surface, K_a, K_f, K_k
from pygame.math import clamp
from pygame.draw import circle, rect
from pygame.transform import scale
from pygame import Rect
from pygame.font import Font
from random import randint, choice
from typing import cast

CAST_KEY = K_k
LEFT_KEY = K_a
RIGHT_KEY = K_f

DEMO_SPEED = 150

class BaseMinigame:

    def __init__(self, game, rendering_engine, lighting_mc) -> None:
        self.game = game
        self.rendering_engine = rendering_engine
        self.lighting_mc = lighting_mc

    def update(self, controller: Controller, keys: list, delta_time: float) -> float | None:
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
            self.fish.append([randint(0, 510), 0, scale(choice(self.rendering_engine.fish_textures), (32, 32)), randint(10, 500)/10, False])

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
    

class CommonMinigame(BaseMinigame):
    
    def __init__(self, game, rendering_engine, lighting_mc) -> None:
        super().__init__(game, rendering_engine, lighting_mc)
        self.fish_y = 0
        self.bar_y = 0
        self.counter_clock = 5
        self.last_fish_move_direction = 0
        self.fish_img = scale(choice(rendering_engine.fish_textures), (32, 32))
        self.fish_colliding = False

    def update(self, controller: Controller, keys: list, delta_time: float) -> float | None:
        if controller.get_button(controller.a):
            self.bar_y -= 160 * delta_time
        else:
            self.bar_y += 130 * delta_time
        self.bar_y = clamp(self.bar_y, 6, 144)

        match self.last_fish_move_direction:
            case 0:
                increase_odds = 50
            case 1:
                increase_odds = 1
            case -1:
                increase_odds = 99
            case _: # just in case
                increase_odds = 50
        if randint(0, 100) > increase_odds:
            self.fish_y -= 125 * delta_time
            self.last_fish_move_direction = 1
        else:
            self.fish_y += 125 * delta_time
            self.last_fish_move_direction = -1
        old_fish_y = self.fish_y
        self.fish_y = clamp(self.fish_y, 10, 188)
        if old_fish_y != self.fish_y:
            self.last_fish_move_direction = 0

        if self.fish_y+32 > self.bar_y and self.fish_y < self.bar_y+80:
            self.counter_clock += delta_time*2
            self.fish_colliding = True
        else:
            self.counter_clock -= delta_time*4
            self.fish_colliding = False

        if self.counter_clock > 10:
            return randint(100, 250)/10
        elif self.counter_clock < 0:
            return 0.0
        else:
            return None

    def render(self, surface: Surface) -> Surface:
        surface.fill("#0099ff")
        rect(surface, (255, 255, 0), (239, 5, 42, 220))
        rect(surface, (0, 127, 0) if self.fish_colliding else (0, 255, 0), (240, self.bar_y, 40, 80))
        surface.blit(self.fish_img, (244, self.fish_y))
        rect(surface, (0, 255, 0), (0, 0, 16, (self.counter_clock/10)*230))
        rect(surface, (255, 0, 0), (0, (self.counter_clock/10)*230, 16, 231-(self.counter_clock/10)*230))
        return surface


class UncommonMinigame(BaseMinigame):

    def __init__(self, game, rendering_engine, lighting_mc) -> None:
        super().__init__(game, rendering_engine, lighting_mc)

        self.fish_x = 250
        self.fish_y = 120

        self.last_fish_move_direction_x = 0
        self.last_fish_move_direction_y = 0

        self.circle_x = 250
        self.circle_y = 120

        self.counter_clock = 4

        self.circle_rect = Rect(0, 0, 0, 0)
        self.fish_rect = Rect(1, 1, 1, 1) # don't want these two to be colliding so for frame 1 the color is default
    
    def update(self, controller: Controller, keys: list, delta_time: float) -> float | None:
        x_move = controller.get_direction(controller.left_stick)[0]
        y_move = controller.get_direction(controller.left_stick)[1]
        self.circle_x += x_move * 200 * delta_time
        self.circle_y += y_move * 200 * delta_time

        match self.last_fish_move_direction_x:
            case 0:
                right_odds = 50
            case 1:
                right_odds = 5
            case -1:
                right_odds = 95
            case _: # just in case
                right_odds = 50
        if randint(0, 100) > right_odds:
            self.fish_x += 70 * delta_time
            self.last_fish_move_direction_x = 1
        else:
            self.fish_x -= 70 * delta_time
            self.last_fish_move_direction_x = -1

        match self.last_fish_move_direction_y:
            case 0:
                increase_odds = 50
            case 1:
                increase_odds = 5
            case -1:
                increase_odds = 95
            case _: # just in case
                increase_odds = 50
        if randint(0, 100) > increase_odds:
            self.fish_y -= 70 * delta_time
            self.last_fish_move_direction_y = 1
        else:
            self.fish_y += 70 * delta_time
            self.last_fish_move_direction_y = -1

        prev_x = self.circle_x
        prev_y = self.circle_y

        self.circle_x = clamp(self.circle_x, 16, 510)
        self.circle_y = clamp(self.circle_y, 0, 230)

        if prev_x != self.circle_x:
            self.last_fish_move_direction_x = 0
        if prev_y != self.circle_y:
            self.last_fish_move_direction_y = 0

        self.fish_x = clamp(self.fish_x, 16, 510)
        self.fish_y = clamp(self.fish_y, 0, 230)

        self.fish_colliding = self.circle_rect.colliderect(self.fish_rect)

        if self.fish_colliding:
            self.counter_clock += delta_time*2
            self.fish_colliding = True
        else:
            self.counter_clock -= delta_time*4
            self.fish_colliding = False

        if self.counter_clock > 8:
            return randint(251, 400)/10
        elif self.counter_clock < 0:
            return 0.0
        else:
            return None
    
    def render(self, surface: Surface) -> Surface:
        surface.fill("#0099ff")
        self.circle_rect = circle(surface, "#0000ff" if self.fish_colliding else "#000055", (self.circle_x, self.circle_y), 32)
        self.fish_rect = circle(surface, "#000011", (self.fish_x, self.fish_y), 6)
        rect(surface, (0, 255, 0), (0, 0, 16, (self.counter_clock/8)*230))
        rect(surface, (255, 0, 0), (0, (self.counter_clock/8)*230, 16, 231-(self.counter_clock/10)*230))
        return surface


class RareMinigame(BaseMinigame):

    def __init__(self, game, rendering_engine, lighting_mc) -> None:
        super().__init__(game, rendering_engine, lighting_mc)

        self.fish_x = 250
        self.fish_y = 120

        self.last_fish_move_direction_x = 0
        self.last_fish_move_direction_y = 0

        self.circle_x = 250
        self.circle_y = 120

        self.circle_rect = Rect(0, 0, 0, 0)
        self.fish_rect = Rect(1, 1, 1, 1) # don't want these two to be colliding so for frame 1 the color is default
    
        self.sequence = "".join([choice(["A", "B", "X", "Y"]) for _ in range(4)])
        self.counter = 0
        self.time_clock = 0

        self.font: Font = self.rendering_engine.font

        self.first_frame = True

    def update(self, controller: Controller, keys: list, delta_time: float) -> float | None:
        x_move = controller.get_direction(controller.left_stick)[0]
        y_move = controller.get_direction(controller.left_stick)[1]
        self.circle_x += x_move * 200 * delta_time
        self.circle_y += y_move * 200 * delta_time

        match self.last_fish_move_direction_x:
            case 0:
                right_odds = 50
            case 1:
                right_odds = 1
            case -1:
                right_odds = 99
            case _: # just in case
                right_odds = 50
        if randint(0, 100) > right_odds:
            self.fish_x += 50 * delta_time
            self.last_fish_move_direction_x = 1
        else:
            self.fish_x -= 50 * delta_time
            self.last_fish_move_direction_x = -1

        match self.last_fish_move_direction_y:
            case 0:
                increase_odds = 50
            case 1:
                increase_odds = 1
            case -1:
                increase_odds = 99
            case _: # just in case
                increase_odds = 50
        if randint(0, 100) > increase_odds:
            self.fish_y -= 50 * delta_time
            self.last_fish_move_direction_y = 1
        else:
            self.fish_y += 50 * delta_time
            self.last_fish_move_direction_y = -1

        prev_x = self.circle_x
        prev_y = self.circle_y

        self.circle_x = clamp(self.circle_x, 16, 510)
        self.circle_y = clamp(self.circle_y, 0, 230)

        if prev_x != self.circle_x:
            self.last_fish_move_direction_x = 0
        if prev_y != self.circle_y:
            self.last_fish_move_direction_y = 0

        self.fish_x = clamp(self.fish_x, 16, 510)
        self.fish_y = clamp(self.fish_y, 0, 230)

        self.fish_colliding = self.circle_rect.colliderect(self.fish_rect)

        # wait when did i write this gem lmfao
        # please help its 1 am i need sleep
        # but seriously though i genuinely have zero recollection of typing this
        # its all a blur
        if self.fish_colliding:
            self.fish_colliding = True
        else:
            self.fish_colliding = False

        if not self.fish_colliding:
            self.time_clock += delta_time
        
        if self.time_clock > 3:
            self.counter -= 1
            self.time_clock = 0

        try:
            next_btn = self.sequence[self.counter]
            match next_btn:
                case "A":
                    next_btn_id = controller.a
                case "B":
                    next_btn_id = controller.b
                case "X":
                    next_btn_id = controller.x
                case "Y":
                    next_btn_id = controller.y
            if controller.get_button(next_btn_id, just_pressed=True) and not self.first_frame:
                if self.fish_colliding:
                    self.counter += 1
                else:
                    self.counter -= 1
            incorrect_ids = [controller.a, controller.b, controller.x, controller.y]
            incorrect_ids.remove(next_btn_id)
            for incorrect_id in incorrect_ids:
                if controller.get_button(incorrect_id, just_pressed=True) and not self.first_frame:
                    self.counter -= 1
        except IndexError:
            pass

        self.first_frame = False

        if self.counter > 3:
            return randint(401, 700)/10
        elif self.counter < 0:
            return randint(-700, -401)/15
        else:
            return None
    
    def render(self, surface: Surface) -> Surface:
        surface.fill("#0099ff")
        self.circle_rect = circle(surface, "#0000ff" if self.fish_colliding else "#000055", (self.circle_x, self.circle_y), 32)
        self.fish_rect = circle(surface, "#000011", (self.fish_x, self.fish_y), 6)
        #rect(surface, (0, 255, 0), (0, 0, 16, (self.counter_clock/8)*230))
        #rect(surface, (255, 0, 0), (0, (self.counter_clock/8)*230, 16, 231-(self.counter_clock/10)*230))
        for idx, char in enumerate(self.sequence):
            surface.blit(self.font.render(char, False, (0, 255, 0) if self.counter>idx else (255, 0, 0)), (416+idx*24, 180))
        return surface
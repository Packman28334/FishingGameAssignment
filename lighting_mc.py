
# this glorious codebase is what you get when you just finished a C++ equivalent that runs directly
# on the Arduino, and you then rewrite the entire thing in python using the same mindset
# despite the fact that you're now driving every individial led remotely instead of just sending high-level
# instructions over serial

# i apologize for the timing system (it being independant from the cpu tick or any update loops
# or anything that'd keep it actually in sync with the other parts of the game)

import pyfirmata2, serial
from time import time
from typing import Callable

ALL_OFF = 0
ALL_ON = 1
RED_ONLY = 2
BLUE_ONLY = 3
YELLOW_ONLY = 4
FAST_CYCLE = 5
MEDIUM_CYCLE = 6
SLOW_CYCLE = 7
FAST_INVERSE_CYCLE = 8
MEDIUM_INVERSE_CYCLE = 9
SLOW_INVERSE_CYCLE = 10
FAST_FLASH = 11
MEDIUM_FLASH = 12
SLOW_FLASH = 13

def nop(*args, **kwargs):
    pass

class LightingMC:

    def __init__(self, tty: str = "/dev/ttyACM0") -> None:
        try:
            self.board = pyfirmata2.Arduino(tty)
            self.disable = False
        except serial.SerialException:
            print("[lighting_mc] arduino connection error, lights disabled")
            self.disable = True
        except AttributeError:
            print("[lighting_mc] arduino connection error, lights disabled")
            self.disable = True
    
        if not self.disable:
            self.red = self.board.get_pin("d:9:o")
            self.blue = self.board.get_pin("d:10:o")
            self.yellow = self.board.get_pin("d:11:o")
            self.set_leds(False, False, False)

        self.mode = 0
        self.state = 0
        self.sequenced_callbacks: list[Callable | int | None] = []

        print("[lighting_mc] initialized")

        self.last_state_change_time = time()

    def set_leds(self, red: bool, blue: bool, yellow: bool):
        if self.disable:
            return
        self.red.write(1 if red else 0)
        self.blue.write(1 if blue else 0)
        self.yellow.write(1 if yellow else 0)

    def set_mode(self, mode: int):
        if mode > -1 and mode < 14:
            self.mode = mode
            self.state = 0
            self.last_state_change_time = time()

    def add_sequenced_callback(self, callback: Callable | int | None, next: bool = False):
        if next:
            self.sequenced_callbacks.insert(0, callback)
        else:
            self.sequenced_callbacks.append(callback)
    
    def bulk_add_sequenced_callbacks(self, callbacks: list[Callable | int | None], next: bool = False):
        if next:
            callbacks.extend(self.sequenced_callbacks.copy())
            self.sequenced_callbacks = callbacks
        else:
            self.sequenced_callbacks.extend(callbacks)

    def clear_sequenced_callbacks(self):
        self.sequenced_callbacks = []

    def trigger_state_change(self, highest_state: int, inverse_direction: bool = False):
        self.state += -1 if inverse_direction else 1
        if self.state > highest_state:
            self.state = 0
        if self.state < 0:
            self.state = highest_state
        self.last_state_change_time = time()
        try:
            callback = self.sequenced_callbacks.pop(0)
            if isinstance(callback, int):
                self.mode = callback
            elif isinstance(callback, Callable):
                callback(self)
        except IndexError:
            pass

    def update(self):
        #self.board.iterate() # THIS LINE IS VERY IMPORTANT BUT IT BLOCKS THE ENTIRE F***ING PROJECT I NEED SLEEP HELP ME PLEASE

        match self.mode:
            case 0:
                self.set_leds(False, False, False)
                if time()-self.last_state_change_time > 0.1:
                    self.trigger_state_change(0)
            case 1:
                self.set_leds(True, True, True)
                if time()-self.last_state_change_time > 0.1:
                    self.trigger_state_change(0)
            case 2:
                self.set_leds(True, False, False)
                if time()-self.last_state_change_time > 0.1:
                    self.trigger_state_change(0)
            case 3:
                self.set_leds(False, True, False)
                if time()-self.last_state_change_time > 0.1:
                    self.trigger_state_change(0)
            case 4:
                self.set_leds(False, False, True)
                if time()-self.last_state_change_time > 0.1:
                    self.trigger_state_change(0)
            case 5:
                self._update_cycle()
            case 6:
                self._update_cycle()
            case 7:
                self._update_cycle()
            case 8:
                self._update_cycle(inverse=True)
            case 9:
                self._update_cycle(inverse=True)
            case 10:
                self._update_cycle(inverse=True)
            case 11:
                self._update_flash()
            case 12:
                self._update_flash()
            case 13:
                self._update_flash()

    def _update_cycle(self, inverse: bool = False):
        if time() - self.last_state_change_time > 0.250 * (self.mode-4):
            self.trigger_state_change(2, inverse)
        match self.state:
            case 0:
                self.set_leds(True, False, False)
            case 1:
                self.set_leds(False, True, False)
            case 2:
                self.set_leds(False, False, True)
    
    def _update_flash(self):
        if time() - self.last_state_change_time > 0.100 * (self.mode-10):
            self.trigger_state_change(1)
        match self.state:
            case 0:
                self.set_leds(False, False, False)
            case 1:
                self.set_leds(True, True, True)
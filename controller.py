
import pygame

L_X_AXIS = 0
L_Y_AXIS = 1
L_TRIGGER_AXIS = 2
R_X_AXIS = 3
R_Y_AXIS = 4
R_TRIGGER_AXIS = 5

A_BTN = 0
B_BTN = 1
X_BTN = 2
Y_BTN = 3
L_BTN = 4
R_BTN = 5
SELECT_BTN = 6
START_BTN = 7
HOME_BTN = 8
L_STICK_BTN = 9
R_STICK_BTN = 10

DPAD_HAT = 0

class Controller:

    def __init__(self, controller_id: int) -> None:
        pygame.joystick.init()

        try:
            self.controller = pygame.joystick.Joystick(controller_id)
            self.loaded = True
        except pygame.error:
            self.loaded = False

        self.left_stick = L_X_AXIS
        self.right_stick = R_X_AXIS
        
        self.a = 0
        self.b = 1
        self.x = 2
        self.y = 3
        self.lb = 4
        self.rb = 5
        self.ls = 6
        self.rs = 7
        self.select = 8
        self.start = 9
        self.home = 10
        
        self.lt = 0
        self.rt = 1
        
        self.current_buttons = [False, False, False, False, False, False, False, False, False, False, False]
        self.current_dpad = [0.0, 0.0]
        self.current_triggers = [0.0, 0.0]
        self.previous_buttons = self.current_buttons.copy()
        self.previous_dpad = self.current_dpad.copy()
        self.previous_triggers = self.current_triggers.copy()

        if self.loaded:
            print(f"[controller] located controller "+self.controller.get_name())
    
    def update(self) -> None:
        if self.loaded:
            self.previous_buttons = self.current_buttons.copy()
            self.previous_dpad = self.current_dpad.copy()
            self.previous_triggers = self.current_triggers.copy()
            self.current_buttons = [
                bool(self.controller.get_button(A_BTN)),
                bool(self.controller.get_button(B_BTN)),
                bool(self.controller.get_button(X_BTN)),
                bool(self.controller.get_button(Y_BTN)),
                bool(self.controller.get_button(L_BTN)),
                bool(self.controller.get_button(R_BTN)),
                bool(self.controller.get_button(L_STICK_BTN)),
                bool(self.controller.get_button(R_STICK_BTN)),
                bool(self.controller.get_button(SELECT_BTN)),
                bool(self.controller.get_button(START_BTN)),
                bool(self.controller.get_button(HOME_BTN)),
            ]
            self.current_dpad = list(self.controller.get_hat(DPAD_HAT))
            self.current_triggers = [(self.controller.get_axis(L_TRIGGER_AXIS)+1)/2, (self.controller.get_axis(R_TRIGGER_AXIS)+1)/2]

    def get_joystick(self, joystick: int) -> tuple[float, float]:
        if self.loaded:
            return round(self.controller.get_axis(joystick), 1), round(self.controller.get_axis(joystick+1), 1)
        else:
            return 0.0, 0.0

    def get_dpad(self) -> tuple[float, float]:
        if self.loaded:
            return self.current_dpad
        else:
            return 0, 0

    def get_dpad_as_btn(self, just_pressed: bool = False, just_released: bool = False) -> tuple[bool, bool, bool, bool]:
        if self.loaded:
            if just_pressed:
                out = (
                    self.current_dpad[1]>0 and not self.previous_dpad[0],
                    self.current_dpad[1]<0 and not self.previous_dpad[1],
                    self.current_dpad[0]<0 and not self.previous_dpad[2],
                    self.current_dpad[0]>0 and not self.previous_dpad[3]
                )
            elif just_released:
                out = (
                    not self.current_dpad[1]>0 and self.previous_dpad[0],
                    not self.current_dpad[1]<0 and self.previous_dpad[1],
                    not self.current_dpad[0]<0 and self.previous_dpad[2],
                    not self.current_dpad[0]>0 and self.previous_dpad[3]
                )
            else:
                out = (self.current_dpad[1]>0, self.current_dpad[1]<0, self.current_dpad[0]<0, self.current_dpad[0]>0)
            return out
        else:
            return False, False, False, False

    def get_button(self, button: int, just_pressed: bool = False, just_released: bool = False) -> bool:
        if self.loaded:
            if just_pressed:
                return self.current_buttons[button] and not self.previous_buttons[button]
            elif just_released:
                return not self.current_buttons[button] and self.previous_buttons[button]
            else:
                return self.current_buttons[button]
        else:
            return False
    
    def get_trigger(self, trigger: int) -> float:
        if self.loaded:
            return self.current_triggers[trigger]
        else:
            return 0
    
    def get_trigger_as_btn(self, trigger: int, just_pressed: bool = False, just_released: bool = False) -> bool:
        if self.loaded:
            if just_pressed:
                return self.current_triggers[trigger]>0.5 and not self.previous_triggers[trigger]>0.5
            elif just_released:
                return not self.current_triggers[trigger]>0.5 and self.previous_triggers[trigger]>0.5
            else:
                return self.current_triggers[trigger]>0.5
        else:
            return False
        
    def get_direction(self, joystick: int):
        joy_value = self.get_joystick(joystick)
        dpad_value = self.get_dpad()
        return (joy_value[0]+dpad_value[0], joy_value[1]+dpad_value[1]*-1)
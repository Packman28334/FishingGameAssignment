
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
        
        self.a = A_BTN
        self.b = B_BTN
        self.X = X_BTN
        self.y = Y_BTN
        self.lb = L_BTN
        self.rb = R_BTN
        self.ls = L_STICK_BTN
        self.rs = R_STICK_BTN
        self.select = SELECT_BTN
        self.start = START_BTN
        self.home = HOME_BTN
        
        self.lt = L_TRIGGER_AXIS
        self.rt = R_TRIGGER_AXIS
        
        if self.loaded:
            print(f"[controller] located controller "+self.controller.get_name())
    
    def get_joystick(self, joystick: int) -> tuple[float, float]:
        if self.loaded:
            return round(self.controller.get_axis(joystick), 2), round(self.controller.get_axis(joystick+1), 2)
        else:
            return 0.0, 0.0

    def get_dpad(self) -> tuple[float, float]:
        if self.loaded:    
            return self.controller.get_hat(DPAD_HAT)
        else:
            return 0, 0

    def get_dpad_as_btn(self) -> tuple[bool, bool, bool, bool]:
        data = self.get_dpad()
        return data[1]>0, data[1]<0, data[0]<0, data[0]>0

    def get_button(self, button: int) -> bool:
        if self.loaded:
            return bool(self.controller.get_button(button))
        else:
            return False
    
    def get_trigger(self, trigger: int) -> float:
        if self.loaded:
            return (self.controller.get_axis(trigger)+1)/2
        else:
            return 0
    
    def get_trigger_as_btn(self, trigger: int) -> bool:
        return self.get_trigger(trigger) > 0
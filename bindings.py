import pygame
from typing import Callable
import sys


class JoystickNotFoundError(Exception):
    pass

class BindingActionNotFoundError(Exception):
    pass


class Bindings:
    def __init__(self):
        self.binary_actions: dict[str, list[Callable[[], bool]]] = {}
        self.axis_actions: dict[str, list[Callable[[], float]]] = {}
        self.hat_actions: dict[str, list[Callable[[], tuple[float, float]]]] = {}

        self.previous_binary_actions: dict[str, bool] = {}

    def add_binary_action(self, action_name: str, bindings: list[Callable[[], bool]]):
        self.binary_actions[action_name] = bindings
        self.previous_binary_actions[action_name] = False
    
    def add_axis_action(self, action_name: str, bindings: list[Callable[[], float]]):
        self.axis_actions[action_name] = bindings
    
    def add_hat_action(self, action_name: str, bindings: list[Callable[[], tuple[float, float]]]):
        self.axis_actions[action_name] = bindings

    def get_binary_action(self, action_name: str, default=False) -> bool:
        try:
            result = any(b() for b in self.binary_actions[action_name])
        except KeyError:
            raise BindingActionNotFoundError(f'Invalid binary action "{action_name}"')
        except JoystickNotFoundError as e:
            result = default
        
        return result
    
    def get_pressed_binary_action(self, action_name: str, default=False) -> bool:
        """
        Returns True if the action was just pressed
        Requires `save_previous_binary_actions` to be called
        at the end of each frame.
        """
        prev = self.previous_binary_actions.get(action_name)
        current = self.get_binary_action(action_name, default)
        return not prev and current
    
    def get_axis_action(self, action_name: str, default=0.0) -> float:
        try:
            return any(b() for b in self.axis_actions[action_name])
        except KeyError:
            raise BindingActionNotFoundError(f'Invalid axis action "{action_name}"')
        except JoystickNotFoundError:
            return default
    
    def get_hat_action(self, action_name: str, default: tuple[float, float]=(0, 0)) -> tuple[float, float]:
        try:
            return any(b() for b in self.axis_actions[action_name])
        except KeyError:
            raise BindingActionNotFoundError(f'Invalid hat action "{action_name}"')
        except JoystickNotFoundError:
            return default
    
    def save_previous_binary_actions(self):
        for action_name in self.binary_actions:
            self.previous_binary_actions[action_name] = self.get_binary_action(action_name)


class JoystickWrapper:
    """
    Wrapper for pygame's Joystick with some extra features
    """
    def __init__(self, joystick_number: int):
        if joystick_number >= pygame.joystick.get_count():
            raise JoystickNotFoundError(f'Could not find joystick #{joystick_number}')

        self.joystick_number = joystick_number
        self.joystick = pygame.Joystick(joystick_number)
    
    def get_button(self, button_number: int):
        return self.joystick.get_button(button_number)
    
    def get_axis(self, axis_number: int, deadzone: float=0.05):
        axis = self.joystick.get_axis(axis_number)
        if abs(axis) < deadzone:
            return 0.0
        return axis

    def get_hat(self, hat_number: int):
        return self.joystick.get_hat(hat_number)


class JoystickCache:
    def __init__(self):
        self.joysticks: list[JoystickWrapper] = []
        self.reload()

    def reload(self):
        self.joysticks = [JoystickWrapper(i) for i in range(pygame.joystick.get_count())]
    
    def get_joystick(self, joystick_number: int):
        try:
            return self.joysticks[joystick_number]
        except IndexError:
            raise JoystickNotFoundError(f'Could not find joystick #{joystick_number}')


_joystick_cache = None

def init_joystick_cache():
    global _joystick_cache
    _joystick_cache = JoystickCache()


def reload_joystick_cache():
    _joystick_cache.reload()


def joystick(joystick_number: int) -> JoystickWrapper:
    return _joystick_cache.get_joystick(joystick_number)

# Ren'Py Advanced Gamepad Plugin
# Advanced gamepad/controller input system for Ren'Py
# Version 1.0

import renpy
import pygame
from pygame.locals import *

class GamepadInputBuffer:
    """Stores recent gamepad inputs for combo detection."""
    
    def __init__(self, buffer_size=10):
        self.buffer = []
        self.max_size = buffer_size
    
    def add_input(self, button, state, timestamp):
        """Add input to buffer."""
        self.buffer.append({
            'button': button,
            'state': state,
            'time': timestamp
        })
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)
    
    def get_buffer(self):
        """Get current buffer."""
        return self.buffer
    
    def clear(self):
        """Clear the buffer."""
        self.buffer = []
    
    def get_recent(self, time_window=0.5):
        """Get inputs within a time window."""
        current_time = renpy.display.core.get_time()
        return [
            inp for inp in self.buffer
            if (current_time - inp['time']) <= time_window
        ]


class AdvancedGamepad:
    """Advanced gamepad controller with enhanced features."""
    
    BUTTONS = {
        'A': pygame.CONTROLLER_BUTTON_A,
        'B': pygame.CONTROLLER_BUTTON_B,
        'X': pygame.CONTROLLER_BUTTON_X,
        'Y': pygame.CONTROLLER_BUTTON_Y,
        'LB': pygame.CONTROLLER_BUTTON_LEFTSHOULDER,
        'RB': pygame.CONTROLLER_BUTTON_RIGHTSHOULDER,
        'BACK': pygame.CONTROLLER_BUTTON_BACK,
        'START': pygame.CONTROLLER_BUTTON_START,
        'LEFT_STICK': pygame.CONTROLLER_BUTTON_LEFTSTICK,
        'RIGHT_STICK': pygame.CONTROLLER_BUTTON_RIGHTSTICK,
        'GUIDE': pygame.CONTROLLER_BUTTON_GUIDE,
    }
    
    AXES = {
        'LEFT_X': pygame.CONTROLLER_AXIS_LEFTX,
        'LEFT_Y': pygame.CONTROLLER_AXIS_LEFTY,
        'RIGHT_X': pygame.CONTROLLER_AXIS_RIGHTX,
        'RIGHT_Y': pygame.CONTROLLER_AXIS_RIGHTY,
        'LEFT_TRIGGER': pygame.CONTROLLER_AXIS_TRIGGERLEFT,
        'RIGHT_TRIGGER': pygame.CONTROLLER_AXIS_TRIGGERRIGHT,
    }
    
    DPAD = {
        'UP': pygame.CONTROLLER_BUTTON_DPAD_UP,
        'DOWN': pygame.CONTROLLER_BUTTON_DPAD_DOWN,
        'LEFT': pygame.CONTROLLER_BUTTON_DPAD_LEFT,
        'RIGHT': pygame.CONTROLLER_BUTTON_DPAD_RIGHT,
    }
    
    def __init__(self, controller_index=0, deadzone=0.15):
        self.index = controller_index
        self.controller = None
        self.deadzone = max(0.0, min(1.0, deadzone))
        self.button_states = {}
        self.axis_values = {}
        self.input_buffer = GamepadInputBuffer()
        self.on_button_pressed = None
        self.on_button_released = None
        self.on_axis_motion = None
        self.on_trigger_motion = None
        self.button_mappings = {}
        self.axis_mappings = {}
        self._initialize_controller()
    
    def _initialize_controller(self):
        """Initialize the pygame controller."""
        try:
            if pygame.controller.get_count() > self.index:
                self.controller = pygame.controller.Controller(self.index)
        except Exception as e:
            pass
    
    def is_connected(self):
        """Check if controller is connected and initialized."""
        return self.controller is not None
    
    def get_button_state(self, button):
        """Get current state of a button (True = pressed, False = released)."""
        if not self.is_connected():
            return False
        
        button_id = self.BUTTONS.get(button)
        if button_id is None:
            return False
        
        try:
            return bool(self.controller.get_button(button_id))
        except Exception:
            return False
    
    def get_axis_value(self, axis):
        """Get analog axis value with deadzone applied."""
        if not self.is_connected():
            return 0.0
        
        axis_id = self.AXES.get(axis)
        if axis_id is None:
            return 0.0
        
        try:
            raw_value = self.controller.get_axis(axis_id)
            normalized = raw_value / 32768.0
            
            if abs(normalized) < self.deadzone:
                return 0.0
            
            sign = 1.0 if normalized >= 0 else -1.0
            return sign * ((abs(normalized) - self.deadzone) / (1.0 - self.deadzone))
        except Exception:
            return 0.0
    
    def get_trigger_value(self, trigger):
        """Get trigger value (0.0 to 1.0)."""
        if not self.is_connected():
            return 0.0
        
        axis_id = self.AXES.get(trigger)
        if axis_id is None or trigger not in ('LEFT_TRIGGER', 'RIGHT_TRIGGER'):
            return 0.0
        
        try:
            raw_value = self.controller.get_axis(axis_id)
            return raw_value / 32768.0
        except Exception:
            return 0.0
    
    def get_stick_vector(self, stick):
        """Get analog stick as (x, y) vector."""
        if stick == 'LEFT_STICK':
            return (self.get_axis_value('LEFT_X'), self.get_axis_value('LEFT_Y'))
        elif stick == 'RIGHT_STICK':
            return (self.get_axis_value('RIGHT_X'), self.get_axis_value('RIGHT_Y'))
        else:
            return (0.0, 0.0)
    
    def get_dpad_direction(self):
        """Get D-PAD direction."""
        if not self.is_connected():
            return 'NEUTRAL'
        
        for direction, button_id in self.DPAD.items():
            try:
                if self.controller.get_button(button_id):
                    return direction
            except Exception:
                pass
        
        return 'NEUTRAL'
    
    def get_multiple_buttons(self):
        """Get all currently pressed buttons."""
        pressed = []
        for button_name in self.BUTTONS.keys():
            if self.get_button_state(button_name):
                pressed.append(button_name)
        return pressed
    
    def update(self):
        """Update controller state and call callbacks."""
        if not self.is_connected():
            return
        
        current_time = renpy.display.core.get_time()
        
        for button_name in self.BUTTONS.keys():
            new_state = self.get_button_state(button_name)
            old_state = self.button_states.get(button_name, False)
            
            if new_state != old_state:
                self.button_states[button_name] = new_state
                self.input_buffer.add_input(button_name, new_state, current_time)


class GamepadManager:
    """Manages multiple gamepads and provides global gamepad access."""
    
    def __init__(self, max_controllers=4):
        self.gamepads = {}
        self.max_controllers = max_controllers
        self._init_all_controllers()
    
    def _init_all_controllers(self):
        """Initialize all connected controllers."""
        try:
            pygame.controller.init()
            for i in range(min(pygame.controller.get_count(), self.max_controllers)):
                self.gamepads[i] = AdvancedGamepad(i)
        except Exception:
            pass
    
    def get_gamepad(self, index=0):
        """Get a specific gamepad."""
        return self.gamepads.get(index)
    
    def get_active_gamepads(self):
        """Get all connected gamepads."""
        return [gp for gp in self.gamepads.values() if gp.is_connected()]
    
    def update(self):
        """Update all gamepads."""
        for gamepad in self.gamepads.values():
            gamepad.update()


_gamepad_manager = None

def get_manager():
    """Get the global gamepad manager."""
    global _gamepad_manager
    if _gamepad_manager is None:
        _gamepad_manager = GamepadManager()
    return _gamepad_manager

def get_gamepad(index=0):
    """Get a specific gamepad from global manager."""
    return get_manager().get_gamepad(index)

def update():
    """Update all gamepads."""
    get_manager().update()

# Game screens and UI

init -999 python:
    """Import the advanced gamepad plugin."""
    try:
        import gamepad_plugin
        renpy.gamepad_plugin = gamepad_plugin
    except ImportError:
        class DummyGamepad:
            def get_button_state(self, button): return False
            def get_axis_value(self, axis): return 0.0
            def get_trigger_value(self, trigger): return 0.0
            def get_stick_vector(self, stick): return (0.0, 0.0)
            def get_dpad_direction(self): return "NEUTRAL"
            def get_multiple_buttons(self): return []
            def update(self): pass
            def is_connected(self): return False
        
        class DummyManager:
            def get_gamepad(self, index=0): return DummyGamepad()
            def update(self): pass
        
        renpy.gamepad_plugin = type('GamepadPlugin', (), {
            'get_gamepad': lambda idx=0: DummyManager().get_gamepad(idx),
            'update': lambda: DummyManager().update(),
        })()


def _gamepad_periodic():
    """Called every frame to update gamepad input."""
    try:
        renpy.gamepad_plugin.update()
    except Exception:
        pass

config.periodic_callbacks.append(_gamepad_periodic)


# Utility functions
def gamepad_button_pressed(button, controller=0):
    """Check if a gamepad button is pressed."""
    try:
        gp = renpy.gamepad_plugin.get_gamepad(controller)
        if gp:
            return gp.get_button_state(button)
    except Exception:
        pass
    return False

def gamepad_stick_vector(stick, controller=0):
    """Get gamepad analog stick vector."""
    try:
        gp = renpy.gamepad_plugin.get_gamepad(controller)
        if gp:
            return gp.get_stick_vector(stick)
    except Exception:
        pass
    return (0.0, 0.0)

def gamepad_dpad_direction(controller=0):
    """Get D-PAD direction."""
    try:
        gp = renpy.gamepad_plugin.get_gamepad(controller)
        if gp:
            return gp.get_dpad_direction()
    except Exception:
        pass
    return "NEUTRAL"

def gamepad_is_connected(controller=0):
    """Check if gamepad is connected."""
    try:
        gp = renpy.gamepad_plugin.get_gamepad(controller)
        return gp and gp.is_connected()
    except Exception:
        pass
    return False


# Main game screen - Simple Action Game
screen game_screen(player_x=None, player_y=None, enemy_x=None, enemy_y=None, player_health=100, enemy_health=100):
    """Main game screen with player and enemy."""
    
    if player_x is None:
        default player_x = 300
    if player_y is None:
        default player_y = 400
    if enemy_x is None:
        default enemy_x = 600
    if enemy_y is None:
        default enemy_y = 300
    
    # Background
    frame:
        xsize 1280
        ysize 720
        background Solid("#1a1a2e")
    
    # Player character
    frame:
        xpos player_x - 25
        ypos player_y - 50
        xsize 50
        ysize 100
        background Solid("#00ff41")
    
    # Enemy character
    frame:
        xpos enemy_x - 25
        ypos enemy_y - 50
        xsize 50
        ysize 100
        background Solid("#ff2e63")
    
    # Health bars
    frame:
        xpos 20
        ypos 20
        xsize 300
        ysize 30
        background Solid("#333")
    
    text "Player HP: {}/100".format(player_health) xpos 30 ypos 30 size 18
    frame:
        xpos 20
        ypos 60
        xsize int(player_health * 3)
        ysize 20
        background Solid("#00ff41")
    
    frame:
        xpos 1280 - 320
        ypos 20
        xsize 300
        ysize 30
        background Solid("#333")
    
    text "Enemy HP: {}/100".format(enemy_health) xpos 1280 - 310 ypos 30 size 18
    frame:
        xpos 1280 - 320
        ypos 60
        xsize int(enemy_health * 3)
        ysize 20
        background Solid("#ff2e63")
    
    # Instructions
    text "Use D-PAD or LEFT STICK to move | Press [A] to attack | [B] to dodge" xpos 50 ypos 680 size 16 color "#00ff41"
    
    # Display gamepad status
    if gamepad_is_connected():
        text "GAMEPAD CONNECTED" xpos 1280 - 300 ypos 680 size 14 color "#00ff41"
    else:
        text "GAMEPAD NOT DETECTED" xpos 1280 - 300 ypos 680 size 14 color "#ff2e63"


# Main menu screen
screen main_menu():
    """Main menu screen."""
    
    frame:
        xsize 1280
        ysize 720
        background Solid("#1a1a2e")
        xalign 0.5
        yalign 0.5
    
    vbox:
        xalign 0.5
        yalign 0.3
        spacing 20
    
        text "GAMEPAD ACTION GAME" size 60 color "#00ff41" xalign 0.5
        text "Demo using Advanced Gamepad Plugin" size 24 color "#0ff" xalign 0.5
        
        null height 40
        
        textbutton "START GAME":
            action Return("start_game")
            xalign 0.5
            xsize 400
            background Solid("#00ff41")
            text_color "#000"
            text_size 30
        
        textbutton "GAMEPAD TEST":
            action Return("gamepad_test")
            xalign 0.5
            xsize 400
            background Solid("#0ff")
            text_color "#000"
            text_size 30
        
        textbutton "QUIT":
            action Return("quit")
            xalign 0.5
            xsize 400
            background Solid("#ff2e63")
            text_color "#000"
            text_size 30


# Gamepad test screen
screen gamepad_test_screen():
    """Debug screen to test gamepad input values."""
    
    frame:
        xsize 1280
        ysize 720
        background Solid("#1a1a2e")
    
    vbox:
        xpos 50
        ypos 50
        spacing 15
    
        text "GAMEPAD TEST SCREEN" size 40 color "#00ff41"
        
        python:
            gp = renpy.gamepad_plugin.get_gamepad(0)
            
            if gp and gp.is_connected():
                left_x, left_y = gp.get_stick_vector('LEFT_STICK')
                right_x, right_y = gp.get_stick_vector('RIGHT_STICK')
                left_trig = gp.get_trigger_value('LEFT_TRIGGER')
                right_trig = gp.get_trigger_value('RIGHT_TRIGGER')
                buttons = gp.get_multiple_buttons()
                dpad = gp.get_dpad_direction()
                
                text "Status: CONNECTED" size 20 color "#00ff41"
                text "Left Stick: ({:.2f}, {:.2f})".format(left_x, left_y) size 18 color "#0ff"
                text "Right Stick: ({:.2f}, {:.2f})".format(right_x, right_y) size 18 color "#0ff"
                text "Left Trigger: {:.2f}".format(left_trig) size 18 color "#0ff"
                text "Right Trigger: {:.2f}".format(right_trig) size 18 color "#0ff"
                text "D-PAD: {}".format(dpad) size 18 color "#0ff"
                text "Pressed Buttons: {}".format(", ".join(buttons) if buttons else "None") size 18 color "#0ff"
            else:
                text "Status: NO GAMEPAD DETECTED" size 20 color "#ff2e63"
        
        null height 30
        text "Press [START] to go back" size 16 color "#666"

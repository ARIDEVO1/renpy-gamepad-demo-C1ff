# Gamepad Testing Script
# This script provides an interactive gamepad/controller testing interface

# Initialize variables for gamepad state tracking
default gamepad_button_pressed = None
default gamepad_test_active = False
default current_button_test = None
default recheck_count = 0

# Character for dialogue
define narrator = Character(None, kind=nvl)

label gamepad_test_start:
    scene bg black
    with fade
    
    "Gamepad Testing Interface"
    ""
    "This tool will help you test all your gamepad buttons."
    ""
    menu:
        "Start gamepad test":
            jump test_button_a
        "Exit":
            return

label test_button_a:
    $ current_button_test = "pad_a"
    $ gamepad_button_pressed = False
    $ recheck_count = 0
    
    "Press button A"
    ""
    
    call wait_for_button("pad_a")
    
    if gamepad_button_pressed:
        "Good! I can see you clicking button A."
        ""
        menu:
            "Recheck button A":
                $ recheck_count += 1
                jump test_button_a
            "Continue to next button (B)":
                jump test_button_b
            "Exit test":
                return
    else:
        "No button press detected. Try again."
        jump test_button_a

label test_button_b:
    $ current_button_test = "pad_b"
    $ gamepad_button_pressed = False
    $ recheck_count = 0
    
    "Press button B"
    ""
    
    call wait_for_button("pad_b")
    
    if gamepad_button_pressed:
        "Good! I can see you clicking button B."
        ""
        menu:
            "Recheck button B":
                $ recheck_count += 1
                jump test_button_b
            "Continue to next button (X)":
                jump test_button_x
            "Exit test":
                return
    else:
        "No button press detected. Try again."
        jump test_button_b

label test_button_x:
    $ current_button_test = "pad_x"
    $ gamepad_button_pressed = False
    $ recheck_count = 0
    
    "Press button X"
    ""
    
    call wait_for_button("pad_x")
    
    if gamepad_button_pressed:
        "Good! I can see you clicking button X."
        ""
        menu:
            "Recheck button X":
                $ recheck_count += 1
                jump test_button_x
            "Continue to next button (Y)":
                jump test_button_y
            "Exit test":
                return
    else:
        "No button press detected. Try again."
        jump test_button_x

label test_button_y:
    $ current_button_test = "pad_y"
    $ gamepad_button_pressed = False
    $ recheck_count = 0
    
    "Press button Y"
    ""
    
    call wait_for_button("pad_y")
    
    if gamepad_button_pressed:
        "Good! I can see you clicking button Y."
        ""
        menu:
            "Recheck button Y":
                $ recheck_count += 1
                jump test_button_y
            "Continue to D-Pad":
                jump test_dpad
            "Exit test":
                return
    else:
        "No button press detected. Try again."
        jump test_button_y

label test_dpad:
    $ current_button_test = "dpad"
    $ gamepad_button_pressed = False
    $ recheck_count = 0
    
    "Press D-Pad (any direction)"
    ""
    
    call wait_for_dpad
    
    if gamepad_button_pressed:
        "Good! I detected D-Pad input."
        ""
        menu:
            "Recheck D-Pad":
                $ recheck_count += 1
                jump test_dpad
            "Continue to Triggers":
                jump test_triggers
            "Exit test":
                return
    else:
        "No D-Pad input detected. Try again."
        jump test_dpad

label test_triggers:
    $ current_button_test = "triggers"
    $ gamepad_button_pressed = False
    $ recheck_count = 0
    
    "Press LT or RT (Trigger buttons)"
    ""
    
    call wait_for_triggers
    
    if gamepad_button_pressed:
        "Good! I detected trigger input."
        ""
        menu:
            "Recheck Triggers":
                $ recheck_count += 1
                jump test_triggers
            "Test Complete":
                jump test_complete
            "Exit test":
                return
    else:
        "No trigger input detected. Try again."
        jump test_triggers

label test_complete:
    "Gamepad test complete!"
    ""
    "All buttons tested successfully."
    ""
    menu:
        "Start over":
            jump gamepad_test_start
        "Exit":
            return

# Subroutine to wait for a specific button press
label wait_for_button(button_name):
    $ gamepad_button_pressed = False
    $ timeout_counter = 0
    
    while not gamepad_button_pressed and timeout_counter < 600:  # ~10 seconds at 60 FPS
        $ timeout_counter += 1
        $ renpy.pause(0.01)
        
        # Check for the specific button press
        if renpy.input_type() == "pad" and renpy.get_key_pressed() == button_name:
            $ gamepad_button_pressed = True
    
    return

# Subroutine to wait for D-Pad input
label wait_for_dpad:
    $ gamepad_button_pressed = False
    $ timeout_counter = 0
    $ dpad_buttons = ["pad_up", "pad_down", "pad_left", "pad_right"]
    
    while not gamepad_button_pressed and timeout_counter < 600:
        $ timeout_counter += 1
        $ renpy.pause(0.01)
        
        if renpy.input_type() == "pad":
            $ pressed_key = renpy.get_key_pressed()
            if pressed_key in dpad_buttons:
                $ gamepad_button_pressed = True
    
    return

# Subroutine to wait for trigger input
label wait_for_triggers:
    $ gamepad_button_pressed = False
    $ timeout_counter = 0
    $ trigger_buttons = ["pad_ltrigger", "pad_rtrigger"]
    
    while not gamepad_button_pressed and timeout_counter < 600:
        $ timeout_counter += 1
        $ renpy.pause(0.01)
        
        if renpy.input_type() == "pad":
            $ pressed_key = renpy.get_key_pressed()
            if pressed_key in trigger_buttons:
                $ gamepad_button_pressed = True
    
    return

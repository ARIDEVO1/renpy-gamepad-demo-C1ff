# Main game script with gamepad input handling

define player_speed = 15
define enemy_speed = 8
define attack_cooldown = 0.5
define attack_range = 80

init python:
    import math
    
    class GameState:
        def __init__(self):
            self.player_x = 300
            self.player_y = 400
            self.enemy_x = 600
            self.enemy_y = 300
            self.player_health = 100
            self.enemy_health = 100
            self.player_last_attack = 0
            self.enemy_last_attack = 0
            self.player_dodging = False
            self.dodge_cooldown = 0
            self.game_over = False
            self.winner = None
        
        def distance_to_enemy(self):
            dx = self.enemy_x - self.player_x
            dy = self.enemy_y - self.player_y
            return math.sqrt(dx*dx + dy*dy)
        
        def update(self, dt=0.016):
            """Update game state based on gamepad input."""
            
            if self.game_over:
                return
            
            # Get gamepad input
            left_x, left_y = gamepad_stick_vector('LEFT_STICK', 0)
            dpad = gamepad_dpad_direction(0)
            a_pressed = gamepad_button_pressed('A', 0)
            b_pressed = gamepad_button_pressed('B', 0)
            
            # Player movement with left stick
            if abs(left_x) > 0.3:
                self.player_x += left_x * player_speed
            if abs(left_y) > 0.3:
                self.player_y += left_y * player_speed
            
            # Player movement with D-PAD
            if dpad == 'LEFT':
                self.player_x -= player_speed
            elif dpad == 'RIGHT':
                self.player_x += player_speed
            elif dpad == 'UP':
                self.player_y -= player_speed
            elif dpad == 'DOWN':
                self.player_y += player_speed
            
            # Clamp player position
            self.player_x = max(50, min(1230, self.player_x))
            self.player_y = max(50, min(650, self.player_y))
            
            # Enemy AI - move towards player
            if self.distance_to_enemy() > 100:
                dx = self.player_x - self.enemy_x
                dy = self.player_y - self.enemy_y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    self.enemy_x += (dx / dist) * enemy_speed
                    self.enemy_y += (dy / dist) * enemy_speed
            
            # Clamp enemy position
            self.enemy_x = max(50, min(1230, self.enemy_x))
            self.enemy_y = max(50, min(650, self.enemy_y))
            
            # Update dodge cooldown
            if self.dodge_cooldown > 0:
                self.dodge_cooldown -= dt
                self.player_dodging = self.dodge_cooldown > 0.2
            
            # Player attack
            current_time = renpy.display.core.get_time()
            if a_pressed and current_time - self.player_last_attack >= attack_cooldown:
                if self.distance_to_enemy() < attack_range:
                    self.enemy_health -= 15
                    self.player_last_attack = current_time
            
            # Player dodge
            if b_pressed and self.dodge_cooldown <= 0:
                self.dodge_cooldown = 0.5
            
            # Enemy attack
            if self.distance_to_enemy() < attack_range and current_time - self.enemy_last_attack >= 1.0:
                if not self.player_dodging:
                    self.player_health -= 10
                self.enemy_last_attack = current_time
            
            # Check win/lose conditions
            if self.enemy_health <= 0:
                self.game_over = True
                self.winner = "PLAYER"
            elif self.player_health <= 0:
                self.game_over = True
                self.winner = "ENEMY"


label start:
    """Main entry point."""
    
    python:
        game_state = GameState()
        update_timer = 0
    
    label main_menu_loop:
        call screen main_menu
        
        if _return == "start_game":
            jump game_loop
        elif _return == "gamepad_test":
            jump gamepad_test_loop
        elif _return == "quit":
            return
    
    label game_loop:
        """Main game loop."""
        
        python:
            game_state = GameState()
        
        while not game_state.game_over:
            python:
                # Update game state
                game_state.update()
            
            show screen game_screen(
                player_x=game_state.player_x,
                player_y=game_state.player_y,
                enemy_x=game_state.enemy_x,
                enemy_y=game_state.enemy_y,
                player_health=game_state.player_health,
                enemy_health=game_state.enemy_health
            )
            
            pause 0.016  # ~60 FPS
        
        # Show game over screen
        hide screen game_screen
        
        if game_state.winner == "PLAYER":
            "YOU WIN! You defeated the enemy!"
        else:
            "GAME OVER! You were defeated..."
        
        jump main_menu_loop
    
    label gamepad_test_loop:
        """Gamepad test screen."""
        
        show screen gamepad_test_screen
        
        # Wait for START button to go back
        while not gamepad_button_pressed('START', 0):
            python:
                pass
            pause 0.1
        
        hide screen gamepad_test_screen
        
        jump main_menu_loop

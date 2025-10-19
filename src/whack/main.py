import pygame
import sys
from level_select import show_level_select

def main():
    pygame.init()
    
    # This shows the level selection screen
    selected_level = show_level_select()
    
    # It will ALWAYS return 1 (since only Level 1 is clickable)
    if selected_level == 1:
    # Run your credit card game
        from level1_credit import main as level1_main
        result = level1_main()  # NEW - capture return value
        if result == "level2":  # NEW - check if they clicked NEXT LEVEL
            from level2_identity import main as level2_main
            level2_main()

    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
# ===== main.py =====
import pygame
import sys
from src.core.game_manager import GameManager

def main():
    """Punto de entrada principal del juego"""
    try:
        pygame.init()
        game = GameManager()
        game.run()
    except Exception as e:
        print(f"Error al iniciar el juego: {e}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
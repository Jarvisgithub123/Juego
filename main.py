import pygame
import sys
import cProfile
import pstats
import io
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

def main_with_profiling():
    """Ejecuta el juego con profiling activado"""
    profiler = cProfile.Profile()
    
    try:
        profiler.enable()
        main()
    except KeyboardInterrupt:
        print("\nJuego interrumpido por el usuario")
    finally:
        profiler.disable()
        
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(30)
        print(s.getvalue())
        # Guardar estadisticas en archivo
        stats.dump_stats('profile_results.prof')
if __name__ == "__main__":
    # Cambiar entre normal y con profiling
    import sys
    if '--profile' in sys.argv:
        main_with_profiling()
    else:
        main()
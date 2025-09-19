import pygame
import sys
import cProfile
import pstats
import io
import traceback
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
def main_debug():
    """Ejecuta el juego y, si ocurre un error, muestra archivo y linea exacta."""
    try:
        pygame.init()
        game = GameManager()
        game.run()
    except Exception as e:
        # Extraer lista de frames del traceback
        tb_list = traceback.extract_tb(e.__traceback__)
        if tb_list:
            last = tb_list[-1]
            filename = last.filename
            lineno = last.lineno
            func = last.name
            line_text = last.line
            print(f"ERROR: excepción en {filename}, línea {lineno}, función {func}")
            if line_text:
                print(f"  Código: {line_text.strip()}")
        else:
            print("ERROR: excepción sin traceback disponible")

        # Imprimir traceback completo en consola
        print("\nTraceback completo:")
        traceback.print_exc()

        # Guardar informe en archivo para inspección posterior
        try:
            with open("crash_report.txt", "w", encoding="utf-8") as f:
                f.write("ERROR: excepción capturada\n\n")
                if tb_list:
                    f.write(f"Archivo: {filename}\nLínea: {lineno}\nFunción: {func}\n")
                    if line_text:
                        f.write(f"Código: {line_text.strip()}\n\n")
                f.write("Traceback completo:\n")
                traceback.print_exc(file=f)
            print("Crash report guardado en crash_report.txt")
        except Exception as write_err:
            print(f"No se pudo escribir crash_report.txt: {write_err}")

        # Salir con código de error
        try:
            pygame.quit()
        except Exception:
            pass
        sys.exit(1)
        
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
    if '--debug' in sys.argv:
        main_debug()
    else:
        main()
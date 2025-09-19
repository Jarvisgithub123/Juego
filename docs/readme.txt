Instrucciones para ejecutar el juego

Abre una terminal
Navega hasta la carpeta del juego

Instala las dependencias necesarias
 # pip install pygame
Ejecuta el juego
 # python main.py 

#Recomendaciones
A la hora de ejecutar el juego, no tener programas abiertos como Spotify, Discord, Deezer, Youtube Music
ya que puede producir inestabilidad en el juego, caidas de fps, etc.
Esto es debido a que Pygame utiliza el modulo de audio de SDL (Simple DirectMedia Layer) de una forma erronea de forma nativa
haciendo que compita con estos programas por recursos de audio.
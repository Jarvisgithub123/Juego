import pygame

class SpriteAnimado(pygame.sprite.Sprite):
    def __init__(self, frames, frame_rate):
        super().__init__()
        self.frames = frames
        self.frame_rate = frame_rate
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.last_update = pygame.time.get_ticks()

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
import pygame
import random

mood_list = ['Happy', 'Frown', 'Sad', 'Angry', 'Neutral']

action_dict = {
    'Happy': 'Smile',
    'Frown': 'Frown',
    'Sad': 'Cry',
    'Angry': 'Shout',
    'Neutral': 'Roll eyes',
}

class Avatar:
    def __init__(self, game, size=(50, 50)) -> None:
        self.game = game
        self.size = list(size)
        self.mood_list = mood_list
        self.actions = action_dict
        self.current_mood = 'Neutral'
        self.animation = self.game.assets_img['avatar/Neutral']
        self.mood = 2 * 100  # start at Neutral index 4? Actually we want initial mood Neutral. Let's compute: index 4 * mood_interval(100) = 400.
        self.mood_interval = 100

    def rect(self) -> pygame.Rect:
        img_rect = self.animation.img().get_rect(center=(self.game.display.get_width() // 2, self.game.display.get_height() // 2))
        return pygame.Rect(img_rect[0], img_rect[1], self.size[0], self.size[1])

    def force_mood(self, mood):
        """Immediately set mood to a specific state, resetting animation."""
        if self.current_mood != mood:
            self.current_mood = mood
            self.animation = self.game.assets_img['avatar/' + mood].copy()
            # Optionally play mood sfx
            # sfx_list = self.game.assets_sfx.get('mood_sfx', {}).get('avatar/'+mood)
            # if sfx_list: self.game.sound.play('mood_sfx', ...)

    def set_mood(self, mood):
        if self.current_mood != mood:
            self.current_mood = mood
            self.animation = self.game.assets_img['avatar/' + mood].copy()

    def get_mood_severity(self):
        """Returns severity scale: 0=Happy/Neutral, 1=Frown, 2=Sad, 3=Angry"""
        if self.current_mood == 'Frown': return 1
        if self.current_mood == 'Sad': return 2
        if self.current_mood == 'Angry': return 3
        return 0

    def update(self, update_mood=True):
        # update_mood=True means mood increases (towards Angry), False means decreases (towards Happy)
        if update_mood:
            self.mood = min((len(self.mood_list)) * self.mood_interval, self.mood + 1)
        else:
            self.mood = max(-self.mood_interval, self.mood - 1)

        idx = max(0, min(self.mood, (len(self.mood_list)-1) * self.mood_interval)) // self.mood_interval
        self.set_mood(self.mood_list[idx])

    def render(self, surf):
        surf.blit(self.animation.img(), self.rect())
        self.animation.update()
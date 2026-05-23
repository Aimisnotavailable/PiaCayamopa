import pygame
import sys
from Scripts.utils import load_image, load_images, load_sound, load_sounds, Animation
from Scripts.assets import Assets
from Scripts.avatar import Avatar
from Scripts.sfx import SoundMixer
from Scripts.shop import Shop

MAP_GOAL = 5000
INITIAL_TOKENS = 3
PATIENCE_MAX = 100.0

class Engine:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((1200, 800))   # doubled window size
        self.display = pygame.Surface((600, 400))            # doubled internal resolution
        self.clock = pygame.time.Clock()
        pygame.mixer.init()
        pygame.init()

        scale = (100, 100)

        # Assets (unchanged)
        assets = Assets()
        assets.insert({
            'moods': {
                'avatar/Neutral': Animation(load_images('avatar/Neutral', scale=scale), dur=8, loop=True),
                'avatar/Happy': Animation(load_images('avatar/Happy', scale=scale), dur=8, loop=True),
                'avatar/Frown': Animation(load_images('avatar/Frown', scale=scale), dur=8, loop=True),
                'avatar/Sad': Animation(load_images('avatar/Sad', scale=scale), dur=8, loop=True),
                'avatar/Angry': Animation(load_images('avatar/Angry', scale=scale), dur=8, loop=True),
                'cursor': Animation(load_images('cursor'), dur=7, loop=True),
                'cursor_provoke': Animation(load_images('cursor_provoke'), dur=7, loop=True),
            }
        }, key='img')

        assets.insert({
            'mood_sfx': {
                'avatar/Neutral': load_sounds('avatar/Neutral'),
                'avatar/Happy': load_sounds('avatar/Happy'),
                'avatar/Frown': load_sounds('avatar/Frown'),
                'avatar/Sad': load_sounds('avatar/Sad'),
                'avatar/Angry': load_sounds('avatar/Angry'),
            }
        }, key='sfx')

        game_sfx = {
            'gavel': [load_sound('gavel.wav')],
            'buy': [load_sound('buy.wav')],
            'victory': [load_sound('victory.wav')],
            'warning': [load_sound('warning.wav')],
            'map_tick': [load_sound('map_tick.wav')],
        }
        assets.insert({'game_sfx': game_sfx}, key='sfx')

        self.assets_img = assets.fetch(payload={'img': ['all']})
        self.assets_sfx = assets.fetch(payload={'sfx': ['all']})
        self.sound = SoundMixer(self.assets_sfx)
        self.avatar = Avatar(self, size=scale)

        # Game state
        self.map_points = 0
        self.patience = PATIENCE_MAX
        self.gavel_tokens = INITIAL_TOKENS
        self.provoke_unlocked = False
        self.provoke_mode = False
        self.active_cursor = self.assets_img['cursor']
        self.active_effects = []
        self.state = 'playing'

        # Shop
        self.shop = Shop(self)

        # Fonts
        self.font = pygame.font.Font(None, 32)          # doubled size to match bigger surface
        self.big_font = pygame.font.Font(None, 64)

        # Timers
        self.map_timer = 0
        self.patience_timer = 0

        pygame.mouse.set_visible(False)

    def reset(self):
        self.map_points = 0
        self.patience = PATIENCE_MAX
        self.gavel_tokens = INITIAL_TOKENS
        self.provoke_unlocked = False
        self.provoke_mode = False
        self.active_cursor = self.assets_img['cursor']
        self.active_effects.clear()
        self.state = 'playing'
        self.avatar.force_mood('Neutral')
        self.sound.stop(stop_all=True)

    def run(self) -> None:
        while True:
            self.display.fill((0, 0, 0))
            mpos = list(pygame.mouse.get_pos())
            # Scale mouse position to internal coordinates
            mpos[0] = mpos[0] // 2
            mpos[1] = mpos[1] // 2

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        if self.state in ('playing', 'shop'):
                            self.state = 'shop' if self.state == 'playing' else 'playing'
                    if event.key == pygame.K_q and self.provoke_unlocked:
                        self.provoke_mode = not self.provoke_mode
                        self.active_cursor = self.assets_img['cursor_provoke'] if self.provoke_mode else self.assets_img['cursor']
                    # Restart on any key when game ended
                    if self.state in ('victory', 'gameover'):
                        self.reset()

                # Shop scroll handling (cross-version)
                if self.state == 'shop':
                    if event.type == pygame.MOUSEWHEEL:
                        self.shop.handle_scroll(event.y)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 4:   # scroll up (old pygame)
                            self.shop.handle_scroll(1)
                        elif event.button == 5: # scroll down
                            self.shop.handle_scroll(-1)

                # Shop item clicks
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == 'shop':
                        self.shop.handle_click(mpos)

            if self.state == 'playing':
                self.update_playing(mpos)

            self.render(mpos)

            self.screen.blit(
                pygame.transform.scale(self.display, (self.screen.get_width(), self.screen.get_height())),
                (0, 0)
            )
            pygame.display.update()
            self.clock.tick(60)

    def update_playing(self, mpos):
        # (update logic – unchanged from your latest working version)
        for effect in self.active_effects[:]:
            effect['timer'] -= 1
            if effect['timer'] <= 0:
                self.active_effects.remove(effect)

        touching = self.avatar.rect().collidepoint(mpos)
        update_mood = False

        if self.provoke_mode:
            if touching:
                update_mood = True
                self.map_timer += 1
                if self.map_timer >= 10:
                    severity = self.avatar.get_mood_severity()
                    gain = 1 + severity * 0.5
                    multiplier = 1.0
                    for eff in self.active_effects:
                        if eff['type'] == 'map_multiplier':
                            multiplier = max(multiplier, eff.get('value', 1.0))
                    self.map_points += int(gain * multiplier)
                    self.map_timer = 0
                    self.sound.play('game_sfx', variant='map_tick', vol=0.3)
                self.active_cursor = self.assets_img['cursor_provoke']
            else:
                update_mood = False
                self.map_timer = 0
        else:
            if touching:
                update_mood = False
            else:
                update_mood = True
            self.active_cursor = self.assets_img['cursor']

        self.avatar.update(update_mood=update_mood)

        mood = self.avatar.current_mood
        if mood in ['Frown', 'Sad', 'Angry']:
            drain_rate = {'Frown': 0.2, 'Sad': 0.5, 'Angry': 1.0}[mood]
            locked = any(eff['type'] == 'patience_lock' for eff in self.active_effects)
            if not locked:
                self.patience = max(0, self.patience - drain_rate)
                if self.patience <= 0:
                    self.gavel_event()
        else:
            self.patience = min(PATIENCE_MAX, self.patience + 0.5)

        if touching:
            self.active_cursor.update()
        else:
            self.active_cursor.frame = 0

        if self.gavel_tokens <= 0 and self.patience <= 0:
            self.state = 'gameover'
            self.sound.play('game_sfx', variant='gavel')

    def gavel_event(self):
        self.avatar.force_mood('Happy')
        self.patience = PATIENCE_MAX
        self.gavel_tokens -= 1
        penalty = 300
        self.map_points = max(0, self.map_points - penalty)
        self.sound.play('game_sfx', variant='gavel')

    def apply_effect(self, effect_dict):
        self.active_effects.append(effect_dict)

    def buy_item(self, item):
        if self.map_points < item['cost']:
            return False
        self.map_points -= item['cost']
        self.sound.play('game_sfx', variant='buy', vol=0.8)

        if item['effect'] == 'provoke_unlock':
            self.provoke_unlocked = True
            self.provoke_mode = True
            self.active_cursor = self.assets_img['cursor_provoke']
        elif item['effect'] == 'crash_out':
            self.state = 'victory'
            self.sound.play('game_sfx', variant='victory')
        elif item['effect'] == 'instant_mood':
            self.avatar.force_mood(item['mood'])
            if item.get('map_bonus', 0):
                self.map_points += item['map_bonus']
        elif item['effect'] == 'restore_token':
            self.gavel_tokens = min(INITIAL_TOKENS, self.gavel_tokens + 1)
        elif item['effect'] == 'timed_patience_lock':
            self.apply_effect({'type': 'patience_lock', 'timer': item['duration']})
        elif item['effect'] == 'timed_map_multiplier':
            self.apply_effect({'type': 'map_multiplier', 'value': item.get('multiplier', 2), 'timer': item['duration']})
        return True

    def render(self, mpos):
        # UI – now drawn with larger font for better readability
        self.display.blit(self.font.render(f'Media Points: {self.map_points}', True, (255,255,255)), (10, 10))
        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = self.display.get_height() - 45
        pygame.draw.rect(self.display, (60,60,60), (bar_x, bar_y, bar_width, bar_height))
        patience_ratio = self.patience / PATIENCE_MAX
        color = (0,200,0) if patience_ratio > 0.3 else (200,0,0)
        pygame.draw.rect(self.display, color, (bar_x, bar_y, int(bar_width * patience_ratio), bar_height))
        self.display.blit(self.font.render('Patience', True, (255,255,255)), (bar_x, bar_y - 25))
        for i in range(self.gavel_tokens):
            pygame.draw.circle(self.display, (200,200,0), (30 + i*30, self.display.get_height() - 70), 10)
        self.display.blit(self.font.render('Orders', True, (255,255,255)), (10, self.display.get_height() - 100))

        self.avatar.render(self.display)

        cursor_img = self.active_cursor.img()
        cursor_rect = cursor_img.get_rect(center=mpos)
        self.display.blit(cursor_img, cursor_rect)

        self.display.blit(self.font.render(f'Mood: {self.avatar.current_mood}', True, (255,255,255)), (10, 50))
        self.display.blit(self.font.render(f'Action: {self.avatar.actions[self.avatar.current_mood]}', True, (255,255,255)), (10, 80))

        if self.state == 'shop':
            self.shop.render(self.display, mpos)
        elif self.state == 'victory':
            self.display.fill((0,0,0))
            msg = self.big_font.render('ADJOURNED! Walkout!', True, (255,215,0))
            self.display.blit(msg, (self.display.get_width()//2 - msg.get_width()//2, 80))
            msg2 = self.font.render(f'Final Media Points: {self.map_points}', True, (255,255,255))
            self.display.blit(msg2, (self.display.get_width()//2 - msg2.get_width()//2, 200))
            msg3 = self.font.render('Press any key to restart', True, (200,200,200))
            self.display.blit(msg3, (self.display.get_width()//2 - msg3.get_width()//2, 260))
        elif self.state == 'gameover':
            self.display.fill((0,0,0))
            msg = self.big_font.render('CONTEMPT! Ejected!', True, (255,0,0))
            self.display.blit(msg, (self.display.get_width()//2 - msg.get_width()//2, 80))
            msg2 = self.font.render('You exhausted all warnings.', True, (255,255,255))
            self.display.blit(msg2, (self.display.get_width()//2 - msg2.get_width()//2, 200))
            msg3 = self.font.render('Press any key to restart', True, (200,200,200))
            self.display.blit(msg3, (self.display.get_width()//2 - msg3.get_width()//2, 260))
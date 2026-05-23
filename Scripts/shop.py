import pygame

class Shop:
    def __init__(self, engine):
        self.engine = engine
        self.font = pygame.font.Font(None, 24)          # larger for readability
        self.small_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 36)

        # Removed provoke cursor item; always available.
        self.items = [
            {
                'name': 'Walkout (Crash Out)',
                'desc': 'Cause an uproar and\nadjourn the hearing!',
                'cost': 5000,
                'effect': 'crash_out',
                'color': (255, 215, 0),
            },
            {
                'name': 'Tissue Box',
                'desc': 'Instant tears\n(+200 MAP)',
                'cost': 300,
                'effect': 'instant_mood',
                'mood': 'Sad',
                'map_bonus': 200,
                'color': (100, 149, 237),
            },
            {
                'name': 'Objection!',
                'desc': 'Restore 1 Order token\n(max 3)',
                'cost': 400,
                'effect': 'restore_token',
                'color': (50, 205, 50),
            },
            {
                'name': 'Gag Order',
                'desc': 'Patience freezes for\n10 seconds',
                'cost': 250,
                'effect': 'timed_patience_lock',
                'duration': 600,
                'color': (138, 43, 226),
            },
            {
                'name': 'Media Frenzy',
                'desc': 'Double MAP gain for\n10 seconds',
                'cost': 300,
                'effect': 'timed_map_multiplier',
                'multiplier': 2,
                'duration': 600,
                'color': (255, 140, 0),
            }
        ]

        # Grid layout
        self.grid_cols = 3
        self.slot_size = 90
        self.spacing = 15
        self.start_x = 40
        self.start_y = 60
        self.panel_width = self.engine.display.get_width() - 80
        self.panel_height = self.engine.display.get_height() - 120

        self.scroll_y = 0
        self.scroll_speed = 25
        self.content_height = 0
        self.item_rects = []

    def render(self, surface, mouse_pos):
        # Semi‑transparent backdrop over entire display
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Shop window (with a border and title)
        win_rect = pygame.Rect(20, 30, self.panel_width + 40, self.panel_height + 40)
        pygame.draw.rect(surface, (60, 60, 60), win_rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), win_rect, 2, border_radius=8)

        title_surf = self.title_font.render("Media Manipulation Shop", True, (255,255,255))
        surface.blit(title_surf, (win_rect.centerx - title_surf.get_width()//2, win_rect.y + 10))

        # Close instruction
        tip = self.small_font.render("Press TAB to close | Scroll with mouse wheel", True, (180,180,180))
        surface.blit(tip, (win_rect.x + 10, win_rect.bottom - 25))

        # Clipping area for items
        clip_rect = pygame.Rect(win_rect.x + 10, self.start_y, self.panel_width, self.panel_height)
        surface.set_clip(clip_rect)

        # Calculate content height
        rows = (len(self.items) + self.grid_cols - 1) // self.grid_cols
        self.content_height = rows * (self.slot_size + self.spacing) + self.spacing

        self.item_rects.clear()
        mouse_over = None

        for i, item in enumerate(self.items):
            col = i % self.grid_cols
            row = i // self.grid_cols
            x = self.start_x + col * (self.slot_size + self.spacing)
            y = self.start_y + row * (self.slot_size + self.spacing) - self.scroll_y

            if y + self.slot_size < clip_rect.top or y > clip_rect.bottom:
                continue

            slot_rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
            self.item_rects.append((slot_rect, i))

            bg = (70,70,70)
            if slot_rect.collidepoint(mouse_pos):
                bg = (110,110,110)
                mouse_over = i

            pygame.draw.rect(surface, bg, slot_rect, border_radius=5)
            pygame.draw.rect(surface, (200,200,200), slot_rect, 1, border_radius=5)

            # Placeholder icon circle
            circle_center = (x + self.slot_size//2, y + 30)
            pygame.draw.circle(surface, item['color'], circle_center, 25)

            # Name
            name = item['name'][:10] + '..' if len(item['name']) > 10 else item['name']
            name_surf = self.small_font.render(name, True, (255,255,255))
            surface.blit(name_surf, (x + 5, y + self.slot_size - 25))

            # Cost
            cost_surf = self.small_font.render(f"{item['cost']} MAP", True, (255,255,0))
            surface.blit(cost_surf, (x + 5, y + 5))

        surface.set_clip(None)

        # Scrollbar
        if self.content_height > self.panel_height:
            sb_x = win_rect.right - 15
            sb_w = 8
            sb_h = self.panel_height * (self.panel_height / self.content_height)
            sb_y = clip_rect.top + (self.scroll_y / self.content_height) * self.panel_height
            pygame.draw.rect(surface, (80,80,80), (sb_x, clip_rect.top, sb_w, self.panel_height))
            pygame.draw.rect(surface, (200,200,200), (sb_x, sb_y, sb_w, sb_h))

        # Tooltip
        if mouse_over is not None:
            self.draw_tooltip(surface, mouse_pos, self.items[mouse_over])

    def draw_tooltip(self, surface, mouse_pos, item):
        pad = 8
        w = 180
        h = 80
        x = mouse_pos[0] + 20
        y = mouse_pos[1] + 10
        if x + w > surface.get_width():
            x = mouse_pos[0] - w - 20
        if y + h > surface.get_height():
            y = mouse_pos[1] - h - 10

        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (30,30,30), rect, border_radius=4)
        pygame.draw.rect(surface, (255,255,255), rect, 1, border_radius=4)

        name_surf = self.font.render(item['name'], True, (255,255,0))
        surface.blit(name_surf, (x+pad, y+pad))

        cost_surf = self.small_font.render(f"Cost: {item['cost']} MAP", True, (255,255,255))
        surface.blit(cost_surf, (x+pad, y+pad+22))

        lines = item['desc'].split('\n')
        for i, line in enumerate(lines):
            line_surf = self.small_font.render(line, True, (200,200,200))
            surface.blit(line_surf, (x+pad, y+pad+42 + i*16))

    def handle_click(self, pos):
        for rect, idx in self.item_rects:
            if rect.collidepoint(pos):
                self.engine.buy_item(self.items[idx])
                break

    def handle_scroll(self, y_offset):
        self.scroll_y += y_offset * self.scroll_speed
        max_scroll = max(0, self.content_height - self.panel_height)
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))
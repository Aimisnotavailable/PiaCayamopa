import pygame

class Shop:
    def __init__(self, engine):
        self.engine = engine
        self.font = pygame.font.Font(None, 16)          # for item names
        self.small_font = pygame.font.Font(None, 12)    # for cost and tooltip
        self.title_font = pygame.font.Font(None, 24)    # shop title

        self.items = [
            {
                'name': 'Provoke Cursor',
                'desc': 'Equip to anger her.\n(Toggle with Q)',
                'cost': 50,
                'effect': 'provoke_unlock',
                'color': (220, 20, 60),   # crimson
            },
            {
                'name': 'Walkout (Crash Out)',
                'desc': 'Cause an uproar\nand adjourn the hearing!',
                'cost': 5000,
                'effect': 'crash_out',
                'color': (255, 215, 0),   # gold
            },
            {
                'name': 'Tissue Box',
                'desc': 'Instant tears\n(+200 MAP)',
                'cost': 300,
                'effect': 'instant_mood',
                'mood': 'Sad',
                'map_bonus': 200,
                'color': (100, 149, 237), # cornflower blue
            },
            {
                'name': 'Objection!',
                'desc': 'Restore 1 Order token\n(max 3)',
                'cost': 400,
                'effect': 'restore_token',
                'color': (50, 205, 50),   # lime green
            },
            {
                'name': 'Gag Order',
                'desc': 'Patience freezes for\n10 seconds',
                'cost': 250,
                'effect': 'timed_patience_lock',
                'duration': 600,
                'color': (138, 43, 226),  # blue violet
            },
            {
                'name': 'Media Frenzy',
                'desc': 'Double MAP gain for\n10 seconds',
                'cost': 300,
                'effect': 'timed_map_multiplier',
                'multiplier': 2,
                'duration': 600,
                'color': (255, 140, 0),   # dark orange
            }
        ]

        # Layout constants
        self.grid_cols = 3
        self.slot_size = 70
        self.spacing = 10
        self.start_x = 15
        self.start_y = 40
        self.panel_width = self.engine.display.get_width() - 30
        self.panel_height = self.engine.display.get_height() - 60

        # Scroll offset
        self.scroll_y = 0
        self.scroll_speed = 20
        self.content_height = 0   # calculated later

        self.item_rects = []      # store (rect, item_index)

    def render(self, surface, mouse_pos):
        # Semi-transparent backdrop
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Draw shop window border
        shop_rect = pygame.Rect(5, 25, self.panel_width + 20, self.panel_height + 20)
        pygame.draw.rect(surface, (80, 80, 80), shop_rect)
        pygame.draw.rect(surface, (200, 200, 200), shop_rect, 2)

        # Title
        title_surf = self.title_font.render("Media Manipulation Shop", True, (255, 255, 255))
        surface.blit(title_surf, (shop_rect.centerx - title_surf.get_width() // 2, shop_rect.y + 5))

        # Clip area for scrolling (items only visible inside this rectangle)
        clip_rect = pygame.Rect(shop_rect.x + 5, self.start_y, self.panel_width, self.panel_height)
        surface.set_clip(clip_rect)

        # Compute total content height needed
        rows = (len(self.items) + self.grid_cols - 1) // self.grid_cols
        self.content_height = rows * (self.slot_size + self.spacing) + self.spacing

        # Draw items
        self.item_rects.clear()
        mouse_over_item = None
        for i, item in enumerate(self.items):
            col = i % self.grid_cols
            row = i // self.grid_cols
            x = self.start_x + col * (self.slot_size + self.spacing) - self.scroll_y * 0  # no horizontal scroll
            y = self.start_y + row * (self.slot_size + self.spacing) - self.scroll_y

            # Skip items completely out of view (optional optimisation)
            if y + self.slot_size < clip_rect.top or y > clip_rect.bottom:
                continue

            slot_rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
            self.item_rects.append((slot_rect, i))

            # Determine state
            if item['effect'] == 'provoke_unlock':
                if self.engine.provoke_unlocked:
                    state = 'OWNED' if not self.engine.provoke_mode else 'ACTIVE'
                else:
                    state = None
            else:
                state = None

            # Background of slot
            bg_color = (60, 60, 60)
            if slot_rect.collidepoint(mouse_pos):
                bg_color = (100, 100, 100)
                mouse_over_item = i
            if state == 'OWNED':
                bg_color = (40, 40, 100)
            elif state == 'ACTIVE':
                bg_color = (0, 100, 0)

            pygame.draw.rect(surface, bg_color, slot_rect, border_radius=5)
            pygame.draw.rect(surface, (200, 200, 200), slot_rect, 1, border_radius=5)

            # Placeholder icon: colored circle
            circle_center = (x + self.slot_size // 2, y + 25)
            pygame.draw.circle(surface, item['color'], circle_center, 20)
            # Optional: draw a small icon inside circle (we'll leave empty for now)

            # Item name (truncate if too long)
            name = item['name']
            if len(name) > 10:
                name = name[:9] + '.'
            name_surf = self.small_font.render(name, True, (255, 255, 255))
            surface.blit(name_surf, (x + 5, y + self.slot_size - 18))

            # Cost
            cost_surf = self.small_font.render(f"{item['cost']} MAP", True, (255, 255, 0))
            surface.blit(cost_surf, (x + 5, y + 5))

        surface.set_clip(None)  # remove clipping

        # Draw scrollbar if needed
        if self.content_height > self.panel_height:
            scrollbar_x = shop_rect.right - 10
            scrollbar_width = 6
            bar_height = self.panel_height * (self.panel_height / self.content_height)
            bar_y = clip_rect.top + (self.scroll_y / self.content_height) * self.panel_height
            pygame.draw.rect(surface, (120, 120, 120), (scrollbar_x, clip_rect.top, scrollbar_width, self.panel_height))
            pygame.draw.rect(surface, (200, 200, 200), (scrollbar_x, bar_y, scrollbar_width, bar_height))

        # Tooltip on hover
        if mouse_over_item is not None:
            self.draw_tooltip(surface, mouse_pos, self.items[mouse_over_item])

        # Instructions
        tip1 = self.small_font.render("Press TAB to close shop | Scroll with mouse wheel", True, (180, 180, 180))
        surface.blit(tip1, (10, surface.get_height() - 20))

    def draw_tooltip(self, surface, mouse_pos, item):
        # Tooltip appears to the right of the cursor, or left if too close to edge
        padding = 8
        tooltip_width = 150
        tooltip_height = 70
        x = mouse_pos[0] + 15
        y = mouse_pos[1] + 10
        if x + tooltip_width > surface.get_width():
            x = mouse_pos[0] - tooltip_width - 15
        if y + tooltip_height > surface.get_height():
            y = mouse_pos[1] - tooltip_height - 10

        tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
        pygame.draw.rect(surface, (40, 40, 40), tooltip_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), tooltip_rect, 1, border_radius=4)

        # Item name
        name_surf = self.font.render(item['name'], True, (255, 255, 0))
        surface.blit(name_surf, (x + padding, y + padding))

        # Cost
        cost_surf = self.small_font.render(f"Cost: {item['cost']} MAP", True, (255, 255, 255))
        surface.blit(cost_surf, (x + padding, y + padding + 20))

        # Description (split lines)
        desc_lines = item['desc'].split('\n')
        for i, line in enumerate(desc_lines):
            line_surf = self.small_font.render(line, True, (200, 200, 200))
            surface.blit(line_surf, (x + padding, y + padding + 38 + i * 15))

    def handle_click(self, pos):
        for rect, idx in self.item_rects:
            if rect.collidepoint(pos):
                item = self.items[idx]
                if item['effect'] == 'provoke_unlock':
                    if not self.engine.provoke_unlocked:
                        if self.engine.map_points >= item['cost']:
                            self.engine.buy_item(item)
                    else:
                        # Toggle provoke mode if already owned
                        self.engine.provoke_mode = not self.engine.provoke_mode
                        self.engine.active_cursor = self.engine.assets_img['cursor_provoke'] if self.engine.provoke_mode else self.engine.assets_img['cursor']
                else:
                    self.engine.buy_item(item)
                break

    def handle_scroll(self, y_offset):
        """Adjust scroll offset, clamped to valid range."""
        self.scroll_y += y_offset * self.scroll_speed
        max_scroll = max(0, self.content_height - self.panel_height)
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))
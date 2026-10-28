import math
import os
import pygame
from scenes import BaseScene
from ui.phase1_ui import (
    GOLD,
    GOLD_LIGHT,
    GOLD_DIM,
    TEXT_COLOR,
    TEXT_DIM,
    VOID_BLACK,
)

# ── Region definitions ────────────────────────────────────────────────────────
REGIONS = [
    {
        "name": "SUNFIELD",
        "subtitle": "The Golden Farmlands",
        "status": "STARTER TOWN",
        "lore": (
            "Rolling golden fields stretch to the horizon, dotted with windmills "
            "and thatched-roof cottages. Sunfield is the birthplace of hope — a humble "
            "farming town where your journey into the Kingdom of Ariana begins. "
            "The townsfolk are warm, the inn is cheap, and the roads lead everywhere."
        ),
        "color": (255, 210, 80),
        "px": 0.505, "py": 0.668,
        "starter": True,
    },
    {
        "name": "AETHERFALL",
        "subtitle": "The Royal Capital",
        "status": "LOCKED",
        "lore": (
            "The gleaming crown jewel of Ariana. Grand spires pierce the clouds above "
            "the palace district, and the Goddess's light shines perpetually upon the "
            "Royal Citadel. Only those proven worthy may approach its gates — adventurers "
            "must earn their reputation before the capital's doors swing open."
        ),
        "color": (200, 170, 100),
        "px": 0.520, "py": 0.415,
        "starter": False,
    },
    {
        "name": "FROSTVALE",
        "subtitle": "The Frozen North",
        "status": "LOCKED",
        "lore": (
            "An ancient realm of perpetual winter, where blizzards howl through "
            "crumbling mountain passes and frost-giants still stalk the tundra. "
            "Frostvale harbors secrets beneath its glaciers — and dangers that would "
            "freeze the blood of even the hardiest warrior."
        ),
        "color": (160, 220, 255),
        "px": 0.310, "py": 0.250,
        "starter": False,
    },
    {
        "name": "SHADOWMOOR",
        "subtitle": "The Cursed Wasteland",
        "status": "LOCKED",
        "lore": (
            "A twisted land strangled by dark magic emanating from the Demon Lord's "
            "fortress. The sky here is perpetually stained violet, the soil yields "
            "nothing, and the dead do not stay buried. Heroes who venture here rarely "
            "return — those that do are never quite the same."
        ),
        "color": (160, 80, 200),
        "px": 0.790, "py": 0.270,
        "starter": False,
    },
    {
        "name": "VELMOR",
        "subtitle": "The Western Plains",
        "status": "LOCKED",
        "lore": (
            "Wide open plains where wandering merchant caravans and nomadic clans "
            "roam freely. Velmor is the breadbasket of the western provinces, known "
            "for its fierce horseback warriors and legendary trade bazaars. "
            "A land of dust and opportunity."
        ),
        "color": (120, 190, 80),
        "px": 0.188, "py": 0.440,
        "starter": False,
    },
    {
        "name": "LUMENWOOD",
        "subtitle": "The Ancient Forest",
        "status": "LOCKED",
        "lore": (
            "A vast primordial forest where the trees are older than memory and the "
            "canopy blocks out the sun. Lumenwood's ancient spirits guard a sacred "
            "grove at its heart — said to be the source of all life magic in Ariana. "
            "Elves and druids dwell here in careful balance with nature."
        ),
        "color": (60, 160, 80),
        "px": 0.575, "py": 0.535,
        "starter": False,
    },
    {
        "name": "SILVERCOAST",
        "subtitle": "The Merchant Shore",
        "status": "LOCKED",
        "lore": (
            "A bustling coastal city where trade ships from distant lands drop anchor "
            "daily. Silvercoast's harbour district is a labyrinth of market stalls, "
            "taverns, and hidden guilds. Gold flows freely here — as do daggers in the dark."
        ),
        "color": (80, 170, 200),
        "px": 0.175, "py": 0.620,
        "starter": False,
    },
    {
        "name": "EMBERHOLD",
        "subtitle": "The Volcanic Reach",
        "status": "LOCKED",
        "lore": (
            "Built into the flanks of an active volcano, Emberhold is a fortress-city "
            "of dwarven craft and molten fury. Its forges produce the finest weapons in "
            "the kingdom — tempered in lava and cooled in glacier water shipped from the "
            "north. The air here tastes of ash and glory."
        ),
        "color": (220, 100, 40),
        "px": 0.870, "py": 0.460,
        "starter": False,
    },
    {
        "name": "ISLE OF DAWN",
        "subtitle": "The Blessed Isle",
        "status": "LOCKED",
        "lore": (
            "A sacred island bathed in eternal dawn light, where the Goddess's chosen "
            "priests maintain ancient temples. Pilgrims travel from across the kingdom "
            "to seek blessings here. The Isle of Dawn is said to be the last sanctuary "
            "should darkness ever fully consume the mainland."
        ),
        "color": (255, 240, 160),
        "px": 0.845, "py": 0.698,
        "starter": False,
    },
]

PANEL_W   = 340    # fixed panel width
MARGIN    = 16     # screen edge margin
PAD       = 14     # inner padding


def _word_wrap(text, font, max_w):
    """Break text into lines that fit max_w pixels wide."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class MapScene(BaseScene):
    """
    Phase 2 map screen.
    - MAP.jpeg shown full-screen, NO header overlay.
    - HOVER  → panel preview (disappears when mouse leaves).
    - CLICK  → panel locks in place (persists even when mouse moves away).
    - CLICK again on same dot → panel dismisses with smooth fade-out.
    - Panel fades in/out smoothly via panel_alpha.
    - Sunfield has gentle idle pulse; locked dot shows a ring indicator.
    - Enter button lives inside the panel (Sunfield only), clickable when locked.
    """

    def __init__(self, game_state, particles, fonts):
        super().__init__(game_state, particles, fonts)
        self.elapsed = 0.0
        self.fade_in = 0.0
        self.fade_in_speed = 0.55

        self.body_font  = fonts["body"]
        self.ui_font    = fonts["ui"]
        self.small_font = fonts["small"]

        self.map_image   = None
        self._map_scaled = None
        self._load_map()

        self.hotspot_radius = 40

        self.hovered_idx  = None   # which dot the mouse is over right now
        self.selected_idx = None   # which dot is LOCKED (clicked to pin)
        self.ripple_t     = 0.0

        # Panel fade
        self.panel_alpha  = 0.0
        self.panel_target = 0.0
        self.panel_speed  = 7.0

        # Which region the panel is currently showing
        # (selected takes priority over hovered so panel doesn't jump while locked)
        self._panel_region_idx = None

        self.enter_btn_rect = pygame.Rect(0, 0, 0, 0)

        self.map_rect = pygame.Rect(0, 0, 1280, 720)
        if self.map_image:
            self._compute_map_rect()

        self._starter_idx = next((i for i, r in enumerate(REGIONS) if r.get("starter")), 0)

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _load_map(self):
        path = os.path.join("assets", "ui", "MAP.jpeg")
        try:
            self.map_image = pygame.image.load(path).convert()
        except Exception as e:
            print(f"[MapScene] Could not load map: {e}")

    def _compute_map_rect(self):
        iw, ih = self.map_image.get_size()
        scale = min(1280 / iw, 720 / ih)
        dw, dh = int(iw * scale), int(ih * scale)
        self.map_rect    = pygame.Rect((1280 - dw) // 2, (720 - dh) // 2, dw, dh)
        self._map_scaled = pygame.transform.smoothscale(self.map_image, (dw, dh))

    def _region_screen_pos(self, region):
        rx = self.map_rect.x + region["px"] * self.map_rect.width
        ry = self.map_rect.y + region["py"] * self.map_rect.height
        return int(rx), int(ry)

    def _hit_test(self, mx, my):
        for i, reg in enumerate(REGIONS):
            sx, sy = self._region_screen_pos(reg)
            if math.hypot(mx - sx, my - sy) <= self.hotspot_radius:
                return i
        return None

    # ── Events / Update ───────────────────────────────────────────────────────

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        self.hovered_idx = self._hit_test(mx, my)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # ── Enter Sunfield button (inside the locked/hovered panel) ──
                if self.enter_btn_rect.width > 0 and self.enter_btn_rect.collidepoint(mx, my):
                    active = self.selected_idx if self.selected_idx is not None else self.hovered_idx
                    if active is not None and REGIONS[active].get("starter"):
                        self.next_scene = "world_intro"
                    continue   # don't process the dot-click below

                # ── Dot click: toggle lock ────────────────────────────────────
                hit = self._hit_test(mx, my)
                if hit is not None:
                    if self.selected_idx == hit:
                        # Same dot clicked again → dismiss (unlock)
                        self.selected_idx = None
                    else:
                        # New or different dot → lock it
                        self.selected_idx = hit
                        self.ripple_t = 0.0
                # Click on empty map area → deselect
                elif hit is None and self.hovered_idx is None:
                    self.selected_idx = None

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.selected_idx is not None:
                    self.selected_idx = None   # first ESC clears lock
                else:
                    self.next_scene = "title"

    def update(self, dt):
        self.elapsed  += dt
        self.ripple_t += dt
        self.particles.update(dt)

        if self.fade_in < 1.0:
            self.fade_in = min(1.0, self.fade_in + self.fade_in_speed * dt)

        # Panel is visible when LOCKED (selected) OR hovering over a dot
        panel_visible = (self.selected_idx is not None) or (self.hovered_idx is not None)
        self.panel_target = 1.0 if panel_visible else 0.0

        diff = self.panel_target - self.panel_alpha
        self.panel_alpha += diff * min(1.0, self.panel_speed * dt)
        self.panel_alpha  = max(0.0, min(1.0, self.panel_alpha))

        # Which region to show in the panel — locked takes priority
        if self.selected_idx is not None:
            self._panel_region_idx = self.selected_idx
        elif self.hovered_idx is not None:
            self._panel_region_idx = self.hovered_idx
        # If fading out, keep last shown region so the fade looks right
        # (don't reset _panel_region_idx to None until fully hidden)
        if self.panel_alpha < 0.01:
            self._panel_region_idx = None

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw(self, screen):
        screen.fill(VOID_BLACK)

        # Full-screen map — no overlays on top
        if self._map_scaled:
            if self.fade_in < 1.0:
                tmp = self._map_scaled.copy()
                tmp.set_alpha(int(self.fade_in * 255))
                screen.blit(tmp, self.map_rect.topleft)
            else:
                screen.blit(self._map_scaled, self.map_rect.topleft)

        if self.fade_in < 0.05:
            return

        # Hotspot markers (always visible)
        self._draw_markers(screen)

        # Info panel — shown while locked OR hovering, fades smoothly
        if self.panel_alpha > 0.01 and self._panel_region_idx is not None:
            reg = REGIONS[self._panel_region_idx]
            sx  = self._region_screen_pos(reg)[0]
            locked = (self.selected_idx == self._panel_region_idx)
            self._draw_info_panel(screen, reg, sx, self.panel_alpha, locked)

        # Tiny ESC hint bottom-right
        hint_a = int(70 + 50 * (0.5 + 0.5 * math.sin(self.elapsed * 1.8)))
        hint = self.small_font.render("[ ESC ] Return to Title", True, GOLD_DIM)
        hint.set_alpha(hint_a)
        screen.blit(hint, (1280 - hint.get_width() - 14, 720 - hint.get_height() - 6))

        # Fade-in veil (only for initial map appear)
        if self.fade_in < 1.0:
            veil = pygame.Surface((1280, 720), pygame.SRCALPHA)
            veil.fill((6, 4, 8, int((1.0 - self.fade_in) * 255)))
            screen.blit(veil, (0, 0))

    # ── Hotspot markers ───────────────────────────────────────────────────────

    def _draw_markers(self, screen):
        for i, reg in enumerate(REGIONS):
            sx, sy   = self._region_screen_pos(reg)
            hovered  = (i == self.hovered_idx)
            selected = (i == self.selected_idx)
            starter  = (i == self._starter_idx)
            color    = reg["color"]

            if selected:
                # LOCKED: bright static dot + slow steady ring + lock indicator ring
                pr = int(13 + 2 * math.sin(self.elapsed * 2.5))
                gs = pygame.Surface((pr * 4, pr * 4), pygame.SRCALPHA)
                pygame.draw.circle(gs, (*color, 90),  (pr * 2, pr * 2), pr * 2)
                pygame.draw.circle(gs, (*color, 255), (pr * 2, pr * 2), pr)
                screen.blit(gs, (sx - pr * 2, sy - pr * 2))
                # Outer lock ring (solid, not rippling)
                lock_r = self.hotspot_radius - 4
                lr_surf = pygame.Surface((lock_r * 2 + 4, lock_r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(lr_surf, (*color, 180), (lock_r + 2, lock_r + 2), lock_r, 2)
                screen.blit(lr_surf, (sx - lock_r - 2, sy - lock_r - 2))
                # Small "pinned" tick marks at 4 corners of the ring
                for ang in (45, 135, 225, 315):
                    rad = math.radians(ang)
                    tx = int(sx + lock_r * math.cos(rad))
                    ty = int(sy + lock_r * math.sin(rad))
                    pygame.draw.circle(screen, color, (tx, ty), 2)

            elif hovered:
                # HOVER: ripple rings + bright dot
                for ring in range(3):
                    rt = (self.ripple_t - ring * 0.35) % 1.4
                    if rt < 0:
                        continue
                    rr = int(self.hotspot_radius * 0.4 + rt * self.hotspot_radius * 1.8)
                    ra = max(0, int(210 * (1.0 - rt / 1.4)))
                    rs = pygame.Surface((rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA)
                    pygame.draw.circle(rs, (*color, ra), (rr + 2, rr + 2), rr, 2)
                    screen.blit(rs, (sx - rr - 2, sy - rr - 2))
                pr = int(12 + 3 * math.sin(self.elapsed * 4.0))
                gs = pygame.Surface((pr * 4, pr * 4), pygame.SRCALPHA)
                pygame.draw.circle(gs, (*color, 80),  (pr * 2, pr * 2), pr * 2)
                pygame.draw.circle(gs, (*color, 240), (pr * 2, pr * 2), pr)
                screen.blit(gs, (sx - pr * 2, sy - pr * 2))

            elif starter:
                # STARTER idle pulse
                pulse = 0.5 + 0.5 * math.sin(self.elapsed * 2.2)
                pr = int(9 + 2 * pulse)
                gs = pygame.Surface((pr * 4, pr * 4), pygame.SRCALPHA)
                pygame.draw.circle(gs, (*color, int(50 + 40 * pulse)), (pr * 2, pr * 2), pr * 2)
                pygame.draw.circle(gs, (*color, 200), (pr * 2, pr * 2), pr)
                screen.blit(gs, (sx - pr * 2, sy - pr * 2))

            else:
                # DORMANT: tiny dot
                dr = 6
                ds = pygame.Surface((dr * 4, dr * 4), pygame.SRCALPHA)
                pygame.draw.circle(ds, (*color, 30),  (dr * 2, dr * 2), dr * 2)
                pygame.draw.circle(ds, (*color, 110), (dr * 2, dr * 2), dr)
                screen.blit(ds, (sx - dr * 2, sy - dr * 2))

    # ── Info panel ────────────────────────────────────────────────────────────

    def _draw_info_panel(self, screen, region, region_sx, alpha_ratio, locked=False):
        """
        Auto-height panel on the opposite side of the screen from the active region.
        alpha_ratio (0→1) drives overall opacity.
        locked=True shows a small lock indicator in the panel header.
        Enter button for Sunfield lives at the bottom of this panel.
        """
        iw = PANEL_W - PAD * 2

        # Measure content height
        name_h    = self.body_font.get_height() + 6
        sub_h     = self.small_font.get_height() + 4
        divider_h = 10
        badge_h   = self.small_font.get_height() + 8
        lore_lines = _word_wrap(region["lore"], self.ui_font, iw)
        lh         = self.ui_font.get_linesize() + 2
        lore_h     = len(lore_lines) * lh + 4
        btn_h      = 36 + 10 if region.get("starter") else 0   # Enter button space

        PH = PAD + name_h + sub_h + divider_h + badge_h + lore_h + btn_h + PAD

        # Side: opposite to where the region is
        PX = MARGIN if region_sx > 640 else (1280 - PANEL_W - MARGIN)
        # Vertically centred, clamped
        PY = max(MARGIN, min(720 - PH - MARGIN, 360 - PH // 2))

        master_a = int(alpha_ratio * 255)

        # Background
        bg = pygame.Surface((PANEL_W, PH), pygame.SRCALPHA)
        bg.fill((4, 3, 7, int(alpha_ratio * 228)))
        screen.blit(bg, (PX, PY))

        # Border + corner accents
        bsf = pygame.Surface((PANEL_W, PH), pygame.SRCALPHA)
        border_a = int(alpha_ratio * 160)
        pygame.draw.rect(bsf, (*GOLD, border_a), (0, 0, PANEL_W, PH), 1)
        acc = 12
        for (a, b, c) in [
            ((0, 0),       (acc, 0),        (0, acc)),
            ((PANEL_W, 0), (PANEL_W-acc, 0),(PANEL_W, acc)),
            ((0, PH),      (acc, PH),       (0, PH-acc)),
            ((PANEL_W, PH),(PANEL_W-acc, PH),(PANEL_W, PH-acc)),
        ]:
            pygame.draw.line(bsf, (*GOLD, int(alpha_ratio * 210)), a, b, 2)
            pygame.draw.line(bsf, (*GOLD, int(alpha_ratio * 210)), a, c, 2)
        screen.blit(bsf, (PX, PY))

        # Helper: draw text at alpha
        def _blit_a(surf, x, y):
            surf.set_alpha(master_a)
            screen.blit(surf, (x, y))

        ix = PX + PAD
        iy = PY + PAD

        # Colour dot + name + [PINNED] badge when locked
        dot_a = int(alpha_ratio * 255)
        dot_surf = pygame.Surface((14, 24), pygame.SRCALPHA)
        pygame.draw.circle(dot_surf, (*region["color"], dot_a), (7, 12), 6)
        screen.blit(dot_surf, (ix, iy))
        name_s = self.body_font.render(region["name"], True, GOLD_LIGHT)
        _blit_a(name_s, ix + 20, iy)
        if locked:
            pin_s = self.small_font.render("[PINNED]", True, region["color"])
            pin_s.set_alpha(int(alpha_ratio * 180))
            screen.blit(pin_s, (PX + PANEL_W - PAD - pin_s.get_width(), iy + 4))
        iy += name_h

        _blit_a(self.small_font.render(region["subtitle"], True, GOLD_DIM), ix + 20, iy)
        iy += sub_h

        # Divider
        div_surf = pygame.Surface((PANEL_W - PAD * 2, 1), pygame.SRCALPHA)
        div_surf.fill((*GOLD_DIM, int(alpha_ratio * 160)))
        screen.blit(div_surf, (ix, iy))
        iy += divider_h

        # Status badge
        badge_col = (100, 210, 120) if region["status"] == "STARTER TOWN" else (160, 115, 50)
        _blit_a(self.small_font.render(f"[ {region['status']} ]", True, badge_col), ix, iy)
        iy += badge_h

        # Lore — full text, no clipping
        for line in lore_lines:
            _blit_a(self.ui_font.render(line, True, TEXT_COLOR), ix, iy)
            iy += lh

        # Enter button — only for Sunfield, inside the panel
        if region.get("starter"):
            iy += 6
            BW  = PANEL_W - PAD * 2
            BH  = 32
            bx  = PX + PAD
            by  = iy
            btn = pygame.Rect(bx, by, BW, BH)
            self.enter_btn_rect = btn

            mx, my = pygame.mouse.get_pos()
            hov    = btn.collidepoint(mx, my)
            pulse  = 0.5 + 0.5 * math.sin(self.elapsed * 3.0)

            # Button background
            bb = pygame.Surface((BW, BH), pygame.SRCALPHA)
            btn_bg_a = int(alpha_ratio * (235 if hov else 210))
            bb.fill((32, 22, 4, btn_bg_a) if hov else (10, 7, 1, btn_bg_a))
            screen.blit(bb, (bx, by))

            # Border
            border_col = GOLD_LIGHT if hov else GOLD
            bc = (*border_col, int(alpha_ratio * 255))
            bs2 = pygame.Surface((BW, BH), pygame.SRCALPHA)
            pygame.draw.rect(bs2, bc, (0, 0, BW, BH), 1)
            screen.blit(bs2, (bx, by))

            # Label
            lbl = self.ui_font.render(">> Enter Sunfield <<", True, GOLD_LIGHT if hov else GOLD)
            lbl.set_alpha(master_a)
            screen.blit(lbl, (btn.centerx - lbl.get_width() // 2,
                               btn.centery - lbl.get_height() // 2))

            # Hover outer glow
            if hov and alpha_ratio > 0.8:
                ga = int(30 + pulse * 25)
                gs2 = pygame.Surface((BW + 16, BH + 16), pygame.SRCALPHA)
                pygame.draw.rect(gs2, (*GOLD, ga), (0, 0, BW + 16, BH + 16), 3)
                screen.blit(gs2, (bx - 8, by - 8))
        else:
            self.enter_btn_rect = pygame.Rect(0, 0, 0, 0)

        # Dismiss hint at very bottom of panel (shown only when locked)
        if locked:
            iy += BH + 6 if region.get("starter") else 8
            hint_s = self.small_font.render("Click dot again to close", True, GOLD_DIM)
            hint_s.set_alpha(int(alpha_ratio * 120))
            screen.blit(hint_s, (PX + PANEL_W // 2 - hint_s.get_width() // 2,
                                  PY + PH - hint_s.get_height() - 4))

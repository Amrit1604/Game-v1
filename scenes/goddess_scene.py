import os
import pygame
import math
import random
import threading
from groq import Groq
from scene_manager import Scene
from ui.fantasy_frame import FantasyFrame
from ui.particle_system import ParticleSystem
from scenes.world_scene import WorldScene
from ui.text_box import TextBox

# Theme Colors
GOLD = (201, 168, 76)
GOLD_LIGHT = (240, 208, 128)
GOLD_DIM = (122, 96, 48)
PURPLE_LIGHT = (176, 127, 208)
VOID_BG = (6, 4, 8)
TEXT = (232, 223, 200)
TEXT_DIM = (138, 122, 96)
DANGER = (192, 64, 64)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

class GoddessScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.width, self.height = pygame.display.get_surface().get_size()
        
        self.goddess_img = None
        try: self.goddess_img = pygame.image.load("assets/sprites/goddess.png").convert_alpha()
        except: pass
            
        self.frame_rect = pygame.Rect(self.width//2 - 512, self.height//2 - 279, 1024, 559)
        self.frame = FantasyFrame(self.frame_rect, image_path="assets/ui/frameRec.png")
        self.particles = ParticleSystem()
        self.particles.color = GOLD_DIM
        
        self.title_font = pygame.font.SysFont("palatino, georgia", 58, bold=True)
        self.q_font = pygame.font.SysFont("palatino, georgia", 30, italic=True)
        self.dialogue_font = pygame.font.SysFont("palatino, georgia", 24)
        self.hint_font = pygame.font.SysFont("palatino, georgia", 18)
        self.btn_font = pygame.font.SysFont("georgia", 16)
        self.class_title_font = pygame.font.SysFont("palatino, georgia", 36, bold=True)
        
        self.phase = "void" # Skip death_screen as requested
        
        self.timer = 0.0
        self.phase_timer = 0.0
        
        self.blink_alpha = 0.0
        self.blink_state = "none"

        self.text_input = TextBox(pygame.Rect(0, 0, 600, 50), font_size=28)
        self.text_input.rect.center = (self.width//2, self.height//2 + 50)
        
        self.player_profile = {
            "cause_of_death": "",
            "name": "",
            "dob": "",
            "gender": "Male" # Default, then space to toggle
        }
        
        self.identity_step = "name" # name -> dob -> gender
        self.gender_options = ["Male", "Female", "Other"]
        self.gender_idx = 0
        
        self.judgment_data = {"done": False, "raw": "", "error": ""}
        self.goddess_lines = []
        self.printed_lines = []
        self.dialogue_idx = 0
        self.char_idx = 0
        
        self.class_choices = []
        self.selected_class_idx = 0
        self.opt_font = pygame.font.SysFont("palatino, georgia", 25)
        
        self.assigned_world = ""
        self.worlds = ["THE SHADOW REALM", "THE ELYSIAN FIELDS", "THE DRAGON PEAKS", "THE ABYSSAL DEPTHS", "THE CHRONOS WASTES"]

    def draw_divine_panel(self, surface, rect, selected=False, opacity=230):
        # Draw background
        bg = pygame.Surface(rect.size, pygame.SRCALPHA)
        bg.fill((6, 4, 8, opacity)) 
        surface.blit(bg, rect.topleft)
        
        # Border
        border_color = GOLD if selected else GOLD_DIM
        pygame.draw.rect(surface, border_color, rect, width=1)
        
        # Corner brackets (top-left, bottom-right)
        bracket_color = GOLD
        l, t = 16, 2
        # Top-left
        pygame.draw.rect(surface, bracket_color, (rect.left - 1, rect.top - 1, l, t))
        pygame.draw.rect(surface, bracket_color, (rect.left - 1, rect.top - 1, t, l))
        # Bottom-right
        pygame.draw.rect(surface, bracket_color, (rect.right - l + 1, rect.bottom - t + 1, l, t))
        pygame.draw.rect(surface, bracket_color, (rect.right - t + 1, rect.bottom - l + 1, t, l))
        
        if selected:
            # Subtle glow effect center top highlight overlay
            overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.circle(overlay, (201, 168, 76, 20), (rect.width//2, 0), rect.width)
            surface.blit(overlay, rect.topleft)

    def _wrap_text(self, text, font, max_width):
        words = text.split()
        if not words: return [""]
        lines = []
        current = words[0]
        for word in words[1:]:
            if font.size(f"{current} {word}")[0] <= max_width:
                current += " " + word
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def fetch_judgment(self):
        client = Groq(api_key=GROQ_API_KEY)
        sys_prompt = "You are a Goddess of Reincarnation. Speak concisely, with divine authority."
        user_prompt = f"""
Name: {self.player_profile['name']}
DOB: {self.player_profile['dob']}
Gender: {self.player_profile['gender']}
Cause of death: {self.player_profile['cause_of_death']}

In 2 sentences, deliver your judgment to them.
Then pick EXACTLY TWO distinct game classes from this list depending on how they died: 
Swordsman, Archer, Tank, Mage, Assassin, Healer, Necromancer, Summoner, Samurai, Monk, Gunslinger, Beastmaster, Dragon Knight, Time Mage, Alchemist, Bard. 

Format EXACTLY like this:
[JUDGMENT]
<your 2 sentence speech>
[CLASS 1]
<ClassName1>
Strengths: <...strengths...>
Weaknesses: <...weaknesses...>
[CLASS 2]
<ClassName2>
Strengths: <...strengths...>
Weaknesses: <...weaknesses...>
"""
        def fallback():
            self.judgment_data["raw"] = "[JUDGMENT]\nYou lived an unremarkable life. Your death was unfortunate, but not meaningless.\n[CLASS 1]\nSwordsman\nStrengths: Basic power.\nWeaknesses: Average.\n[CLASS 2]\nMage\nStrengths: Magic.\nWeaknesses: Fragile."
            self.judgment_data["done"] = True

        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.3-70b-versatile"
            )
            self.judgment_data["raw"] = response.choices[0].message.content
        except Exception as e:
            self.judgment_data["error"] = str(e)
            fallback()
            return
            
        self.judgment_data["done"] = True

    def process_judgment_text(self):
        text = self.judgment_data["raw"]
        speech = ""
        current_class = None
        mode = "none"
        
        for line in text.split('\n'):
            line = line.strip()
            if not line: continue
            if "[JUDGMENT]" in line.upper():
                mode = "speech"
                continue
            elif "[CLASS 1]" in line.upper():
                mode = "c1_name"
                continue
            elif "[CLASS 2]" in line.upper():
                if current_class: self.class_choices.append(current_class)
                mode = "c2_name"
                current_class = {}
                continue
                
            if mode == "speech":
                speech += line + " "
            elif mode == "c1_name":
                current_class = {"name": line.replace("*", "").strip(), "strengths": "", "weaknesses": ""}
                mode = "c1_stats"
            elif mode == "c2_name":
                current_class = {"name": line.replace("*", "").strip(), "strengths": "", "weaknesses": ""}
                mode = "c2_stats"
            elif mode in ("c1_stats", "c2_stats"):
                line_lower = line.lower()
                if "strength" in line_lower:
                    current_class["strengths"] = line.split(":", 1)[-1].strip()
                elif "weakness" in line_lower:
                    current_class["weaknesses"] = line.split(":", 1)[-1].strip()
                    
        if current_class:
            self.class_choices.append(current_class)
            
        if len(self.class_choices) < 2:
            self.class_choices = [
                {"name": "Swordsman", "strengths": "Average Strength", "weaknesses": "None"},
                {"name": "Mage", "strengths": "Average Magic", "weaknesses": "Squishy"}
            ]
        
        return speech

    def change_phase(self, new_phase):
        self.phase = new_phase
        self.phase_timer = 0.0
        self.text_input.text = ""

    def trigger_blink(self, target_phase, speed=800):
        if self.blink_state == "none":
            self.blink_state = "fade_out"
            self.blink_alpha = 0.0
            self.blink_target = target_phase
            self.blink_speed = speed

    def update(self, dt):
        self.timer += dt
        self.phase_timer += dt
        self.particles.update(dt, pygame.Rect(0, 0, self.width, self.height))
        self.text_input.update(dt)

        if self.blink_state == "fade_out":
            self.blink_alpha += dt * self.blink_speed
            if self.blink_alpha >= 255:
                self.blink_alpha = 255
                self.blink_state = "fade_in"
                self.change_phase(self.blink_target)
        
        elif self.blink_state == "fade_in":
            self.blink_alpha -= dt * self.blink_speed
            if self.blink_alpha <= 0:
                self.blink_alpha = 0
                self.blink_state = "none"

        # SCENE 2: Void -> Cause of Death
        if self.phase == "void" and self.phase_timer > 3.0 and self.blink_state == "none":
            self.trigger_blink("cause_of_death", speed=400)
            
        # SCENE 5: Data Processing -> Goddess
        elif self.phase == "data_processing":
            if self.judgment_data["done"] and self.phase_timer > 4.0 and self.blink_state == "none":
                # Prep dialogue
                self.goddess_lines = [
                    "Welcome, mortal.",
                    "I have reviewed your life.",
                ]
                
                # Fetch raw judgment, parse out the classes, and get the clean speech string
                built_speech = self.process_judgment_text()
                
                # Wrap text dynamically based on screen width
                max_w = min(800, self.width - 100) - 60
                wrapped = self._wrap_text(built_speech.strip(), self.dialogue_font, max_w)
                self.goddess_lines.extend(wrapped)
                
                self.trigger_blink("goddess_appears", speed=200) # Bright flash

        # SCENE 6: Goddess Appears -> AI Judgment
        elif self.phase == "goddess_appears":
            if self.phase_timer > 2.0 and self.blink_state == "none":
                self.change_phase("ai_judgment")
                self.dialogue_idx = 0
                self.char_idx = 0
                self.printed_lines = [""]
                
        # SCENE 7: AI Judgment typing logic
        elif self.phase == "ai_judgment":
            # type line by line
            if self.dialogue_idx < len(self.goddess_lines):
                target_str = self.goddess_lines[self.dialogue_idx]
                if self.char_idx < len(target_str):
                    self.char_idx += dt * 30.0 # typing speed
                    idx = min(int(self.char_idx), len(target_str))
                    self.printed_lines[-1] = target_str[:idx]
                else:
                    # Line finished waiting
                    if self.phase_timer > 1.5:
                        self.dialogue_idx += 1
                        self.char_idx = 0
                        self.phase_timer = 0.0
                        if self.dialogue_idx < len(self.goddess_lines):
                            self.printed_lines.append("")
            else:
                if self.phase_timer > 2.0 and self.blink_state == "none":
                    # Transition to offering the classes instead of going right to world assignment
                    self.change_phase("class_selection")
                    
        # SCENE 7b: Class Selection
        elif self.phase == "class_selection":
            if self.phase_timer > 0.0:
                pass # wait for user to press ENTER in handle_event

        # SCENE 8: World Assignment
        elif self.phase == "world_assignment":
            if self.phase_timer > 4.0 and self.blink_state == "none": # Wait 2s for world, then let them read
                self.trigger_blink("reincarnation_prep", speed=200)
                
        # SCENE 9: Reincarnation Prep -> World Scene
        elif self.phase == "reincarnation_prep":
            if self.phase_timer > 3.0 and self.blink_state == "none":
                # White transition inside world scene or switch directly
                self.manager.change_scene(WorldScene(self.manager))


    def draw(self, screen):
        # Background
        screen.fill(VOID_BG)

        # Particles
        if self.phase in ("void", "cause_of_death", "identity_form", "data_processing"):
            # Floating subtle particles
            self.particles.draw(screen)

        if self.phase == "void":
            # Just dark empty space playing particles, then glowing interface starts to form
            pass # We removed frame so we just show void
            
        elif self.phase == "cause_of_death":
            panel_w, panel_h = max(600, min(800, self.width - 60)), 200
            panel_rect = pygame.Rect(self.width//2 - panel_w//2, self.height//2 - panel_h//2, panel_w, panel_h)
            self.draw_divine_panel(screen, panel_rect)

            lbl = self.btn_font.render("DESCRIBE HOW YOU DIED", True, GOLD)
            screen.blit(lbl, (self.width//2 - lbl.get_width()//2, panel_rect.top + 30))

            self.text_input.rect.width = panel_w - 60
            self.text_input.rect.center = panel_rect.center
            self.text_input.draw(screen)
            
            if self.text_input.text.strip():
                hint = self.btn_font.render("[ ENTER ] TO CONTINUE", True, GOLD_DIM)
                screen.blit(hint, (self.width//2 - hint.get_width()//2, panel_rect.bottom - 40))

        elif self.phase == "identity_form":
            panel_w, panel_h = max(560, min(700, self.width - 60)), 220
            panel_rect = pygame.Rect(self.width//2 - panel_w//2, self.height//2 - panel_h//2, panel_w, panel_h)
            self.draw_divine_panel(screen, panel_rect)

            texts = {"name": "ENTER YOUR NAME", "dob": "ENTER DATE OF BIRTH", "gender": "SELECT GENDER"}
            lbl = self.btn_font.render(texts[self.identity_step], True, GOLD)
            screen.blit(lbl, (self.width//2 - lbl.get_width()//2, panel_rect.top + 30))

            if self.identity_step != "gender":
                self.text_input.rect.width = panel_w - 60
                self.text_input.rect.center = panel_rect.center
                self.text_input.draw(screen)
                if self.text_input.text.strip():
                    hint = self.btn_font.render("[ ENTER ] TO SUBMIT", True, GOLD_DIM)
                    screen.blit(hint, (self.width//2 - hint.get_width()//2, panel_rect.bottom - 40))
            else:
                for i, opt in enumerate(self.gender_options):
                    is_sel = (i == self.gender_idx)
                    opt_color = GOLD_LIGHT if is_sel else TEXT_DIM
                    pre = ">>>  " if is_sel else "      "
                    g_txt = self.dialogue_font.render(f"{pre}{opt}", True, opt_color)
                    y_pos = panel_rect.top + 70 + (i * 35)
                    screen.blit(g_txt, (self.width//2 - 60, y_pos))

                hint = self.btn_font.render("[ ARROWS ] TOGGLE   |   [ ENTER ] SUBMIT", True, GOLD_DIM)
                screen.blit(hint, (self.width//2 - hint.get_width()//2, panel_rect.bottom - 40))
        elif self.phase == "data_processing":
            t = pygame.time.get_ticks() * 0.002
            # Darken screen effect
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            lbl = self.q_font.render("Analyzing life data...", True, PURPLE_LIGHT)
            lbl.set_alpha(150 + int(math.sin(t*3)*100))
            screen.blit(lbl, (self.width//2 - lbl.get_width()//2, self.height//2))
            
            # Rotating symbols
            cx, cy = self.width//2, self.height//2 - 60
            for i in range(3):
                ang = t + i * (math.pi * 2 / 3)
                px = cx + math.cos(ang) * 40
                py = cy + math.sin(ang) * 40
                pygame.draw.circle(screen, GOLD, (int(px), int(py)), 4)

        elif self.phase in ("goddess_appears", "ai_judgment", "class_selection", "world_assignment"):
            # White light logic / goddess image
            if self.goddess_img:
                screen.blit(self.goddess_img, (self.width//2 - self.goddess_img.get_width()//2, self.height//2 - self.goddess_img.get_height()//2 - 50))
            
            if self.phase == "goddess_appears":
                pass # Just silent appearance
                
            elif self.phase == "ai_judgment" or self.phase == "class_selection":
                panel_w = min(800, self.width - 60)
                
                # Dynamically resize the judgment box if text is taking up too much room
                num_lines = len(self.printed_lines) + 2 
                req_h = 80 + (num_lines * (self.dialogue_font.get_height() + 8))
                panel_h = max(220, req_h)
                
                panel_rect = pygame.Rect(self.width//2 - panel_w//2, max(20, min(80, self.height//2 - panel_h)), panel_w, panel_h)
                self.draw_divine_panel(screen, panel_rect)

                # Speaker label
                speaker = self.btn_font.render("DIVINE VOICE", True, GOLD)
                screen.blit(speaker, (panel_rect.left + 20, panel_rect.top + 15))
                pygame.draw.line(screen, GOLD_DIM, (panel_rect.left + 20 + speaker.get_width() + 10, panel_rect.top + 23), (panel_rect.right - 20, panel_rect.top + 23))

                y = panel_rect.y + 50
                for line in self.printed_lines:
                    txt = self.dialogue_font.render(line, True, TEXT)
                    screen.blit(txt, (panel_rect.left + 30, y))
                    y += txt.get_height() + 8

                # Render the 2 choices during class selection
                if self.phase == "class_selection" and len(self.class_choices) >= 2:
                    card_w = min(400, (self.width//2) - 30)
                    gap = 40
                    total_w = card_w * 2 + gap
                    x_start = self.width//2 - total_w // 2
                    
                    for i in range(2):
                        c_data = self.class_choices[i]
                        
                        # Calculate heights dynamically so we don't bleed out of cards
                        sw_lines = self._wrap_text(c_data['strengths'], self.btn_font, card_w - 50)
                        ww_lines = self._wrap_text(c_data['weaknesses'], self.btn_font, card_w - 50)
                        req_card_height = 80 + (len(sw_lines) + len(ww_lines)) * 20 + 30
                        card_h = max(230, req_card_height)
                        
                        y_start = self.height - card_h - 40
                        
                        rect = pygame.Rect(x_start + i*(card_w + gap), y_start, card_w, card_h)
                        is_sel = (i == self.selected_class_idx)

                        self.draw_divine_panel(screen, rect, selected=is_sel)

                        # Fix giant overlapping title font
                        cname = self.class_title_font.render(c_data["name"].upper(), True, GOLD_LIGHT if is_sel else GOLD)
                        # Fix name going out of cards horizontally by scaling down if too big
                        if cname.get_width() > card_w - 20:
                            cname = pygame.transform.smoothscale(cname, (card_w - 20, int(cname.get_height() * ((card_w - 20) / cname.get_width()))))
                        screen.blit(cname, (rect.centerx - cname.get_width()//2, rect.y + 15))

                        wy = rect.y + 60
                        s_lab = self.btn_font.render("STR: ", True, (150, 255, 150))
                        screen.blit(s_lab, (rect.x + 15, wy))
                        for l in sw_lines:
                            stxt = self.btn_font.render(l, True, TEXT)
                            screen.blit(stxt, (rect.x + 15 + s_lab.get_width(), wy))
                            wy += 20

                        wy += 10
                        w_lab = self.btn_font.render("WEAK: ", True, (255, 150, 150))
                        screen.blit(w_lab, (rect.x + 15, wy))
                        for l in ww_lines:
                            stxt = self.btn_font.render(l, True, TEXT)
                            screen.blit(stxt, (rect.x + 15 + w_lab.get_width(), wy))
                            wy += 20

                    hint = self.btn_font.render("[ LEFT / RIGHT ] TO SELECT CLASS    |   [ ENTER ] TO ACCEPT DESTINY", True, GOLD_DIM)
                    screen.blit(hint, (self.width//2 - hint.get_width()//2, self.height - 20))
            elif self.phase == "world_assignment":
                lbl = self.q_font.render("I will now assign your next world.", True, GOLD_LIGHT)
                screen.blit(lbl, (self.width//2 - lbl.get_width()//2, self.height//2 + 80))
                
                if self.phase_timer > 2.0:
                    lbl2 = self.btn_font.render("YOU WILL BE REBORN IN:", True, GOLD_DIM)
                    screen.blit(lbl2, (self.width//2 - lbl2.get_width()//2, self.height//2 + 140))
                    
                    w_txt = self.title_font.render(self.assigned_world, True, GOLD_LIGHT)
                    # Pulse effect
                    w_txt.set_alpha(155 + int(math.sin(self.phase_timer * 5) * 100))
                    screen.blit(w_txt, (self.width//2 - w_txt.get_width()//2, self.height//2 + 190))

        elif self.phase == "reincarnation_prep":
            lbl = self.q_font.render("Preparing reincarnation...", True, GOLD_DIM)
            screen.blit(lbl, (self.width//2 - lbl.get_width()//2, self.height//2 - 40))
            
            if self.phase_timer > 1.5:
                lbl2 = self.btn_font.render("LOADING...", True, GOLD)
                screen.blit(lbl2, (self.width//2 - lbl2.get_width()//2, self.height//2 + 20))


        # Blink Overlay
        if self.blink_alpha > 0:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # If transitioning to Goddess or Reinc, use white flash
            color = (255, 255, 255) if getattr(self, "blink_target", "") in ("goddess_appears", "reincarnation_prep") else (0, 0, 0)
            overlay.fill((*color, int(self.blink_alpha)))
            screen.blit(overlay, (0, 0))

    def handle_event(self, event):
        if self.blink_state != "none": return
        
        self.text_input.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if self.phase == "cause_of_death":
                if event.key == pygame.K_RETURN and len(self.text_input.text.strip()) > 0:
                    self.player_profile["cause_of_death"] = self.text_input.text.strip()
                    self.trigger_blink("identity_form")
            
            elif self.phase == "identity_form":
                if self.identity_step == "name":
                    if event.key == pygame.K_RETURN and len(self.text_input.text.strip()) > 0:
                        self.player_profile["name"] = self.text_input.text.strip()
                        self.text_input.text = ""
                        self.identity_step = "dob"
                elif self.identity_step == "dob":
                    if event.key == pygame.K_RETURN and len(self.text_input.text.strip()) > 0:
                        self.player_profile["dob"] = self.text_input.text.strip()
                        self.text_input.text = ""
                        self.identity_step = "gender"
                elif self.identity_step == "gender":
                    if event.key in (pygame.K_LEFT, pygame.K_UP):
                        self.gender_idx = (self.gender_idx - 1) % len(self.gender_options)
                    elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                        self.gender_idx = (self.gender_idx + 1) % len(self.gender_options)
                    elif event.key == pygame.K_RETURN:
                        self.player_profile["gender"] = self.gender_options[self.gender_idx]

                        # Generate world
                        self.assigned_world = random.choice(self.worlds)

                        # Trigger processing
                        self.trigger_blink("data_processing", speed=400)
                        threading.Thread(target=self.fetch_judgment, daemon=True).start()
            
            elif self.phase == "class_selection":
                if event.key == pygame.K_LEFT:
                    self.selected_class_idx = 0
                elif event.key == pygame.K_RIGHT:
                    self.selected_class_idx = 1
                elif event.key == pygame.K_RETURN:
                    self.player_profile["class"] = self.class_choices[self.selected_class_idx]
                    self.trigger_blink("world_assignment", speed=400)
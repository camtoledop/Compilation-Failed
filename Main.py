import math
import random
import sys
from pathlib import Path
import pygame
from abc import ABC, abstractmethod

# 1. ENCAPSULAMIENTO Y ABSTRACCIÓN
class AssetManager:
    """Encapsula la carga, el almacenamiento y el acceso a los recursos multimedia."""
    def __init__(self):
        self._base_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
        self._sounds = {}
        self._images = {}
        self._fonts = {}
        self._characters_expressions = {}
        self.all_characters = []
        
        self._init_sounds()
        self._init_images()
        self._init_expressions()
        self._init_fonts()

    def _init_sounds(self):
        sounds_map = {
            "btn": "iniciarjuego.mp3",
            "select": "seleccion.mp3",
            "countdown": "321.mp3",
            "juego": "juego.mp3",
            "winner": "ganador.mp3"
        }
        for key, filename in sounds_map.items():
            try:
                self._sounds[key] = pygame.mixer.Sound(str(self._base_dir / "sounds" / filename))
            except Exception as e:
                print(f"Error cargando sonido {key}: {e}")
                self._sounds[key] = None

    def _init_images(self):
        images_map = {
            "title": "titulo.png",
            "btn_start": "iniciar_juego.png",
            "btn_exit": "salir_del_juego.png",
            "btn_inicio": "inicio.png",
            "personajes_portada": "personjes_portada.png",
            "compu": "compu.png",
            "btn_up": "botonarriba.png",
            "btn_down": "botonabajo2.png"
        }
        for key, filename in images_map.items():
            try:
                self._images[key] = pygame.image.load(str(self._base_dir / "images" / filename)).convert_alpha()
            except Exception as e:
                print(f"Error cargando imagen {key}: {e}")
                self._images[key] = None

    def _init_expressions(self):
        expression_mapping = {
            "neutral": ["personaje_1.png", "personaje_2.png", "personaje_3.png", "personaje_4.png"],
            "alivio": ["alivio1.png", "alivio2.png", "alivio3.png", "alivio4.png"],
            "anticipacion": ["anticipacion1.png", "anticipacion2.png", "anticipacion3.png", "anticipacion4.png"],
            "crouch": ["crouch1.png", "crouch2.png", "crouch3.png", "crouch4.png"],
            "euforico": ["euforico1.png", "euforico2.png", "euforico3.png", "euforico4.png"],
            "peakjoy": ["peakjoy1.png", "peakjoy2.png", "peakjoy3.png", "peakjoy4.png"],
            "tristeza": ["tristeza1.png", "tristeza2.png", "tristeza3.png", "tristeza4.png"],
        }
        
        for char_id in range(1, 5):
            self._characters_expressions[char_id] = {}
            idx = char_id - 1
            for exp_name, file_list in expression_mapping.items():
                filename = file_list[idx]
                path = self._base_dir / "images" / filename
                if path.exists():
                    img = pygame.image.load(str(path)).convert_alpha()
                    bbox = img.get_bounding_rect()
                    sub_img = img.subsurface(bbox) if bbox.height > 0 else img
                    target_height = 185
                    orig_rect = sub_img.get_rect()
                    scale_factor = target_height / orig_rect.height
                    new_width = int(orig_rect.width * scale_factor)
                    img_scaled = pygame.transform.smoothscale(sub_img, (new_width, target_height))
                    canvas = pygame.Surface((200, 200), pygame.SRCALPHA)
                    draw_x = (200 - new_width) // 2
                    draw_y = 200 - target_height
                    canvas.blit(img_scaled, (draw_x, draw_y))
                    self._characters_expressions[char_id][exp_name] = canvas
                else:
                    if "neutral" in self._characters_expressions[char_id]:
                        self._characters_expressions[char_id][exp_name] = self._characters_expressions[char_id]["neutral"]
                    else:
                        self._characters_expressions[char_id][exp_name] = pygame.Surface((200, 200), pygame.SRCALPHA)
        
        names = ["Camila", "José", "Angelo", "Abelardo"]
        for i in range(1, 5):
            self.all_characters.append({
                "id": i,
                "name": names[i-1],
                "image": self._characters_expressions[i]["neutral"]
            })

    def _init_fonts(self):
        font_head, font_body = "Impact", "Consolas"
        try:
            self._fonts["giant"] = pygame.font.SysFont(font_head, 110)
            self._fonts["title"] = pygame.font.SysFont(font_head, 40)
            self._fonts["timer"] = pygame.font.SysFont(font_head, 48, bold=True)
            self._fonts["winner"] = pygame.font.SysFont(font_head, 42)
            self._fonts["sala_title"] = pygame.font.SysFont(font_head, 34)
            self._fonts["medium"] = pygame.font.SysFont(font_body, 20, bold=True)
            self._fonts["small"] = pygame.font.SysFont(font_body, 14, bold=True)
        except Exception:
            self._fonts["giant"] = pygame.font.Font(None, 110)
            self._fonts["title"] = pygame.font.Font(None, 40)
            self._fonts["timer"] = pygame.font.Font(None, 48)
            self._fonts["winner"] = pygame.font.Font(None, 42)
            self._fonts["sala_title"] = pygame.font.Font(None, 34)
            self._fonts["medium"] = pygame.font.Font(None, 20)
            self._fonts["small"] = pygame.font.Font(None, 14)

    def play_sound(self, sound_key, loops=0, volume=1.0):
        snd = self._sounds.get(sound_key)
        if snd:
            snd.set_volume(volume)
            snd.play(loops)

    def stop_sound(self, sound_key):
        snd = self._sounds.get(sound_key)
        if snd:
            snd.stop()

    def set_sound_volume(self, sound_key, volume):
        snd = self._sounds.get(sound_key)
        if snd:
            snd.set_volume(volume)

    def get_img(self, key): return self._images.get(key)
    def get_font(self, key): return self._fonts.get(key)
    def get_expressions(self, char_id): return self._characters_expressions.get(char_id)

class Player:
    """Abstracción y encapsulamiento de la lógica del jugador."""
    def __init__(self, key_binding, side_name):
        self.key_binding = key_binding
        self.side_name = side_name
        self.choice = None
        self.score = 0
        self.button_timer = 0

    def reset(self):
        self.choice = None
        self.score = 0
        self.button_timer = 0

    @property
    def name(self):
        return self.choice["name"] if self.choice else "Player"

class ParticleSystem:
    """Encapsula la creación y actualización de partículas en pantalla."""
    def __init__(self, width, height, count=60):
        self.width = width
        self.height = height
        self.particles = []
        for _ in range(count):
            self.particles.append({
                "x": random.randint(0, width),
                "y": random.randint(0, height),
                "radius": random.randint(2, 6),
                "speed": random.uniform(1, 3),
                "color": random.choice([(255, 0, 128), (0, 255, 255), (255, 255, 0), (128, 0, 255)])
            })

    def update(self):
        for p in self.particles:
            p["y"] -= p["speed"]
            if p["y"] < 0:
                p["y"] = self.height
                p["x"] = random.randint(0, self.width)

    def draw(self, screen):
        for p in self.particles:
            pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["radius"])

# 2. HERENCIA Y POLIMORFISMO 
class Scene(ABC):
    """Clase base abstracta. Establece el contrato (Polimorfismo) para las escenas."""
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def handle_events(self, events): pass

    @abstractmethod
    def update(self): pass

    @abstractmethod
    def draw(self, screen): pass

    def draw_arcade_background(self, screen):
        screen.fill((15, 10, 35))
        for y in range(0, self.game.height, 20):
            alpha_val = int(25 * (y / self.game.height))
            surf = pygame.Surface((self.game.width, 20), pygame.SRCALPHA)
            surf.fill((255, 0, 128, alpha_val))
            screen.blit(surf, (0, y))
        self.game.particles.draw(screen)

    def draw_button(self, screen, rect, img, bg_color, text, is_pressed):
        offset = 3 if is_pressed else 0
        if img:
            scaled = pygame.transform.smoothscale(img, (rect.width, rect.height))
            screen.blit(scaled, (rect.x, rect.y + offset))
        else:
            pygame.draw.rect(screen, bg_color, (rect.x, rect.y + offset, rect.width, rect.height), border_radius=15)

class StartScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.btn_start = pygame.Rect((game.width // 2) - 125 + 5, 480, 250, 100)
        self.btn_exit = pygame.Rect((game.width // 2) - 125 + 5, 550, 250, 100)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_start.collidepoint(event.pos):
                    self.game.assets.play_sound("btn")
                    self.game.reset_players()
                    self.game.change_scene(MenuScene(self.game))
                elif self.btn_exit.collidepoint(event.pos):
                    self.game.assets.play_sound("btn")
                    pygame.time.wait(400)
                    self.game.running = False

    def update(self): pass

    def draw(self, screen):
        self.draw_arcade_background(screen)
        
        img_title = self.game.assets.get_img("title")
        if img_title:
            scaled_title = pygame.transform.smoothscale(img_title, (1050, 400))
            screen.blit(scaled_title, scaled_title.get_rect(center=(self.game.width // 2, 250)))
            
        img_portada = self.game.assets.get_img("personajes_portada")
        if img_portada:
            scaled_portada = pygame.transform.smoothscale(img_portada, (550, 700))
            screen.blit(scaled_portada, scaled_portada.get_rect(center=(self.game.width // 2, 400)))

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        self.draw_button(screen, self.btn_start, self.game.assets.get_img("btn_start"), (0, 200, 100), "INICIAR JUEGO", mouse_click and self.btn_start.collidepoint(mouse_pos))
        self.draw_button(screen, self.btn_exit, self.game.assets.get_img("btn_exit"), (200, 50, 50), "SALIR DEL JUEGO", mouse_click and self.btn_exit.collidepoint(mouse_pos))

class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.selecting_turn = 1
        self.delay_timer = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and self.selecting_turn in (1, 2):
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    idx = event.key - pygame.K_1
                    chosen = self.game.assets.all_characters[idx]
                    
                    if self.selecting_turn == 1:
                        self.game.p1.choice = chosen
                        self.game.assets.play_sound("select")
                        self.selecting_turn = 2
                    elif self.selecting_turn == 2:
                        if chosen["id"] != self.game.p1.choice["id"]:
                            self.game.p2.choice = chosen
                            self.game.assets.play_sound("select")
                            self.selecting_turn = 3
                            self.delay_timer = 60

    def update(self):
        if self.selecting_turn == 3:
            if self.delay_timer > 0:
                self.delay_timer -= 1
            else:
                self.game.change_scene(CountdownScene(self.game))

    def draw(self, screen):
        self.draw_arcade_background(screen)
        
        font_title = self.game.assets.get_font("title")
        title = font_title.render("SELECCIÓN DE PERSONAJES", True, (0, 255, 255))
        screen.blit(title, (self.game.width // 2 - title.get_width() // 2, 25))
        
        if self.selecting_turn == 1:
            txt = "TURNO J1: Elige personaje [Presiona 1, 2, 3 o 4]"
            color = (255, 255, 0)
        elif self.selecting_turn == 2:
            txt = f"¡J1 eligió a {self.game.p1.name}! | TURNO J2"
            color = (255, 0, 128)
        else:
            txt = "¡SELECCIÓN COMPLETADA!"
            color = (255, 255, 0)
            
        turn_text = self.game.assets.get_font("medium").render(txt, True, color)
        screen.blit(turn_text, (self.game.width // 2 - turn_text.get_width() // 2, 80))
        
        card_w, card_h = 260, 480
        start_x = (self.game.width - (4 * card_w + 3 * 20)) // 2
        for i, c in enumerate(self.game.assets.all_characters):
            cx = start_x + i * (card_w + 20)
            cy = 135
            rect = pygame.Rect(cx, cy, card_w, card_h)
            
            is_chosen = (self.game.p1.choice and self.game.p1.choice["id"] == c["id"]) or \
                        (self.game.p2.choice and self.game.p2.choice["id"] == c["id"])
            
            bg_card = (20, 60, 40) if is_chosen else (40, 20, 60)
            border_col = (0, 255, 128) if is_chosen else (128, 0, 255)
            
            pygame.draw.rect(screen, bg_card, rect, border_radius=15)
            pygame.draw.rect(screen, border_col, rect, 4, border_radius=15)
            
            num_surf = font_title.render(f"[{i+1}]", True, (255, 255, 0))
            screen.blit(num_surf, (cx + card_w // 2 - num_surf.get_width() // 2, cy + 15))
            
            menu_img = self.game.assets.get_expressions(c["id"])["neutral"]
            screen.blit(menu_img, menu_img.get_rect(center=(cx + card_w // 2, cy + 200)))
            
            name_surf = font_title.render(c["name"], True, (255, 255, 255))
            screen.blit(name_surf, (cx + card_w // 2 - name_surf.get_width() // 2, cy + 370))
            
            if is_chosen:
                status = self.game.assets.get_font("medium").render("INICIO", True, (0, 255, 128))
                screen.blit(status, (cx + card_w // 2 - status.get_width() // 2, cy + 425))

class CountdownScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.timer = 180
        self.game.assets.play_sound("countdown")

    def handle_events(self, events): pass

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.game.change_scene(PlayScene(self.game))

    def draw(self, screen):
        self.draw_arcade_background(screen)
        
        font_title = self.game.assets.get_font("sala_title")
        title = font_title.render("¡SALA DE BATALLA LISTA!", True, (255, 255, 0))
        screen.blit(title, (self.game.width // 2 - title.get_width() // 2, 70))
        
        for p_data, cx in [(self.game.p1, 250), (self.game.p2, 1030)]:
            if p_data.choice:
                img = self.game.assets.get_expressions(p_data.choice["id"])["euforico"]
                screen.blit(img, img.get_rect(center=(cx, 360)))
                color = (0, 255, 255) if cx == 250 else (255, 0, 128)
                name_surf = self.game.assets.get_font("title").render(f"J: {p_data.name}", True, color)
                screen.blit(name_surf, (cx - name_surf.get_width() // 2, 480))
        
        vs_surf = self.game.assets.get_font("giant").render("VS", True, (255, 255, 255))
        screen.blit(vs_surf, (self.game.width // 2 - vs_surf.get_width() // 2, 310))
        
        count_str = "3" if self.timer > 120 else "2" if self.timer > 60 else "1"
        count_surf = self.game.assets.get_font("giant").render(count_str, True, (0, 255, 128))
        screen.blit(count_surf, (self.game.width // 2 - count_surf.get_width() // 2, self.game.height // 2 + 180 - count_surf.get_height() // 2))

class PlayScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.duration = 10.0
        self.remaining_time = 10.0
        self.start_ticks = pygame.time.get_ticks()
        self.button_pressed_side = None
        self.game.assets.play_sound("juego", loops=-1)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.assets.stop_sound("juego")
                    self.game.change_scene(StartScene(self.game))
                elif event.key == self.game.p1.key_binding:
                    self.game.p1.score += 1
                    self.game.p1.button_timer = 6
                    self.button_pressed_side = "p1"
                elif event.key == self.game.p2.key_binding:
                    self.game.p2.score += 1
                    self.game.p2.button_timer = 6
                    self.button_pressed_side = "p2"

    def update(self):
        for p in (self.game.p1, self.game.p2):
            if p.button_timer > 0:
                p.button_timer -= 1
            elif self.button_pressed_side == p.side_name:
                self.button_pressed_side = None

        elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
        self.remaining_time = max(0.0, self.duration - elapsed)

        if self.remaining_time <= 0:
            if self.game.p1.score > self.game.p2.score:
                self.end_game(self.game.p1)
            elif self.game.p2.score > self.game.p1.score:
                self.end_game(self.game.p2)
            else:
                self.end_game(None)

    def end_game(self, winner):
        if winner is None:
            self.game.winner_text = "¡EMPATE SENSACIONAL! ¡MISMA CANTIDAD DE CLICS!"
            self.game.winning_character = None
        else:
            self.game.winner_text = f"¡{winner.name} ES EL GANADOR - {winner.score} CLICS EN 10s!"
            self.game.winning_character = winner.choice
        self.game.assets.set_sound_volume("juego", 0.3)
        self.game.change_scene(VictoryScene(self.game))

    def _draw_cable(self, screen, start_p, control_p, end_p, color_core, width=8):
        points = []
        for i in range(26):
            t = i / 25
            x = ((1 - t)**2 * start_p[0] + 2 * (1 - t) * t * control_p[0] + t**2 * end_p[0])
            y = ((1 - t)**2 * start_p[1] + 2 * (1 - t) * t * control_p[1] + t**2 * end_p[1])
            points.append((x, y))
        pygame.draw.lines(screen, (15, 10, 25), False, points, width)
        pygame.draw.lines(screen, color_core, False, points, max(2, width - 4))

    def _get_expression(self, player):
        exprs = self.game.assets.get_expressions(player.choice["id"])
        if player.button_timer > 0:
            return exprs.get("crouch", exprs["neutral"]), 0
            
        score_diff = self.game.p1.score - self.game.p2.score if player == self.game.p1 else self.game.p2.score - self.game.p1.score
        if score_diff > 5:
            return exprs.get("anticipacion", exprs["euforico"]), 0
        elif score_diff < -5:
            return exprs.get("alivio", exprs["neutral"]), 0
        return exprs.get("neutral", exprs["neutral"]), 0

    def draw(self, screen):
        self.draw_arcade_background(screen)
        
        font_med = self.game.assets.get_font("medium")
        font_small = self.game.assets.get_font("small")
        font_timer = self.game.assets.get_font("timer")
        
        title = self.game.assets.get_font("sala_title").render("SALA DE HACKERS - ¡MÁS CLICS EN 10 SEGUNDOS!", True, (255, 255, 0))
        screen.blit(title, (self.game.width // 2 - title.get_width() // 2, 10))
        
        # TEMPORIZADOR EN PARTE SUPERIOR Y MEDIO DE LA PANTALLA
        timer_box = pygame.Rect(self.game.width // 2 - 120, 48, 240, 56)
        is_low_time = self.remaining_time <= 3.0
        border_col = (255, 50, 50) if is_low_time else (0, 255, 255)
        bg_col = (50, 10, 20) if is_low_time else (15, 25, 45)
        text_col = (255, 80, 80) if is_low_time else (255, 255, 0)
        
        pygame.draw.rect(screen, bg_col, timer_box, border_radius=12)
        pygame.draw.rect(screen, border_col, timer_box, 3, border_radius=12)
        
        timer_str = f"{self.remaining_time:.1f} s"
        timer_text = font_timer.render(timer_str, True, text_col)
        screen.blit(timer_text, (timer_box.centerx - timer_text.get_width() // 2, timer_box.centery - timer_text.get_height() // 2))
        
        pygame.draw.rect(screen, (50, 30, 80), pygame.Rect(150, 340, 980, 220), border_radius=15)
        pygame.draw.rect(screen, (0, 255, 255), pygame.Rect(150, 340, 980, 220), 4, border_radius=15)
        
        term_rect = pygame.Rect(self.game.width // 2 - 210, 220, 420, 195)
        pygame.draw.rect(screen, (8, 12, 22), term_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 0, 128), term_rect, 4, border_radius=10)
        
        for idx, line in enumerate(["1 class Pixel {", " void run()", " sys.init()", "}"]):
            code_surf = font_small.render(line, True, (30, 65, 75))
            screen.blit(code_surf, (term_rect.x + 12, term_rect.y + 15 + idx * 18))
            screen.blit(code_surf, (term_rect.right - 120, term_rect.y + 15 + idx * 18))

        green = (0, 255, 128)
        screen.blit(font_med.render("[ESTADO DEL SISTEMA]:", True, green), (term_rect.x + 20, term_rect.y + 15))
        screen.blit(font_med.render("MODO: MÁS CLICS EN 10 SEGUNDOS", True, green), (term_rect.x + 20, term_rect.y + 40))
        
        pct = max(0.0, min(100.0, (self.remaining_time / self.duration) * 100))
        pct_box = pygame.Rect(term_rect.x + 20, term_rect.y + 68, term_rect.width - 40, 26)
        pygame.draw.rect(screen, (15, 25, 38), pct_box, border_radius=6)
        
        fill_w = int((pct_box.width - 6) * (pct / 100))
        if fill_w > 0:
            bar_color = (255, 50, 50) if is_low_time else green
            pygame.draw.rect(screen, bar_color, pygame.Rect(pct_box.x + 3, pct_box.y + 3, fill_w, pct_box.height - 6), border_radius=4)
        pygame.draw.rect(screen, (0, 255, 255), pct_box, 2, border_radius=6)
        
        pct_surf = font_small.render(f"TIEMPO RESTANTE: {self.remaining_time:.1f}s", True, (255, 255, 255))
        screen.blit(pct_surf, (pct_box.centerx - pct_surf.get_width()//2, pct_box.centery - pct_surf.get_height()//2))

        # BARRA DE PROGRESO DINÁMICA CON BARRITAS PEQUEÑAS (|)
        total_bars = 17
        filled_count = int((pct / 100.0) * total_bars)
        filled_count = min(total_bars, max(0, filled_count))
        bar_content = "|" * filled_count + "_" * (total_bars - filled_count)
        prog_surf = font_small.render(f"TIEMPO: [{bar_content}]", True, green)
        screen.blit(prog_surf, (term_rect.x + 20, term_rect.y + 104))

        btn_c_x, btn_c_y = self.game.width // 2, 475
        self._draw_cable(screen, (btn_c_x - 70, btn_c_y + 10), (430, 510), (270, 420), (0, 255, 255))
        self._draw_cable(screen, (btn_c_x + 70, btn_c_y + 10), (850, 510), (1010, 420), (255, 0, 128))
        
        btn_img = self.game.assets.get_img("btn_down") if self.button_pressed_side else self.game.assets.get_img("btn_up")
        if btn_img:
            scaled_btn = pygame.transform.smoothscale(btn_img, (240, 120))
            screen.blit(scaled_btn, scaled_btn.get_rect(center=(btn_c_x, btn_c_y)))
        else:
            by = 6 if self.button_pressed_side else 0
            brect = pygame.Rect(self.game.width//2 - 80, 455 + by, 160, 60)
            pygame.draw.rect(screen, (255, 128, 0) if self.button_pressed_side else (255, 0, 64), brect, border_radius=30)

        img_c = self.game.assets.get_img("compu")
        if img_c:
            for cx in [220, 1060]:
                sc = pygame.transform.smoothscale(img_c, (460, 360))
                screen.blit(sc, sc.get_rect(center=(cx, 330)))

        for p_data, cx in [(self.game.p1, 220), (self.game.p2, 1060)]:
            img, jump = self._get_expression(p_data)
            screen.blit(img, img.get_rect(center=(cx, 310 + jump)))

        screen.blit(font_med.render(f"J1 - {self.game.p1.name} [A]: {self.game.p1.score} clics", True, (0, 255, 255)), (120, 75))
        txt2 = font_med.render(f"J2 - {self.game.p2.name} [L]: {self.game.p2.score} clics", True, (255, 0, 128))
        screen.blit(txt2, (self.game.width - txt2.get_width() - 120, 75))
        
        inst = font_med.render("Presiona repetidamente las teclas 'A' (J1) y 'L' (J2)", True, (255, 255, 255))
        screen.blit(inst, (self.game.width // 2 - inst.get_width() // 2, 670))

class VictoryScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.game.assets.play_sound("winner")
        self.confetti = []
        colors = [(255, 0, 128), (0, 255, 255), (255, 255, 0), (0, 255, 128), (255, 128, 0)]
        for _ in range(200):
            self.confetti.append({
                "x": random.randint(0, game.width), "y": random.randint(-game.height, 0),
                "size": random.randint(8, 14), "speed_y": random.randint(5, 10),
                "speed_x": random.randint(-4, 4), "color": random.choice(colors)
            })
        self.btn_restart = pygame.Rect((game.width // 2) - 125 + 1, 480, 250, 100)
        self.btn_exit = pygame.Rect((game.width // 2) - 125 + 5, 550, 250, 100)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_restart.collidepoint(event.pos):
                    self.game.assets.play_sound("btn")
                    self.game.assets.stop_sound("juego")
                    self.game.reset_players()
                    self.game.change_scene(StartScene(self.game))
                elif self.btn_exit.collidepoint(event.pos):
                    self.game.assets.play_sound("btn")
                    pygame.time.wait(400)
                    self.game.running = False

    def update(self):
        for c in self.confetti:
            c["y"] += c["speed_y"]
            c["x"] += c["speed_x"]

    def draw(self, screen):
        self.draw_arcade_background(screen)
        for c in self.confetti:
            pygame.draw.rect(screen, c["color"], (c["x"], c["y"], c["size"], c["size"]))
            
        win_surf = self.game.assets.get_font("winner").render(self.game.winner_text, True, (255, 255, 0))
        screen.blit(win_surf, (self.game.width // 2 - win_surf.get_width() // 2, 50))
        
        for p_data, cx in [(self.game.p1, 380), (self.game.p2, 900)]:
            is_win = (self.game.winning_character and self.game.winning_character["id"] == p_data.choice["id"])
            is_tie = (self.game.winning_character is None)
            expr = "euforico" if (is_win or is_tie) else "tristeza"
            img = self.game.assets.get_expressions(p_data.choice["id"])[expr]
            bounce = int(15 * abs(math.sin(pygame.time.get_ticks() * 0.01))) if (is_win or is_tie) else 0
            screen.blit(img, img.get_rect(center=(cx, 290 - bounce)))
            
            if is_tie:
                lbl = f"J: {p_data.name} (EMPATE: {p_data.score} clics)"
                color = (255, 255, 0)
            else:
                lbl = f"J: {p_data.name} ({'¡GANADOR!' if is_win else 'DERROTA'})"
                color = (0, 255, 255) if is_win and cx == 380 else (255, 0, 128) if is_win else (200, 100, 100)
            surf = self.game.assets.get_font("medium").render(lbl, True, color)
            screen.blit(surf, (cx - surf.get_width() // 2, 400))

        m_pos, m_clk = pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]
        self.draw_button(screen, self.btn_restart, self.game.assets.get_img("btn_inicio"), (0, 200, 100), "INICIO", m_clk and self.btn_restart.collidepoint(m_pos))
        self.draw_button(screen, self.btn_exit, self.game.assets.get_img("btn_exit"), (200, 50, 50), "SALIR DEL JUEGO", m_clk and self.btn_exit.collidepoint(m_pos))

class CompileFileGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.width, self.height = 1280, 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("COMPILATION FAILED GAME")
        self.clock = pygame.time.Clock()
        self.running = True

        self.assets = AssetManager()
        self.particles = ParticleSystem(self.width, self.height)
        self.p1 = Player(pygame.K_a, "p1")
        self.p2 = Player(pygame.K_l, "p2")
        
        self.winner_text = None
        self.winning_character = None
        self.current_scene = StartScene(self)

    def reset_players(self):
        self.p1.reset()
        self.p2.reset()
        self.winner_text = None
        self.winning_character = None

    def change_scene(self, new_scene):
        self.current_scene = new_scene

    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.current_scene.handle_events(events)
            self.particles.update()
            self.current_scene.update()
            self.current_scene.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CompileFileGame()
    game.run()
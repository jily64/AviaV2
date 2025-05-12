import pygame, os, math, json
from dotenv import load_dotenv
from Modules import MAVLinkAdapter, Func, Touch, classes
from datetime import datetime, timezone

load_dotenv()

PATH = os.path.abspath('.')+'/'
RESOURCES_PATH = PATH + "res/"
WIDTH, HEIGHT = int(os.getenv("SCREEN_WIDTH")), int(os.getenv("SCREEN_HEIGHT"))


class Main:
    def __init__(self, app):
        self.app = app
        self.screen = self.app.screen

        self.cfg = {}
        self.load_cfg()

        self.data = self.app.mav.data

        self.default_pressure = None
        self.is_pr_updated = False

        self.pressure = 1013.25
        self.alt = 0
        self.speed = 0
        self.heading = 0
        self.airspeed = 0

        self.alt_comp = [0, 0, 0, 0]
        self.alt_pad_delt = 0
        self.alt_y_pad = 0

        self.speed_comp = [0, 0, 0, 0]
        self.speed_pad_delt = 0

        self.speed_vz_comp = []
        self.speed_pad_delt_vz = 0

        self.debug_c = 0

        self.is_opened = False

        self.init_lat = None
        self.init_lon = None
        self.to_home = 0

        self.wind_direction = 0

        self.indicate_heading = [(WIDTH//2, 165), (WIDTH//2, 265), 7]

        # Graphics
        self.font_big = pygame.font.Font(None, 350)
        self.font_middle = pygame.font.Font(None, 125)
        self.font_small = pygame.font.Font(None, 50)

        self.font_middle_small = pygame.font.Font(None, 95)
        self.font_small_middle = pygame.font.Font(None, 75)

        # Arrows

        self.arrow_sprite_middle = pygame.transform.flip(pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "arrow.png").convert_alpha(), (345, 230)), True, False)
        self.arrow_sprite_small = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "arrow.png").convert_alpha(), (185, 100))

        self.box_sprite_small = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "box.png").convert(), (250, 150))
        self.box_sprite_big = pygame.transform.scale(self.box_sprite_small, (750, 450))
        

        self.alt_rect = self.arrow_sprite_middle.get_rect()
        self.alt_rect.center = (250, HEIGHT//2)

        self.speed_rect = self.arrow_sprite_middle.get_rect()
        self.speed_rect.center = (WIDTH-400, HEIGHT//2)

        self.speed_rect_vz = self.arrow_sprite_small.get_rect()
        self.speed_rect_vz.center = (WIDTH-120, HEIGHT//2)

        self.heading_rect = self.box_sprite_small.get_rect()
        self.heading_rect.center = (WIDTH//2, 75)

        self.minus_rect = self.box_sprite_big.get_rect(center=(WIDTH//2, HEIGHT-250))
        self.minus_text = self.font_big.render("-", False, (255, 255, 255))

        self.plus_rect = self.box_sprite_big.get_rect(center=(WIDTH//2, 250))
        self.plus_text = self.font_big.render("+", False, (255, 255, 255))

        self.app.touchable.add_rect("plus-main", self.plus_rect, "main", self.plus_callback)
        self.app.touchable.add_rect("minus-main", self.minus_rect, "main", self.minus_callback)

        

        # Touchable
        self.to_page_button = pygame.transform.scale(self.box_sprite_small, (400, 300))
        self.to_page_text = self.font_middle.render("Путь", False, (255, 255, 255))
        self.to_page_rect = self.to_page_button.get_rect(center=(200, HEIGHT-150))
        self.to_page_text_rect = self.to_page_text.get_rect(center=(200, HEIGHT-150))

        self.scale_button = pygame.transform.scale(self.box_sprite_small, (500, 300))
        self.scale_text = self.font_middle.render("Давл.", False, (255, 255, 255))
        self.scale_rect = self.scale_button.get_rect(center=(WIDTH-250, HEIGHT-150))
        self.scale_text_rect = self.scale_text.get_rect(center=(WIDTH-250, HEIGHT-150))

        self.wind_button = pygame.transform.scale(self.box_sprite_small, (200, 150))
        self.wind_text = self.font_small.render("Ветер", False, (255, 255, 255))
        self.wind_rect = self.wind_button.get_rect(center=(502, HEIGHT-75))
        self.wind_text_rect = self.wind_text.get_rect(center=(502, HEIGHT-75))

        self.num_button = pygame.transform.scale(self.box_sprite_small, (700, 150))
        self.num_text = self.font_middle.render("N0 000 0:0", False, (255, 255, 255))
        self.num_rect = self.num_button.get_rect(center=(350, 75))
        self.num_text_rect = self.num_text.get_rect(center=(350, 75))

        self.app.touchable.add_rect("page-main", self.to_page_rect, "main", self.to_page_callback)
        self.app.touchable.add_rect("scale-main", self.scale_rect, "main", self.scale_callback)
        self.app.touchable.add_rect("wind-main", self.wind_rect, "main", self.wind_dir_callback)


        # Time 
        self.time = datetime.now(timezone.utc).strftime("%H:%M:%S")

        # Horizon Setup
        self.horizon_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Background.png").convert_alpha(), (WIDTH*2, HEIGHT*2))
        self.horizon_rect = self.horizon_sprite.get_rect()
        self.horizon_rect.center = (WIDTH//2, HEIGHT//2)

        self.horizon_sprite = pygame.transform.rotate(self.horizon_sprite, 0)
        self.horizon_rect = self.horizon_sprite.get_rect(center=self.horizon_rect.center)

        self.horizon_sprite_current = self.horizon_sprite

        # Compass
        self.compass_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Compass.png"), (WIDTH//2.5, WIDTH//2.5))
        self.compass_rect = self.compass_sprite.get_rect()
        self.compass_rect.center = (WIDTH//2, HEIGHT//2)

        self.compass_sprite = pygame.transform.rotate(self.compass_sprite, 0)
        self.compass_rect = self.compass_sprite.get_rect(center=self.compass_rect.center)

        self.compass_sprite_current = self.compass_sprite

        # Wings
        self.left_wing = [(WIDTH//4-150, HEIGHT//2), (WIDTH//4+125, HEIGHT//2), 10]
        self.right_wing = [(WIDTH-WIDTH//4-150, HEIGHT//2), (WIDTH-WIDTH//4+125, HEIGHT//2), 10]

        self.left_body = [(WIDTH//2-50, HEIGHT//2-25), (WIDTH//2, HEIGHT//2), 7]
        self.right_body = [(WIDTH//2+50, HEIGHT//2-25), (WIDTH//2, HEIGHT//2), 7]

        # Pointers
        self.red_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "pointer_red.png"), (WIDTH//2.5, WIDTH//2.5))
        self.red_rect = self.red_sprite.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.red_sprite_current = self.red_sprite

        self.green_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "pointer_green.png"), (WIDTH//2.5, WIDTH//2.5))
        self.green_rect = self.green_sprite.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.green_sprite_current = self.green_sprite

        self.yellow_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "pointer_yellow.png"), (WIDTH//2.5, WIDTH//2.5))
        self.yellow_rect = self.yellow_sprite.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.yellow_sprite_current = self.yellow_sprite




    def update(self):
        self.debug_c += 1

        self.data = self.app.mav.data
        
        if self.init_lat == None and self.init_lon == None:
            if self.data["gps"]["lat"] != None and self.data["gps"]["lon"] != None:
                self.init_lat = self.data["gps"]["lat"]
                self.init_lon = self.data["gps"]["lon"]
        else:
            self.to_home = Func.calculate_bearing(self.init_lat, self.init_lon, self.data["gps"]["lat"], self.data["gps"]["lon"])

        if self.data["pressure"]["abs_pressure"] != None and not self.is_pr_updated:
            self.default_pressure = self.data["pressure"]["abs_pressure"]
            self.is_pr_updated = True

        self.pressure = self.data["pressure"]["abs_pressure"]
        self.alt = round(Func.calculate_height_from_pressure(self.default_pressure, self.pressure + self.cfg["pressure_diff"]))
        self.speed = round(self.data["airspeed"] * 3.6)
        self.airspeed = round(Func.count_speed_module(self.data["global_position"]["vx"], self.data["global_position"]["vy"])*3.6)
        self.speed_vz = round(self.data["global_position"]["vz"], 2)
        self.heading = self.data["heading"]

        delta_speed_vz = round(self.speed_vz, -1)
        self.speed_vz_comp = []
        for i in range(5):
            self.speed_vz_comp.append(delta_speed_vz + 10*(i-2))
        
        self.speed_pad_delt_vz = round(self.speed_vz - delta_speed_vz)*10
        self.speed_vz_comp.reverse()

        self.time = datetime.now(timezone.utc).strftime("%H:%M:%S")

        self.scale_text = self.font_middle.render(str(round(self.pressure + self.cfg["pressure_diff"])) + " ГПа", False, (255, 255, 255))
        self.scale_text_rect = self.scale_text.get_rect(center=(WIDTH-250, HEIGHT-150))

        delta_vert = round(self.data["attitude"]["pitch"]+self.cfg["pitch_diff"], 2)
        self.horizon_sprite_current = pygame.transform.rotate(self.horizon_sprite, -self.data["attitude"]["roll"]+self.cfg["roll_diff"])
        self.horizon_rect = self.horizon_sprite_current.get_rect(center=(self.horizon_rect.center[0], HEIGHT//2+delta_vert*12))

        self.compass_sprite_current = pygame.transform.rotate(self.compass_sprite, self.heading)
        self.compass_rect = self.compass_sprite_current.get_rect(center=self.compass_rect.center)

        self.red_sprite_current = pygame.transform.rotate(self.red_sprite, (self.heading-self.app.t_h.headings[self.app.t_h.active_zone]+90)%360)
        self.red_rect = self.red_sprite_current.get_rect(center=self.red_rect.center)

        self.green_sprite_current = pygame.transform.rotate(self.green_sprite, self.heading-self.to_home)
        self.green_rect = self.green_sprite_current.get_rect(center=self.green_rect.center)

        self.yellow_sprite_current = pygame.transform.rotate(self.yellow_sprite, self.heading-self.wind_direction)
        self.yellow_rect = self.yellow_sprite_current.get_rect(center=self.yellow_rect.center)



    def render(self):
        self.screen.blit(self.horizon_sprite_current, self.horizon_rect)
        pygame.draw.line(self.screen, (235, 235, 0), self.indicate_heading[0], self.indicate_heading[1], self.indicate_heading[2])
        self.screen.blit(self.compass_sprite_current, self.compass_rect)

        if self.app.t_h.is_active:
            self.screen.blit(self.red_sprite_current, self.red_rect)

        self.screen.blit(self.green_sprite_current, self.green_rect)
        self.screen.blit(self.yellow_sprite_current, self.yellow_rect)

        pygame.draw.line(self.screen, (235, 0, 0), self.left_wing[0], self.left_wing[1], self.left_wing[2])
        pygame.draw.line(self.screen, (235, 0, 0), self.right_wing[0], self.right_wing[1], self.right_wing[2])

        pygame.draw.line(self.screen, (235, 0, 0), self.left_body[0], self.left_body[1], self.left_body[2])
        pygame.draw.line(self.screen, (235, 0, 0), self.right_body[0], self.right_body[1], self.right_body[2])

        for i in range(len(self.speed_vz_comp)):
            if self.speed_vz_comp[i] == None:
                continue

            text = self.font_small.render(str(abs(self.speed_vz_comp[i])), False, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(WIDTH-100, self.speed_pad_delt_vz+(i-2)*100+HEIGHT//2)))

        self.screen.blit(self.arrow_sprite_middle, self.alt_rect)
        self.screen.blit(pygame.transform.flip(self.arrow_sprite_middle, True, False), self.speed_rect)
        self.screen.blit(self.arrow_sprite_small, self.speed_rect_vz)

        self.screen.blit(self.box_sprite_small, self.heading_rect)

        text = self.font_middle.render(str(self.alt)+ "", False, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(WIDTH-375, HEIGHT//2)))

        text = self.font_middle_small.render("AS "+str(self.speed), False, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(225, HEIGHT//2-45)))

        pygame.draw.line(self.screen, (255, 255, 255), (150, HEIGHT//2), (300, HEIGHT//2), 5)

        text = self.font_small_middle.render("GS " + str(self.airspeed), False, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(225, HEIGHT//2+45)))

        text = self.font_small.render(str(self.speed_vz), False, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(WIDTH-100, HEIGHT//2)))

        text = self.font_middle.render(str(self.heading)+"°", False, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(WIDTH//2, 75)))
            
        self.screen.blit(self.to_page_button, self.to_page_rect)
        self.screen.blit(self.to_page_text, self.to_page_text_rect)

        self.screen.blit(self.scale_button, self.scale_rect)
        self.screen.blit(self.scale_text, self.scale_text_rect)

        self.screen.blit(self.wind_button, self.wind_rect)
        self.screen.blit(self.wind_text, self.wind_text_rect)

        if self.app.t_h.is_active:
            time = self.app.t_h.temp_zones[self.app.t_h.active_zone]
            new_time = datetime.now()
            time = time - new_time

            hours = round(time.total_seconds()) // 3600
            minutes = round(time.total_seconds()) // 60 % 60
            str_time = f'{hours}:{"0"*(len(str(minutes))%2)}{minutes}'

            self.screen.blit(self.num_button, self.num_rect)
            self.num_text = self.font_middle.render(f'N{self.app.t_h.active_zone+1} {self.app.t_h.headings[self.app.t_h.active_zone]}° {str_time}', False, (255, 255, 255))
            self.num_text_rect = self.num_text.get_rect(center=(350, 75))
            self.screen.blit(self.num_text, self.num_text_rect)

        text = self.font_middle.render(str(round(self.app.clock.get_fps(), 2)) + " (FPS)", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT-50)))


        if self.is_opened:
            self.screen.blit(self.box_sprite_big, self.minus_rect)
            self.screen.blit(self.box_sprite_big, self.plus_rect)

            self.screen.blit(self.plus_text, self.plus_text.get_rect(center=self.plus_rect.center))
            self.screen.blit(self.minus_text, self.minus_text.get_rect(center=self.minus_rect.center))

        # text = self.font_middle.render(str(round(self.data["attitude"]["pitch"])), False, (255, 255, 255))
        # self.screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))        

    def load_cfg(self):
        with open("cfg.json", "r", encoding="UTF-8") as f:
            self.cfg = json.load(f)

    def save_cfg(self):
        with open("cfg.json", "w", encoding="UTF-8") as f:
            json.dump(self.cfg, f, ensure_ascii=False, indent=4)

    def to_page_callback(self):
        self.app.change_group("head_menu")

    def plus_callback(self):
        if self.is_opened:
            self.cfg["pressure_diff"] += 1
            self.cfg["pressure_diff"] = round(self.cfg["pressure_diff"], 2)
            self.save_cfg()

    def minus_callback(self):
        if self.is_opened:
            self.cfg["pressure_diff"] -= 1
            self.cfg["pressure_diff"] = round(self.cfg["pressure_diff"], 2)
            self.save_cfg()

    def scale_callback(self):
        self.is_opened = not self.is_opened

    def wind_dir_callback(self):
        self.app.groups["num_keyboard"].setup_value(value=str(self.wind_direction), callback=self.wind_dir_scale_callback, return_group="main", mark="Град.")
        self.app.change_group("num_keyboard")

    def wind_dir_scale_callback(self, value):
        self.wind_direction = int("".join(value.split(":")))%360


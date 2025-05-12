import pygame, os, math, json
from dotenv import load_dotenv
from Modules import MAVLinkAdapter, Func, Touch, classes
from datetime import datetime, timezone

load_dotenv()

RESOURCES_PATH = os.getenv("RESOURCES_PATH")
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
        self.init_fonts()
        self.init_sprites()
        self.init_touchable()

        # Time 
        self.time = datetime.now(timezone.utc).strftime("%H:%M:%S")

    def init_fonts(self):
        self.font_big = pygame.font.Font(None, 350)
        self.font_middle = pygame.font.Font(None, 125)
        self.font_small = pygame.font.Font(None, 50)
        self.font_middle_small = pygame.font.Font(None, 95)
        self.font_small_middle = pygame.font.Font(None, 75)

    def init_sprites(self):
        def load_image(name, size=None, flip=False):
            image = pygame.image.load(RESOURCES_PATH + name).convert_alpha()
            if size:
                image = pygame.transform.scale(image, size)
            if flip:
                image = pygame.transform.flip(image, True, False)
            return image

        self.arrow_sprite_middle = load_image("arrow.png", (345, 230), flip=True)
        self.arrow_sprite_small = load_image("arrow.png", (185, 100))

        self.box_sprite_small = load_image("box.png", (250, 150))
        self.box_sprite_big = pygame.transform.scale(self.box_sprite_small, (750, 450))

        self.horizon_sprite = load_image("Background.png", (WIDTH*2, HEIGHT*2))
        self.compass_sprite = load_image("Compass.png", (WIDTH//2.5, WIDTH//2.5))

        self.red_sprite = load_image("pointer_red.png", (WIDTH//2.5, WIDTH//2.5))
        self.green_sprite = load_image("pointer_green.png", (WIDTH//2.5, WIDTH//2.5))
        self.yellow_sprite = load_image("pointer_yellow.png", (WIDTH//2.5, WIDTH//2.5))

    def init_touchable(self):
        self.app.touchable.add_rect("plus-main", self.create_rect(self.box_sprite_big, (WIDTH//2, 250)), "main", self.plus_callback)
        self.app.touchable.add_rect("minus-main", self.create_rect(self.box_sprite_big, (WIDTH//2, HEIGHT-250)), "main", self.minus_callback)

    def create_rect(self, sprite, center):
        rect = sprite.get_rect()
        rect.center = center
        return rect

    def update(self):
        self.debug_c += 1
        self.data = self.app.mav.data

        if self.init_lat is None and self.init_lon is None:
            if self.data["gps"]["lat"] and self.data["gps"]["lon"]:
                self.init_lat = self.data["gps"]["lat"]
                self.init_lon = self.data["gps"]["lon"]
        else:
            self.to_home = Func.calculate_bearing(self.init_lat, self.init_lon, self.data["gps"]["lat"], self.data["gps"]["lon"])

        if self.data["pressure"]["abs_pressure"] and not self.is_pr_updated:
            self.default_pressure = self.data["pressure"]["abs_pressure"]
            self.is_pr_updated = True

        self.pressure = self.data["pressure"]["abs_pressure"]
        self.alt = round(Func.calculate_height_from_pressure(self.default_pressure, self.pressure + self.cfg["pressure_diff"]))
        self.speed = round(self.data["airspeed"] * 3.6)
        self.airspeed = round(Func.count_speed_module(self.data["global_position"]["vx"], self.data["global_position"]["vy"])*3.6)
        self.speed_vz = round(self.data["global_position"]["vz"], 2)
        self.heading = self.data["heading"] + self.debug_c % 360

        delta_speed_vz = round(self.speed_vz, -1)
        self.speed_vz_comp = [delta_speed_vz + 10*(i-2) for i in range(5)]
        self.speed_pad_delt_vz = round(self.speed_vz - delta_speed_vz)*10
        self.speed_vz_comp.reverse()

        self.time = datetime.now(timezone.utc).strftime("%H:%M:%S")

        self.scale_text = self.font_middle.render(f"{round(self.pressure + self.cfg['pressure_diff'])} ГПа", False, (255, 255, 255))
        self.scale_text_rect = self.scale_text.get_rect(center=(WIDTH-250, HEIGHT-150))

        delta_vert = round(self.data["attitude"]["pitch"]+self.cfg["pitch_diff"] + self.debug_c % 360, 2)
        self.horizon_sprite_current = pygame.transform.rotate(self.horizon_sprite, -self.data["attitude"]["roll"]+self.cfg["roll_diff"] + self.debug_c % 360)
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

        for i, comp in enumerate(self.speed_vz_comp):
            if comp is None:
                continue
            text = self.font_small.render(str(abs(comp)), False, (255, 255, 255))
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

class HeadingPlanner:
    def __init__(self, app):
        self.app=app
        self.screen = app.screen
        self.zones = app.t_h.zones_count//2

        self.title_font = pygame.font.Font(None, 75)

        self.GREEN = (0, 200, 0)
        self.RED = (200, 0, 0)
        self.ACTIVE = (0, 0, 200)

        self.ACTIVE_COLOR = self.RED

        self.current_pad = None

        

        self.heading_buttons = []
        self.time_buttons = []

        self.texts = [[], []]

        self.texts = []
        self.main_font = pygame.font.Font(None, 75)

        self.padding = 50
        self.size = [400, 150]
        self.text_center = [self.size[0]//2, self.size[1]//2]


        self.now_used = [None, None]
        self.page = 0


        self.onoff_button = pygame.Rect(1300, self.padding, self.size[0], self.size[0])
        self.clear_button = pygame.Rect(1300, self.padding + 500, self.size[0], self.size[1]-50)
        self.back_button = pygame.Rect(1300, self.padding + 650, self.size[0], self.size[1]-50)
        self.page_swap = pygame.Rect(1300, self.padding + 850, self.size[0], self.size[1]-50)

        self.app.touchable.add_rect(id="hd-onoff", obj=self.onoff_button, group="head_menu", listner=self.set_active)
        self.app.touchable.add_rect(id="hd-back", obj=self.back_button, group="head_menu", listner=self.back_to_menu_callback)
        self.app.touchable.add_rect(id="hd-pageswap", obj=self.page_swap, group="head_menu", listner=self.page_swap_callback)
        self.app.touchable.add_rect(id="hd-clear", obj=self.clear_button, group="head_menu", listner=self.clear_callback)


        self.onoff_text = self.main_font.render("Вкл/Выкл", False, (255, 255, 255))
        self.onoff_text_rect = self.onoff_text.get_rect(center=self.onoff_button.center)

        self.clear_text = self.main_font.render("Сброс", False, (255, 255, 255))
        self.clear_text_rect = self.clear_text.get_rect(center=self.clear_button.center)

        self.page_text = self.main_font.render("Страница Null", False, (255, 255, 255))
        self.page_text_rect = self.page_text.get_rect(center=self.page_swap.center)

        self.back_text = self.main_font.render("Назад", False, (255, 255, 255))
        self.back_text_rect = self.back_text.get_rect(center=self.back_button.center)


        self.callbacks = [[self.m1_c, self.m2_c, self.m3_c, self.m4_c, self.m5_c], [self.h1_c, self.h2_c, self.h3_c, self.h4_c, self.h5_c]]

        self.generate_buttons()

    def generate_buttons(self):
        for i in range(self.zones):
            pad_delt = (i + 1) * self.padding
            size_delt = i * self.size[1]
            self.heading_buttons.append(pygame.Rect(100 + self.padding + self.size[0], size_delt + pad_delt, self.size[0], self.size[1]))
            self.app.touchable.add_rect(id="hd-m-"+str(i+1), obj=self.heading_buttons[i], group="head_menu", listner=self.callbacks[0][i])

        
        for i in range(self.zones):
            pad_delt = (i + 1) * self.padding
            size_delt = i * self.size[1]
            self.time_buttons.append(pygame.Rect(100, size_delt + pad_delt, self.size[0], self.size[1]))
            self.app.touchable.add_rect(id="hd-h-"+str(i+1), obj=self.time_buttons[i], group="head_menu", listner=self.callbacks[1][i])




    def update(self):
        self.page_text = self.main_font.render("Страница " + str(self.page+1) + " ", False, (255, 255, 255))
        self.page_text_rect = self.onoff_text.get_rect(center=self.page_swap.center)


        if self.app.t_h.is_active == True:
            self.ACTIVE_COLOR = self.GREEN
        else:
            self.ACTIVE_COLOR = self.RED

    def render(self):
        for i in range(len(self.heading_buttons)):
            color = (190, 190, 190)

            if self.app.t_h.active_zone == i+5*self.page and self.app.t_h.is_active == True:
                color = self.ACTIVE

            pad_delt = (i + 1) * self.padding
            size_delt = i * self.size[1]

            pygame.draw.rect(self.screen, color, self.heading_buttons[i])
            text_render = self.main_font.render(str(self.app.t_h.headings[i+5*self.page]) + " Град.", True, (255, 255, 255))
            self.screen.blit(text_render, text_render.get_rect(center=(100 + self.padding + self.size[0] + self.text_center[0], size_delt + pad_delt + self.text_center[1])))
        
        for i in range(len(self.time_buttons)):
            color = (190, 190, 190)

            if self.app.t_h.active_zone == i+5*self.page and self.app.t_h.is_active == True:
                color = self.ACTIVE

            pad_delt = (i + 1) * self.padding
            size_delt = i * self.size[1]

            hours = str(round(self.app.t_h.zones[i+5*self.page].total_seconds() // 3600))
            minutes = str(round(self.app.t_h.zones[i+5*self.page].total_seconds() // 60 % 60))

            d_m = "0"*(len(minutes)%2)

            pygame.draw.rect(self.screen, color, self.time_buttons[i])
            text_render = self.main_font.render(hours + ":" + str(d_m) + minutes + " Ч:М", True, (255, 255, 255))
            self.screen.blit(text_render, text_render.get_rect(center=(100 + self.text_center[0], size_delt + pad_delt + self.text_center[1])))
        
        pygame.draw.rect(self.screen, self.ACTIVE_COLOR, self.onoff_button)

        pygame.draw.rect(self.screen, (190, 190, 0), self.clear_button)
        pygame.draw.rect(self.screen, (190, 190, 190), self.back_button)
        pygame.draw.rect(self.screen, (190, 190, 190), self.page_swap)


        self.screen.blit(self.onoff_text, self.onoff_text_rect)
        self.screen.blit(self.clear_text, self.clear_text_rect)
        self.screen.blit(self.page_text, self.page_text_rect)
        self.screen.blit(self.back_text, self.back_text_rect)

    def m1_c(self):
        self.current_pad = "m1"
        self.app.groups["num_keyboard"].setup_value(value=str(self.app.t_h.headings[0+5*self.page]), callback=self.confirm_heading, return_group="head_menu", mark="Град.")

        self.app.change_group("num_keyboard")
        print("m1")
    
    def m2_c(self):
        self.current_pad = "m2"
        self.app.groups["num_keyboard"].setup_value(value=str(self.app.t_h.headings[1+5*self.page]), callback=self.confirm_heading, return_group="head_menu", mark="Град.")

        self.app.change_group("num_keyboard")
        print("m2")

    def m3_c(self):
        self.current_pad = "m3"
        self.app.groups["num_keyboard"].setup_value(value=str(self.app.t_h.headings[2+5*self.page]), callback=self.confirm_heading, return_group="head_menu", mark="Град.")

        self.app.change_group("num_keyboard")
        print("m3")

    def m4_c(self):
        self.current_pad = "m4"
        self.app.groups["num_keyboard"].setup_value(value=str(self.app.t_h.headings[3+5*self.page]), callback=self.confirm_heading, return_group="head_menu", mark="Град.")

        self.app.change_group("num_keyboard")
        print("m4")

    def m5_c(self):
        self.current_pad = "m5"
        self.app.groups["num_keyboard"].setup_value(value=str(self.app.t_h.headings[4+5*self.page]), callback=self.confirm_heading, return_group="head_menu", mark="Град.")

        self.app.change_group("num_keyboard")
        print("m5")

    def h1_c(self):
        hours = round(self.app.t_h.zones[0+5*self.page].total_seconds() // 3600)
        minutes = round(self.app.t_h.zones[0+5*self.page].total_seconds() // 60) % 60

        self.current_pad = "h1"
        self.app.groups["num_keyboard"].setup_value(value=str(hours)+":"+str(minutes), callback=self.confirm_time, return_group="head_menu", mark="Ч:М")

        self.app.change_group("num_keyboard")
        print("h1")
    
    def h2_c(self):
        hours = round(self.app.t_h.zones[1+5*self.page].total_seconds() // 3600)
        minutes = round(self.app.t_h.zones[1+5*self.page].total_seconds() // 60) % 60

        self.current_pad = "h2"
        self.app.groups["num_keyboard"].setup_value(value=str(hours)+":"+str(minutes), callback=self.confirm_time, return_group="head_menu", mark="Ч:М")

        self.app.change_group("num_keyboard")
        print("h2")

    def h3_c(self):
        hours = round(self.app.t_h.zones[2+5*self.page].total_seconds() // 3600)
        minutes = round(self.app.t_h.zones[2+5*self.page].total_seconds() // 60) % 60

        self.current_pad = "h3"
        self.app.groups["num_keyboard"].setup_value(value=str(hours)+":"+str(minutes), callback=self.confirm_time, return_group="head_menu", mark="Ч:М")

        self.app.change_group("num_keyboard")
        print("h3")

    def h4_c(self):
        hours = round(self.app.t_h.zones[3+5*self.page].total_seconds() // 3600)
        minutes = round(self.app.t_h.zones[3+5*self.page].total_seconds() // 60) % 60

        self.current_pad = "h4"
        self.app.groups["num_keyboard"].setup_value(value=str(hours)+":"+str(minutes), callback=self.confirm_time, return_group="head_menu", mark="Ч:М")

        self.app.change_group("num_keyboard")
        print("h4")

    def h5_c(self):
        hours = round(self.app.t_h.zones[4+5*self.page].total_seconds() // 3600)
        minutes = round(self.app.t_h.zones[4+5*self.page].total_seconds() // 60) % 60

        self.current_pad = "h5"
        self.app.groups["num_keyboard"].setup_value(value=str(hours)+":"+str(minutes), callback=self.confirm_time, return_group="head_menu", mark="Ч:М")

        self.app.change_group("num_keyboard")
        print("h5")

    def clear_callback(self):
        self.app.t_h.renew()
        print("c1")

    def set_active(self):
        self.app.t_h.set_active()

    def clear_time_head(self):
        self.app.t_h.renew(self)

    def back_to_menu_callback(self):
        self.app.change_group("main")

    def start_stop(self):
        self.app.t_h.set_active()

    def page_swap_callback(self):
        self.page = 1 - (self.page%2)
        print(self.page)

    def confirm_time(self, value):
        self.app.t_h.set_zone(int("".join(self.current_pad.split("h")))-1+5*self.page, value, "hm")
        print(value)
        self.current_pad = None

    def confirm_heading(self, value):
        if value == ":" or value == "":
            value = "0"
        value = int(value.split(":")[0])%360
        self.app.t_h.set_heading(int("".join(self.current_pad.split("m")))-1+5*self.page, value)
        print(value)
        self.current_pad = None


import pygame, os, math, json
from dotenv import load_dotenv
from Modules import MAVLinkAdapter, Func, Touch, classes
from datetime import datetime, timezone

load_dotenv()

RESOURCES_PATH = os.getenv("RESOURCES_PATH")
WIDTH, HEIGHT = int(os.getenv("SCREEN_WIDTH")), int(os.getenv("SCREEN_HEIGHT"))

class MainScreen:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen

        self.state = "main"

        self.save = {}

        self.default_pressure = 1013.25

        # Horizon Setup
        self.horizon_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Background.png"), (WIDTH*2, HEIGHT*2))
        self.horizon_rect = self.horizon_sprite.get_rect()
        self.horizon_rect.center = (WIDTH//2, HEIGHT//2)

        self.horizon_sprite = pygame.transform.rotate(self.horizon_sprite, 0)
        self.horizon_rect = self.horizon_sprite.get_rect(center=self.horizon_rect.center)

        self.horizon_sprite_current = self.horizon_sprite

        # Compass Setup
        self.compass_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Compass.png"), (WIDTH//3, WIDTH//3))
        self.compass_rect = self.compass_sprite.get_rect()
        self.compass_rect.center = (WIDTH//2, HEIGHT//2)

        self.compass_sprite = pygame.transform.rotate(self.compass_sprite, 0)
        self.compass_rect = self.compass_sprite.get_rect(center=self.compass_rect.center)

        self.compass_sprite_current = self.compass_sprite

        # Heading Setup
        self.heading_font = pygame.font.Font(None, 50)
        self.heading = 0

        self.indicate_heading = [(WIDTH//2, HEIGHT//3-135), (WIDTH//2, HEIGHT//3-50), 7]

        # Wings Indicator
        self.left_wing = [(WIDTH//4-100, HEIGHT//2), (WIDTH//4+75, HEIGHT//2), 10]
        self.right_wing = [(WIDTH-WIDTH//4-100, HEIGHT//2), (WIDTH-WIDTH//4+75, HEIGHT//2), 10]

        self.left_body = [(WIDTH//2-50, HEIGHT//2-25), (WIDTH//2, HEIGHT//2), 7]
        self.right_body = [(WIDTH//2+50, HEIGHT//2-25), (WIDTH//2, HEIGHT//2), 7]

        # Altitude Setup
        self.alt_font = pygame.font.Font(None, 50)
        self.alt = 0

        self.relative_alt_font = pygame.font.Font(None, 50)
        self.relative_alt = 0

        # Speed Setup
        self.horizon_speed_font = pygame.font.Font(None, 50)
        self.horizon_speed = 0

        # Vertical Speed Setup
        self.vertical_speed_font = pygame.font.Font(None, 50)
        self.vertical_speed = 0

        # Time Setup
        self.time_font = pygame.font.Font(None, 50)
        self.time = datetime.now(timezone.utc).strftime("%H:%M:%S")

        # Settings Setup
        self.settings_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Settings.png"), (100, 100))
        self.settings_rect = self.settings_sprite.get_rect()
        self.settings_rect.center = (75, 75)

        self.app.touchable.add_rect(id="settings_button", obj=self.settings_rect, group="main", listner=self.settings_callback)

        # Menu Setup
        self.menu_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Menu.png"), (100, 100))
        self.menu_rect = self.menu_sprite.get_rect()
        self.menu_rect.center = (WIDTH-75, 75)

        # Pressure Setup
        self.press_font = pygame.font.Font(None, 50)
        self.press_text = self.press_font.render("1013.25", True, (0, 0, 0))
        self.press_rect = None

        press_rect = self.press_text.get_rect(center=(WIDTH-100, HEIGHT-20))
        self.app.touchable.add_rect(id="pressure_change", obj=press_rect, group="main", listner=self.pressure_callback)

        self.pressure = 1013.25

        # FPS Setup
        self.fps_font = pygame.font.Font(None, 50)


    def update(self):
        mav_data = self.app.mav.data

        delta_vert = round((-math.sin(mav_data["attitude"]["pitch"])))*5
        delta_vert = 0

        self.time = datetime.now(timezone.utc).strftime("%H:%M:%S")

        self.heading = mav_data["heading"]

        self.alt = mav_data["global_position"]["alt"] / 1000.0
        self.relative_alt =  mav_data["global_position"]["relative_alt"] / 1000.0

        self.horizon_speed = Func.count_speed_module(mav_data["global_position"]["vx"],mav_data["global_position"]["vy"]) / 1000
        self.vertical_speed = mav_data["global_position"]["vz"] / 1000

        self.horizon_sprite_current = pygame.transform.rotate(self.horizon_sprite, mav_data["attitude"]["roll"])
        self.horizon_rect = self.horizon_sprite_current.get_rect(center=(self.horizon_rect.center[0], HEIGHT//2+delta_vert*10))

        self.compass_sprite_current = pygame.transform.rotate(self.compass_sprite, self.heading)
        self.compass_rect = self.compass_sprite_current.get_rect(center=self.compass_rect.center)

        self.pressure = round(mav_data["pressure"]["abs_pressure"], 2)
        


    def render(self):
        heading_surface = self.heading_font.render(str(self.heading), True, (255, 255, 255))
        heading_text_rect = heading_surface.get_rect(center=(WIDTH//2, 20))

        time_surface = self.heading_font.render(str(round(self.app.clock.get_fps())) + " (UTC)", True, (255, 255, 255))
        time_text_rect = heading_surface.get_rect(center=(WIDTH//2, HEIGHT-20))

        
        alt_surface = self.heading_font.render(str(Func.calculate_height_from_pressure(self.app, self.default_pressure, self.pressure)), True, (255, 255, 255))
        alt_text_rect = heading_surface.get_rect(center=(50, HEIGHT//2-20))

        press_surface = self.press_font.render(str(self.pressure) + " гПа", True, (255, 255, 255))
        press_rect = press_surface.get_rect(center=(WIDTH-100, HEIGHT-20))

        relative_alt_surface = self.heading_font.render(str(self.alt), True, (255, 255, 255))
        relative_alt_text_rect = heading_surface.get_rect(center=(50, HEIGHT//2+20))

        horizon_speed_surface = self.heading_font.render("HorzS " + str(self.horizon_speed), True, (255, 255, 255))
        horizon_speed_rect = horizon_speed_surface.get_rect(center=(WIDTH-100, HEIGHT//2+20))

        vertical_speed_surface = self.heading_font.render("VertS " + str(self.vertical_speed), True, (255, 255, 255))
        vertical_speed_rect = horizon_speed_surface.get_rect(center=(WIDTH-100, HEIGHT//2-20))

        self.screen.blit(self.horizon_sprite_current, self.horizon_rect)

        self.screen.blit(self.settings_sprite, self.settings_rect)
        self.screen.blit(self.menu_sprite, self.menu_rect)

        self.screen.blit(heading_surface, heading_text_rect)

        self.screen.blit(time_surface, time_text_rect)

        self.screen.blit(vertical_speed_surface, vertical_speed_rect)

        self.screen.blit(alt_surface, alt_text_rect)
        self.screen.blit(relative_alt_surface, relative_alt_text_rect)

        self.screen.blit(press_surface, press_rect)

        self.screen.blit(horizon_speed_surface, horizon_speed_rect)

        pygame.draw.line(self.screen, (235, 235, 0), self.indicate_heading[0], self.indicate_heading[1], self.indicate_heading[2])

        self.screen.blit(self.compass_sprite_current, self.compass_rect)

        pygame.draw.line(self.screen, (235, 0, 0), self.left_wing[0], self.left_wing[1], self.left_wing[2])
        pygame.draw.line(self.screen, (235, 0, 0), self.right_wing[0], self.right_wing[1], self.right_wing[2])

        pygame.draw.line(self.screen, (235, 0, 0), self.left_body[0], self.left_body[1], self.left_body[2])
        pygame.draw.line(self.screen, (235, 0, 0), self.right_body[0], self.right_body[1], self.right_body[2])

    def update_save(self):
        with open("save.json", "r", encoding="UTF-8") as f:
            self.save = json.load(f)


    def settings_callback(self):
        self.app.change_group("settings")
    
    def pressure_callback(self):
        self.app.groups["scale_keyboard"].setup_value(value=self.default_pressure, callback=self.pressure_scale_callback, step=0.25)
        self.app.change_group("scale_keyboard")

    def pressure_scale_callback(self, value):
        self.default_pressure = value
        self.app.data["ground_pressure"] = value
        self.app.update_save()

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
        value = int(value.split(":")[0])%360
        self.app.t_h.set_heading(int("".join(self.current_pad.split("m")))-1+5*self.page, value)
        print(value)
        self.current_pad = None


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

        # Graphics
        self.font_big = pygame.font.Font(None, 350)
        self.font_middle = pygame.font.Font(None, 125)
        self.font_small = pygame.font.Font(None, 50)

        # Arrows

        self.arrow_sprite_middle = pygame.transform.flip(pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "arrow.png"), (360, 220)), True, False)
        self.arrow_sprite_small = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "arrow.png"), (200, 100))

        self.box_sprite_small = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "box.png"), (220, 130))
        self.box_sprite_big = pygame.transform.scale(self.box_sprite_small, (750, 450))
        

        self.alt_rect = self.arrow_sprite_middle.get_rect()
        self.alt_rect.center = (250, HEIGHT//2)

        self.speed_rect = self.arrow_sprite_middle.get_rect()
        self.speed_rect.center = (WIDTH-400, HEIGHT//2)

        self.speed_rect_vz = self.arrow_sprite_small.get_rect()
        self.speed_rect_vz.center = (WIDTH-120, HEIGHT//2)

        self.heading_rect = self.box_sprite_small.get_rect()
        self.heading_rect.center = (WIDTH//2, 65)

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

        self.app.touchable.add_rect("to-page-main", self.to_page_rect, "main", self.to_page_callback)
        self.app.touchable.add_rect("scale-main", self.scale_rect, "main", self.scale_callback)

        # Time 
        self.time = datetime.now(timezone.utc).strftime("%H:%M:%S")

        # Horizon Setup
        self.horizon_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Background.png"), (WIDTH*2, HEIGHT*2))
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
        self.left_wing = [(WIDTH//4-100, HEIGHT//2), (WIDTH//4+75, HEIGHT//2), 10]
        self.right_wing = [(WIDTH-WIDTH//4-100, HEIGHT//2), (WIDTH-WIDTH//4+75, HEIGHT//2), 10]

        self.left_body = [(WIDTH//2-50, HEIGHT//2-25), (WIDTH//2, HEIGHT//2), 7]
        self.right_body = [(WIDTH//2+50, HEIGHT//2-25), (WIDTH//2, HEIGHT//2), 7]

        # Pointers
        self.red_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "pointer_red.png"), (WIDTH//2.5, WIDTH//2.5))
        self.red_rect = self.red_sprite.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.red_sprite_current = self.red_sprite

        self.green_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "pointer_green.png"), (WIDTH//2.5, WIDTH//2.5))
        self.green_rect = self.green_sprite.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.green_sprite_current = self.green_sprite




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
        self.alt = Func.calculate_height_from_pressure(self.default_pressure, self.pressure + self.cfg["pressure_diff"])
        self.speed = Func.count_speed_module(self.data["global_position"]["vx"], self.data["global_position"]["vy"])
        self.speed_vz = round(self.data["global_position"]["vz"], 2)
        self.heading = self.data["heading"]
        

        delta_alt = round(self.alt, -1)
        self.alt_comp = []
        for i in range(7):
            self.alt_comp.append(delta_alt + 10*(i-3))
        
        self.alt_pad_delt = round(self.alt - delta_alt)*23
        self.alt_comp.reverse()
        
        delta_speed = round(self.speed, -1)
        self.speed_comp = []
        for i in range(7):
            self.speed_comp.append(delta_speed + 10*(i-3))
        
        self.speed_pad_delt = round(self.speed - delta_speed)*23
        self.speed_comp.reverse()

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

        self.green_sprite_current = pygame.transform.rotate(self.green_sprite, self.heading-self.to_home+90)
        self.green_rect = self.green_sprite_current.get_rect(center=self.green_rect.center)



    def render(self):
        self.screen.blit(self.horizon_sprite_current, self.horizon_rect)
        self.screen.blit(self.compass_sprite_current, self.compass_rect)

        if self.app.t_h.is_active:
            self.screen.blit(self.red_sprite_current, self.red_rect)

        self.screen.blit(self.green_sprite_current, self.green_rect)

        pygame.draw.line(self.screen, (235, 0, 0), self.left_wing[0], self.left_wing[1], self.left_wing[2])
        pygame.draw.line(self.screen, (235, 0, 0), self.right_wing[0], self.right_wing[1], self.right_wing[2])

        pygame.draw.line(self.screen, (235, 0, 0), self.left_body[0], self.left_body[1], self.left_body[2])
        pygame.draw.line(self.screen, (235, 0, 0), self.right_body[0], self.right_body[1], self.right_body[2])

        for i in range(len(self.alt_comp)):
            if self.alt_comp[i] == None or self.alt_comp[i] < 0:
                continue

            text = self.font_middle.render(str(self.alt_comp[i]), False, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(200, self.alt_pad_delt+self.alt_y_pad+(i-3)*230+HEIGHT//2)))

        for i in range(len(self.speed_comp)):
            if self.speed_comp[i] == None or self.speed_comp[i] < 0:
                continue

            text = self.font_middle.render(str(self.speed_comp[i]), False, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(WIDTH-375, self.speed_pad_delt+(i-3)*230+HEIGHT//2)))
        for i in range(len(self.speed_vz_comp)):
            if self.speed_vz_comp[i] == None:
                continue

            text = self.font_small.render(str(abs(self.speed_vz_comp[i])), False, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(WIDTH-100, self.speed_pad_delt_vz+(i-2)*100+HEIGHT//2)))

        self.screen.blit(self.arrow_sprite_middle, self.alt_rect)
        self.screen.blit(pygame.transform.flip(self.arrow_sprite_middle, True, False), self.speed_rect)
        self.screen.blit(self.arrow_sprite_small, self.speed_rect_vz)

        self.screen.blit(self.box_sprite_small, self.heading_rect)

        text = self.font_middle.render(str(self.alt), False, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(200, HEIGHT//2)))

        text = self.font_middle.render(str(self.speed), False, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(WIDTH-375, HEIGHT//2)))

        text = self.font_small.render(str(self.speed_vz), False, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(WIDTH-100, HEIGHT//2)))

        text = self.font_middle.render(str(self.heading), False, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(WIDTH//2, 65)))
            
        self.screen.blit(self.to_page_button, self.to_page_rect)
        self.screen.blit(self.to_page_text, self.to_page_text_rect)

        self.screen.blit(self.scale_button, self.scale_rect)
        self.screen.blit(self.scale_text, self.scale_text_rect)

        text = self.font_middle.render(str(self.time) + " (UTC)", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT-50)))


        if self.is_opened:
            self.screen.blit(self.box_sprite_big, self.minus_rect)
            self.screen.blit(self.box_sprite_big, self.plus_rect)

            self.screen.blit(self.plus_text, self.plus_text.get_rect(center=self.plus_rect.center))
            self.screen.blit(self.minus_text, self.minus_text.get_rect(center=self.minus_rect.center))

        text = self.font_middle.render(str(round(self.data["attitude"]["pitch"])), False, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))        

    def load_cfg(self):
        with open("cfg.json", "r", encoding="UTF-8") as f:
            self.cfg = json.load(f)

    def save_cfg(self):
        with open("cfg.json", "w", encoding="UTF-8") as f:
            json.dump(self.cfg, f, ensure_ascii=False, indent=4)

    def to_page_callback(self):
        self.app.change_group("head_menu")

    def plus_callback(self):
        self.cfg["pressure_diff"] += 0.05
        self.save_cfg()

    def minus_callback(self):
        self.cfg["pressure_diff"] -= 0.05
        self.cfg["pressure_diff"] = round(self.cfg["pressure_diff"], 2)
        self.save_cfg()

    def scale_callback(self):
        self.is_opened = not self.is_opened
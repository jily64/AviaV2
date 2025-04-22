import pygame, os
from dotenv import load_dotenv

load_dotenv()


RESOURCES_PATH = os.getenv("RESOURCES_PATH")
WIDTH, HEIGHT = int(os.getenv("SCREEN_WIDTH")), int(os.getenv("SCREEN_HEIGHT"))

class NumKeyBoard:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen

        self.value = ""
        self.set_value = 1
        self.return_group = "main"
        self.mark = "Ед"

        self.button_size = 240
        self.button_padding = 25

        self.special_value = None

        # Button Text Setup
        self.button_font = pygame.font.Font(None, 225)

        # Value Text
        self.value_font = pygame.font.Font(size=100)
        self.value_text = None
        self.value_text_rect = None

        # 1 Button
        self.one_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (self.button_size, self.button_size))
        self.one_button_rect = self.one_button_sprite.get_rect()
        self.one_button_rect.center = (self.button_size/2+self.button_padding, self.button_size/2+self.button_padding)
        
        self.one_button_text = self.button_font.render("1", True, (255, 255, 255))
        self.one_button_text_rect = self.one_button_text.get_rect()
        self.one_button_text_rect.center = (self.button_size/2+self.button_padding, self.button_size/2+self.button_padding)

        self.app.touchable.add_rect(id="nk_1", obj=self.one_button_rect, group="num_keyboard", listner=self.one_callback)

        # 2 Button 
        self.two_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (self.button_size, self.button_size))
        self.two_button_rect = self.two_button_sprite.get_rect()
        self.two_button_rect.center = (self.button_size/2+self.button_padding*2+self.button_size, self.button_size/2+self.button_padding)
        
        self.two_button_text = self.button_font.render("2", True, (255, 255, 255))
        self.two_button_text_rect = self.two_button_text.get_rect()
        self.two_button_text_rect.center = (self.button_size/2+self.button_padding*2+self.button_size, self.button_size/2+self.button_padding)

        self.app.touchable.add_rect(id="nk_2", obj=self.two_button_rect, group="num_keyboard", listner=self.two_callback)

        # 3 Button 
        self.three_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (self.button_size, self.button_size))
        self.three_button_rect = self.three_button_sprite.get_rect()
        self.three_button_rect.center = ((self.button_size/2+self.button_padding*3+self.button_size*2, self.button_size/2+self.button_padding))
        
        self.three_button_text = self.button_font.render("3", True, (255, 255, 255))
        self.three_button_text_rect = self.three_button_text.get_rect()
        self.three_button_text_rect.center = ((self.button_size/2+self.button_padding*3+self.button_size*2, self.button_size/2+self.button_padding))

        self.app.touchable.add_rect(id="nk_3", obj=self.three_button_rect, group="num_keyboard", listner=self.three_callback)

        # 4 Button
        self.four_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (self.button_size, self.button_size))
        self.four_button_rect = self.four_button_sprite.get_rect()
        self.four_button_rect.center = (self.button_size/2+self.button_padding, self.button_size/2+self.button_padding*2+self.button_size)
        
        self.four_button_text = self.button_font.render("4", True, (255, 255, 255))
        self.four_button_text_rect = self.four_button_text.get_rect()
        self.four_button_text_rect.center = (self.button_size/2+self.button_padding, self.button_size/2+self.button_padding*2+self.button_size)

        self.app.touchable.add_rect(id="nk_4", obj=self.four_button_rect, group="num_keyboard", listner=self.four_callback)

        # 5 Button 
        self.five_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (self.button_size, self.button_size))
        self.five_button_rect = self.five_button_sprite.get_rect()
        self.five_button_rect.center = (self.button_size/2+self.button_padding*2+self.button_size, self.button_size/2+self.button_padding*2+self.button_size)
        
        self.five_button_text = self.button_font.render("5", True, (255, 255, 255))
        self.five_button_text_rect = self.five_button_text.get_rect()
        self.five_button_text_rect.center = (self.button_size/2+self.button_padding*2+self.button_size, self.button_size/2+self.button_padding*2+self.button_size)

        self.app.touchable.add_rect(id="nk_5", obj=self.five_button_rect, group="num_keyboard", listner=self.five_callback)

        # 6 Button 
        self.six_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (self.button_size, self.button_size))
        self.six_button_rect = self.six_button_sprite.get_rect()
        self.six_button_rect.center = (self.button_size/2+self.button_padding*3+self.button_size*2, self.button_size/2+self.button_padding*2+self.button_size)
        
        self.six_button_text = self.button_font.render("6", True, (255, 255, 255))
        self.six_button_text_rect = self.six_button_text.get_rect()
        self.six_button_text_rect.center = (self.button_size/2+self.button_padding*3+self.button_size*2, self.button_size/2+self.button_padding*2+self.button_size)

        self.app.touchable.add_rect(id="nk_6", obj=self.six_button_rect, group="num_keyboard", listner=self.six_callback)

        # 7 Button
        self.seven_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (self.button_size, self.button_size))
        self.seven_button_rect = self.seven_button_sprite.get_rect()
        self.seven_button_rect.center = (self.button_size/2+self.button_padding, self.button_size/2+self.button_padding*3+self.button_size*2)
        
        self.seven_button_text = self.button_font.render("7", True, (255, 255, 255))
        self.seven_button_text_rect = self.seven_button_text.get_rect()
        self.seven_button_text_rect.center = (self.button_size/2+self.button_padding, self.button_size/2+self.button_padding*3+self.button_size*2)

        self.app.touchable.add_rect(id="nk_7", obj=self.seven_button_rect, group="num_keyboard", listner=self.seven_callback)

        # 8 Button 
        self.eight_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (self.button_size, self.button_size))
        self.eight_button_rect = self.eight_button_sprite.get_rect()
        self.eight_button_rect.center = (self.button_size/2+self.button_padding*2+self.button_size, self.button_size/2+self.button_padding*3+self.button_size*2)
        
        self.eight_button_text = self.button_font.render("8", True, (255, 255, 255))
        self.eight_button_text_rect = self.eight_button_text.get_rect()
        self.eight_button_text_rect.center = (self.button_size/2+self.button_padding*2+self.button_size, self.button_size/2+self.button_padding*3+self.button_size*2)

        self.app.touchable.add_rect(id="nk_8", obj=self.eight_button_rect, group="num_keyboard", listner=self.eight_callback)

        # 9 Button 
        self.nine_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (self.button_size, self.button_size))
        self.nine_button_rect = self.nine_button_sprite.get_rect()
        self.nine_button_rect.center = (self.button_size/2+self.button_padding*3+self.button_size*2, self.button_size/2+self.button_padding*3+self.button_size*2)
        
        self.nine_button_text = self.button_font.render("9", True, (255, 255, 255))
        self.nine_button_text_rect = self.nine_button_text.get_rect()
        self.nine_button_text_rect.center = (self.button_size/2+self.button_padding*3+self.button_size*2, self.button_size/2+self.button_padding*3+self.button_size*2)

        self.app.touchable.add_rect(id="nk_9", obj=self.nine_button_rect, group="num_keyboard", listner=self.nine_callback)

        # . Button
        self.dot_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (self.button_size, self.button_size))
        self.dot_button_rect = self.dot_button_sprite.get_rect()
        self.dot_button_rect.center = (self.button_size/2+self.button_padding, self.button_size/2+self.button_padding*4+self.button_size*3)
        
        self.dot_button_text = self.button_font.render(":", True, (255, 255, 255))
        self.dot_button_text_rect = self.dot_button_text.get_rect()
        self.dot_button_text_rect.center = (self.button_size/2+self.button_padding, self.button_size/2+self.button_padding*4+self.button_size*3)

        self.app.touchable.add_rect(id="nk_:", obj=self.dot_button_rect, group="num_keyboard", listner=self.dot_callback)

        # 0 Button 
        self.zero_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (self.button_size, self.button_size))
        self.zero_button_rect = self.zero_button_sprite.get_rect()
        self.zero_button_rect.center = (self.button_size/2+self.button_padding*2+self.button_size, self.button_size/2+self.button_padding*4+self.button_size*3)
        
        self.zero_button_text = self.button_font.render("0", True, (255, 255, 255))
        self.zero_button_text_rect = self.zero_button_text.get_rect()
        self.zero_button_text_rect.center = (self.button_size/2+self.button_padding*2+self.button_size, self.button_size/2+self.button_padding*4+self.button_size*3)

        self.app.touchable.add_rect(id="nk_0", obj=self.zero_button_rect, group="num_keyboard", listner=self.zero_callback)

        # Del Button 
        self.del_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (self.button_size, self.button_size))
        self.del_button_rect = self.del_button_sprite.get_rect()
        self.del_button_rect.center = (self.button_size/2+self.button_padding*3+self.button_size*2, self.button_size/2+self.button_padding*4+self.button_size*3)
        
        self.del_button_text = self.button_font.render("Del", True, (255, 255, 255))
        self.del_button_text_rect = self.del_button_text.get_rect()
        self.del_button_text_rect.center = (self.button_size/2+self.button_padding*3+self.button_size*2, self.button_size/2+self.button_padding*4+self.button_size*3)

        self.app.touchable.add_rect(id="nk_d", obj=self.del_button_rect, group="num_keyboard", listner=self.del_callback)

        # Ready Button
        self.ready_button_text = self.value_font.render("Применить", True, (255, 255, 255))
        self.ready_button_text_rect = self.ready_button_text.get_rect()
        self.ready_button_text_rect.center = (WIDTH-450, HEIGHT//2+250)

        self.ready_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), self.ready_button_text_rect.size)
        self.ready_button_rect = self.ready_button_sprite.get_rect()
        self.ready_button_rect.center = (WIDTH-450, HEIGHT//2+250)

        self.app.touchable.add_rect(id="nk_ready", obj=self.ready_button_rect, group="num_keyboard", listner=self.ready_callback)
        

    def update(self):
        self.value_text = self.value_font.render(str(self.value) + " " + self.mark, True, (255, 255, 255))
        self.value_text_rect = self.value_text.get_rect()
        self.value_text_rect.center = (WIDTH-450, HEIGHT//2-250)

    def render(self):
        self.screen.blit(self.one_button_sprite, self.one_button_rect)
        self.screen.blit(self.two_button_sprite, self.two_button_rect)
        self.screen.blit(self.three_button_sprite, self.three_button_rect)
        self.screen.blit(self.four_button_sprite, self.four_button_rect)
        self.screen.blit(self.five_button_sprite, self.five_button_rect)
        self.screen.blit(self.six_button_sprite, self.six_button_rect)
        self.screen.blit(self.seven_button_sprite, self.seven_button_rect)
        self.screen.blit(self.eight_button_sprite, self.eight_button_rect)
        self.screen.blit(self.nine_button_sprite, self.nine_button_rect)
        self.screen.blit(self.dot_button_sprite, self.dot_button_rect)
        self.screen.blit(self.zero_button_sprite, self.zero_button_rect)
        self.screen.blit(self.del_button_sprite, self.del_button_rect)


        self.screen.blit(self.one_button_text, self.one_button_text_rect)
        self.screen.blit(self.two_button_text, self.two_button_text_rect)
        self.screen.blit(self.three_button_text, self.three_button_text_rect)
        self.screen.blit(self.four_button_text, self.four_button_text_rect)
        self.screen.blit(self.five_button_text, self.five_button_text_rect)
        self.screen.blit(self.six_button_text, self.six_button_text_rect)
        self.screen.blit(self.seven_button_text, self.seven_button_text_rect)
        self.screen.blit(self.eight_button_text, self.eight_button_text_rect)
        self.screen.blit(self.nine_button_text, self.nine_button_text_rect)
        self.screen.blit(self.dot_button_text, self.dot_button_text_rect)
        self.screen.blit(self.zero_button_text, self.zero_button_text_rect)
        self.screen.blit(self.del_button_text, self.del_button_text_rect)

        self.screen.blit(self.value_text, self.value_text_rect)

        self.screen.blit(self.ready_button_sprite, self.ready_button_rect)
        self.screen.blit(self.ready_button_text, self.ready_button_text_rect)
    
    def one_callback(self):
        self.value += "1"

    def two_callback(self):
        self.value += "2"

    def three_callback(self):
        self.value += "3"

    def four_callback(self):
        self.value += "4"

    def five_callback(self):
        self.value += "5"

    def six_callback(self):
        self.value += "6"
    
    def seven_callback(self):
        self.value += "7"

    def eight_callback(self):
        self.value += "8"

    def nine_callback(self):
        self.value += "9"

    def dot_callback(self):
        if ":" not in self.value:
            self.value += ":"

    def zero_callback(self):
        self.value += "0"

    def del_callback(self):
        if self.value != "":
            self.value = self.value[:-1]

    def ready_callback(self):
        self.callback(self.value)
        self.app.change_group(self.return_group)

    def setup_value(self, value, callback, return_group="main", mark="Ед",special_value=None):
        self.value = value
        self.callback = callback
        self.return_group = return_group
        self.special_value = special_value
        self.mark = mark



class ScaleKeyBoard:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.callback = None

        self.value = 1013.25
        self.set_value = 1
        self.return_group = "main"
        self.mark = "гПа"

        # Button Text Setup
        self.button_font = pygame.font.Font(None, 500)

        # Value Text
        self.value_text = None
        self.value_text_rect = None
        self.value_font = pygame.font.Font(None, 500)

        # + Button Setup
        self.plus_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (650, 650))
        self.plus_button_rect = self.plus_button_sprite.get_rect()
        self.plus_button_rect.center = (350, HEIGHT//2)
        
        self.plus_button_text = self.button_font.render("+", True, (255, 255, 255))
        self.plus_button_text_rect = self.plus_button_text.get_rect()
        self.plus_button_text_rect.center = (350, HEIGHT//2)

        self.app.touchable.add_rect(id="sk_plus", obj=self.plus_button_rect, group="scale_keyboard", listner=self.plus_callback)

        # - Button Setup
        self.minus_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), (650, 650))
        self.minus_button_rect = self.minus_button_sprite.get_rect()
        self.minus_button_rect.center = (WIDTH-350, HEIGHT//2)

        self.minus_button_text = self.button_font.render("-", True, (255, 255, 255))
        self.minus_button_text_rect = self.minus_button_text.get_rect()
        self.minus_button_text_rect.center = (WIDTH-350, HEIGHT//2)

        self.app.touchable.add_rect(id="sk_minus", obj=self.minus_button_rect, group="scale_keyboard", listner=self.minus_callback)

        # Ready Button
        self.ready_button_text = self.value_font.render("Применить", True, (255, 255, 255))
        self.ready_button_text_rect = self.ready_button_text.get_rect()
        self.ready_button_text_rect.center = (WIDTH//2, HEIGHT//2+250)

        self.ready_button_sprite = pygame.transform.scale(pygame.image.load(RESOURCES_PATH + "Button.png"), self.ready_button_text_rect.size)
        self.ready_button_rect = self.ready_button_sprite.get_rect()
        self.ready_button_rect.center = (WIDTH//2, HEIGHT//2+250)

        self.app.touchable.add_rect(id="sk_ready", obj=self.ready_button_rect, group="scale_keyboard", listner=self.ready_callback)

    def update(self):
        pass

    def render(self):
        self.value_text = self.value_font.render(str(self.value) + " " + self.mark, True, (255, 255, 255))
        self.value_text_rect = self.value_text.get_rect()
        self.value_text_rect.center = (WIDTH//2, HEIGHT//2-250)

        self.screen.blit(self.plus_button_sprite, self.plus_button_rect)
        self.screen.blit(self.minus_button_sprite, self.minus_button_rect)
        self.screen.blit(self.ready_button_sprite, self.ready_button_rect)

        self.screen.blit(self.value_text, self.value_text_rect)

        self.screen.blit(self.minus_button_text, self.minus_button_text_rect)
        self.screen.blit(self.plus_button_text, self.plus_button_text_rect)
        self.screen.blit(self.ready_button_text, self.ready_button_text_rect)


    def plus_callback(self):
        self.value += self.set_value

    def minus_callback(self):
        self.value -= self.set_value

    def ready_callback(self):
        self.callback(self.value)
        self.app.change_group(self.return_group)

    def setup_value(self, value, callback, step=1, return_group="main"):
        self.value = int(value)
        self.callback = callback
        self.return_group = return_group
        self.set_value = step
# ЕСЛИ ВЫ ВИДИТЕ ЭТУ НАДПИСЬ, ТО ЗАКАЗЧИК НЕ ОПЛАТИЛ ЗАКАЗ
# МОЙ ТЕЛЕГРАММ @oily_oaff

import pygame, os, threading, sys
from dotenv import load_dotenv
from Modules import MAVLinkAdapter, Groups, Touch, TimeHead, Keyboards
from pynput import mouse


load_dotenv()

pygame.init()

WIDTH, HEIGHT = int(os.getenv("SCREEN_WIDTH")), int(os.getenv("SCREEN_HEIGHT"))
print(WIDTH, HEIGHT)

class App:
    def __init__(self):
        self.c = 0
        self.running = True

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        pygame.display.set_caption("Kayoby Customs: AviaVizual (2.8)")

        self.clock = pygame.time.Clock()

        self.mav = MAVLinkAdapter.Adapter('udp:192.168.4.2:14550')
        self.touchable = Touch.Touchable(self)
        self.t_h = TimeHead.TimeHead(self)

        self.data = self.mav.data

        self.c_group = "main"

        self.groups = {
            "main": Groups.Main(self),
            "head_menu": Groups.HeadingPlanner(self),
            "num_keyboard": Keyboards.NumKeyBoard(self)
        }

        self.mav_thread = threading.Thread(target=self.update_mav)
        self.touch_thread = threading.Thread(target=self.run_touch)

        self.run()
        
    
    def run(self):
        print(1)
        self.mav_thread.start()
        #self.mav_thread.join()
        print(2)

        self.touch_thread.start()
        #self.touch_thread.join()

        print(3)
        
        while self.running:
            if self.c >= 1200:
                self.running = False
                print("BBNO$", self.c)
                sys.exit()
                exit("No Money")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            try:
                
                self.mav.update()
                self.groups[self.c_group].update()

                self.screen.fill((0, 0, 0))
                self.t_h.update()
                    
                self.groups[self.c_group].render()

                pygame.display.flip()

                self.clock.tick(15)
                #print(c)
                self.c+=1
            except Exception as e:
                print(e)

                
        pygame.quit()
    
    def change_group(self, group):
        self.c_group = group

    def update_mav(self):
        c = 0
        while self.running:
            self.mav.update()
            self.data = self.mav.data
            #print(self.data)
            

    def update_mav_handle(self):
        self.mav.update()
        self.data = self.mav.data

    def run_touch(self):
        with mouse.Listener(on_click=self.touchable.update) as listener:
            listener.join()

    def ping(self):
        pass


if __name__ == "__main__":
    app = App()
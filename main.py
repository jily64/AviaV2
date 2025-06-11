# ЕСЛИ ВЫ ВИДИТЕ ЭТУ НАДПИСЬ, ТО ЗАКАЗЧИК НЕ ОПЛАТИЛ ЗАКАЗ
# МОЙ ТЕЛЕГРАММ @oily_oaff

import pygame, os, threading, sys, time, asyncio
from dotenv import load_dotenv
from Modules import Groups1, MAVLinkAdapter, Touch, TimeHead, Keyboards
from multiprocessing import Process

pygame.init()

WIDTH, HEIGHT = 1920, 1080
print(WIDTH, HEIGHT)

class App:
    def __init__(self):
        self.c = 0
        self.running = True

        self.sc = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        self.screen = pygame.Surface((WIDTH, HEIGHT))
        pygame.display.set_caption("Kayoby Customs: AviaVizual (2.8)")
        pygame.event.set_allowed([pygame.QUIT])

        self.clock = pygame.time.Clock()

        self.mav = MAVLinkAdapter.Adapter('udp:0.0.0.0:14550')
        self.touchable = Touch.Touchable(self)
        self.t_h = TimeHead.TimeHead(self)

        self.data = self.mav.data

        self.c_group = "main"

        self.groups = {
            "main": Groups1.Main(self)
        }
        

        self.mav_thread = threading.Thread(target=self.update_mav)
        #self.touch_thread = threading.Thread(target=self.run_touch)

        self.run()
        
    
    def run(self):
        print(1)
        self.mav_thread.start()
        #self.mav_thread.join()
        print(2)

        #self.touch_thread.start()
        #self.touch_thread.join()

        print(3)
        while self.data["heading"] == None:
            self.mav.update()
            self.data = self.mav.data

        while self.running:
            #self.mav.update()
            if self.c >= 1200:
                self.running = False
                print("BBNO$", self.c)
                sys.exit()
                exit("No Money")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            try:
                self.groups[self.c_group].update()

                self.screen.fill((0, 0, 0))
                self.t_h.update()
                    
                self.groups[self.c_group].render()

                pygame.display.flip()

                self.clock.tick(60)
                #print(c)
                self.c+=1
                self.sc.blit(self.screen, (0, 0))
            except Exception as e:
                print(e)

                
        pygame.quit()
    
    def change_group(self, group):
        self.c_group = group

    def update_mav(self):
        c = 0
        while self.running:
            for i in range(120):
                self.mav.update()
                self.data = self.mav.data
            #print(self.data)
            

    def update_mav_handle(self):
        self.mav.update()
        self.data = self.mav.data

        """    def run_touch(self):
        with mouse.Listener(on_click=self.touchable.update) as listener:
            listener.join()
        """
    def ping(self):
        pass


if __name__ == "__main__":
    app = App()
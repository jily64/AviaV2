import pygame


RECTS = {}


class Touchable:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen

    def add_rect(self, id, obj:pygame.Rect, group, listner):

        pos_1 = (obj.centerx-obj.width//2, obj.centery-obj.height//2)
        pos_2 = (obj.centerx+obj.width//2, obj.centery+obj.height//2)

        RECTS[id] = [pos_1, pos_2, group, listner, id]
        print(RECTS[id])


    def update(self, x, y, button, pressed):
        try:
            self.app.ping()
        except:
            exit()
        if pressed:
            
            for obj in RECTS:
                if self.app.c_group != RECTS[obj][2]:
                    continue
                if x > RECTS[obj][0][0] and x < RECTS[obj][1][0]:
                    if y > RECTS[obj][0][1] and y < RECTS[obj][1][1]:
                        RECTS[obj][3]()
                        break

    def update_app(self, app):
        self.app = app

    def destroy(self):
        exit()
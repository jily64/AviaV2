import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Rectangle, Color, Rotate, PushMatrix, PopMatrix
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics.svg import Svg
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import NumericProperty

import random

from Modules import MAVLinkAdapter


class Sprite( Image ):
    angle = NumericProperty(0)

    def __init__( self, x=0, y=0, **kwargs ):
        super( Sprite, self ).__init__( **kwargs )
        
        self.angle_to = 0

        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate()
            self.rot.angle  = 0
            self.rot.origin = self.center
            self.rot.axis = (0, 0, 1)
        
        self.allow_stretch = True
        with self.canvas.after:
            PopMatrix()
        
        self.angle = 0
        self.source = '.res/Background.png'
        self.size = (1920*2, 1080*2)
        self.pos = (0, 0)
        self.fit_mode = "contain"

        self.center = (1970/2, 1100/2)

        self.rot.origin = self.center
        self.animate()

    def animateComplete( self, *kargs ):
        Animation.cancel_all( self )
        self.rot.angle = self.angle_to
        self.animate()

    def animate( self ):
        self.anim = Animation( angle=self.angle_to, duration=0.05 )
        self.anim.bind( on_complete=self.animateComplete )
        self.anim.repeat = True
        self.anim.start( self.rot ) 

class AltLabel(Label):
    def __init__(self, **kwargs):
        super(Label, self).__init__(**kwargs)

        self.text = "123"
        self.font_style='H1'
        self.center = (1920//2, 1080//2)



class Applet(App):
    def build(self):
        self.mav = MAVLinkAdapter.Adapter("udp:0.0.0.0:14550")
        self.c = 0

        Window.fullscreen = 'auto'

        root = Widget()

        self.img = Image(source ='.res/Background.png')

        Clock.schedule_interval(self.update, 1 / 150)

        self.spr = Sprite()
        self.altLabel = Label(text='1000 М.')
        self.altLabel.center = (175, 1080//2)
        self.altLabel.font_size = 75

        root.add_widget(self.spr)
        root.add_widget(self.altLabel)

        return root
    
    def update(self, dt):
        self.mav.update()
        if self.mav.data["attitude"]["roll"] != None:
            self.spr.angle_to = self.mav.data["attitude"]["roll"]
            self.spr.rot.origin = (1920/2, 1080/2)

            self.altLabel.text = str(self.mav.data["global_position"]["alt"]) + " М."
        else:
            self.spr.angle_to = 0





if __name__ == '__main__':
    Applet().run()

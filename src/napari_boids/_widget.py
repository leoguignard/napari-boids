"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
import time
from ._BoidFlock import BoidFlock
from napari import Viewer
import numpy as np
from qtpy.QtWidgets import (QWidget,
                            QVBoxLayout,
                            QTabWidget,
                            QPushButton)
from magicgui import widgets
from napari.qt.threading import thread_worker
from functools import partial

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import napari

class BoidViewer(QWidget):
    def update_layer(self, data):
        self.boids_layer.data = data
        self.boids_layer.refresh()

    @thread_worker
    def play_click_worker(self):
        self.play.clicked.disconnect
        if self.nb_workers == 0:
            self.nb_workers += 1
            self.continue_playing = True
            while self.continue_playing:
                time.sleep(.1)
                self.flock.move_boids(5)
                yield self.flock.pos

    def play_click(self, event):
        worker = self.play_click_worker()
        worker.yielded.connect(self.update_layer)
        worker.start()

    def pause_click(self):
        if self.nb_workers == 1:
            self.nb_workers -= 1
            self.play.clicked.connect(self.play_click)
        self.continue_playing = False

    def stop_click(self):
        if self.nb_workers == 1:
            self.nb_workers -= 1
            self.play.clicked.connect(self.play_click)
        self.continue_playing = False
        self.create_flock()

    def reset_all_values_click(self):
        self.rdp1.value=.1
        self.rdp2.value=1
        self.rdp3.value=1
        self.vision.value=100
        self.repulsion.value=20

    @staticmethod
    def reset_value_click(value, slider):
        slider.value = value

    def update_values(self):
        self.flock.rdp1 = self.rdp1.value/100
        self.flock.rdp2 = self.rdp2.value/100
        self.flock.rdp3 = self.rdp3.value/100
        self.flock.vision = self.vision.value
        self.flock.repulsion_range = self.repulsion.value

    @staticmethod
    def create_button(button_name):
        btn = QPushButton(button_name)
        btn.native = btn
        btn.name = button_name
        btn.label = button_name
        btn._explicitly_hidden = False
        btn.tooltip = ''
        btn.label_changed = None
        return btn

    def create_slider(self, name, value, min, max, change_connect=None):
        label = widgets.Label(value=name)
        slider = widgets.FloatSlider(value=value, min=min, max=max)
        btn = widgets.PushButton(name='Reset')
        btn.changed.connect(partial(self.reset_value_click, value=value, slider=slider))
        s_container = widgets.Container(widgets=[slider, btn],
                                        layout='horizontal', labels=False)
        container = widgets.Container(widgets=[label, s_container], labels=False)
        if change_connect:
            slider.changed.connect(change_connect)
        return slider, container

    def create_flock(self):
        arena_shape = (1000, 1000)
        nb_boids = 100
        if not hasattr(self, 'center'):
            points = [[0             , 0             ],
                      [0             , arena_shape[1]],
                      [arena_shape[0], arena_shape[1]],
                      [arena_shape[0], 0             ] ]
            l = self.viewer.add_points(points)
            self.center = self.viewer.camera.center
            self.zoom = self.viewer.camera.zoom
            self.viewer.layers.remove(l)
        self.flock = BoidFlock(nb_boids, vision=self.vision.value,
                               arena_shape=arena_shape,
                               init_shape=((250, 750), (250, 750)),
                               rdp1=self.rdp1.value/100,
                               rdp2=self.rdp2.value/100,
                               rdp3=self.rdp3.value/100,
                               reflection=True,
                               speed_limit=15,
                               repulsion_range=self.repulsion.value,
                               margin=5)

        if hasattr(self, 'boids_layer'):
            self.viewer.layers.remove(self.boids_layer)
        properties = {'color': self.flock.color}
        self.boids_layer = self.viewer.add_points(self.flock.pos,
                                                  cache=False,
                                                  properties=properties,
                                                  face_color='color',
                                                  face_colormap='rainbow',
                                                  name='Boids')
        self.viewer.camera.center = self.center
        self.viewer.camera.zoom = self.zoom
        self.boids_layer.refresh()

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        np.random.seed(0)
        self.continue_playing = False
        self.nb_workers = 0
        self.play = self.create_button('Play')
        self.play.clicked.connect(self.play_click)
        pause = self.create_button('Pause')
        pause.clicked.connect(self.pause_click)
        stop = self.create_button('Restart')
        stop.clicked.connect(self.stop_click)
        reset_values = self.create_button('Reset values')
        reset_values.clicked.connect(self.reset_all_values_click)
        control_w = widgets.Container(widgets=[self.play, pause, stop],
                                      labels=False, layout='horizontal')

        self.rdp1, rdp1_w = self.create_slider('Attraction', value=.1, min=0.01, max=1,
                                               change_connect=self.update_values)
        self.rdp2, rdp2_w = self.create_slider('Avoidance', value=1, min=0.1, max=10,
                                               change_connect=self.update_values)
        self.rdp3, rdp3_w = self.create_slider('Mimicking', value=1, min=0.1, max=10,
                                               change_connect=self.update_values)
        self.vision, vision_w = self.create_slider('Vision radius', value=100, min=10, max=1000,
                                               change_connect=self.update_values)
        self.repulsion, repulsion_w = self.create_slider('Avoidance radius', value=20, min=1, max=40,
                                               change_connect=self.update_values)
        w = widgets.Container(widgets=[control_w,
                                       rdp1_w,
                                       rdp2_w,
                                       rdp3_w,
                                       vision_w,
                                       repulsion_w,
                                       reset_values],
                                       labels=False)

        w.native.layout().addStretch(1)
        layout = QVBoxLayout()
        layout.addStretch(1)
        self.setLayout(layout)
        self.layout().addWidget(w.native)
        w.native.adjustSize()

        self.create_flock()











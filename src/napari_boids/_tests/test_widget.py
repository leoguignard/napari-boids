import numpy as np
import time

from napari_boids import BoidViewer


# make_napari_viewer is a pytest fixture that returns a napari viewer object
# capsys is a pytest fixture that captures stdout and stderr output streams
def test_example_q_widget(make_napari_viewer, capsys):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()
    viewer = Viewer()
    my_widget = BoidViewer(viewer)
    my_widget.play_click()
    my_widget.rdp1.value = .2
    my_widget.rdp3.value = 9
    my_widget.reset_all_values_click()
    my_widget.stop_click()
    time.sleep(.2)
    my_widget.play.click()
    time.sleep(.2)
    my_widget.pause_click()
    time.sleep(.2)
    my_widget.play.click()
    my_widget.nb_birds.value = 20
    my_widget.play.click()
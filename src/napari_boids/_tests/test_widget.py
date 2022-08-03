import numpy as np

from napari_boids import BoidViewer


# make_napari_viewer is a pytest fixture that returns a napari viewer object
# capsys is a pytest fixture that captures stdout and stderr output streams
def test_example_q_widget(make_napari_viewer, capsys):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()
    my_widget = BoidViewer(viewer)
    my_widget.play.click()
    my_widget.pause.click()
    my_widget.stop.click()
    my_widget.play.click()
    my_widget.rdp1.value = .2



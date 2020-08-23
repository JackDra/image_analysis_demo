from traits.api import (
    HasStrictTraits, Instance, DelegatesTo, on_trait_change, 
    File, Button, Callable
)
from traitsui.api import UItem, View, Item
from enable.component_editor import ComponentEditor

from chaco.api import Plot, ImageData, ImagePlot
import numpy as np
from PIL import Image
import os
from skimage import feature
from scipy import stats

# generate a test image to display
BLANK_IMG = np.zeros((1920, 1080, 3)).astype(np.uint8)

def load_image(image_path):
    """ load an image from disk """
    pil_image = Image.open(image_path)
    return np.array(pil_image).swapaxes(0, 1)[::-1, :, :]

def canny_analysis(input_image):
    """ run canny edge detection on black and white version of image """
    # convert to black and white since canny only works on greyscale
    bw_image = np.dot(input_image, [0.2989, 0.5870, 0.1140]).astype(np.uint8)
    # run the edge detection
    edge_image = feature.canny(bw_image)
    # will return boolean array, need to convert True -> 252, False -> 0
    edge_image = edge_image.astype(np.uint8) * 252
    # chaco will only plot rgb images, so we duplicate the value for rgb    
    return np.repeat(edge_image[:, :, np.newaxis], 3, axis=2)

class ImageAnalysis(HasStrictTraits):

    image_file = File(filter=['*.jpg','*.png'])

    plot = Instance(Plot)

    plot_data = Instance(ImageData)

    img_plot = Instance(ImagePlot)

    data = DelegatesTo('plot_data')

    analyse = Button()

    analysis_function = Callable()

    def _analyse_changed(self):
        if self.analysis_function is not None:
            self.data = self.analysis_function(self.data)

    def _image_file_changed(self):
        if os.path.isfile(self.image_file):
            self.data = load_image(self.image_file)

    def _plot_data_default(self):
        return ImageData(data=BLANK_IMG)

    def _plot_default(self):
        plot = Plot(datasources={'image': self.plot_data})
        self.img_plot = plot.img_plot(
            'image', origin='top left'
        )[0]
        return plot

    def default_traits_view(self):
        return View(
            Item('image_file'),
            UItem('analyse'),
            UItem('plot', editor=ComponentEditor()),
            resizable=True
        )

image_analysis = ImageAnalysis(analysis_function=canny_analysis)
image_analysis.configure_traits()

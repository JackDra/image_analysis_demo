from traits.api import (
    HasStrictTraits, Instance, DelegatesTo, on_trait_change, 
    File, Callable, List, Range, Array, Bool, cached_property, Property
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
    # just some corrections to get the orientation right
    return np.array(pil_image).swapaxes(0, 1)[::-1, :, :]

def canny_analysis(input_image, sigma):
    """ 
        run canny edge detection on black and white version of image 
        sigma is passed to the canny function, it does smoothing.
    """
    # convert to black and white since canny only works on greyscale
    bw_image = np.dot(input_image, [0.2989, 0.5870, 0.1140]).astype(np.uint8)
    # run the edge detection
    edge_image = feature.canny(bw_image, sigma=sigma)
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

    analysed_data = Property(
        Array(dtype='uint8'), 
        depends_on='original_data,analysis_function,input_argument'
    )

    original_data = Array(dtype='uint8')

    view_analysis = Bool()

    analysis_function = Callable()

    input_argument = Range(1, 5)

    def _input_argument_changed(self):
        if self.view_analysis:
            self.data = self.analysed_data

    def _view_analysis_changed(self):
        if self.view_analysis:
            self.data = self.analysed_data
        elif len(self.original_data) > 0:
            self.data = self.original_data
            
    @cached_property
    def _get_analysed_data(self):     
        if self.analysis_function is not None and len(self.original_data) > 0:
            return self.analysis_function(self.original_data, self.input_argument)
        return np.array()

    def _image_file_changed(self):
        if os.path.isfile(self.image_file):
            self.original_data = load_image(self.image_file)
            if not self.view_analysis:
                self.data = self.original_data

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
            Item('view_analysis'),
            Item('input_argument'),
            UItem('plot', editor=ComponentEditor()),
            resizable=True
        )

image_analysis = ImageAnalysis(analysis_function=canny_analysis)
image_analysis.configure_traits()

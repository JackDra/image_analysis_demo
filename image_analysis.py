from traits.api import (
    HasStrictTraits, Instance, DelegatesTo, on_trait_change, File
)
from traitsui.api import UItem, View, Item
from enable.component_editor import ComponentEditor

from chaco.api import Plot, ImageData, ImagePlot
import numpy as np
from PIL import Image
import os

# generate a test image to display
BLANK_IMG = np.zeros((1920, 1080, 3)).astype(np.uint8)

def load_image(image_path):
    """ load an image from disk """
    pil_image = Image.open(image_path)
    return np.array(pil_image).swapaxes(0, 1)[::-1, :, :]

class ImageAnalysis(HasStrictTraits):

    image_file = File(filter=['*.jpg','*.png'])

    plot = Instance(Plot)

    plot_data = Instance(ImageData)

    img_plot = Instance(ImagePlot)

    data = DelegatesTo('plot_data')

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
            UItem('plot', editor=ComponentEditor()),
            resizable=True
        )

image_analysis = ImageAnalysis()
image_analysis.configure_traits()

from traits.api import HasStrictTraits, Instance, DelegatesTo, on_trait_change
from traitsui.api import UItem, View
from enable.component_editor import ComponentEditor

from chaco.api import Plot, ImageData, ImagePlot
import numpy as np

# generate a test image to display
BLANK_IMG = np.arange(800*600*3)
BLANK_IMG = BLANK_IMG.reshape(800, 3, 600)
BLANK_IMG = BLANK_IMG.swapaxes(1,2)
BLANK_IMG = BLANK_IMG.astype(np.uint8) % 252

class ImageAnalysis(HasStrictTraits):

    plot = Instance(Plot)

    plot_data = Instance(ImageData)

    img_plot = Instance(ImagePlot)

    data = DelegatesTo('plot_data')

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
            UItem('plot', editor=ComponentEditor()),
            resizable=True
        )

image_analysis = ImageAnalysis()
image_analysis.configure_traits()

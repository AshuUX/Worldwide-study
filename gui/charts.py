from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Set dark theme for matplotlib
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.fig.tight_layout()

def create_bar_chart(canvas, labels, values, title):
    canvas.axes.cla()
    canvas.axes.bar(labels, values, color='#007acc')
    canvas.axes.set_title(title)
    canvas.fig.tight_layout()
    canvas.draw()

def create_fan_chart(canvas, x, p10, p50, p90, title):
    canvas.axes.cla()
    canvas.axes.fill_between(x, p10, p90, color='rgba(0,122,204,0.2)', label='P10-P90')
    canvas.axes.plot(x, p50, color='#007acc', marker='o', label='P50')
    canvas.axes.set_title(title)
    canvas.axes.legend()
    canvas.fig.tight_layout()
    canvas.draw()

def create_prob_curve(canvas, samples, threshold, title):
    canvas.axes.cla()
    canvas.axes.hist(samples, bins=50, density=True, alpha=0.7, color='#007acc')
    canvas.axes.axvline(threshold, color='red', linestyle='--', label='Threshold')
    canvas.axes.set_title(title)
    canvas.axes.legend()
    canvas.fig.tight_layout()
    canvas.draw()

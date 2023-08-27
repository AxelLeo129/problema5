import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QInputDialog

class UniformChargeLine:
    def __init__(self, start, end, charge, n_segments=100):
        self.start = np.array(start)
        self.end = np.array(end)
        self.charge = charge
        self.n_segments = n_segments
        self.dL = (self.end - self.start) / self.n_segments

    def electric_field(self, point):
        r = np.array(point)
        lambda_charge = self.charge / np.linalg.norm(self.end - self.start)
        e_field = np.zeros(2)

        for i in range(self.n_segments):
            r_prime = self.start + i * self.dL
            r_rel = r - r_prime
            r_rel_magnitude = np.linalg.norm(r_rel)
            dE = (1 / (4 * np.pi * 8.85e-12)) * (lambda_charge / r_rel_magnitude**3) * r_rel * np.linalg.norm(self.dL)
            e_field += dE

        return e_field

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.canvas = FigureCanvas(plt.figure())
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.grid(True)
        layout.addWidget(self.canvas)

        self.point_number = 0
        self.canvas.mpl_connect('button_press_event', self.on_click)

        self.btn = QPushButton('Calculate Electric Field')
        self.btn.clicked.connect(self.calculate_field)
        layout.addWidget(self.btn)

        self.btn_zoom_in = QPushButton('Zoom In')
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        layout.addWidget(self.btn_zoom_in)

        self.btn_zoom_out = QPushButton('Zoom Out')
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        layout.addWidget(self.btn_zoom_out)

        self.setLayout(layout)
        self.show()

    def zoom_in(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.set_xlim([xlim[0]*0.5, xlim[1]*0.5])
        self.ax.set_ylim([ylim[0]*0.5, ylim[1]*0.5])
        self.canvas.draw()

    def stop_measurement(self):
        self.stop = True

    def zoom_out(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.set_xlim([xlim[0]*2, xlim[1]*2])
        self.ax.set_ylim([ylim[0]*2, ylim[1]*2])
        self.canvas.draw()

    def on_click(self, event):
        if event.inaxes is not self.ax:
            return
        
        xp, yp = event.xdata, event.ydata
        
        if self.point_number == 0:
            self.x1, self.y1 = xp, yp
            self.ax.plot(self.x1, self.y1, 'bo')
            self.canvas.draw()
            self.point_number += 1
        elif self.point_number == 1:
            self.x2, self.y2 = xp, yp
            self.ax.plot(self.x2, self.y2, 'bo')
            self.ax.plot([self.x1, self.x2], [self.y1, self.y2], 'b-', linewidth=6)
            self.canvas.draw()
            self.point_number += 1
        else:
            self.ax.plot(xp, yp, 'go')
            self.point_of_interest = [xp, yp]
            self.canvas.draw()

    def calculate_field(self):
        if self.point_number < 2:
            return

        charge, ok = QInputDialog.getDouble(self, 'Input', 'Enter charge (Coulombs):')
        if not ok:
            return

        self.line = UniformChargeLine([self.x1, self.y1], [self.x2, self.y2], charge)

        e_field = self.line.electric_field(self.point_of_interest)
        e_field_magnitude = np.linalg.norm(e_field)
        e_field_direction = e_field / e_field_magnitude

        scale = 1e5  # just for visualization purposes
        xp, yp = self.point_of_interest
        self.ax.arrow(xp, yp, e_field_direction[0] * scale, e_field_direction[1] * scale, head_width=0.2, head_length=0.3, fc='red', ec='red')
        self.ax.annotate(f'{e_field_magnitude:.2e} N/C', (xp, yp), textcoords="offset points", xytext=(0,10), ha='center')
        self.canvas.draw()

        print(f'Electric field at ({xp}, {yp}) is {e_field_magnitude} N/C')
        
app = QApplication(sys.argv)
ex = App()
sys.exit(app.exec_())

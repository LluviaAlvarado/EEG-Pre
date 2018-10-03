import wx
import matplotlib

matplotlib.use('WXAgg')

# Imports
import wx.lib.agw.buttonpanel
import wx.lib.scrolledpanel
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# Local Imports
from WindowEditor import *
from KMeans import *
from sklearn.metrics import silhouette_samples, silhouette_score
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas


class SilhouetteWindow(wx.Frame):

    def __init__(self, pa, k, data, selected, p):
        wx.Frame.__init__(self, pa, -1, "Silhouette", style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
        self.SetSize(600, 600)
        self.pbutton = p
        self.Maximize()
        self.fig = None
        self.Centre()
        self.selceted = selected
        self.k = k
        self.db = []
        for r in range(len(data)):
            t = []
            for c in range(len(data[r]) - 1):
                t.append(data[r][c])
            self.db.append(t)
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2)
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN, size=(600, 600))
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        lefSizer = wx.BoxSizer(wx.VERTICAL)
        self.rightSizer = wx.BoxSizer(wx.VERTICAL)
        infoLabel = wx.StaticText(self.pnl, label="Atributo")
        self.opc1C = wx.ComboBox(self.pnl, value=selected[0], style=wx.CB_READONLY, choices=selected)
        self.opc2C = wx.ComboBox(self.pnl, value=selected[1], style=wx.CB_READONLY, choices=selected)
        applyButton = wx.Button(self.pnl, label="Aplicar")
        applyButton.Bind(wx.EVT_BUTTON, self.update)
        self.silhouette()
        self.canvas = FigureCanvas(self.pnl, -1, self.fig)
        lefSizer.Add(infoLabel, 0, wx.EXPAND | wx.ALL, 2)
        lefSizer.Add(self.opc1C, 0, wx.EXPAND | wx.ALL, 2)
        lefSizer.Add(self.opc2C, 0, wx.EXPAND | wx.ALL, 2)
        lefSizer.Add(applyButton, 0, wx.EXPAND | wx.ALL, 2)
        self.rightSizer.Add(self.canvas, 0, wx.EXPAND | wx.ALL, 2)
        baseContainer.Add(lefSizer, 0, wx.EXPAND | wx.ALL, 0)
        baseContainer.Add(self.rightSizer, 0, wx.EXPAND | wx.ALL, 0)
        self.pnl.SetSizer(baseContainer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        self.pbutton.onCloseModule()
        self.Hide()

    def update(self, event):
        o1 = self.opc1C.GetSelection()
        o2 = self.opc1C.GetSelection()
        self.canvas.ClearBackground()
        self.rightSizer.Clear()
        self.silhouette(o1, o2)
        self.canvas.draw()

    def silhouette(self, opc1=0, opc2=1):
        db = np.array(self.db)
        self.fig.clf()
        self.fig.add_subplot(self.ax1)
        self.fig.add_subplot(self.ax2)
        self.fig.set_size_inches(13, 6)
        n_clusters = len(self.k.clusters)
        # The 1st subplot is the silhouette plot
        # The silhouette coefficient can range from -1, 1 but in this example all
        # lie within [-0.1, 1]
        self.ax1.set_xlim([-0.1, 1])
        # The (n_clusters+1)*10 is for inserting blank space between silhouette
        # plots of individual clusters, to demarcate them clearly.
        self.ax1.set_ylim([0, len(db) + (n_clusters + 1) * 10])
        silhouette_avg = silhouette_score(db, self.k.labels)
        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(db, self.k.labels)
        y_lower = 10
        for i in range(n_clusters):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = \
                sample_silhouette_values[self.k.labels == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.nipy_spectral(float(i) / n_clusters)
            self.ax1.fill_betweenx(np.arange(y_lower, y_upper),
                                   0, ith_cluster_silhouette_values,
                                   facecolor=color, edgecolor=color, alpha=0.7)

            # Label the silhouette plots with their cluster numbers at the middle
            self.ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        self.ax1.set_title("Visualización de silhouette.")
        self.ax1.set_xlabel("Valor de silhouette")
        self.ax1.set_ylabel("Etiqueta del cluster")

        # The vertical line for average silhouette score of all the values
        self.ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

        self.ax1.set_yticks([])  # Clear the yaxis labels / ticks
        self.ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

        # 2nd Plot showing the actual clusters formed
        dX = db[:, 0]
        dY = db[:, 2]
        aX = []
        aY = []
        for a in dY:
            aY.append(round(float(a), 2))
        for a in dX:
            aX.append(round(float(a), 2))

        colors = cm.nipy_spectral(self.k.labels.astype(float) / n_clusters)
        self.ax2.scatter(aX, aY, marker='.', s=30, lw=0, alpha=0.7,
                         c=colors, edgecolor='k')

        # Labeling the clusters
        centers = self.k.clusters
        # Draw white circles at cluster centers
        self.ax2.scatter(centers[:, opc1], centers[:, opc2], marker='o',
                         c="white", alpha=1, s=200, edgecolor='k')

        for i, c in enumerate(centers):
            self.ax2.scatter(c[opc1], c[opc2], marker='$%d$' % i, alpha=1,
                             s=50, edgecolor='k')

        self.ax2.set_title("Visualización de los clusters")
        self.ax2.set_xlabel("Primer Atributo")
        self.ax2.set_ylabel("Segundo Atributo")

        plt.suptitle(("Análisis de Silhouette para KMeans clustering "
                      "con %d clusters." % n_clusters),
                     fontsize=14, fontweight='bold')


import wx
from import_file import import_file
import os
import sys
import dabo

#import latest
import imp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
#import matplotlib
#matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg
#from matplotlib.figure import Figure
#from numpy import arange, sin, pi
import numpy as np


class Extract_Data(object):
    def __init__(self):
        if dimension == 'two':
            if task == 'tracking':
                self.extract_tracking()   # CHANGE
            elif task == 'goal':
                self.extract_tracking()   # CHANGE
        else:
            if task == 'tracking':
                self.extract_tracking()
            elif task == 'goal':
                self.extract_tracking()   # CHANGE

    def extract_tracking(self):   # extract data from the algorithm file for tracking
        self.load_file()
        global x_UAV, y_UAV, z_UAV, x_target, y_target, z_target
        x_UAV = latest.plot_points[1]
        y_UAV = latest.plot_points[2]
        z_UAV = latest.plot_points[3]

        x_target = latest.plot_points[4]
        y_target = latest.plot_points[5]
        z_target = latest.plot_points[6]


    def load_file(self):
        openFileDialog = wx.FileDialog(None, "Open the desired algorithm", "", "",
                                           "Python files (*.py)|*.py",
                                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        alg_path = openFileDialog.GetPath()
        #global alg_path_filename
        alg_path_filename = openFileDialog.GetFilename
        #print alg_path_filename.strip('.py')
        alg_path_directory = openFileDialog.GetDirectory()
##        global latest
##        latest = imp.load_source(alg_path_filename, alg_path)
        global latest
        latest = import_file(alg_path)
##        sys.path.append(os.path.abspath(alg_path_directory))
##        import alg
        openFileDialog.Destroy()


class PlotFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Simulation', (756,100), (600,532))
        data_extraction = Extract_Data()
        self.plot_data()
        self.draw_obstacle()

    def add_toolbar(self):
        self.toolbar = NavigationToolbar2WxAgg(self.canvas)
        self.toolbar.Realize()
        if wx.Platform == '__WXMAC__':
            # Mac platform (OSX 10.3, MacPython) does not seem to cope with
            # having a toolbar in a sizer. This work-around gets the buttons
            # back, but at the expense of having the toolbar at the top
            self.SetToolBar(self.toolbar)
        else:
            # On Windows platform, default window size is incorrect, so set
            # toolbar width to figure width.
            tw, th = self.toolbar.GetSizeTuple()
            fw, fh = self.canvas.GetSizeTuple()
            # By adding toolbar in sizer, we are able to put it at the bottom
            # of the frame - so appearance is closer to GTK version.
            # As noted above, doesn't work for Mac.
            self.toolbar.SetSize(wx.Size(fw, th))
            self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        # update the axes menu on the toolbar
        self.toolbar.update()

    def plot_close(self):
        '''Function to close the plotframe(current)'''
        self.Close()

    def plot_data(self):
        '''FUnction to plot the data on the figure embedded on the frame panel'''
        self.figure = plt.figure()   # create a figure to plot data
        self.canvas = FigureCanvas(self, -1, self.figure)
        if dimension == 'two':
            self.axes = plt.axes()   # create 2D axes in the figure
            self.axes.plot(x_UAV,y_UAV,'o-r')
            if task == 'tracking':
                self.axes.plot(x_target, y_target, 'o-g')
            plt.axis('equal')
        else:
            self.axes = plt.axes(projection = '3d')   # create 3D axes in the figure
            self.axes.plot(np.array(x_UAV), np.array(y_UAV),np.array(z_UAV),'-r')
            if task == 'tracking':
                self.axes.plot(x_target, y_target, z_target, 'o-g')
            self.axes.set_zlabel('z axis')
            #self.plot_equal_axis()
            self.axisEqual3D(self.axes)
        self.axes.set_xlabel('x axis')
        self.axes.set_ylabel('y axis')
        self.axes.margins(0.05)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.add_toolbar()

    def draw_obstacle(self):
        for shape in obstacle_type:
            if shape == 'sphere':
                pass





    def axisEqual3D(self, ax):
        extents = np.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
        sz = extents[:,1] - extents[:,0]
        centers = np.mean(extents, axis=1)
        maxsize = max(abs(sz))
        r = maxsize/2
        for ctr, dim in zip(centers, 'xyz'):
            getattr(ax, 'set_{}lim'.format(dim))(ctr - r, ctr + r)

class MainFrame(wx.Frame):
    ''' Frame that controls the plot'''
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Motion Planning', (15,100), (741,531))
        self.mainframe_panel = wx.Panel(self)
        self.mainframe_panel.Bind(wx.EVT_MOTION, self.OnMove)   # Add a event handler which tracks pointer motion
        # Add a button which shows the plot on click
        self.plotshow_but = wx.Button( self.mainframe_panel,-1, 'PLOT', size=(100,20),pos=(40,380))
        self.plotshow_but.Bind(wx.EVT_BUTTON, self.PlotShow)
        # Add a button which is used to add obstacles
        self.addobstacle_but = wx.Button( self.mainframe_panel,-1, 'Add Obstacle', size=(100,20),pos=(40,200))
        self.addobstacle_but.Bind(wx.EVT_BUTTON, self.AddObstacle)
        # Add text and a combo box for selection of type of simulation (2D or 3D)
        self.simulationtype_text = wx.StaticText(self.mainframe_panel, -1, 'Simulation Type', size = (80,20), pos = (20, 20))
        self.simulationtype_combobox = wx.ComboBox(self.mainframe_panel, pos = (105,17.5), size = (90,30),
                                                        choices = ['3 Dimension', '2 Dimension'], style = wx.CB_READONLY)
        self.simulationtype_combobox.Bind(wx.EVT_COMBOBOX, self.SimulationType)
        # Add text and a combo box for selection of task (tracking or goal)
        self.tasktype_text = wx.StaticText(self.mainframe_panel, -1, 'TASK', size = (30,20), pos = (70, 50))
        self.tasktype_combobox = wx.ComboBox(self.mainframe_panel, pos = (105,48), size = (90, 30),
                                                        choices = ['Tracking', 'Goal'], style = wx.CB_READONLY)
        self.tasktype_combobox.Bind(wx.EVT_COMBOBOX, self.TaskType)
        # Add a text control which shows the position of mouse pointer on the frame
        self.posCtrl = wx.TextCtrl(self.mainframe_panel, -1, "", pos=(640, 450))

        # INTPUTS
        global dimension, task, algorithm, obstacle_type, obstalce_pos
        dimension = ''
        task = ''
        algorithm = 'modified dubins'
        obstacle_type = []
        obstacle_pos = []

    def AddObstacle(self, event):
        '''Function to add obstacles in simulation environment'''
        obs_sel_dlg = wx.SingleChoiceDialog(None, 'Select the type of obstacle', 'Obstacle Selection', ['Scatter', 'Sphere', 'Cylinder' ])
        if obs_sel_dlg.Show() == wx.ID_OK:
                new_obstacle = obs_sel_dlg.GetStringSelection()
                obstacle_type.append(new_obstacle)
        self.obstacleproperties = ObstacleProperties()
        self.obstacleproperties.Show()


    def OnMove(self, event):
        '''Function to get the position of pointer on the frame'''
        pos = event.GetPosition()
        self.posCtrl.SetValue("%s, %s" % (pos.x, pos.y))

    def MatplotlibPlot(self, event):
        pass
        #self.plotframe.plot_close()   # close the plotframe

    def PlotShow(self, event):
        global obstacle_pos
        try:
            self.plotframe.plot_close()
        except:
            print 'error'
        else:
            print 'no error'

        self.plotframe = PlotFrame(self)   # create a plot frame, as the child of the main(current) frame
        self.plotframe.Show(True)
        print obstacle_pos

    def SimulationType(self, event):
        item = event.GetSelection()
        #global dimension
        if item == 0:   # seletion is '3 Dimension'
            dimension = 'three'
        else:   # selection is '2 Dimension'
            dimension = 'two'

    def TaskType(self, event):
        item = event.GetSelection()
        global task
        if item == 0:   # selection is 'tracking'
            task = 'tracking'
            alg_sel_dlg = wx.SingleChoiceDialog(None, 'What is the algorithm you want to use?', 'Single Choice', ['Modified Dubins', 'Add Later 1', 'Add Later 2' ])
            if alg_sel_dlg.Show() == wx.ID_OK:
                algorithm = alg_sel_dlg.GetStringSelection()
        elif item == 1:   # selection is 'goal'
            task = 'goal'


class PictureFrame(wx.Frame):
    '''Frame class that displays an welcome image'''
    def __init__(self, image, parent = None, id = -1, pos = wx.DefaultPosition, title = 'Interactive Motion Planning'):
        temp = image.ConvertToBitmap()
        size = temp.GetWidth(), temp.GetHeight()   # Get image size to create a frame of same size
        wx.Frame.__init__(self, parent, id, title, pos, size)
        self.bmp = wx.StaticBitmap(parent = self, bitmap = temp)
        wx.FutureCall(4000, self.Destroy)   # close the welcome frame after 4 seconds

class ObstacleProperties(wx.Frame):
    '''Frame class that is used to specify obstacle properties'''
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Obstacle Properties', (100,100), (250,250))
        self.ObstacleProperties_panel = wx.Panel(self)
        # Add a textctrl to get x position of obstacle
        self.x_pos = wx.TextCtrl(self.ObstacleProperties_panel, -1, "", size = (80,20), pos=(20, 20))
        self.x_pos_text = wx.StaticText(self.ObstacleProperties_panel, -1, 'x position', pos = (105,17.5), size = (90, 30))
        self.y_pos = wx.TextCtrl(self.ObstacleProperties_panel, -1, "", size = (80,20), pos=(20, 50))
        self.y_pos_text = wx.StaticText(self.ObstacleProperties_panel, -1, 'y position', pos = (105,47.5), size = (90, 30))
        self.z_pos = wx.TextCtrl(self.ObstacleProperties_panel, -1, "", size = (80,20), pos=(20, 80))
        self.z_pos_text = wx.StaticText(self.ObstacleProperties_panel, -1, 'z position', pos = (105,77.5), size = (90, 30))
        self.radius = wx.TextCtrl(self.ObstacleProperties_panel, -1, "", size = (80,20), pos=(20, 0))
        self.radius_text = wx.StaticText(self.ObstacleProperties_panel, -1, 'radius', pos = (105,77.5), size = (90, 30))
        self.ok_button = wx.Button(self.ObstacleProperties_panel, -1, 'OK', pos = (50, 120), size = (50,30))
        self.ok_button.Bind(wx.EVT_BUTTON, self.OkBut)



    def OkBut(self, event):
        # INPUTS
        global obstalce_pos
        obstacle_pos = []
        print obstacle_pos
        x = float(self.x_pos.GetValue())
        y = float(self.y_pos.GetValue())
        z = float(self.z_pos.GetValue())
        print x, y, z
##        x = self.x_pos.GetValue()
        new_obstacle_pos = [x,y,z]
        #new_obstacle_pos = [int(self.x_pos.GetValue()), int(self.y_pos.GetValue()), int(self.z_pos.GetValue())]
        obstacle_pos.append(new_obstacle_pos)
        print obstacle_pos


class App(wx.App):
    def OnInit(self):
        # Display main frame
        self.mainframe = MainFrame()
        self.mainframe.Show()

        # Display the welcome frame with picture and close it after few seconds
        image = wx.Image('different type obstacles.jpg', wx.BITMAP_TYPE_JPEG)
        self.pictureframe = PictureFrame(image)
        self.pictureframe.Centre()
        self.pictureframe.Show()
        self.SetTopWindow(self.pictureframe)

        return True


if __name__ == '__main__':
    app = App(False)
    app.MainLoop()
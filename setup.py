import Tkinter
import FileDialog

from setuptools import setup
import py2exe, sys, os
from glob import glob
import matplotlib
import Functions
import excel
import latest

##imagepath = 'C:/Documents and Settings/Integration Lab/Desktop/GUI'
##images = [os.path.join(imagepath, image) for image in os.listdir(imagepath)]

##datafiles = [("Microsoft.VC90.CRT", glob(r'C:\Documents and Settings\Integration Lab\Desktop\Microsoft.VC90.CRT\*.*'))
##             ]

datafiles = [('./datafiles', ['./datafiles/different_type_obstacles.jpg', './latest.py'
                          ,'./datafiles/Target_Positions.xlsx']) ]
##datafiles.extend(('./algorithm', ['./latest.py'] ))
datafiles.extend(matplotlib.get_py2exe_datafiles())
##datafiles.extend(
##("Microsoft.VC90.CRT",
##glob(r'C:\Documents and Settings\Integration Lab\Desktop\Microsoft.VC90.CRT\*.*') ) )
#sys.argv.append('py2exe')

setup(windows=['GUI.py'],
      data_files= datafiles,
      options={"py2exe": {"includes": ["matplotlib", "excel", "latest", "Functions", "FileDialog", "matplotlib.backends.backend_tkagg" ]

                        }

              }
      )



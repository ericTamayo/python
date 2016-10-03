#
# Display Lane Rate Calculator - Ver 0.0
# Author : Ajith Peter
# Date   : 8/25/16

import win32api, win32con
import gtk

def GetDisplayLaneRate():
	print "-----------------------------------------------------"
	window = gtk.Window()
	# the screen contains all monitors
	screen = window.get_screen()
	monitors = []
	nmons = screen.get_n_monitors()
	print "Number of monitors : %d" % nmons
	for m in range(nmons):
	  mg = screen.get_monitor_geometry(m)
	  print "Monitor %d: %d x %d" % (m,mg.width,mg.height)
	  monitors.append(mg)

	PyDISPLAY_DEVICE = win32api.EnumDisplayDevices(None,0,0)
	print "Display Device Name : %s" % (PyDISPLAY_DEVICE.DeviceName)
	print "Display Device Make : %s" % (PyDISPLAY_DEVICE.DeviceString)
	print "Display Device Drive ID : %s" % (PyDISPLAY_DEVICE.DeviceID)
	print "Display Device Registry : %s" % (PyDISPLAY_DEVICE.DeviceKey)
	PyDEVMODE = win32api.EnumDisplaySettings(PyDISPLAY_DEVICE.DeviceName,0)
	print "Color resolution : %d" % (PyDEVMODE.BitsPerPel)
	print "Pixel Width : %d" %(PyDEVMODE.PelsWidth)
	print "Pixel Height : %d" % (PyDEVMODE.PelsHeight)
	print "Refresh Rate : %d" % (PyDEVMODE.DisplayFrequency)
	print "Display Orientation (0 Normal) : %d" % (PyDEVMODE.DisplayOrientation)

	k = gtk.gdk.screen_get_default()
	print "Width x Height in mm : %d x %d " % (k.get_width_mm(), k.get_height_mm())
	print "Width x Height with 1.5 Scaling %d x %d" % (k.get_width() * 1.5, k.get_height() * 1.5)
	f =  (k.get_height() * 1.5) * (k.get_width() * 1.5) * PyDEVMODE.DisplayFrequency * (PyDEVMODE.BitsPerPel * 0.25)
	print "Display Per Lane Rate (assuming 4 lanes) :  %f Gbps" % (f / 1000000000)
	print "-----------------------------------------------------"

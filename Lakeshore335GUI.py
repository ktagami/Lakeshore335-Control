from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import time
import threading
import psutil
import os
import pyqtgraph as pg
import numpy as np
import scipy as sp
import scipy.interpolate
import serial
 


class GUI(QWidget):

    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)
        
        grid = QGridLayout()
        grid.addWidget(self.Temperature_Channels(), 1, 0)
        grid.addWidget(self.Controller_Connect(), 0, 0)
        grid.addWidget(self.Heater_Select(), 0, 1)
        grid.addWidget(self.plot_temp(), 1, 1)
        self.setLayout(grid)
        global curve_func
        self.setWindowTitle("LakeShore 335 Temperature Controller")
        self.resize(400, 300)
        calcurve_temp_points = [4.2,13.7,77.35,295]
        calcurve_ohms_points = [14907,1506,463,95]
        curve_func = sp.interpolate.interp1d(calcurve_ohms_points,calcurve_temp_points,'quadratic')


    def Temperature_Channels(self):
        self.GB = QGroupBox("Set and Read Temperature")
        layout0 = QGridLayout()
        layout1 = QGridLayout()
        layout2 = QGridLayout()
        #self.setLayout(layout)
        
        
        #Lines for Entering Desired temperature
        self.temp_set_label = QLabel()
        self.temp_set_label.setText('Setpoint:')
        layout0.addWidget(self.temp_set_label,1,1)
        
        self.temp_1_entry = QDoubleSpinBox(self)
        self.temp_1_entry.setDecimals(4)
        self.temp_1_entry.setRange(0,335)
        layout0.addWidget(self.temp_1_entry, 1, 2)
        self.temp_1_entry.valueChanged.connect(self.on_tempChange1_clicked)

        self.temp_2_entry = QDoubleSpinBox(self)
        self.temp_2_entry.setDecimals(4)
        self.temp_2_entry.setRange(0,335)
        layout0.addWidget(self.temp_2_entry, 1, 3)
        self.temp_2_entry.valueChanged.connect(self.on_tempChange2_clicked)

        #Buttons for sending setting temperature
        self.temp_send_label = QLabel()
        self.temp_send_label.setText('Send Setpoint:')
        layout0.addWidget(self.temp_send_label,2,1)
        
        self.temp_1_button = QPushButton('Set Temp 1',self)
        layout0.addWidget(self.temp_1_button, 2, 2)
        self.temp_1_button.clicked.connect(self.on_temp1_button_clicked)

        self.temp_2_button = QPushButton('Set Temp 2',self)
        layout0.addWidget(self.temp_2_button, 2, 3)
        self.temp_2_button.clicked.connect(self.on_temp2_button_clicked)
        
        #Connect Buttons for sending set temperature

        #Display of current temperature
        self.temp_read_label = QLabel()
        self.temp_read_label.setText('Current Temp (K):')
        layout0.addWidget(self.temp_read_label,3,1)
        
        self.lcd_1 = QLCDNumber(self)
        self.lcd_1.setDigitCount(8)
        self.lcd_1.setSegmentStyle(QLCDNumber.Flat)
        layout0.addWidget(self.lcd_1, 3, 2)

        self.lcd_2 = QLCDNumber(self)
        self.lcd_2.setDigitCount(8)
        self.lcd_2.setSegmentStyle(QLCDNumber.Flat)
        layout0.addWidget(self.lcd_2, 3, 3)
        
        
        
        #Display of current sensor reading (mV and ohms)
        self.temp_read_label = QLabel()
        self.temp_read_label.setText('Sensor Reading (mV, ohms):')
        layout0.addWidget(self.temp_read_label,4,1)
        
        self.lcd_3 = QLCDNumber(self)
        self.lcd_3.setDigitCount(8)
        self.lcd_3.setSegmentStyle(QLCDNumber.Flat)
        layout0.addWidget(self.lcd_3, 4, 2)

        self.lcd_4 = QLCDNumber(self)
        self.lcd_4.setDigitCount(8)
        self.lcd_4.setSegmentStyle(QLCDNumber.Flat)
        layout0.addWidget(self.lcd_4, 4, 3)
        #Display of current Heater Level
        
        self.htr_read_label = QLabel()
        self.htr_read_label.setText('Heater Level (%):')
        layout0.addWidget(self.htr_read_label,5,1)
        
        self.lcd_h1 = QLCDNumber(self)
        self.lcd_h1.setDigitCount(8)
        self.lcd_h1.setSegmentStyle(QLCDNumber.Flat)
        layout0.addWidget(self.lcd_h1, 5, 2)

        self.lcd_h2 = QLCDNumber(self)
        self.lcd_h2.setDigitCount(8)
        self.lcd_h2.setSegmentStyle(QLCDNumber.Flat)
        layout0.addWidget(self.lcd_h2, 5, 3)
        
        self.GB.setLayout(layout0)
        return self.GB
    def Controller_Connect(self):
        self.GB = QGroupBox("Connect and read Temperature Controller")
        layout1 = QGridLayout()
        #Buttons for starting and stopping temperature reading
        self.start_button = QPushButton('Start Temp Monitoring',self)
        layout1.addWidget(self.start_button, 2, 1)
        self.start_button.clicked.connect(self.on_start_button_clicked)
        self.start_button.clicked.connect(self.plot_t)

        self.stop_button = QPushButton('Stop Temp Monitoring',self)
        layout1.addWidget(self.stop_button, 2, 2)
        self.stop_button.clicked.connect(self.on_stop_button_clicked)
        
        #Button for connecting to serial port
        self.Connect = QPushButton('Connect',self)
        layout1.addWidget(self.Connect, 1, 1)
        self.Connect.clicked.connect(self.on_Connect_button_clicked)
        
        self.Disconnect = QPushButton('Disconnect',self)
        layout1.addWidget(self.Disconnect, 1, 2)
        self.Disconnect.clicked.connect(self.on_Disconnect_button_clicked)
        
        #Button for reseting tempperature controller
        self.Reset = QPushButton('Reset',self)
        layout1.addWidget(self.Reset, 1, 3)
        self.Reset.clicked.connect(self.on_rst_button_clicked)
        
        #Button for saving data to file
        self.SaveData = QPushButton('Save Temp Data',self)
        layout1.addWidget(self.SaveData, 3, 1)
        self.SaveData.clicked.connect(self.on_save_button_clicked)

        self.GB.setLayout(layout1)
        return self.GB
    def Heater_Select(self):
        self.GB = QGroupBox("Set Heater Level")
        layout2 = QGridLayout()
        
        self.heater1_label = QLabel()
        self.heater1_label.setText('Cold Finger')
        layout2.addWidget(self.heater1_label,1,1)
 
        self.lvl_set = QComboBox()
        #self.comboBox.setGeometry(QRect(40, 40, 491, 31))
        self.lvl_set.setObjectName(("lvl_set"))
        self.lvl_set.addItem("Off")
        self.lvl_set.addItem("Low")
        self.lvl_set.addItem("Medium")
        self.lvl_set.addItem("High")
        layout2.addWidget(self.lvl_set, 2,1)
        self.lvl_set.currentIndexChanged.connect(self.heater_onClicked)
       
        self.htr_entry = QDoubleSpinBox(self)
        self.htr_entry.setDecimals(2)
        self.htr_entry.setRange(0,100)
        layout2.addWidget(self.htr_entry, 3, 1)
        self.htr_entry.valueChanged.connect(self.on_htr_clicked)
        
        ####radio buttons for selecting mode
        self.comboBox = QComboBox()
        #self.comboBox.setGeometry(QRect(40, 40, 491, 31))
        self.comboBox.setObjectName(("comboBox"))
        self.comboBox.addItem("Off")
        self.comboBox.addItem("Closed Loop")
        self.comboBox.addItem("Zone")
        self.comboBox.addItem("Open Loop")
        layout2.addWidget(self.comboBox, 4,1)
        self.comboBox.currentIndexChanged.connect(self.heater_mode_onClicked)
        ############### HEATER 2 Section ########################
        
        self.heater2_label = QLabel()
        self.heater2_label.setText('Probe')
        layout2.addWidget(self.heater2_label,1,2)
        
        self.lvl2_set = QComboBox()
        #self.comboBox.setGeometry(QRect(40, 40, 491, 31))
        self.lvl2_set.setObjectName(("lvl2_set"))
        self.lvl2_set.addItem("Off")
        self.lvl2_set.addItem("Low")
        self.lvl2_set.addItem("Medium")
        self.lvl2_set.addItem("High")
        layout2.addWidget(self.lvl2_set, 2,2)
        self.lvl2_set.currentIndexChanged.connect(self.heater2_onClicked)
        
        self.htr2_entry = QDoubleSpinBox(self)
        self.htr2_entry.setDecimals(2)
        self.htr2_entry.setRange(0,100)
        layout2.addWidget(self.htr2_entry, 3, 2)
        self.htr2_entry.valueChanged.connect(self.on_htr2_clicked)
        
        ####radio buttons for selecting mode
        self.comboBox2 = QComboBox()
        #self.comboBox.setGeometry(QRect(40, 40, 491, 31))
        self.comboBox2.setObjectName(("comboBox"))
        self.comboBox2.addItem("Off")
        self.comboBox2.addItem("Closed Loop")
        self.comboBox2.addItem("Zone")
        self.comboBox2.addItem("Open Loop")
        layout2.addWidget(self.comboBox2, 4,2)
        self.comboBox2.currentIndexChanged.connect(self.heater2_mode_onClicked)
        #layout = QHBoxLayout()
        #layout.addLayout(layout0)
        #layout.addLayout(layout1)
        #layout.addLayout(layout2)
        #layout.addStretch(1)
        self.GB.setLayout(layout2)
        #self.setGeometry(500, 300, 400, 200)
        #self.setWindowTitle('Temperature Controller')
        #self.show()
        return self.GB
        
    def plot_temp(self):
        self.GB = QGroupBox("Set and Read Temperature")
        layout3 = QGridLayout()
        self.temp_plot = pg.PlotWidget()
        self.temp_plot_item = self.temp_plot.plotItem
        self.temp_plot_item.setLabels(left='temperature (K)')
        self.temp_plot_item.setLabels(bottom='Time (min)')
        layout3.addWidget(self.temp_plot, 1, 1)
        
        self.timer3 = pg.QtCore.QTimer()
        self.timer3.timeout.connect(self.plot_t)
        
        self.GB.setLayout(layout3)
        return self.GB
        
    #### Heater 1 ####

    def heater_onClicked(self,i):
        try:
            ser.write(b'RANGE 1 %a \n' % i)
        except:
            print('failed to write heater 1 range')

    def heater_mode_onClicked(self,i):
        try:
            ser.write(b'OUTMODE 1,%a,1,1 \n' % i)
            print(i)
        except:
            print('failed to write heater 1 mode')
                
    def on_htr_clicked(self):
        htr_entry = self.sender()
        try:
            ser.write(b'MOUT 1 %a \n' % htr_entry.value())
        except:
            print('failed to write heater 1 %')

    #### Heater 2 ####

    def heater2_onClicked(self,i):
        try:
            ser.write(b'RANGE 2 %a \n' % i)
        except:
            print('failed to write heater 2 range')

    def heater2_mode_onClicked(self,i):
        try:
            ser.write(b'OUTMODE 2,%a,1,1 \n' % i)
            print(i)
        except:
            print('failed to write heater 2 mode')
                
    def on_htr2_clicked(self):
        htr_entry = self.sender()
        try:
            ser.write(b'MOUT 2 %a \n' % htr2_entry.value())
        except:
            print('failed to write heater 2 %')

    def on_tempChange1_clicked(self):
        global set_temp1
        set_temp1 = 300
        set_temp1 = self.temp_1_entry.value()    
    def on_tempChange2_clicked(self):
        global set_temp2
        set_temp2 = 300
        set_temp2 = self.temp_2_entry.value()
        
    def on_temp1_button_clicked(self):
        try:
            ser.write(b'SETP 1 %a \n' % set_temp1)
        except:
            print('failed to write setpoint 1')
    def on_temp2_button_clicked(self):
        try:
            ser.write(b'SETP 2 %a \n' % set_temp2)
        except:
            print('failed to write setpoint 1')



    def plot_t(self):
        global t_list,temp1_list,temp2_list,htr_list
    
        ser.write(b'KRDG? A\n')
        time.sleep(0.06)
        temp1 = float(ser.readline()[0:7]) 
        self.lcd_1.display(temp1)
        ser.write(b'SRDG? A\n')
        time.sleep(0.06)
        reading1 = float(ser.readline()[0:7]) 
        ser.write(b'KRDG? B\n')
        time.sleep(0.06)
        temp2 = float(ser.readline()[0:7]) 
        self.lcd_1.display(temp1)
        ser.write(b'SRDG? B\n')
        time.sleep(0.06)
        reading2 = float(ser.readline()[0:7]) 
        #try:
        #    temp2 = float(curve_func(reading2))
        #except:
        #    temp2 = 0
        self.lcd_2.display(temp2)
        self.lcd_3.display(reading1)
        self.lcd_4.display(reading2)
        
        ser.write(b'HTR? \n')
        time.sleep(0.06)
        htr = float(ser.readline()[0:7])
        self.lcd_h1.display(htr)
        
        self.temp_plot.clear()
        try: 
            t_list
        except:
            t_list = []
        try:
            temp1_list
            temp2_list
        except:
            temp1_list = []
            temp2_list = []
        try:
            reading1_list
        except:
            reading1_list = []
        try:
            reading2_list
        except:
            reading2_list = []
        try:
            htr_list
        except:
            htr_list = []
        #time.sleep(0.5)
        t = np.array((time.time()-time0)/60)
        t_ = [t]
        t_list.append(t)
        temp1_list.append(temp1)
        temp2_list.append(temp2)
        reading1_list.append(reading1)
        reading2_list.append(reading2)
        temp1_= np.array([temp1])
        temp2_= np.array([temp2])
        htr_list.append(htr)
        try:
            setpoint = np.array([set_temp1])
            self.temp_plot.addLine(y=setpoint, pen = pg.mkPen('r',width = 0.9))
            print(set_temp1)
        except:
            print('no setpoint temp found')
        try:
            PI_1 = pg.PlotDataItem(t_list,temp1_list, pen = pg.mkPen('g',width = 0.9))
            PI_2 = pg.PlotDataItem(t_list,temp2_list, pen = pg.mkPen('y',width = 0.9))
            self.temp_plot.addItem(PI_1)
            self.temp_plot.addItem(PI_2)
        except:
            print('no data')
            print(temp1_list)
        #self.temp_plot.plot(t_,temp1_)
        #self.temp_plot.plot(t_,setpoint, symbol = 'o', symbolSize = 5, symbolBrush = 'b')
        #self.temp_plot.plot(t_list,temp1_list, symbol = 'o', symbolSize = 5, symbolBrush = 'r')


    def on_start_button_clicked(self):
        global time0, ser
        time0 = time.time()
        state=True
        try:
            ser
        except:
            ser = serial.Serial('COM8',57600, parity=serial.PARITY_ODD, bytesize = 7)
        try:
            self.timer3.start(1000)
        except:
            print('temp collection failed')

    def on_stop_button_clicked(self):
        
        self.timer3.stop()
       # self.close()
    
    def on_Connect_button_clicked(self):
        try:
            global ser
            ser = serial.Serial('COM8',57600, parity=serial.PARITY_ODD, bytesize = 7)
        except:
            print('failed to open serial port')
        
    def on_Disconnect_button_clicked(self):
        try:
            ser.close()
        except:
            print('failed to close serial port')
    def on_save_button_clicked(self):
        try:
            np.savetxt('temperature log',[t_list,temp1_list,temp2_list,reading1_list,reading2_list])
        except:
           print('failed to save data')
           
    def on_rst_button_clicked(self):
        try:
            ser.write(b'*RST \n')
            print('device reset')
        except:
           print('failed to reset device')


if __name__ == '__main__':

    app = QApplication(sys.argv)
    G = GUI()
    G.show()
    sys.exit(app.exec_())

def kill_proc_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    if including_parent:
        parent.kill()

me = os.getpid()
kill_proc_tree(me)

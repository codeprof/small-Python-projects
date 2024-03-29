#!/usr/bin/python3
# -*- coding: utf-8 -*-

#The MIT License (MIT)
#Copyright (c) 2016 Stefan Möbius and Manuel Soukup

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import math
import statistics
import subprocess
import dbus
import argparse

# please check your number of the touchscreen with xinput list

XINPUT_NUMBER="13"

#####

def calc(inp, num_inputs, num_outputs):
	out = [0.0 for col in range(num_outputs)]
	for i in range(num_outputs):
		res = 0.0
		for j in range(num_inputs):
				out[i] += weights[i][j][int((math.copysign(1,inp[j])+1)/2)] * inp[j]
	return out	

rotation_matrices = { 
			1 : ' 1  0  0   0  1  0   0  0  1',
			2 : ' 0 -1 1 1 0 0 0 0 1',
			4 : '-1 0 1 0 -1 1 0 0 1',
			8 : ' 0 1 0 -1 0 1 0 0 1' }   

xrandr_rotation = { 
					  1 : 0,
					  2 : 1,
					  4 : 2,
					  8 : 3 }   
					  
def rot(rotationArg):
	try:
		bus = dbus.SessionBus()

		the_object = bus.get_object("org.kde.KScreen", "/backend")
		the_interface = dbus.Interface(the_object, "org.kde.kscreen.Backend")

		reply = the_interface.getConfig()

		reply["outputs"][0]["rotation"] = dbus.Double(float(rotationArg), variant_level=1)

		the_interface.setConfig(reply)
		the_interface.setConfig(reply)
		the_interface.setConfig(reply) #fix redraw problem
	except:
		subprocess.call(["sudo","xrandr", "-o", str(xrandr_rotation[rotationArg])])
		
		

weights = [[[-3.98451914, -0.00526829],
        [ 1.69422094, -1.3032    ],
        [ 0.39181237, -0.51728175],
        [ 0.16442079,  0.0498543 ]],

       [[ 2.60878645, -3.3437604 ],
        [-3.83359202, -1.24903074],
        [-0.38571   ,  0.42935028],
        [ 0.99099488, -0.39721866]],

       [[ 1.15349671,  3.54844658],
        [ 1.76076555, -2.10664579],
        [ 0.3340033 , -0.05241627],
        [ 0.80715387,  0.24041399]],

       [[ 3.36441981, -3.49239282],
        [ 3.62575247,  1.71476538],
        [-0.99880686,  0.81857969],
        [ 0.93902188,  0.22924538]]]
            
  
					  
					          
last_rotation = -1

arr = {'x':[], 'y':[], 'z':[]}

while True:
	
	for dim in ['x', 'y', 'z']:
		file = open('/sys/bus/iio/devices/iio:device1/in_accel_' + dim + '_raw')
		arr[dim].insert(0, float(file.read()) / 16000.0)
		arr[dim] = arr[dim][:3]
		file.close()
			
	if (len(arr['x']) == 3) and (len(arr['y']) == 3) and (len(arr['z']) == 3):
		inp = [statistics.median(arr['x']), statistics.median(arr['y']), statistics.median(arr['z']), 1]

		out = calc(inp, 4, 4)
		print(out)
		maxval = -1.0
		maxidx = -1
		for idx, val in enumerate(out):
			if val >= maxval:
				maxval = val
				maxidx = idx
		rotation = 2**(3 - maxidx)

		#print (value)

		if rotation != last_rotation:
			
			#subprocess.call(["python3", "rotate_kde.py", "--rotation", str(rotation) ])
			rot(rotation)
			subprocess.call(['xinput set-prop '+ XINPUT_NUMBER +' "Coordinate Transformation Matrix" ' + rotation_matrices[rotation]],shell=True) 
			last_rotation = rotation

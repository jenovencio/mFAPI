# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 15:23:46 2017

@author: jenovencio
"""

from mFAPI.modeFRONTIER import modeFrontier 
from matplotlib import pyplot as plt


mf = modeFrontier()
prjpath = r"D:\Cases\2017_02_10_mFAPI_for_python\case1.prj"

mf.setprj(prjpath) # seeting the prj

mf.intro()  # performing the introspection


# Changing variables properties
mf.INPUTS['x_1']['lowerbound']=100.0
mf.INPUTS['x_2']['lowerbound']=-10
mf.INPUTS['x_3']['lowerbound']=-10
#
mf.INPUTS['x_1']['upperbound']=200.0
mf.INPUTS['x_2']['upperbound']=10
mf.INPUTS['x_3']['upperbound']=10

mf.INPUTS['x_1']['base']=4
mf.INPUTS['x_2']['base']=0
mf.INPUTS['x_3']['base']=0


# running the prj
mf.run()


# getting the results
d = mf.getresults()


# ploting the results with matplotlib
plt.plot(d['min_y'],'o')
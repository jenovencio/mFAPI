# mFAPI
This module is an API to provide access to basic modeFRONTIER functionalities throught python.
To acess modeFRONITER show import the module into python namespace:

from mFAPI.modeFRONTIER import modeFrontier 

Then, it can instanciate the modeFrontier class by:

mf = modeFrontier()

Now it is possible to set the prj path, and perform introspections, change variables propesties, run and get the DesignTable

mf.intro()



mf.INPUTS['x_1']['lowerbound']=100.0
mf.INPUTS['x_2']['lowerbound']=-10
mf.INPUTS['x_3']['lowerbound']=-10

mf.INPUTS['x_1']['upperbound']=200.0
mf.INPUTS['x_2']['upperbound']=10
mf.INPUTS['x_3']['upperbound']=10

mf.INPUTS['x_1']['base']=4
mf.INPUTS['x_2']['base']=0
mf.INPUTS['x_3']['base']=0

mf.run()

d = mf.getresults() # equivalent to mf.designTable

where d is a pandas dataframe.

# IMPORTANT
In order to use mFAPI the user must install pandas library (http://pandas.pydata.org/)




# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 15:30:32 2017

@author: jenovencio
"""


import subprocess
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import tostring
from collections import defaultdict
import pandas as pd
import csv
from matplotlib import pyplot as plt

from xml.dom.minidom import Document
import copy
import os

class modeFrontier():
    def __init__(self,prj="",mFpath = u'C:\Program Files\ESTECO\modeFRONTIER2017R1'):
        
        self.mFpath = mFpath
        self.lastfolder = ""
        self.setprj(prj)
        self.getprjname()
        
        
        
    def openGUI(self):
        
        
        try:
            command = '"' + self.mFpath    + '//bin//modeFRONTIER.exe" ' + self.prj
            print(command)
            subprocess.call(command, shell=True)
        except:    
            print("Please make sure that mFpath was ser correctly")
        
    def intro(self):
        #print("nothing")
#        try:
            
            command = '"' +  self.mFpath + '\\bin\\modefrontier.bat"'' -generate_batch_xml "' + self.prj + '"' #+ '-batch_xml intro.xml'
            print(command)
            subprocess.call(command, shell=True)
            filename = self.prjname + ".xml"
            tree = ET.parse(filename)
            root = tree.getroot()
            xmldict=etree_to_dict(root)               
            self.__xmldict__ = xmldict
            var = {}
            inputs = {}
            outputs = {}
            obj = {}
            cons = {}
            for k in xmldict['BATCH_MODE']['DESIGNS_DB']['VARIABLES']['VARIABLE']:
                
                if k['class'].split('.')[-1]== 'DesignInputVariable':
                    var[k['name']] = {'name':k['name'],'value':k['value'],'lowerbound':k['lowerbound'],
                                    'upperbound':k['upperbound'],'base':k['base'],'type':'input'}
                    inputs[k['name']] = var[k['name']]
                                    
                
                elif k['class'].split('.')[-1]== 'DesignOutputVariable':
                    var[k['name']] = {'name':k['name'],'value':k['value'],'type':'output'}
                    outputs[k['name']] = var[k['name']]
                
                elif k['class'].split('.')[-1]== 'DesignObjective':
                    if k['kind']==-1:
                        kind = "minimize"
                    else:
                        kind = "maximize"
                    
                    var[k['name']] = {'name':k['name'],'value':k['value'],
                                        'kind':kind,'type':'objective'}
                    obj[k['name']] = var[k['name']]

                elif k['class'].split('.')[-1]== 'DesignConstraint':
                    
                    if k['kind']==-1:
                        kind = "greater than"
                    elif k['kind']==1:
                        kind = "less than"
                    else:
                        kind = "equal to"
                        
                    var[k['name']] = {'name':k['name'],'limit':k['limit'],
                                        'kind':kind,'tolerance':k['tolerance'],'type':'constraint'}
                    
                    cons[k['name']] = var[k['name']]
                else:
                    None
                                     
                
            self.VARIABLES = var    
            self.INPUTS = inputs
            self.OUTPUTS = outputs
            self.OBJECTIVES = obj
            self.CONSTRAINS = cons
            
            
#        except:    
#            print("Please make sure that mFpath was ser correctly")
#            return None

    def run(self):
        
        # update xml        
        self.__uptadexml__()
        command = '"' +  self.mFpath + '\\bin\\modefrontier.bat"'' -batch "' + self.prj +  '"' + \
                  ' -batch_xml temp.xml' #+ '-batch_xml intro.xml'
        print(command)                  
        subprocess.call(command, shell=True)        

        # delete temp.xml        
        #os.remove("temp.xml")
        
    def __uptadexml__(self):    
        print("nothing")
        
        
        
        
        for i,j in enumerate(self.__xmldict__['BATCH_MODE']['DESIGNS_DB']['VARIABLES']['VARIABLE']):
        
            # update input        
            if j['class'].split('.')[-1] == 'DesignInputVariable':         
                
                doe = self.__xmldict__['BATCH_MODE']['DOE_DB']['VARIABLES']['VARIABLE'][i]
                mordo = self.__xmldict__['BATCH_MODE']['MORDO_DB']['VARIABLES']['VARIABLE'][i]                 
                
                j['value'] = str(self.INPUTS[j['name']]['value'])
                j['lowerbound'] = str(self.INPUTS[j['name']]['lowerbound'])
                j['upperbound'] = str(self.INPUTS[j['name']]['upperbound'])
                j['base'] = str(self.INPUTS[j['name']]['base'])
                
                doe['value'] = j['value']
                doe['lowerbound'] = j['lowerbound']
                doe['upperbound'] = j['upperbound']                 
                doe['base'] = j['base']
                
                mordo['value'] = j['value']
                mordo['lowerbound'] = j['lowerbound']
                mordo['upperbound'] = j['upperbound']                 
                mordo['base'] = j['base']                 
                
                
            elif j['class'].split('.')[-1]== 'DesignObjective':         
                
                # update objectives         
                if self.OBJECTIVES[j['name']]['kind'] == "minimize":
                    j['kind'] = '-1'
                else:
                    j['kind'] = '1'
                
            
            elif j['class'].split('.')[-1]== 'DesignConstraint':                         
                
                # update contraints
                k = self.CONSTRAINS[j['name']]['kind'] 
                if k=="greater than":
                    j['kind'] = '-1'
                elif k=="less than":
                    j['kind'] = '1'
                else:
                    j['kind'] = '0' 
                    
                j['tolerance']=self.CONSTRAINS[j['name']]['tolerance']    

        
        xml = dict2xml(self.__xmldict__)
        xmlname = "temp.xml" 
        f = open(xmlname,"wb")
        f.write(xml.display())
        f.close()
        return xmlname

    def getresults(self):         
        ''' this function get the last des file and return the design table
        as a pandas data frame
        
        '''
        try:
            self.__getlastFolder__() # method that update the self.lastfoler variable
         
            self.desfile = self.lastfolder + '\\' + self.prjprefix + '.des'
        
            self.designTable = self.__readdes__(self.desfile)         
            return self.designTable
        except:
            print("There is no des file. Please run the prj file in order to get results.")
        
    def setprj(self, prj=""):
        ''' enter will the full prj name
        if the prj is the folder of the python execution folder, then the full 
        path may be omited 
        '''
        
        self.prj = prj 
        self.getprjname()

    
    def getprjname(self):
        
        self.prjname = self.prj.split("\\")[-1]
        self.prjpath = ("\\").join(self.prj.split("\\")[0:-1])
        return self.prjname
        
    def __getlastFolder__(self):
        
        self.prjprefix = self.prjname.split('.prj')[0]
        b = ['_0000','_000','_00','_0']
        
        for i in range(200):
            if i < 10:
                k = 0
                runfolder = self.prjpath + '\\' + self.prjprefix + b[k] + str(i)
            
            elif i < 100:    
                k = 1
                runfolder = self.prjpath + '\\' + self.prjprefix + b[k] + str(i)

            elif i < 1000:
                k = 2
                runfolder = self.prjpath + '\\' + self.prjprefix + b[k] + str(i)
                
            else:
                k = 3
                runfolder = self.prjpath + '\\' + self.prjprefix + b[k] + str(i)
            
            
            if os.path.isdir(runfolder):
                
                lastfolder = runfolder
                
            else:

                self.lastfolder = lastfolder
                return self.lastfolder
                
    def __readdes__(self,filename, sep='\t',header=22):
        with open(filename, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=sep, quotechar='|')
            data =[]
            for i,row in enumerate(spamreader):
                #print(i)
                if i== (header - 1):
                    #print '* '.join(row)
                    for j,c in enumerate(row):
                        row[j] = c.replace(' ','').replace('<','').replace('>','')
                        
                    h = row
                    
                elif i > (header - 1):
                    for j,c in enumerate(row):
                        try:                    
                            row[j] = float(c.replace(' ',''))
                        except:
                            row[j] = (c.replace(' ',''))
    
                    data.append(row)
        datastruc = {}
        for k,s in enumerate(h):
            columnk =[i[k] for i in data]
            datastruc[s]=columnk
        
        d = pd.Series(datastruc) 
        
        return d
 
 
 
class dict2xml(object):
    #doc     = Document()

    def __init__(self, structure):
        self.doc     = Document()
        if len(structure) == 1:
            rootName    = str(structure.keys()[0])
            self.root   = self.doc.createElement(rootName)

            self.doc.appendChild(self.root)
            self.build(self.root, structure[rootName])

    def build(self, father, structure):
        if type(structure) == dict:
            for k in structure:
                #print(k)
                if k[0].islower() : 
                    #print(k)
                    #tag = self.doc.createElement(k)                   
                    #print(tag)
                    #tag.attributes[k]=structure[k]
                    father.attributes[k]=structure[k]
                    
                else:
                    tag = self.doc.createElement(k)                   
                    father.appendChild(tag)
                    self.build(tag, structure[k])

        elif type(structure) == list:
            #print(structure)
            grandFather = father.parentNode
            tagName     = father.tagName
            grandFather.removeChild(father)
            for l in structure:
                tag = self.doc.createElement(tagName)
                #self.doc.ATTRIBUTE_NODE()
                #print(l)
                for atr in l:
                    #grandFather.setAttribute(atr, l[atr])
                    #print(tagName)
                    #tag = self.doc.createElement(tagName)
                    
                    tag.attributes[atr]=l[atr]
                grandFather.appendChild(tag)
                    #tag.__setattr__(atr,l[atr])
                    #print(atr + "=" +l[atr])
                #self.build(tag, l)
                    #grandFather.
                    #grandFather.__setattr__(atr,l[atr])
                #grandFather.appendChild(tag)

        else:
            data    = str(structure)
            tag     = self.doc.createTextNode(data)
            father.appendChild(tag)

    def display(self):
        #print self.doc.toprettyxml(indent="  ")
        return self.doc.toprettyxml(indent="  ")




def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        #d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
        d[t.tag].update((k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children:
            if text:
              d[t.tag]['#text'] = text
        elif t.attrib:
            d[t.tag]['#text'] = [text]
        else:
            d[t.tag] = text
    return d


def readdes(filename, sep='\t',header=22):
    with open(filename, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=sep, quotechar='|')
        data =[]
        for i,row in enumerate(spamreader):
            #print(i)
            if i== (header - 1):
                #print '* '.join(row)
                for j,c in enumerate(row):
                    row[j] = c.replace(' ','').replace('<','').replace('>','')
                    
                h = row
                
            elif i > (header - 1):
                for j,c in enumerate(row):
                    try:                    
                        row[j] = float(c.replace(' ',''))
                    except:
                        row[j] = (c.replace(' ',''))

                data.append(row)
    datastruc = {}
    for k,s in enumerate(h):
        columnk =[i[k] for i in data]
        datastruc[s]=columnk
        
    return datastruc
                       




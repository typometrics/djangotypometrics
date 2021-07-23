import os
from pathlib import Path
import numpy as np

import matplotlib.pyplot as plt
import pandas as pd

from typometricsapp import simpledtw
from typometricsapp.tsv2json import tsv2json, getoptions, gettypes


#creat position dataframe from the input jsondata
def posData(xty, x, yty, y, xminOcc = 0, yminOcc= 0):
    """return positions data after normalization (in [0,1])"""
    jsonData, _, _, _ = tsv2json(xty =xty, x=x , xminocc = xminOcc,yty = yty,y = y, yminocc = yminOcc, verbose= True)
    
    N = len(jsonData)
    dataDict = {}
    for la in jsonData:
        assert(len(la.get('data'))==1)
        data = la.get('data')[0]
        dataDict[data.get('label')]={'x': data.get('x'), 'y': data.get('y')}
        
    XY = pd.DataFrame(data=dataDict).T
    #norm = np.linalg.norm(XY.values, axis = 0)
    return (XY-XY.min())/(XY.max()-XY.min())


def langInter(posG1,posG2):
    """
    extract languges in both graph1 and graph2
    posG1, posG2 : dataframes of languges positions in graph1 & graph2
    """
    lanG1 = sorted(posG1.index.tolist())
    lanG2 = sorted(posG2.index.tolist())
    #print(lanG1 ==lanG2)
    
    if lanG1 !=lanG2:
        print("\nextract languages")
        langN = [lan for lan in lanG1 if lan in lanG2 ]
        #extract positions of langN 
        posG1 =  posG1.loc[langN]
        posG2 = posG2.loc[langN]
        assert(posG1.index.tolist() == posG2.index.tolist())
    return posG1, posG2


def dist(p1,p2):
    return np.sum((p1-p2)**2)**0.5


def distGraphDep(g1,g2):
    """
    languages' deplacement between g1 and g2 
    g1,g2: 2 dataframes contain positions of languages in both graph1 and graph2
    """
    g1,g2 = langInter(g1,g2)
    distSum = 0
    for la in g1.index:
        dl = dist(g1.loc[la].values, g2.loc[la].values)
        distSum += dl
        #print( la, "\ndeplacement: ", dl)
        #distSum += dist(g1.loc[la].values, g2.loc[la].values)
    return distSum


def distData0(graphs):
    """
    distance of cloudform with DTW and languge deplacement for 1D graphs
    graphs: list of tuple (ty,option) in analysis data 
    
    """
    distDataDep = {} 
    distDataDTW = {'distDTW':{},
                    'mapping':{}
                    }

    for g1 in graphs:
        k1 = ':'.join(g1)
        distDataDep[k1] = distDataDep.get(k1,{})
        distDataDTW['distDTW'][k1] = distDataDTW['distDTW'].get(k1,{})
        distDataDTW['mapping'][k1] = distDataDTW['mapping'].get(k1,{})
        
        for g2 in graphs:
            
            k2 = ':'.join(g2)
            distDataDep[k2] = distDataDep.get(k2,{})
            distDataDTW['distDTW'][k2] = distDataDTW['distDTW'].get(k2,{})
            distDataDTW['mapping'][k2] = distDataDTW['mapping'].get(k2,{})
            
            if distDataDep[k1].get(k2)==None:
                #print('g1 = ',k1, " g2 = ",k2)
                posG1 = posData(g1[0],g1[1],g1[0],g1[1])
                posG2 = posData(g2[0],g2[1],g2[0],g2[1])

                distDep = distGraphDep(posG1,posG2)
                matches, distDTW, mapping1, mapping2, matrix = simpledtw.dtw(posG1.values, posG2.values)
                distDataDep[k1][k2]= distDep
                distDataDep[k2][k1]= distDep
                
                assert(distDataDTW['distDTW'][k1].get(k2) == None)
                #print("--------\n", distData['cloudForm'][k1].get(k2))
                distDataDTW['distDTW'][k1][k2]= distDTW
                distDataDTW['distDTW'][k2][k1]= distDTW
                distDataDTW['mapping'][k1][k2] = mapping1
                distDataDTW['mapping'][k2][k1] = mapping2

    return distDataDep,distDataDTW


def writeData(filenames,dicts,resFolder = "clustering"):
    assert(len(filenames)==len(dicts))
    Path(resFolder).mkdir(parents=True, exist_ok=True)
    for i in range(len(filenames)):
        print(filenames[i])
        with open(resFolder+'/'+filenames[i], 'w+',encoding="utf8")as t:
                line0 = "options"+'\t'+'\t'.join(list(dicts[i]))+'\n' #index labels = column labels
                t.write(line0)
                for k, val in dicts[i].items():
                    line = k + '\t'+ '\t'.join([str(d) for d in val.values()])+'\n'
                    t.write(line)

def prepareDist0():
    types = gettypes()
    #types = ['distance']
    graphs = [(ty,opt) for ty in types for opt in getoptions(ty)]
    distDataDep,distDataDTW =  distData0(graphs)

    files = ["distDep.tsv", "distDTW.tsv","mappingDTW.tsv"]
    dicts = [distDataDep, distDataDTW['distDTW'],distDataDTW['mapping']]
    writeData(files, dicts)



if __name__ == '__main__':
    prepareDist0()







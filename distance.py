import os,time,multiprocessing, psutil, tqdm, collections.abc
from pathlib import Path
import numpy as np

import matplotlib.pyplot as plt
import pandas as pd

from typometricsapp import simpledtw
from typometricsapp.tsv2json import tsv2jsonNew, getoptions, gettypes

#global var : graphs, id2graphDf, gr2id
#types = gettypes()
types = ['menzerath']
print(types)
graphs = [(ty,opt) for ty in types for opt in getoptions(ty)]
#print(graphs)
#id2graphDf, gr2id = prepareData(graphs)

#creat position dataframe from the input jsondata
def posData(axtypes, ax, dim, axminOcc = None):
    """
    dim as dimension, axtypes & ax: list with len=dim or string with dim 1
    return positions data after normalization (in [0,1])
    """
    if axminOcc == None:
        axminOcc = np.zeros(dim)
    assert(len(axminOcc) == dim)
    jsonData, _, _, _, _,_ = tsv2jsonNew(axtypes = axtypes, ax = ax , axminocc = axminOcc,dim = dim, verbose = True)
    
    N = len(jsonData)
    dataDict = {}
    for la in jsonData:
        assert(len(la.get('data'))==1)
        data = la.get('data')[0]
        dataDict[data.get('label')]={'y': data.get('y')} #graph1d with pts at y axis
        if dim > 1:
            dataDict[data.get('label')]['x'] = data.get('x')
        #if dim == 3:
            
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


def get1Data(graph):
    #graph 1D
    name = graph.split(':')
    typ,opt = name[0], ':'.join(name[1:])
    #print("get data: ", typ, opt)
    return posData(typ,opt, dim = 1)

def prepareData(graphs):
    """return graph2id and id2graphDf dict, graph 1D"""
    ti = time.time()
    gr2id = {}
    id2gr = {}
    print("prepare data\n ",len(graphs),'\n', graphs)
    for i, v in enumerate(graphs):
        #print("idx: ", i, " items ", v)
        gr = ':'.join(v)
        #print(gr)
        gr2id[gr] = i
        id2gr[i] = [gr,get1Data(gr)]
    print("data prepared, take time: ", time.time()-ti)
    return id2gr, gr2id 

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

id2graphDf, gr2id = prepareData(graphs)

def distData0(graphss):
    """
    distance of cloudform with DTW and languge deplacement for 1D graphs
    graphss: list of tuple (ty,option) in analysis data 
    
    """
    ti = time.time()

    if isinstance(graphss, tuple):
        graphss = [graphss]

    print("compute distance for ", graphss) # process", multiprocessing.current_process())
    #id2graphDf, gr2id = prepareData(graphs)

    distDataDep = {} 
    distDataDTW = {'distDTW':{},
                    'mapping':{}
                    }

    for g1 in graphss:
        k1 = ':'.join(g1)
        distDataDep[k1] = distDataDep.get(k1,{})
        distDataDTW['distDTW'][k1] = distDataDTW['distDTW'].get(k1,{})
        distDataDTW['mapping'][k1] = distDataDTW['mapping'].get(k1,{})
        
        for id2, val2 in id2graphDf.items():
            
            k2 = val2[0] 
            #if(k1 == k2):   print("self", k1, id2)
            distDataDep[k2] = distDataDep.get(k2,{})
            distDataDTW['distDTW'][k2] = distDataDTW['distDTW'].get(k2,{})
            distDataDTW['mapping'][k2] = distDataDTW['mapping'].get(k2,{})
            
            if distDataDep[k1].get(k2)==None:
                #print('g1 = ',k1, " g2 = ",k2)
                posG1 = id2graphDf[gr2id[k1]][1]    
                posG2 = val2[1] 

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

    print("take time: ", time.time()-ti)
    return distDataDep,distDataDTW


#copied from datapreparation/conll.py
def update(d, u):
	for k, v in u.items():
		if isinstance(v, collections.abc.Mapping): 
			r = update(d.get(k, {}), v)
			d[k] = r
		else:
			d[k] = u[k]
	return d

def distDataMulti(graphs):

    ti = time.time()
    print("compute distance multi")

    #id2graphDf, gr2id = prepareData(graphs)
    distDataDep = {} 
    distDataDTW = {'distDTW':{},
                    'mapping':{}
                    }

    pbar = tqdm.tqdm(total=len(graphs))
    results = []
    
    with multiprocessing.Pool(psutil.cpu_count()) as pool:
        for res in pool.imap_unordered(distData0, graphs):
            pbar.update()
            results.append(res)
            
    print("it took",time.time()-ti,"seconds")
    print("\n\n\n====================== finished reading in. \n combining...")
    
    for dists in results:
        update(distDataDep, dists[0])
        update(distDataDTW['distDTW'], dists[1]['distDTW'])
        update(distDataDTW['mapping'], dists[1]['mapping'])
        
    print("it took",time.time()-ti,"seconds")
    return distDataDep,distDataDTW

#algo marriage
def preferList(lang, graph):
    """
    for language with position lang in graph1, find its preference list of languages in graph2 'graph'
    graph1 and graph2 have the same dimension
    """
    pl = {}
    for la in range(len(graph)):
        d = dist(lang, graph.iloc[la].values)
        pl[la] = d
    #print(pl)
    return sorted(pl.items(), key=lambda x: x[1])


def prepareList(gr1, gr2):
    """
    gr1, gr2: 2 dataframes
    return preference list for languages in gr1 with index and dist of pts in gr2
    """
    plists = {}
    for la in range(len(gr1)):
        plists[la] = preferList(gr1.iloc[la], gr2)
    return plists

def initMatch(graph):
    """
    graph: a dataframe
    return a dictionary with indice of languages in gr1 as keys 
    and [partner index in gr2, distance, partener index in plists] as values, set to default value [-1,-1.,-1]  
    """
    matchInit = {}
    for la in range(len(graph)):
        matchInit[la] = [-1,-1., -1]
    return matchInit    

def singleRound(singleOnes,prLists1, matchDict1, matchDict2):
    """
    algo marriage, graph1-optimal : gr1 propose, gr2 decide
    prLists1: a dictionary with{language index i: [prefefence list of i ],... }
    """
    #global matchDict1
    #global matchDict2
    for idx in singleOnes:
        candidat = matchDict1[idx][2]+1 #index of candidate in prLists1
        cinfo = prLists1[idx][candidat] #(id in graph2, distance)
        #print("idx= ", idx, "can = ", candidat, matchDict1[idx] )
        matchDict1[idx][-1] = candidat

        if matchDict2[cinfo[0]][0] == -1: # if candidate unmarried
            matchDict1[idx][:2] = [cinfo[0],cinfo[1]] #partner index in graph2, dist, index in prLIst1
            matchDict2[cinfo[0]]=[idx, cinfo[1]] #, -1]
        else:#if married, compare preference (i.e distance)
            #print("idx",idx," can ",candidat, " current ", matchDict2[cinfo[0]])
            if cinfo[1] < matchDict2[cinfo[0]][1]: #if candidate prefer idx than her current partener
                #print("marriage: ", idx, " ", cinfo[0], "candidat n ", candidat)
                matchDict1[matchDict2[cinfo[0]][0]][:2] = [-1,-1.] #divorce
                matchDict1[idx][:2] = [cinfo[0],cinfo[1]] #re marry
                matchDict2[cinfo[0]]=[idx, cinfo[1]] #, -1]
    return matchDict1, matchDict2

def distMarriage(prLists1, gr1,gr2):
    """return dist of stable marriage match between  graph1 et graph2 """
    match1 = initMatch(gr1)
    match2 = initMatch(gr2)
    
    single = [ idx for idx, val in match1.items() if val[0] == -1 ]
    while(single):
        #print(len(single))
        match1, match2 = singleRound(single, prLists1, match1, match2)
        single = [ idx for idx, val in match1.items() if val[0] == -1 ]
    
    distls= [ val[1] for idx, val in match1.items()]
    return sum(distls),match1


def distDataMarry(graphss):
    """
    distance of cloudform with stable marriage problem
    graphss: list of tuple (ty,option) in analysis data 
    
    """
    ti = time.time()

    if isinstance(graphss, tuple):
        graphss = [graphss]

    print("compute distance for ", graphss) # process", multiprocessing.current_process())

    distDataM = {'dist': {}, 'match':{}}

    for g1 in graphss:
        k1 = ':'.join(g1)
        distDataM['dist'][k1] = distDataM['dist'].get(k1,{})
        distDataM['match'][k1] = distDataM['match'].get(k1,{}) #k1 optimal

        distDataM['dist'][k1][k1]= 0.0
        posG1 = id2graphDf[gr2id[k1]][1] 
        distDataM['match'][k1][k1] = list(range(len(posG1)))
        print("g1 = ", k1)
        
        for id2, val2 in id2graphDf.items():
            
            k2 = val2[0] 
            #if(k1 == k2):   print("self", k1, id2)
            distDataM['dist'][k2] = distDataM['dist'].get(k2,{})
            distDataM['match'][k2] = distDataM['match'].get(k2,{})
            
            if distDataM['dist'][k1].get(k2)==None:
                print('g1 = ',k1, " g2 = ",k2)
                posG2 = val2[1] 

                prl1 = prepareList(posG1, posG2)
                distM, match1 = distMarriage( prl1, posG1, posG2)
                distDataM['dist'][k1][k2]= distM
                distDataM['dist'][k2][k1]= distM
                distDataM['match'][k1][k2] = [match1[idx][0] for idx in range(len(match1))] #range(len(match1)) == sorted(match1)
                
                prl2 = prepareList(posG2, posG1)
                _, match2 = distMarriage(prl2, posG2, posG1)
                distDataM['match'][k2][k1] = [match2[idx][0] for idx in range(len(match2))]
                
    
    print("take time: ", time.time()-ti)
    return distDataM

def distMarryMulti(graphs):
    ti = time.time()
    print("compute distance multi")
    distDataM = {'dist': {}, 'match':{}}

    pbar = tqdm.tqdm(total=len(graphs))
    results = []
    
    with multiprocessing.Pool(psutil.cpu_count()) as pool:
        for res in pool.imap_unordered(distDataMarry, graphs):
            pbar.update()
            results.append(res)        
    print("it took",time.time()-ti,"seconds")
    print("\n\n\n====================== finished reading in. \n combining...")
    
    for dists in results:
        update(distDataM['dist'], dists['dist'])
        update(distDataM['match'], dists['match'])
        
    print("it took",time.time()-ti,"seconds")
    return distDataM


def writeData(filenames,dicts,resFolder = "clustering"):
    print("writing files")
    assert(len(filenames)==len(dicts))
    Path(resFolder).mkdir(parents=True, exist_ok=True)
    for i in range(len(filenames)):
        print(filenames[i])
        with open(resFolder+'/'+filenames[i], 'w+',encoding="utf8")as t:
            #index labels = column labels, 'total' not at the end of each type in the distfile
            line0 = "options"+'\t'+'\t'.join(sorted(dicts[i]))+'\n' 
            t.write(line0)
            for gr in sorted(dicts[i]):
                #print("line for", gr)
                line = gr +'\t'+ '\t'.join([str(dicts[i][gr].get(g)) for g in sorted(dicts[i][gr])])+'\n'
                t.write(line)


def prepareDist0(version, resfolder = "clustering" ):
    #types = gettypes()
    #graphs = [(ty,opt) for ty in types for opt in getoptions(ty)]
    distDataDep,distDataDTW = distDataMulti(graphs) # distData0(graphs)

    files = ["distDep_"+version+".tsv", "distDTW_"+version+".tsv","mappingDTW_"+version+".tsv"]
    dicts = [distDataDep, distDataDTW['distDTW'],distDataDTW['mapping']]

    writeData(files, dicts, resFolder = resfolder)

def prepareDistMarr(version, resfolder = "clustering" ):
    distDataMarr =  distMarryMulti(graphs)
    files = [ "distMarry_"+version+".tsv","mappingMarry_"+version+".tsv"]
    writeData(files, [distDataMarr['dist'],distDataMarr['match'] ] , resFolder = resfolder)



if __name__ == '__main__':
    resfolder = "clusteringTest"
    #prepareDist0(version = "sudTIMEtest",resfolder = resfolder )
    #prepareDistMarr(version = "sudtest0",resfolder = resfolder )

    
    dM = distDataMarry(('menzerath', 'a_any_any_same'))
    for i, v in dM['dist'].items():
        print(i,'\n',v)


    








import time,json
from pathlib import Path
import numpy as np
import pandas as pd

#global var
typeGroups = ['direction','distance','menzerath','distribution']
distDict = {}

print("load distance files")
dictSUD = {1:{'dep':{},'dtw':{},'marry':{}}, 
         2:{'dep':{},'dtw':{},'marry':{}} 
}
dictUD = {1:{'dep':{},'dtw':{},'marry':{}},
        2:{'dep':{},'dtw':{},'marry':{}}}
#SUD
for group in typeGroups:
    for typ in ['Dep','DTW','Marry']:
        fl = "dist"+typ+"_sud1d_"+group+".tsv"
        dictGroup =  pd.read_csv("~/typometrics/djangotypometrics/clustering/dist1D/"+group+'/'+fl,sep = '\t',index_col = 0)
        dictSUD[1][typ.lower()][group] = dictGroup

#UD
for group in typeGroups:
    for typ in ['Dep','DTW','Marry']:
        fl = "dist"+typ+"_ud1d_"+group+".tsv"
        dictGroup =  pd.read_csv("~/typometrics/djangotypometrics/clustering/dist1D/"+group+'/'+fl,sep = '\t',index_col = 0)
        dictUD[1][typ.lower()][group] = dictGroup

#2D graph, group = distribution        
for typ in ['Dep','DTW','Marry']:
    fl = "dist"+typ+"_sud2d_"+"distribution"+".tsv"
    dictGroup =  pd.read_csv("~/typometrics/djangotypometrics/clustering/dist2D/"+'distribution'+'/'+fl,sep = '\t',index_col = 0)
    dictSUD[2][typ.lower()]['distribution'] = dictGroup

    fl1 = "dist"+typ+"_ud2d_"+"distribution"+".tsv"
    dictGroup =  pd.read_csv("~/typometrics/djangotypometrics/clustering/dist2D/"+'distribution'+'/'+fl1,sep = '\t',index_col = 0)
    dictUD[2][typ.lower()]['distribution'] = dictGroup


#default scheme as 'SUD'
distDict = dictSUD

def setSchemeGraph(sche):
    global distDict
    if sche == 'UD':
        distDict = dictUD 
        print("similar graph: scheme changed from SUD to UD")
        return True
    if sche == 'SUD':
        distDict = dictSUD
        print("similar graph: scheme changed from UD to SUD")
        return True
    return False

def closestGr(distData, n = 10):
    """
    find n closest graphs to the Graph, distData: a dictionary including distance data between graphs &Graph
    i.e. return keys of n min values
    """
    v = distData.values 
    k = np.array(list(distData.keys())) #same ordre as v in python3
    sortedIdx = v.argsort() 
    return k[sortedIdx[1:n+1]], v[sortedIdx[1:n+1]] #first one is self


def myClosestGraph(typ,ax, version, dim):
    #type(typ) == type(ax) ==list , typ != treeheight
    print(version)
    if typ[0] == 'treeHeight':  return typ,ax,0.
    if version not in ['dep', 'dtw','marry']:   return 

    distVersion = typ[0] if typ[0] in typeGroups else typ[0][:-4] #len(-cfc)==len(-abs) == 4

    name = ':'.join([typ[0],ax[0]])
    if dim ==2:
        if typ[0]==typ[1] and ax[0]==ax[1]:#if graph is diagonal
            grs, ds = closestGr(distDict[1][version][distVersion].loc[name], n = 1)
            rowsJs = getRows(name, distVersion,dim = 1, version = version)
            n = grs[0].split(':')
            return [n[0], n[0]],[':'.join(n[1:]), ':'.join(n[1:]) ],ds[0], rowsJs
        else:
            name = "::".join([name,':'.join([typ[1],ax[1]])])    
            
    grs, ds = closestGr(distDict[dim][version][distVersion].loc[name], n = 1)
    print("closest graph ", grs, ds)
    rowsJs = getRows(name, distVersion,dim = dim, version = version)

    #find the type and option of the most similar graph 
    typ,opt = graphParam(grs[0],dim = dim)
    return typ,opt,ds[0], rowsJs
    
def graphParam(grname, dim):
    #find the type and option of the most similar graph 
    print("hello graphParam\n!!!!!!!!!!!!!!!!!!!",grname,"\n\n")
    split_name =  grname.split('::')
    if len(split_name) == 1: #dim == 1 or graphe diagonal
        n = grname.split(':')
        typ,opt = [n[0]], [':'.join(n[1:])]
    else:#dim == 2, 
        #pour distribution, name format: distriution:g1_opt::g2_opt, or distriution:g1_opt::distribution:g2_opt
        #a naive method to fix name format incoherence bug, to improve after
        nx = split_name[0].split(':')
        ny = split_name[1].split(':')
        if ny[0] == "distribution":
            typ,opt = [nx[0],ny[0]], [':'.join(nx[1:]), ':'.join(ny[1:]) ]
        else:
            typ,opt = [nx[0],nx[0]], [':'.join(nx[1:]), split_name[1] ]
        print("======",typ,opt)
    return typ,opt


def getRows(graphName, distVersion, dim, version='dep'):
    rowsDf = distDict[dim][version][distVersion][[graphName]]
    rows=[]
    
    for index, row in rowsDf.iterrows():
        if str(row.iloc[0]) not in ['nan','inf']:
            shorten_name = index.split('::')
            if len(shorten_name) == 1:
                rows.append({'name':index, "distance": round(row.iloc[0],6)}) #use this line for all cases after re computed the data
            else:
                #code to shorten graph name in the table, remove them when re compute the data with the good(short) graph name
                ax0,ax1 = index.split('::')
                keep_ax1 = ax1.split(':')
                rows.append({"name":ax0+'::'+':'.join(keep_ax1[1:]), "distance":round(row.iloc[0],6)})
    return sorted(rows, key=lambda x: x['distance'])
    

if __name__ == '__main__':
    typ0,ax0, grdist, jsrow= myClosestGraph(['distance'],['comp:obj'], version = 'dep',dim =1)
    print("close graph of distance:subj: ", ':'.join([typ0[0],ax0[0]]), " dist= ", grdist)

    grs, ds = closestGr(distDict['dtw']['direction'].loc['direction:subj'], n = 10)
    print("closest gr dtw", grs, "\n",ds)

    grs, ds = closestGr(distDict['dep']['direction'].loc['direction:subj'], n = 10)
    print("closest gr dep", grs,"\n",ds)

    

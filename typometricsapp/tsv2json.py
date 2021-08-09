import json
import math
import pandas as pd 
import numpy as np

sudFolder = 'sud-treebanks-v2.8-analysis'
udFolder = 'ud-treebanks-v2.8-analysis'
#anafolder = sudFolder


groupColors={
    'Indo-European-Romance':'brown',
    'Indo-European-Baltoslavic':'purple',
    'Indo-European-Germanic':'olive',
    'Indo-European':'royalBlue',
    'Sino-Austronesian':'limeGreen', 
    'Agglutinating':'red', 
    'Semitic':'orange', 
    'Afroasiatic':'orange',
    'Niger-Congo':'black',
    'Tupian':'black',
    'Arawakan': 'black',
    'Mayan':'darkblue', #to verify
    'Dravidian':'black',
    'isolate':'black',
    'Pama–Nyungan':'cyan', #changed color
    'Eskimo–Aleut':'cyan', # to verify
    }
# groupMarkers={'Indo-European-Romance':'<','Indo-European-Baltoslavic':'^','Indo-European-Germanic':'v','Indo-European':'>','Sino-Austronesian':'s', 'Agglutinating':'+'}
groupMarkers={
    'Indo-European-Romance':'triangle',
    'Indo-European-Baltoslavic':'triangle',
    'Indo-European-Germanic':'triangle',
    'Indo-European':'triangle',
    'Sino-Austronesian':'star', 
    'Agglutinating':'cross', 
    'Semitic':'crossRot', #semitic is a branch of afroasiatic
    'Afroasiatic':'crossRot',
    'Niger-Congo':'rect',
    'Tupian':'rectRounded',
    'Arawakan': 'rectRounded',
    'Mayan': 'rectRounded', # to verify
    'Dravidian':'rectRot',
    'isolate':'circle',
    'Pama–Nyungan':'circle',
    'Eskimo–Aleut':'circle', # to verify
    }

langNames={}
langcodef=open('languageCodes.tsv')
langcodef.readline()
for li in langcodef:
	lis = li.strip().split('\t')
	langNames[lis[0]]=lis[-1]

mylangNames = {li.split('\t')[0]: li.split('\t')[1] for li in open(
	'myLanguageCodes.tsv').read().strip().split('\n')}

langNames = dict(langNames, **mylangNames)

langnameGroup={li.split('\t')[0]:li.split('\t')[1] for li in open('languageGroups.tsv').read().strip().split('\n')  }

dfs = {}
"""
minnonzero = 50

for ty,fi in {
    'menzerath': '/abc.languages.v2.8_sud_typometricsformat.tsv',
    'direction': '/positive-direction.tsv',
    'direction-cfc':'/posdircfc.tsv',
    'distance': '/f-dist.tsv',
    'distance-cfc':'/cfc-dist.tsv',
    'treeHeight': '/height.tsv',
    'distribution':'/f.tsv'
    }.items():
    print(anafolder+fi)
    dfs[ty] = pd.read_csv(anafolder+fi,
            sep='\t',
            index_col=['name'])

    goodcols = [name for name, values in dfs[ty].astype(bool).sum(axis=0).iteritems() if values>= minnonzero]
    dfs[ty] = dfs[ty][goodcols]

    
#print(dfs['distance'])
#print(dfs['distance'].head() )

# cfc:
df = pd.read_csv(anafolder+'/cfc.tsv',
            sep='\t',
            index_col=['name'])
goodcols = [name for name, values in df.astype(bool).sum(axis=0).iteritems() if values>minnonzero]

#dfs['direction-cfc']=pd.read_csv(anafolder+'/posdircfc.tsv',
#            sep='\t',
#            index_col=['name'],)#[goodcols]
# print('nr columns:',len(dfs['direction-cfc'].columns)) #df[column])

"""

def getRawData(inputfolder, sud = True, minnonzero = 50):
    print("\ncurrent analysis folder: ", inputfolder)

    dfs={}
    version = 'sud' if sud else 'ud'

    for ty,fi in {
        'menzerath': '/abc.languages.v2.8_{}_typometricsformat.tsv'.format(version),
        'direction': '/positive-direction.tsv',
        'direction-cfc':'/posdircfc.tsv',
        'distance': '/f-dist.tsv',
        'distance-cfc':'/cfc-dist.tsv',
        'distribution':'/f.tsv',
        'treeHeight': '/height.tsv'
        }.items():
        print(inputfolder+fi)
        dfs[ty] = pd.read_csv(inputfolder+fi,
                sep='\t',
                index_col=['name'])

        goodcols = [name for name, values in dfs[ty].astype(bool).sum(axis=0).iteritems() if values>= minnonzero]
        dfs[ty] = dfs[ty][goodcols]
    return dfs

#!!!!! begin get input raw data
dfsSUD = getRawData(sudFolder)
dfsUD = getRawData(udFolder, sud = False)

dfs = dfsSUD
#dfs = dfsUD

def setScheme(sche):
    print("\n----here!!")
    global dfs
    #global anafolder 
    if sche == 'UD':
        dfs = dfsUD 
        #anafolder = udFolder
        print("scheme changed from SUD to UD")
        return True
    if sche == 'SUD':
        dfs = dfsSUD
        #anafolder = sudFolder
        print("scheme changed from UD to SUD")
        return True
    return False



def gettypes():
    print(11111,list(dfs.keys()) )
    return list(dfs.keys())


def getoptions(ty):
    print(333333,ty)
    # print(dfs['direction'].head(),list(dfs[ty].head()) )
    if ty == 'menzerath':
    	return sorted(list(dfs[ty].head()))
    return list(dfs[ty].head())
"""
def tsv2json(xty, x, xminocc, yty, y, yminocc, verbose = True):
    #print("anafolder ", anafolder)
    if verbose:
        print('!!!!!!!!!!!!!', xty, x, xminocc, yty, y, yminocc)
        print('number languages:',len(dfs[xty]), len(dfs[yty]))
    #if xty==yty: codf = dfs[xty]
    #else: codf = pd.concat([dfs[xty], dfs[yty]], axis=1)
    xdf = dfs[xty][[x]]
    ydf = dfs[yty][[y]]
    codf = pd.concat([xdf, ydf], axis=1)


    if 'nb_'+x in dfs[xty].columns.values.tolist(): 
        #print("x before concat\n", codf)

        codf = pd.concat([codf,dfs[xty][['nb_'+x]]], axis = 1)
        #print("added nb_", x,"\n",codf)
        codf = codf[codf['nb_'+x] >= xminocc] 
    if 'nb_'+y in dfs[yty].columns.values.tolist() and x != y : 
        #print("y != x, before concat\n", codf)
        
        codf = pd.concat([codf,dfs[yty][['nb_'+y]]], axis = 1)
        #print("added nb_", y,"\n",codf)
        codf = codf[codf['nb_'+y] >= yminocc]

    nblang = len(codf)
    jsos=[]
    
    for index, row in codf.iterrows():
        # print(groupColors)
        # print('***',index,'!!!',row)
        # print('***', index, '!!!', row[x], row[y])
        
        if str(row.iloc[0]) == 'nan': row.iloc[0] = 0
        if str(row.iloc[1]) == 'nan': row.iloc[1] = 0
       
        jsos+=['''
            {{
                    "label":["{index}/{group}"],
                    "backgroundColor": "{color}",
                    "borderColor": "{color}",
                    "pointStyle": "{style}",                    
                    "data": [{{
                        "x": {rx},
                        "y": {ry},
                        "r": 5,
                        "label": "{index}"
                    }}]
                }}
        '''.format(
            index=index,
            rx=row.iloc[0],  # [x],
            ry=row.iloc[1],  # [y],
            color= groupColors[langnameGroup[index]], 
            style=groupMarkers[langnameGroup[index]],
            group=langnameGroup[index]
            ) ]
   
    jso='[ \n'+', '.join(jsos)+']'
    #print(jso,"\n \n")
    j=json.loads(jso)
    #print(j)

    #idxMax = np.argmax(codf[x].values)
    #xlimMax =  math.ceil(codf[x].iloc[idxMax] + len(codf[[x]].iloc[idxMax].name))
    xlimMax = math.ceil(np.nanmax(codf[[x]].values))+1

    mi, ma = np.nanmin(codf[[x, y]].values), np.nanmax(codf[[x, y]].values)
    
    if (ma-mi)   < 10: divi = 1
    elif (ma-mi) < 60: divi = 5
    elif (ma-mi) < 120: divi = 10
    elif (ma-mi) < 600: divi = 50
    else: divi=100
    # print(444444444, mi, ma, divi, ma-((ma-.1) % divi)+divi)
    return j, nblang, mi-(mi % divi), ma-((ma-.1) % divi)+divi,xlimMax
"""

def tsv2jsonNew(axtypes, ax, axminocc, dim, verbose = True):
    """"
    axtypes : types, e.g. distance or [distance, direction]
    ax: axis, e.g. x or [x,y]
    aminocc: min occurences of relevant axis 
    """
    #check input dimension
    axminocc = [axminocc] if np.isscalar(axminocc) else axminocc
    if dim == 1:
        axtypes = [axtypes] if type(axtypes)==str else axtypes
        ax = [ax] if type(ax) == str else ax
    #print(type(axtypes), len(axtypes), type(ax), len(ax), type(axminocc),len(axminocc))
    assert(len(axtypes) == dim and len(ax) == dim and len(axminocc) == dim)
    

    #xty, x, xminocc, yty, y, yminocc,
    if verbose:
        print('!!!!!!!!!!!!!', axtypes, ax, axminocc)
        nLang = [len(dfs[ty]) for ty in axtypes]
        print('number languages:',nLang)

    axdf = []
    for d in range(dim):
        axdf.append(dfs[axtypes[d]][[ax[d]]]) 
    #xdf = dfs[xty][[x]]
    #ydf = dfs[yty][[y]]
    codf = pd.concat(axdf, axis=1)

    for d in range(dim):
        if 'nb_'+ax[d] in dfs[axtypes[d]].columns.values.tolist() and ax[d] not in ax[:d]:
            codf = pd.concat([codf, dfs[axtypes[d]][['nb_'+ ax[d]]]], axis = 1)
            #print("added nb_", x,"\n",codf)
            codf = codf[codf['nb_'+ ax[d]] >= axminocc[d]] 

    nblang = len(codf)
    jsos=[]
    
    for index, row in codf.iterrows():
        # print(groupColors)
        # print('***',index,'!!!',row)
        # print('***', index, '!!!', row[x], row[y])

        for d in range(dim):
            if str(row.iloc[d]) == 'nan': row.iloc[d] = 0
       
        jsos+=['''
            {{
                    "label":["{index}/{group}"],
                    "backgroundColor": "{color}",
                    "borderColor": "{color}",
                    "pointStyle": "{style}",                    
                    "data": [{{
                        "x": {rx},
                        "y": {ry},
                        "z": {rz},
                        "r": 5,
                        "label": "{index}"
                    }}]
                }}
        '''.format(
            index=index,
            rx=row.iloc[0] if dim>1 else 0,  # [x],
            ry=row.iloc[1] if dim >1 else row.iloc[0], # [y],
            rz= row.iloc[2] if dim == 3 else 0,
            color= groupColors[langnameGroup[index]], 
            style=groupMarkers[langnameGroup[index]],
            group=langnameGroup[index]
            ) ]
   
    jso='[ \n'+', '.join(jsos)+']'
    #print(jso,"\n \n")
    j=json.loads(jso)
    #print(j)

    #idxMax = np.argmax(codf[x].values)
    #xlimMax =  math.ceil(codf[x].iloc[idxMax] + len(codf[[x]].iloc[idxMax].name))
    xlimMax = math.ceil(np.nanmax(codf[[ax[0]]].values))
    xlimMin = np.nanmin(codf[[ax[0]]].values) #math.ceil(np.nanmin(codf[[ax[0]]].values))
    print("\nxmin =", xlimMin, "max = ", xlimMax)

    mi, ma = np.nanmin(codf[ax].values), np.nanmax(codf[ax].values) #ax = [x,y] if dim = 2
    
    if (ma-mi)   < 10: divi = 1
    elif (ma-mi) < 60: divi = 5
    elif (ma-mi) < 120: divi = 10
    elif (ma-mi) < 600: divi = 50
    else: divi=100
    # print(444444444, mi, ma, divi, ma-((ma-.1) % divi)+divi)
    return j, nblang, mi-(mi % divi), ma-((ma-.1) % divi)+divi,xlimMax, xlimMin


if __name__ == '__main__':
    res = tsv2json('distance',x='subj',xminocc = 0,yty='direction',y='comp:obj',yminocc = 0)

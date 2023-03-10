import json
import math
import pandas as pd 
import numpy as np


version_corpus = '2.11'
sudFolder = f'sud-treebanks-v{version_corpus}-analysis'
udFolder = f'ud-treebanks-v{version_corpus}-analysis'
#anafolder = sudFolder


groupColors={
    'Indo-European-Romance':'brown',
    'Indo-European-Baltoslavic':'purple',
    'Indo-European-Germanic':'olive',
    'Indo-European':'royalBlue',
    'Austronesian': 'limeGreen', # or another color
    'Sino-Austronesian':'limeGreen',  #7 lang
    'Agglutinating':'red', 
    'Semitic':'orange', #semitic is a branch of afroasiatic 6 lang
    'Afroasiatic':'orange', #3 lang
    'Niger-Congo':'black', #3 lang
    'Tupian':'cadetBlue',  #'olive', #7 lang
    'Arawakan': 'black',#1 lang
    'Arawan':'black', # 1langugae
    'Mayan':'black', # 1 lang
    'Dravidian':'black',#2 lang
    'isolate':'black', #1 lang
    'Pama–Nyungan':'black',#'cyan', 1 lang
    'Eskimo–Aleut':'black',#'cyan', 1 lang
    'Tungusic': 'black', # 1 lang
    'NorthwestCaucasian':'black', # 1 lang
    'Nahuan': 'black', # 1 lang
    'Macro-Jê': 'black', # 1 lang
    }
# groupMarkers={'Indo-European-Romance':'<','Indo-European-Baltoslavic':'^','Indo-European-Germanic':'v','Indo-European':'>','Sino-Austronesian':'s', 'Agglutinating':'+'}
groupMarkers={
    'Indo-European-Romance':'triangle',
    'Indo-European-Baltoslavic':'triangle',
    'Indo-European-Germanic':'triangle',
    'Indo-European':'triangle',
    'Austronesian': 'star', # or another one?
    'Sino-Austronesian':'star',
    'Agglutinating':'cross', 
    'Semitic':'crossRot',
    'Afroasiatic':'crossRot',
    'Niger-Congo':'circle', #'rect',
    'Tupian':'star', 
    'Arawakan': 'circle', #'rectRounded',
    'Arawan': 'circle',
    'Mayan': 'circle', #'rectRounded', 
    'Dravidian': 'circle', #'rectRot',
    'isolate':'circle',
    'Pama–Nyungan':'circle',
    'Eskimo–Aleut':'circle', 
    'Tungusic': 'circle',
    'NorthwestCaucasian':'circle',
    'Nahuan':'circle',
    'Macro-Jê': 'circle'
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


def getRawData(inputfolder, sud = True, minnonzero = 5):
    print("\ncurrent analysis folder: ", inputfolder)

    dfs={}
    scheme = 'sud' if sud else 'ud'

    cfc_fn = '/direction-cfc_extend.tsv' if sud else '/posdircfc.tsv'
    cfc_freq_fn = '/distribution-cfc_extend.tsv' if sud else '/cfc.tsv'
    positive_direction_fn = '/head_initiality_comb.tsv' if sud else '/positive-direction.tsv'
    dict_data_ud = {
        'menzerath': '/abc.languages.v{}_{}_typometricsformat.tsv'.format(version_corpus, scheme),
        'head-initiality': positive_direction_fn, # change direction as head-initiality ?
        'head-initiality-cfc':cfc_fn ,
        'distance': '/f-dist.tsv',
        'distance-abs':'/f-dist-abs.tsv',
        'distance-cfc':'/cfc-dist.tsv',
        'distribution':'/f.tsv',
        'treeHeight': '/height.tsv',
        'freq-cfc': cfc_freq_fn
    }
        # 'LAS_trankit': '/boot_LAS_t.tsv',
        # 'UAS_trankit': '/boot_UAS_t.tsv',
        # 'UPOS_trankit': '/boot_UPOS_t.tsv',
        # 'LAS_udify': '/boot_LAS_u.tsv',
        # 'UAS_udify': '/boot_UAS_u.tsv',
        # 'UPOS_udify': '/boot_UPOS_u.tsv',
    boot_dict = {
        'ttr':'/boot_ttr.tsv',
        'percent_func':'/boot_percent_fct.tsv',
        'LAS': '/boot_LAS_mean.tsv',
        'UAS': '/boot_UAS_mean.tsv',
        'UPOS': '/boot_UPOS_mean.tsv'
    }
    # 5 relation: comp, mod, udep, subj, dislocated 
    # by construction instead of by language, cannot be shown by current typometrics site
    # 'freq_sample':'/freqSample.tsv',
    # 'head_initial_weight':'/head_initial_weight.tsv',
    # 'head_final_weight':'/head_final_weight.tsv',
    flex_dict = {
        # 'head-initiality':'/head_initiality.tsv',
        'flexibility':'/flexibility_rel.tsv',
        'flexibility-cfc':'/flexibility_cfc_all.tsv',
        'flex_compare_Bakker':'/bak_vs_typo.tsv'
    }
    dict_data_sud = dict_data_ud.copy()
    # dict_data_sud.update(boot_dict)
    dict_data_sud.update(flex_dict)

    dict_data = dict_data_sud if sud else dict_data_ud

    for ty,fi in dict_data.items():
        print(inputfolder+fi)
        dfs[ty] = pd.read_csv(inputfolder+fi,
                sep='\t',
                index_col= 0)# ['name'])
        #remove nan
        notNanCols = (dfs[ty] == dfs[ty])
        goodcols = [name for name, values in  notNanCols.astype(bool).sum(axis=0).items() if values>= minnonzero]#for nan
        print(len(goodcols))
        dfs[ty] = dfs[ty][goodcols]
        
        if ty == 'menzerath':
            goodcols = [name for name, values in  dfs[ty].astype(bool).sum(axis=0).items() if values>= minnonzero]#for 0
            print(len(goodcols))
            dfs[ty] = dfs[ty][goodcols]
    
    return dfs

#!!!!! begin get input raw data
dfsSUD = getRawData(sudFolder)
dfsUD = getRawData(udFolder, sud = False)

dfs = dfsSUD #default scheme: SUD
#dfs = dfsUD 

def setScheme(sche):
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
    #print(11111,list(dfs.keys()) )
    types = list(dfs.keys())
    types.remove('freq-cfc')
    return types


def getoptions(ty):
    print("get options for",ty)
    # print(dfs['direction'].head(),list(dfs[ty].head()) )
    if ty == 'menzerath':
    	return sorted(list(dfs[ty].head()))
    return list(dfs[ty].head())


def tsv2jsonNew(axtypes, ax, axminocc, dim, verbose = True):
    """"
    axtypes : types, e.g. distance or [distance, direction]
    ax: axis, e.g. x or [x,y]
    aminocc: min occurences of relevant axis 
    """
    if verbose:
        print('!!!!!!!!!!!!!', axtypes, ax, axminocc)
    #check input dimension
    axminocc = [axminocc] if np.isscalar(axminocc) else axminocc
    if dim == 1:
        axtypes = [axtypes] if type(axtypes)==str else axtypes
        ax = [ax] if type(ax) == str else ax
    #print(type(axtypes), len(axtypes), type(ax), len(ax), type(axminocc),len(axminocc))
    assert(len(axtypes) == dim and len(ax) == dim and len(axminocc) == dim)

    axdf = []
    for d in range(dim):
        axdf.append(dfs[axtypes[d]][[ax[d]]]) 

    codf = pd.concat(axdf, axis=1)

    #set min occurence of functions in treebank
    freqMax = []
    for d in range(dim):
        #menzerath
        print("====================\n",ax[d], "-----------",ax)
        if ax[d][:3] == 'nb_':
            codf = codf[codf[ax[d]] >= axminocc[d]]
            freqMax.append(int(codf[ax[d]].median()))
            continue
        else:
            if 'nb_'+ax[d] in ax:
                codf = codf[codf['nb_'+ ax[d]] >= axminocc[d]]

            if 'nb_'+ax[d] in dfs[axtypes[d]].columns.values.tolist() and ax[d] not in ax[:d]: 
                #if nb_ in dfs[axtype of given dim] and havn't been added before
                codf = pd.concat([codf, dfs[axtypes[d]][['nb_'+ ax[d]]]], axis = 1)
                codf = codf[codf['nb_'+ ax[d]] >= axminocc[d]] 
        if axtypes[d] == 'menzerath':
            freqMax.append(int(codf['nb_'+ ax[d]].median()))
        #others
        if axtypes[d] in ['distance','distance-abs','head-intiality','distribution'] and 'nb_'+ax[d] not in codf.keys():
            fre = dfs['distribution'][[ax[d]]].rename(columns={ax[d]:'nb_'+ax[d]}) #distribution is percentage as float% but not occurence as int
            freq = fre*dfs['distribution'][['total']].rename(columns={'total':'nb_'+ax[d]})
 
            codf = pd.concat([codf,freq], axis = 1)
            codf = codf[codf['nb_'+ax[d]] >= axminocc[d]]
            freqMax.append(int(freq.median().loc['nb_'+ax[d]]))
        if axtypes[d] in ['distance-cfc','head-intiality-cfc'] and 'nb_'+ax[d] not in codf.keys():
            fre = dfs['freq-cfc'][[ax[d]]].rename(columns={ax[d]:'nb_'+ax[d]}) #distribution is percentage as float% but not occurence as int
            freq = fre*dfs['freq-cfc'][['total']].rename(columns={'total':'nb_'+ax[d]})
            codf = pd.concat([codf,freq], axis = 1)
            codf = codf[codf['nb_'+ax[d]] >= axminocc[d]]
            freqMax.append(int(freq.median().loc['nb_'+ax[d]]))


    jsos=[]    
    for index, row in codf.iterrows():
        #remove row if nan        
        remove = False
        for d in range(dim):
            if str(row.iloc[d]) == 'nan':
                remove = True
                break
        
        if remove:
            continue #skip this language point with value nan

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
            rx=round(row.iloc[0],2) if dim>1 else 0,  # [x],
            ry=round(row.iloc[1],2) if dim >1 else round(row.iloc[0],2), # [y],
            rz= round(row.iloc[2],2) if dim == 3 else 0,
            color= groupColors[langnameGroup[index]], 
            style=groupMarkers[langnameGroup[index]],
            group=langnameGroup[index]
            ) ]
   
    jso='[ \n'+', '.join(jsos)+']'
    # print(jso,"\n \n")
    j=json.loads(jso)
    #print(j)
    nbLang = len(j)
    if verbose:
        #print('!!!!!!!!!!!!!', axtypes, ax, axminocc)
        print('number languages:',nbLang)
        print('occ max', freqMax)

    #idxMax = np.argmax(codf[x].values)
    #xlimMax = math.ceil(np.nanmax(codf[[ax[0]]].values))
    xlimMin = np.nanmin(codf[[ax[0]]].values) #math.ceil(np.nanmin(codf[[ax[0]]].values))

    mi, ma = np.nanmin(codf[ax].values), np.nanmax(codf[ax].values) #ax = [x,y] if dim = 2
    
    if (ma-mi)   < 10: divi = 1
    elif (ma-mi) < 60: divi = 5
    elif (ma-mi) < 120: divi = 10
    elif (ma-mi) < 600: divi = 50
    else: divi=100
    # print(444444444, mi, ma, divi, ma-((ma-.1) % divi)+divi)
    return j, nbLang, mi-(mi % divi), ma-((ma-.1) % divi)+divi, xlimMin,freqMax

if __name__ == '__main__':
    res = tsv2json('distance',x='subj',xminocc = 0,yty='head-intiality',y='comp:obj',yminocc = 0)

import json
import math
import pandas as pd 
import numpy as np

anafolder = 'sud-treebanks-v2.6-analysis'


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
    'Dravidian':'black',
    'isolate':'black',
    'Pama–Nyungan':'black',
    }
# groupMarkers={'Indo-European-Romance':'<','Indo-European-Baltoslavic':'^','Indo-European-Germanic':'v','Indo-European':'>','Sino-Austronesian':'s', 'Agglutinating':'+'}
groupMarkers={
    'Indo-European-Romance':'triangle',
    'Indo-European-Baltoslavic':'triangle',
    'Indo-European-Germanic':'triangle',
    'Indo-European':'triangle',
    'Sino-Austronesian':'star', 
    'Agglutinating':'cross', 
    'Semitic':'crossRot', 
    'Afroasiatic':'crossRot',
    'Niger-Congo':'rect',
    'Tupian':'rectRounded',
    'Arawakan': 'rectRounded',
    'Dravidian':'rectRot',
    'isolate':'circle',
    'Pama–Nyungan':'circle',
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

dfs={}

for ty,fi in {
    'menzerath': '/abc.languages.v2.7_typometricsformat_4.tsv',
    'direction': '/positive-direction.tsv',
    'distance': '/f-dist.tsv',
    'distribution':'/f.tsv'
    }.items():
    dfs[ty] = pd.read_csv(anafolder+fi,
            sep='\t',
            index_col=['name'],)
    # print(dfs['direction'])
    # print(dfs['direction'].head() )

minnonzero = 50

# cfc:
df = pd.read_csv(anafolder+'/cfc.tsv',
            sep='\t',
            index_col=['name'],)
goodcols = [name for name, values in df.astype(bool).sum(axis=0).iteritems() if values>minnonzero]

dfs['direction-cfc']=pd.read_csv(anafolder+'/posdircfc.tsv',
            sep='\t',
            index_col=['name'],)#[goodcols]
# print('nr columns:',len(dfs['direction-cfc'].columns)) #df[column])



def gettypes():
    print(11111,list(dfs.keys()) )
    return list(dfs.keys())


def getoptions(ty):
    print(333333,ty)
    # print(dfs['direction'].head(),list(dfs[ty].head()) )
    if ty == 'menzerath':
    	return sorted(list(dfs[ty].head()))
    return list(dfs[ty].head())

def tsv2json(xty, x, xminocc, yty, y, yminocc):
    print('!!!!!!!!!!!!!', xty, x, xminocc, yty, y, yminocc)
    print('number languages:',len(dfs[xty]), (len(dfs[yty])))
    if xty==yty: codf = dfs[xty]
    else: codf = pd.concat([dfs[xty], dfs[yty]], axis=1)
    if 'nb_'+x in dfs[xty].columns.values.tolist():
        codf = codf[codf['nb_'+x] >= xminocc]
    if 'nb_'+y in dfs[yty].columns.values.tolist():
        codf = codf[codf['nb_'+y] >= yminocc]
    nblang = len(codf)
    
    jsos=[]
    
    for index, row in codf.iterrows():
        # print(groupColors)
        # print('***',index,'!!!',row)
        # print('***', index, '!!!', row[x], row[y])
        
        if str(row[x]) == 'nan': row[x] = 0
        if str(row[y]) == 'nan': row[y] = 0
       
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
            rx=row[x],  # [x],
            ry=row[y],  # [y],
            color= groupColors[langnameGroup[index]], 
            style=groupMarkers[langnameGroup[index]],
            group=langnameGroup[index]
            ) ]
   
    jso='[ \n'+', '.join(jsos)+']'
    # print(jso)
    j=json.loads(jso)
    # print(j)
    mi, ma = np.nanmin(codf[[x, y]].values), np.nanmax(codf[[x, y]].values)
    
    if (ma-mi)   < 10: divi = 1
    elif (ma-mi) < 60: divi = 5
    elif (ma-mi) < 120: divi = 10
    elif (ma-mi) < 600: divi = 50
    else: divi=100
    # print(444444444, mi, ma, divi, ma-((ma-.1) % divi)+divi)
    return j, nblang, mi-(mi % divi), ma-((ma-.1) % divi)+divi

if __name__ == '__main__':
    tsv2json('qsdf',x='subj',y='comp:obj')

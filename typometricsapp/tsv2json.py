import json
import pandas as pd 
import numpy as np

anafolder = 'sud-treebanks-v2.6-analysis'


groupColors={
    "Indo-European-Romance":'brown',
    "Indo-European-Baltoslavic":'purple',
    "Indo-European-Germanic":'olive',
    "Indo-European":'royalBlue',
    "Sino-Austronesian":'limeGreen', 
    "Agglutinating":'red', 
    "Semitic":'orange', 
    "Afroasiatic":'orange',
    'Niger-Congo':'black',
    'Tupian':'black',
    'Dravidian':'black',
    'isolate':'black'
    }
# groupMarkers={"Indo-European-Romance":'<',"Indo-European-Baltoslavic":'^',"Indo-European-Germanic":'v',"Indo-European":'>',"Sino-Austronesian":'s', "Agglutinating":'+'}
groupMarkers={
    "Indo-European-Romance":'triangle',
    "Indo-European-Baltoslavic":'triangle',
    "Indo-European-Germanic":'triangle',
    "Indo-European":'triangle',
    "Sino-Austronesian":'star', 
    "Agglutinating":'cross', 
    "Semitic":'crossRot', 
    "Afroasiatic":'crossRot',
    'Niger-Congo':'rect',
    'Tupian':'rectRounded',
    'Dravidian':'rectRot',
    'isolate':'circle'
    }

langNames={}
langcodef=open("languageCodes.tsv")
langcodef.readline()
for li in langcodef:
	lis = li.strip().split('\t')
	langNames[lis[0]]=lis[-1]
	
mylangNames={'ca': 'Catalan',
			 'cu': 'OldChurchSlavonic',
			 'nl': 'Dutch',
			 'el': 'Greek',
			 'ro': 'Romanian',
			 'es': 'Spanish',
			 'gd':'Gaelic',
			 'ug': 'Uyghur', 
			 'aii':'Assyrian',
			 'bxr':'Buryat', 
			 'fro':'OldFrench', 
			 'grc': 'AncientGreek',  
			 'gsw':'SwissGerman',
			 'gun': 'MbyáGuaraní',
			 'hsb':'UpperSorbian',
			 'kmr':'Kurmanji',
			 'kpv':'Komi', 
			 'lzh':'ClassicalChinese',
			 'orv':'OldEastSlavic',
			 'pcm':'Naija',
			 'qhe':'HindiEnglish',
			 'sms':'SkoltSami',
			 'sme':'NorthSami', 
			 'swl':'SwedishSign',   
			 'yue':'Cantonese'
				 }
			

langNames = dict(langNames, **mylangNames)

langnameGroup={li.split('\t')[0]:li.split('\t')[1] for li in open('languageGroups.tsv').read().strip().split('\n')  }

dfs={}

for ty,fi in {
    'direction':'/positive-direction.tsv',
    'distance':'/f-dist.tsv',
    'distribution':'/f.tsv'
    }.items():
    dfs[ty] = pd.read_csv(anafolder+fi,
            sep='\t',
            index_col=["name"],)
    # print(dfs['direction'])
    # print(dfs['direction'].head() )

minnonzero = 50

# cfc:
df = pd.read_csv(anafolder+'/cfc.tsv',
            sep='\t',
            index_col=["name"],)
goodcols = [name for name, values in df.astype(bool).sum(axis=0).iteritems() if values>minnonzero]

dfs['direction-cfc']=pd.read_csv(anafolder+'/posdircfc.tsv',
            sep='\t',
            index_col=["name"],)#[goodcols]
# print('nr columns:',len(dfs['direction-cfc'].columns)) #df[column])



def gettypes():
    print(11111,list(dfs.keys()) )
    return list(dfs.keys())


def getoptions(ty):
    print(333333,ty)
    # print(dfs['direction'].head(),list(dfs[ty].head()) )
    return list(dfs[ty].head())

def tsv2json(xty, x, yty, y):
    print("!!!!!!!!!!!!!",xty, x, yty, y)
    xdf = dfs[xty][[x]]
    ydf = dfs[yty][[y]]
    codf = pd.concat([xdf, ydf], axis=1)
    # print(xdf)
    # print(ydf)
    # print(codf)
    jsos=[]
    
    for index, row in codf.iterrows():
        # print('***',index,'!!!',row)
        # if index not in langnameGroup:
        #      print('===',index)
        #      qsdf
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
            rx=row.iloc[0],#[x],
            ry=row.iloc[1],#[y], 
            color= groupColors[langnameGroup[index]], 
            style=groupMarkers[langnameGroup[index]],
            group=langnameGroup[index]
            ) ]
   
    jso='[ \n'+', '.join(jsos)+']'
    # print(jso)
    j=json.loads(jso)
    # print(j)
    return j

if __name__ == '__main__':
    tsv2json('qsdf',x='subj',y='comp:obj')
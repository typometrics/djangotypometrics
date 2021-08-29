### compute distances between 2D graph:


* for language distribution and DTW:

python3 distance.py

* for stable matching 

#a bug occured when I tested this file just now, I will submit 'distanceMarry.py' later, after bug fixed

python3 distanceMarry.py

#### groups
'distance' is the current measure group,
to change it as 'menzerath' or 'direction'

* open *distance.py* in main fct, line329-331, change the comment '#' of group <br/>
   group = 'distance' <br/>
    #group = 'direction'<br/>
    #group = 'menzerath'<br/>
* open *distanceMarry.py* in main fct, line297-299, change the comment '#' of group 


#### version
SUD as default version

UD:
* open *tsv2json.py*, at line 100-104, 
dfsSUD = getRawData(sudFolder)<br/>
#dfsUD = getRawData(udFolder, sud = False)
<br/>
dfs = dfsSUD #1162 min = 60 <br/>
#dfs = dfsUD #928 minnonzero = 60<br/>
<br/>
put them as follows:

#dfsSUD = getRawData(sudFolder)<br/>
dfsUD = getRawData(udFolder, sud = False)<br/>
<br/>
#dfs = dfsSUD #1162 min = 60 <br/>
dfs = dfsUD #928 minnonzero = 60 <br/>

* open *distance.py* in main fct, line321, change version as 'ud'
* open *distanceMarry.py* in main fct, line288, change version as 'ud'


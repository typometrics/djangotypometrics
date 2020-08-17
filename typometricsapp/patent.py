# -*- coding: UTF-8 -*-
####
# Copyright (C) 2010-2018 Kim Gerdes
# kim AT gerdes.fr
####
import requests
#import urllib
#import time
import json
import unicodedata
import codecs, os, re, traceback
from bs4 import BeautifulSoup


debug=False
debug=True
#debug=9

class Patent:
	"""
	patent.claims: string. the claims of the patent
	patent.descriptions: string. the description text
	patent.ipcclasses: dictioanry. Code --> machine code
	patent.url: string. URL where the information was taken
	patent.code: string. Used for finding the URL
	"""
	def __init__(self, code):
		self.code=code
		self.description=""
		self.claims=""
		self.url=None
		self.ipcclasses={}
	
	def __str__(self):
		return "___"+self.code+" ___ "+self.claims[:200]+"..."


#API key: 	
#AIzaSyASuuQ7fcPwQDY3Ei-5pCUKQd6nV_zoT-I
#010151085229053963321:ydolrttj-sa

#Referers: 	
#*.cloem.com/*

#https://www.googleapis.com/customsearch/v1?key=AIzaSyASuuQ7fcPwQDY3Ei-5pCUKQd6nV_zoT-I&cx=010151085229053963321:ydolrttj-sa&q=lectures&callback=handleResponse
def searchpatents(q):
	access_token = "AIzaSyASuuQ7fcPwQDY3Ei-5pCUKQd6nV_zoT-I"
	#cse_id = "010151085229053963321:ydolrttj-sa" # gerdes
	cse_id = "010151085229053963321:r4-ylsach2c" # patents
	#010151085229053963321:r4-ylsach2c
	# Build url
	start=1
	#search_text = "+(inassignee:\"Altera\" | \"Owner name: Altera\") site:www.google.com/patents/"
	# &tbm=pts sets you on the patent search
	#&q=EP1391424B2
	#&q=EP1391424B2+site%3Agoogle.com%2Fpatents
	qurl = 'https://www.googleapis.com/customsearch/v1?key={access_token}&cx={cse_id}&start={start}&num=10&tbm=pts&q={q}+site%3Agoogle.com%2Fpatents'.format(access_token=access_token,cse_id=cse_id,start=start,q=q)
	#+ urllib.quote(search_text)
	
	if debug: print("google searching",q)
	response = requests.get(qurl).json()

	print(len(response))
	#json.dumps(response.json(), indent=4))
	
	if "items" in response:
		rurl=None
		its= response["items"]
		for it in its:
			if q in it:
				rurl= it["formattedUrl"]
		if not rurl and its:
			rurl = its[0]["formattedUrl"]
		
		#print "rurl",rurl
		if not rurl.startswith('http'): rurl='https://'+rurl
		return rurl


	
def getEP(nr, typ="claims",ggbeforefail=True):
	
	
	if typ not in ["claims","description"]:return ""
	#nr="JP20080113151"
	#nr="JP2009234553"
	r = requests.get("http://ops.epo.org/3.1/rest-services/published-data/publication/epodoc/{nr}/{typ}".format(nr=nr,typ=typ))
	#r = requests.get("http://ops.epo.org/3.1/rest-services/published-data/application/epodoc/{nr}/{typ}".format(nr=nr,typ=typ))
	#print r.text
	
	answer=""
	
	soup = BeautifulSoup(r.text, "lxml")
	if r.status_code>300:
		answer += "\n".join(["can't obtain the patent automatically!"]+[m.text for m in soup.find_all('message')])
		if ggbeforefail:
			url=searchpatents(nr)
			if url: return getGGPatent(url,typ=typ,ggbeforefail=False)
	else:	
		if typ=="claims":
			for cs in soup.find_all('claims'):
				answer += "\n".join([c.text for c in cs.find_all('claim-text')])
		elif typ=="description":
			for ds in soup.find_all('description'):
				answer += "\n".join([c.text for c in ds.find_all('p')])
	return answer

def getUS(nr, typ="claims",ggbeforefail=True): 
	if typ not in ["claims","description"]:return ""
	
	url="https://www.google.com/patents/{nr}".format(nr=nr)
	
	return getGGPatent(url,typ=typ)

ipcclassre=re.compile(r"[A-H]\d\d[A-Z].*",re.U+re.I)
ipcsymbolre=re.compile(r"symbol\=([A-H]\d\d[A-Z]\w*)",re.U+re.I)

def getGGPatent(url,typ="claims",ggbeforefail=True):
	try:
		r = requests.get(url)
		r.encoding="utf-8"
	except:
		print("error:",url,typ)
		raise Exception("Cannot connect to {url}".format(url=url))
	if debug: 
		print(url)
		print("____________")
	if debug>2: print(r.text.encode("utf-8"))
	
	soup = BeautifulSoup(r.text, "lxml" )
	
	if r.status_code>300:
		try:
			print("\n".join(["gg can't obtain the patent automatically!"]+[m.text for m in soup.find_all('p')]))
		except:
			print("gg can't obtain the patent automatically!")
		if ggbeforefail:
			url=searchpatents(url)
			if url: return getGGPatent(url,typ=typ,ggbeforefail=False)
		else:
			raise Exception("Cannot connect to {url}".format(url=url))
		
	else:	
		patent=Patent(url)
		#if typ=="claims":
		#for cs in soup.find_all("div", class_="patent-section patent-claims-section"):
		for cs in soup.find_all("div", class_="claim-text"):
			print (",,,",cs)
		patent.claims += "\n".join([cs.text for cs in soup.find_all("div", class_="claim-text")])
		
		   
		#</li> <li> <div class="description-line-number">[0000] </div> <div id="p-1748" num="0000" class="description-line">where Enc is the cipher that encrypts plaintext P to C: C=Enc(P).</div>

		#elif typ=="description":
		#for cs in soup.find_all("div", class_="patent-section patent-description-section"):
		#for cs in soup.find_all("div", class_="description-line"):
		patent.description += "\n".join([cs.text for cs in soup.find_all("div", class_="description-line")])
		#print ",,,",patent.description
		
		"""  2018 version:
			<li itemprop="cpcs" itemscope repeat>
			<span itemprop="Code">H04L9/0656</span>&mdash;<span itemprop="Description">Pseudorandom key sequence combined element-for-element with data sequence, e.g. one-time-pad [OTP] or Vernam&#39;s cipher</span>
			<meta itemprop="Leaf" content="true">
            		</li>
		"""
		
		for cs in soup.find_all("li",itemprop="cpcs"): # check out all <li itemprop="cpcs"
			#print "mmmm",cs
			if cs.find_all("meta",itemprop="Leaf", content="true"): # if there is <meta itemprop="Leaf" content="true">
				for c in cs.find_all("span",itemprop="Code"): # check out all <span itemprop="Code">
					#print "nnn",c,"$$$",c.string
					if ipcclassre.match(c.string):  
						patent.ipcclasses[c.string]=None
					else: 
						print("weird ipc class",c.string)
						qsdf
		
		#for cs in soup.find_all("div", class_="patent-section patent-tabular-section"):
			#if cs.a['id']=="classifications":
				#for c in cs.find_all("span",class_="nested-value"):
					##print "___",c
					#for s in c.stripped_strings:
						##print "$$$",s
						#if ipcclassre.match(s):
							#if c.a:
								#sym=ipcsymbolre.search(c.a['href'])
								#if sym:	sym=sym.group(1)
							#patent.ipcclasses[s]=sym
							
		if patent.claims=="": patent.claims="Claims not found. Please paste claims manually."	
		patent.url=url	
		return patent


def getClaims(nr,ggbeforefail=True):
	"""
	main class
	exposed in rpyc
	"""
	
	try:	nr = unicodedata.normalize('NFKD', nr).encode('ASCII', 'ignore').strip()
	except:	nr = unicodedata.normalize('NFKD', str(nr)).encode('ASCII', 'ignore').strip()
	if nr[:2].upper() not in ["US","EP","WO","RE","CA"]: return "invalid code"
	if nr[:2].upper() in ["EP","WO"]:
		return getEP(nr,ggbeforefail=ggbeforefail)
	elif nr[:2].upper() in ["US","CA"]:
		return getUS(nr,ggbeforefail=ggbeforefail)
	elif nr[:2].upper() in ["RE"]:
		return getUS("US"+nr,ggbeforefail=ggbeforefail)
	


def getPatent(nr,ggbeforefail=True):
	"""
	main class
	exposed in rpyc
	
	always use google
	"""
	
	#try:	nr = unicodedata.normalize('NFKD', nr).encode('ASCII', 'ignore').strip().upper()
	#except:	nr = unicodedata.normalize('NFKD', str(nr)).encode('ASCII', 'ignore').strip().upper()
	#print(111,nr)
	nr=nr.strip().upper()
	if nr[:2] not in ["US","EP","WO","RE","CA"]: raise Exception("invalid code")

	if nr[:2] in ["RE"]: nr="US"+nr
	
	return getUS(nr,ggbeforefail=ggbeforefail)
	


	

patnums=""" US20030233323 US8017375 RE43318 EP1784745 US20030059987 US7283978 US7783546 US5193056 US5352605 US5843780 US6029141 US5848105 US5969705 US5566337 US5929852 US6424354 USRE39486 US5915131 US5519867 US6275983 US5920726 US5481721 US6343263 US7383453 US7469381 US7633076 US5946647 US20120127110 US7479949 US7362331 US7657849 US5838906 US4873662 US6384822 US8074167 US5016009 US4701745 US5579430 US6687745 US20100257023 US7451161 US7069308 US7117254 US7188153 US7478078 US6275213 US5933841 EP0625760 US4558302 US20050071741 US8183997 US4873662 US7281047 US7028074 US7486783 US7383337 US6763520 US6871232 US6230171 US6986135 US20040225719 US7496564 US7277904 US6374297 US6438652 US20030200178 US7194439 US7565424 US6816882 US7475145 US6772225 US6591253 US7337150 US7403785 US7401352 US6871232 US7072822 US7506021 US6871232 US6510466 US7457846 US7437730 US6978298 US7334222 US6950931 US6681330 US6928394 US7305431 US7213199 US6981037 US6925481 US5495607 US5825891 US6738799 US6963908 US7032089 US7254621 EP0266049 EP2059868 US7663607 US7469381 US20070150842 US7479949 EP0129439 US7689524 US7565613 US7873620 US20070276728 US20040003343 US20080005075 US7587616 US20070110338 US7370066 US20040148611 US749958 US20080082490 US20040111441 US20080082463 US6137498 US5341457 US5579430 US5960411 US6285999 US6269361 US6289319 US5627938 US5239624 US6389458 US5301348 US5794207 US4405829 US8024241 US5132992 US20100212675 US6026368 US20080281966 US20100199180 US7346545 US6192407 US6907566 US7454509 US7406501 US7668861 US7100111 US7373599 US5983227 US7599935 US7747648 US7269590 US2717437 US4313439 WO2006021430 US2004122530 WO2005039673 WO2007056504 US7686787 US2011224644 US7955302 US20060100494 US6572542 US20060253086 US20100125245 US6659982 US6554798 US7974123 US20020087056 RE35803 US5554166 US2002010432 US20090192461 US20060253085 WO2006102412 US5366609 US20110152757 US20100160902 US6774222 US6292788 US6567790 US4744028 EP2237816A2
"""



#patnums="""
#CA2394886C
#"""

#patnums="""
#US20030233323
#US8017375
#RE43318
#EP1784745
#"""
#patnums="""
#US20030059987
#"""

# twitter!
patnums="""
US8448084
"""

#TODO: done!
#this US20070150842
#should replace this US2007150842

#error: US20030059987


def countwords(filename):
	return len(codecs.open(filename, "r", "utf-8").read().split())

def nums2claims(nums,folder="claims/"):
	nums=nums.strip().split()
	if not os.path.isdir(folder):
		os.mkdir(folder)
	for num in nums:
		if debug: print(num)
		if not os.path.isdir(folder+num):
			os.mkdir(folder+num)
		if os.path.isfile(folder+num+"/ipcs.txt"): #  and False
			print("already done")
			continue
		patent = getPatent(num)
		if patent:
			
			with codecs.open(folder+num+"/claims.txt","w","utf-8") as f: f.write(patent.claims)
			with codecs.open(folder+num+"/description.txt","w","utf-8") as f: f.write(patent.description)
			with codecs.open(folder+num+"/ipcs.txt","w","utf-8") as f: f.write("\n".join([c+"\t"+str(s) for c,s in patent.ipcclasses.items()]))
			#break
		else:
			print(num, "failed!")


def nums2completeCloems(nums, enterIntoDatabase=True, username="cloem", riskLevel=2, inspirationText="", publishBaseClaim=True, standard="", publicationNow="As soon as possible", publicationName="Cloem", alreadyPublished=False, publishCreationDate=True, makeDoFile=False, dbpath="db/test2017.sqlite"):
	"""
	main function for creating the complete series from the given patent numbers
	"""
	from creation import createTemporary #makeSeriesCode, makeSeries
	from claimVocabulary import vocabulary
	import json 
	nums=nums.strip().split()
	infodic={}
	for num in nums:
		if debug: print("\n\n\n_____________",num,"_____________\n")
		
		# get the content online
		patent = getPatent(num)
		seedClaims=patent.claims
		listOfIpcClasses=patent.ipcclasses
		
		vocab=json.loads(vocabulary(seedClaims,listOfIpcClasses))		
		print("vocab",vocab)
		vocabu={}
		for let in vocab:
			print(let,vocab[let])
			for v in vocab[let]:
				vocabu[v]=None
		md5hex, human, orderNumber = createTemporary(username, seedClaims, json.dumps(sorted(vocabu)), additionalWords="[]", listOfIpcClasses=json.dumps(listOfIpcClasses), origKeywords="['HU']", origSeedClaims="", hu=True)
		
	
		
		if debug: print("md5hex, human, orderNumber",md5hex, human, orderNumber)
		
		## actually making the series
		#try:
			#makeSeries(orderNum, enterIntoDatabase=enterIntoDatabase, infodic=infodic)
		#except Exception, e:
			#print "omg.............................................",e
			#print traceback.format_exc()
		
		

		
	
if __name__ == "__main__":
	#print getClaims(u"WO2008014520","description")
	#print getClaims(u"WO2008014520")
	#print getClaims(u"WO0153198A1")
	
	#print getClaims(u"US5590305")
	#print getClaims(u"EP1391424B2")
	
	#nums2claims(patnums)
	#
	#print countwords("claims/US4558302")
	#print countwords("claims/US6659982")
	
	#patent = getUS("US8282626")
	#print patent.ipcclasses
	
	#print getPatent("US8448084")
	#nums2completeCloems(patnums, makeDoFile=True)
	#nums2claims(codecs.open("/home/kim/Documents/mega.cloem.core/BITCOIN/blockchainProject/patentnums/morgan.tsv","r","utf-8").read())
	#nums2claims(codecs.open("/home/kim/Documents/mega.cloem.core/BITCOIN/blockchainProject/patentnums/goldman.tsv","r","utf-8").read())
	#nums2claims("US20170250796A1")
	r = searchpatents("mayonaise")
	print(r)
	
	pass

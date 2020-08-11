import re, string, requests, os, glob
from collections import Counter
from algodraftapp.patent import nums2claims
from algodraftapp.claimin import analyzeClaim, makeClaimAnalysis, cleanupNewlines, suppressBadChars
#from docx import Document
#from docx.shared import Cm, RGBColor

#import nltk
#nltk.download('wordnet')

from nltk.corpus import wordnet

import spacy
import dominate
from dominate.tags import *

from hashlib import sha512

reStepTrigger	=	re.compile(r"comprises|comprising|includes|including|wherein|in which|whereby|configured", re.I+re.U)
remethsys	=	re.compile(r"(system|method|process|device|tool|set|circuit)", re.I+re.U)
rews	=	re.compile(r"(\W|\s)+", re.I+re.U)
resaid	=	re.compile(r"\bsaid\b", re.I+re.U)
renl	=	re.compile(r"\:?\n+", re.I+re.U)
rewordcounters	=	re.compile(r" \(?\d\d\d\d?\d?\)?", re.I+re.U)
reNumberstart	=	re.compile(r"^(\d+)[\.\)]")


def searchpatents(q):

	queryfilename = os.path.join('algodraftapp','patentsearches',rews.sub('_',' '.join(q.split()[:8]))+'_'+sha512(q.encode('utf-8')).hexdigest()+'.txt')
	if os.path.exists(queryfilename):
		gudeci = open(queryfilename).read()
		goodurl, description, citation_patent_number = gudeci.split('\n\n')
		return (goodurl, description, citation_patent_number)



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
	
	#if debug: print("google searching",q)
	response = requests.get(qurl).json()

	#print(len(response))
	#print("items" in response)
	#json.dumps(response.json(), indent=4))
	#return response
	goodurl = ''
	for countrycode in ['US','CA','EP']:
		if goodurl: break
		for it in response["items"]:
			#print(it)
			if it["formattedUrl"].split('google.com/patents/')[1].startswith(countrycode):
				#import pprint
				#pp = pprint.PrettyPrinter(depth=4)
				#pp.pprint(it)
				print(22222222222222,it)
				goodurl = it["formattedUrl"]
				description = it['pagemap']['metatags'][0]["dc.description"]
				print(33333,it['pagemap']['metatags'])
				citation_patent_number = it['pagemap']['metatags'][0].get("citation_patent_number", it['pagemap']['metatags'][0]['citation_patent_application_number'])
				
				break

	gudeci = '\n\n'.join([goodurl, renl.sub('\n',description), citation_patent_number])
	open(queryfilename, 'w').write(gudeci)
	return (goodurl, description, citation_patent_number)
	

def makeDefinitions(text):
	
	uselesslemmas={'a', 'about', 'accord', 'accordance', 'accord', 'according', 'activity', 'adapt',  'adjustment', 'amount', 'an', 'and', 'another', 'any', 'apparatus', 'are', 'article', 'as', 'assembly', 'associate',  'at', 'base',  'basis', 'be', 'between', 'by', 'characterize', 'chemical', 'circuit', 'claim', 'claims', 'co', 'communication', 'composition', 'compound', 'compounds', 'comprise', 'computer', 'consist',  'consists', 'control', 'couple', 'crystal', 'data', 'datum', 'define',   'denote', 'design', 'device', 'different', 'display', 'each', 'element', 'end', 'equal', 'first', 'fluid', 'follow', 'for', 'form', 'forth', 'fourth', 'from', 'further', 'gaming', 'great', 'greater', 'group', 'have', 'in', 'include', 'independently', 'inferior', 'information', 'last', 'least', 'less', 'machine', 'manner', 'manufacture', 'material', 'may', 'mechanism', 'medium', 'member', 'method', 'mixture', 'more', 'non', 'object', 'obtainable', 'obtain', 'of', 'on', 'one', 'operate', 'optical', 'optionally', 'or', 'ornamental', 'other', 'part', 'plurality', 'portion', 'process', 'product', 'profile', 'range', 'readable', 'recite', 'record', 'removable', 'respect', 'respective', 'said', 'same', 'say', 'second', 'select',  'set', 'smaller', 'so', 'step', 'steps', 'storage', 'substance', 'substitute',  'such', 'superior', 'system', 'take', 'than', 'that', 'the', 'thereof', 'thereon', 'thickness', 'third', 'to', 'transmit',  'two', 'unit', 'use', 'value', 'voice', 'way', 'when', 'wherein', 'which', 'window', 'with'}
	
	nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
	doc = nlp(text)
	
	
	lems = Counter([(token.lemma_,token.pos_) for token in doc if token.pos_ in ['NOUN','VERB','ADJ', 'ADV'] and token.is_alpha]) 
	#print(lems)
	
	definitions = []
	
	for (lem,pos),f in lems.most_common():
		if lem in uselesslemmas or len(lem)<3: continue
		#print("________________",lem, pos)
		
		syns = wordnet.synsets(lem)
		if not syns:
			if lem.endswith('able'):
				lem=lem[:-4]
				syns = wordnet.synsets(lem)
			elif lem.endswith('ly'):
				lem=lem[:-2]
				syns = wordnet.synsets(lem)
		#print(syns)
		alllemmasn=[]
		alllemmasv=[]
		alllemmasa=[]
		alldefsn=[]
		alldefsv=[]
		alldefsa=[]
		for syn in syns:
			#print(syn,syn.name(),syn.pos(),syn.lemma_names(),syn.lemmas(),syn.definition())
			if syn.pos()=='n':
				alllemmasn+=syn.lemma_names()
				alldefsn+=[syn.definition()]
			elif syn.pos()=='v':
				alllemmasv+=syn.lemma_names()
				alldefsv+=[syn.definition()]
			elif syn.pos() in 'ar':
				alllemmasa+=syn.lemma_names()
				alldefsa+=[syn.definition()]
		
		ns = Counter(alllemmasn).most_common()
		vs = Counter(alllemmasv).most_common()
		ars = Counter(alllemmasa).most_common()
		#print('ns',ns)
		#print('alldefsn',alldefsn)
		
		if ns:
			#print()
			# definitions are triples normal bold normal
			definitions += [(("An " if lem[0] in "aeiou" else "A "),lem," {inthesenseof} is a and/or means and/or designates one or more of: {defs}.".format(inthesenseof= '(in the sense of '+', '.join([v.replace('_',' ') for v,f in ns if v!=lem])+')' if len(ns)>1 else '', defs='; '.join(alldefsn)))]
		if vs:
			#print()
			definitions += [("In some embodiments the verb to ",lem,("{inthesenseof}can be replaced by: {defs}.".format(inthesenseof= ' (in the sense of '+', '.join([v.replace('_',' ') for v,f in vs if v!=lem])+') ' if len(vs)>1 else ' ', defs='; '.join(alldefsv))))]
		if ars:
			#print()
			d=" {inthesenseof} means: {defs}.".format(lem=lem,inthesenseof= '(in the sense of '+', '.join([v.replace('_',' ') for v,f in ars if v!=lem])+')' if len(ars)>1 else '', defs='; '.join(alldefsa))
			definitions += [("",lem.title(),d)]

	for d in definitions:
		if len(d)!=3:
			print(d)
			qsdf
	
	return definitions

def removepunct(s):
	rea	=	re.compile(r'[]', re.I)
	return rea.sub(' ',s)

def removeaccording(s):
	#according to Claim 17 when
	rea	=	re.compile(r'\s+according to Claim \d+\s+', re.I)
	return rea.sub(' ',s)
def furthercomprising(s):
	rea	=	re.compile(r'\s+further comprising\:?\s+', re.I)
	return rea.split(s)[-1]
	
def firstlower(s):
	return s[0].lower()+s[1:]

def befaft(s, words): # splits at first occurrence of word from words
	reSplit	=	re.compile(r'(\b'+r'\b|\b'.join([w.replace('_',' ') for w in words.split()])+r'\b)', re.I)
	return [t.strip() for t in (reSplit.split(s, maxsplit=1)+['',''])[:3]]
	
def makedescription(claimsOrig):
	
	claimtexts = {}
	developments = {}
	#print(claimsOrig) 
	for i,ic in claimsOrig.items(): # claimsOrig is dictionary: nr -> list of lines eg {1: ['1. A circuit configured to:', '- receive signals o	
		lines = [icc[reNumberstart.search(icc).end():].strip() if reNumberstart.search(icc) else icc for icc in ic ]
		#print(i,lines)
		text = '\n'.join(lines)
		claimtexts[i]=text
		#print(i,text)
		#for icc in ic:
			#if reNumberstart.search(icc): icc=
		if i==1: developments[i]=text
		else:
			dev = 'In a development, '
			#if reStepTrigger.search(text): # 'wherein' in text:
			before, _, after = befaft(text, "wherein in_which whereby") #text.split('wherein')[:2]
			if after:
				#print(before, after) comprises comprising includes including 
				if 'comprising' in before:
					before = before.split('according')[0].strip()  # remove: according any preceding Claim ...
					before = before.replace('comprising','comprises')
					dev += firstlower(before)+' and '
				dev+=after.strip()
			elif 'further configured to' in text:
				before, after = text.split('further configured to')[:2]
				before = before.split('of any preceding')[0].strip()  # remove: of any preceding ...
				dev += firstlower(before) + ' is configured to' + after
			else: # independent claim?
				if 'claim' in text.lower():
					text = removeaccording(text) 

					if 'claim' in text.lower():
						text = furthercomprising(text)
						if 'claim' in text.lower():
							print('\n______________',i,text)
							azer
					# todo: other ways to remove claim references
				dev=text
					
			if 'claim' in dev.lower(): 
				print('before:',before)
				print('after:', after)
				print('->',dev)
				qsdf
			else: developments[i]=dev
	return claimtexts, developments
	
#def algodraft(cfile = "claims/US8448084B2/claims.txt", overwrite=False):
def algodraft(claimstext):
	########################################################
	
	#claims = open(cfile).read()
	theclaims = resaid.sub('the',claimstext)
	theclaims = suppressBadChars(theclaims)
	theclaims = rewordcounters.sub('',theclaims)

	print("\n____ doing",theclaims[:20].replace('\n',''))
	
	#claimsBase, allFillers, allSteps, claimsOrig, tree 	= analyzeClaim(theclaims, returnTree=True, skipReferenceErrors=True)
	##alreadysteps=[]
	#for i,st in list(claimsBase.items()):
		#print('___',i,st)
		#for sst in st.values():
			#for ssst in sst:
				##print('***',len(ssst),ssst)
				#ssst = rewordcounters.sub('',ssst)
				#if ssst not in alreadysteps:
					#if 'claim' in ssst.lower():
						#print('in step computation, skipped:',ssst)
					#else:
						#alreadysteps +=[ssst]
	#print('_______________')
	#print(alreadysteps)
	#return
	#print(cleanupNewlines(theclaims.split('\n')))
	#print((theclaims))
	errorfile = 	os.path.join('algodraftapp','errorlog',rews.sub('_',theclaims[:20])+'.reference.errors.txt')	
	error, individualClaims, claimsOrig = makeClaimAnalysis(theclaims, numbered=False, readable=True, skipReferenceErrors=errorfile)
	
	
	# extract the first two lines of the first claim:
	firstclaim = ' '.join([icc[reNumberstart.search(icc).end():].strip() if reNumberstart.search(icc) else icc for icc in claimsOrig[1] ][:2])
	firstclaim = firstclaim.translate(str.maketrans('', '', string.punctuation)).replace('  ',' ').replace('one or more ','')
	
	# print(firstclaim)
	#firstclaim = renl.sub(' ',individualClaims[1][0])
	print('firstclaim:::',firstclaim)
	methodof = None
	before, _, after = befaft(firstclaim, "wherein in_which whereby comprises comprising includes including")
	if len(before.split())>5:
		title = ' '.join(before.split()[:10])
		before, methodsystem, after = befaft(title, "system method process device tool set circuit")
		#print(999,before, methodsystem, after)
		#aftermethod = remethsys.split(firstclaim)[1]
		methodof = after.translate(str.maketrans('', '', string.punctuation))
		
		#print('methodof',methodof)
	else:
		print(before)
		print(after)
	
		#return
		#print(firstclaim)
		methodsystem = remethsys.search(firstclaim)[0]	
		m = reStepTrigger.search(firstclaim) # re.compile(r"comprises|comprising|includes|including|wherein|in which|whereby|configured to", re.I+re.U)
		
		if m:
			aftertrigger = reStepTrigger.split(firstclaim)[1]
			print('aftertrigger:::',aftertrigger)	
			
			for lil in aftertrigger.split('\n'):
				lil = lil.strip()
				if lil and lil.split()[0].endswith('ing'):
					methodof = lil.translate(str.maketrans('', '', string.punctuation))
					break
		if methodof:
			title = "A "+methodsystem+" of "+methodof
		else:
			aftermethod = remethsys.split(simpfirstclaim)[1]
			aftermethod = lil.translate(str.maketrans('', '', string.punctuation))
			title = "A "+methodsystem+' '+' '.join(aftermethod.split()[:10])
			#print(aftermethod)
			#qsdf
	title = title.replace('andor','and/or')
	print('======>',title)
	
	# docfilename = os.path.join(os.path.split(cfile)[0],title.replace('/',' ')+'.docx')
	# if not overwrite and os.path.exists(docfilename):
	# 	print('doc file',docfilename,'exists. Continuing...')
	# 	return
	
	doc = dominate.document(title=title)
	# document = Document()
	with doc: 
		container = div(cls='container')
		
		with container:
			h1(title)
			h2("Technical field")
	# document.add_heading(title, 0)
	# document.add_heading("Technical field", level=1)
	
	
	if methodof: 
		with container:
			# p = document.add_paragraph('The documents describes examples of systems and methods of '+methodof)
			p('The documents describes examples of systems and methods of '+methodof)
	else: 
		with container:
			# p = document.add_paragraph(('The documents describes examples of a '+methodsystem+' '+' '.join(aftermethod.split()[:10]).replace('andor','and/or')))
			p('The documents describes examples of a '+methodsystem+' '+' '.join(aftermethod.split()[:10]).replace('andor','and/or'))
	
	q=methodof if methodof else title
	goodurl, description, citation_patent_number = searchpatents(q)
	description=description[0].lower()+description[1:] # first letter lower
	redescriptionstarters=re.compile(r"the present disclosure involves ") #TODO: find more!
	with doc: 
		container = div(cls='container')
		with container:
			h2("Background")
			p("The patent document number {patnum} discloses {description}".format(patnum=citation_patent_number, description=redescriptionstarters.sub('',description)))
			p("This approach presents limitations.")
	# document.add_heading("Background", level=1)
	
	# p = document.add_paragraph("The patent document number {patnum} discloses {description}".format(patnum=citation_patent_number, description=description))
	# p = document.add_paragraph("This approach presents limitations.")


	firstclaim = theclaims.split('2.')[0]
	firstclaim=firstclaim[0].lower()+firstclaim[1:]
	firstclaim=firstclaim.replace('\n',' ')
	firstclaim = resaid.sub('the',firstclaim)
	with doc: 
		container = div(cls='container')
		with container:
			h2("Summary")
			p("There is described "+firstclaim)
			h3("Detailed Description")
			p("Advantageously, embodiments of the invention improve:")
			list = ul()
			for adv in 'speed reliability consistency synchronization coupling efficiency'.split():
				list += li(adv)
			h3("Definitions")
			list = ul()
			for aa,bb,cc in makeDefinitions(theclaims):
				# pp=document.add_paragraph(a, style='List Bullet')
				lll = li(aa)
				list += lll
				lll += b(bb) 
				lll += dominate.util.text(cc)

				# + p(cc)
				# pp.add_run(b).bold = True
				# pp.add_run(c)
	# document.add_heading("Summary", level=1)
	
	# pp = document.add_paragraph()
	
	# document.add_heading("Detailed Description", level=2)
	# pp = document.add_paragraph("Advantageously, embodiments of the invention improve:")	
	# for adv in 'speed reliability consistency synchronization coupling efficiency'.split():
	# 	document.add_paragraph(adv, style='List Bullet')
	
	# document.add_heading("DETAILED DESCRIPTION", level=1)
	# document.add_heading("Definitions", level=2)
	
	
	# for a,b,c in makeDefinitions(theclaims):
	# 	pp=document.add_paragraph(a, style='List Bullet')
	# 	pp.add_run(b).bold = True
	# 	pp.add_run(c)
		
	claimtexts, developments = makedescription(claimsOrig)
	
	
	
	# document.add_heading("Developments (enriched recopy of claims)", level=1)
	with doc: 
		container = div(cls='container')
		with container:
			h2("Developments (enriched recopy of claims)")
			list = ul()
			for i,dev in developments.items():
				lll = li(claimtexts[i])
				
				# pp = document.add_paragraph('', style='List Number 2')
				# pp.num_id = 1
				# pp= pp.add_run(claimtexts[i])
				# lll = li()
				if claimtexts[i]!=dev:
					# pp.font.color.rgb = RGBColor(0xaa, 0xaa, 0xaa)
					# pp = pp.add_run('\n'+dev) 
					lll += p(dev, style='color:gray')
				list += lll

			p("The patent document number {patnum} discloses {description}".format(patnum=citation_patent_number, description=redescriptionstarters.sub('',description)))
			p("This approach presents limitations.")
				#p = document.add_paragraph(firstclaim, style='List Bullet')
				#numId = document.get_new_list("10")
				# for i,dev in developments.items():
				# 	pp = document.add_paragraph('', style='List Number 2')
				# 	pp.num_id = 1
				# 	pp= pp.add_run(claimtexts[i])
				# 	if claimtexts[i]!=dev:
				# 		pp.font.color.rgb = RGBColor(0xaa, 0xaa, 0xaa)
				# 		pp = pp.add_run('\n'+dev) 
		container = div(cls='container')
		with container:
			p('Any one of the presently described embodiments can be advantageously combined with any other one embodiment.',cls='blockquote')
			p('The expression "A and/or B" means "A" or "B" or "A and B". ',cls='blockquote')
	

	
	return doc.render()



	
	
	
	document.add_page_break()
	

	document.add_paragraph(
	'first item in unordered list', style='List Bullet'
	)
	document.add_paragraph(
	'first item in ordered list', style='List Number'
	)

	document.add_picture('veltz.png', width=Cm(3.25))

	records = (
	(3, '101', 'Spam'),
	(7, '422', 'Eggs'),
	(4, '631', 'Spam, spam, eggs, and spam')
	)

	table = document.add_table(rows=1, cols=3)
	hdr_cells = table.rows[0].cells
	hdr_cells[0].text = 'Qty'
	hdr_cells[1].text = 'Id'
	hdr_cells[2].text = 'Desc'
	for qty, id, desc in records:
		row_cells = table.add_row().cells
		row_cells[0].text = str(qty)
		row_cells[1].text = id
		row_cells[2].text = desc

	#document.add_page_break()
	
	document.core_properties.author = 'Cloem'
	
	document.save(docfilename)


def allclaimsin(filepattern="patents/fv**/claims.txt"):
	for f in glob.glob(filepattern, recursive=True):
		algodraft(f)
	

#allclaimsin()

def wordlist():
	words = "a about accordance according adapted an and another any apparatus are article as assembly associated at based basis be between by characterized chemical circuit claim claimed claims composition compound compounds comprise comprises comprising computer consist consisting consists control coupled data defined defining denote design device different display each element end equal first following for form forth from further greater group having in includes including independently inferior information is least less machine manner manufacture material may mechanism medium member method mixture more object obtainable obtained of on one operating optionally or ornamental other part plurality portion process product profile range readable recited recording removable respect respective said same second second selected set smaller so step steps storage substance substituted such superior system than that the thereof to transmitted two unit use value way when wherein which with".split()
	print("', '".join(words))
	
#wordlist()

if __name__ == '__main__':
	pass



#c = nums2claims("US8448084B2")
#print(c)

 

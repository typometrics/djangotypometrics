# -*- coding: UTF-8 -*-

import codecs,  re,  os, sys, hashlib # nltk
from collections import OrderedDict
from html.entities import name2codepoint


debug=False
#debug=True
#debug=2


class ReferenceError(Exception):
	"""Base class for exceptions in this module."""
	def __init__(self, expr, line):
		self.expr = expr
		self.line = line
		if debug: print(line)


################### text normalization stuff

reStrangeSpace=re.compile(r" (?=[;:,.])",re.I+re.U)
reNoSpace=re.compile(r"(?<=[;:,.])(?=[^ ])",re.I+re.U)
reMultipleSpace=re.compile(r" +",re.I+re.U)
reMultipleReturn=re.compile(r"[\n\r]+",re.I+re.U)
rePeriodNumber=re.compile(r"(?<=\w\.)(?=(\d+)\.)")

windowsGarbage = {130 :"‚", 131 :"ƒ", 132 :"„", 133 :"…", 134 :"†", 135 :"‡", 136 :"ˆ", 137 :"‰", 138 :"Š", 139 :"‹", 140 :"Œ", 145 :"‘", 146 :"’", 147 :"“", 148 :"”", 149 :"•", 150 :"–", 151 :"—", 152 :"˜", 153 :"™", 154:"š", 155 :"›", 156 :"œ", 159 :"Ÿ"}
windowsGarbageRe=re.compile("["+"".join([chr(c) for c in windowsGarbage ] ) +"]", re.U)
getRid = [r"\/\*", r"\*\/"]  # some garbage to kick out
	
weirdRefNumbers = re.compile(r" \(\d[\d\-abcdefg\,\. ]*?\)[, \.\n]",re.U) # in case references to figures etc are remaining

stepReplacements = {"step (i)":"the first step", "step (ii)":"the second step", "step (iii)":"the third step", "step (iv)":"the forth step", "step (v)":"the fifth step","step (a)":"the first step", "step (b)":"the second step", "step (c)":"the third step", "step (d)":"the forth step", "step (e)":"the fifth step", "steps (i) and (ii)":"the first two steps" , "steps (a) and (b)":"the first two steps" }


def normalize(txt):
	"""
	makes a better version of the text
	
	imported into checkClaims
	"""
	txt = specialChar2Uniode(txt)
	if windowsGarbageRe.search(txt):
		for c in windowsGarbage: # badly coded characters are repleced by correct ones
			#print windowsGarbage[c],unichr(c).encode('utf-8'), "mmmm"
			txt=txt.replace(chr(c),windowsGarbage[c].decode("utf-8"))
	for g in getRid : 	txt = re.sub(g," ",txt)
	txt = re.sub("[ \t\r\f\v\n]*\n+[ \t\r\f\v\n]*","\n",txt)
	txt = re.sub("[ \t\r\f\v]+"," ",txt)#[1:-1]
	
	txt = reNumberedClaimStart.sub(r"\n\1",txt)
	txt = reClaimStart.sub(r"\n\1",txt)
	txt = rePeriodNumber.sub("\n", txt).strip()
	for ng in reRef.finditer(txt): # method as in (1)
		txt = txt.replace(ng.group(0),ng.group(0).replace("(","claim ").replace(")","")) # --> method as in claim 1
	txt = weirdRefNumbers.sub(" ", txt).strip()
	for repl in stepReplacements: 
		txt = txt.replace(repl,stepReplacements[repl])
			
	txt = reMultipleSpace.sub(" ", txt).strip()
	txt = reMultipleReturn.sub("\n", txt).strip()
	txt = reStrangeSpace.sub("", txt).strip()
	txt = reNoSpace.sub(" ", txt).strip()
	txt = txt.replace('\ufeff'," ")
	txt = reMultipleSpace.sub(" ", txt).strip()	
	return txt	

	
def specialChar2Uniode(codeHTML):
	"""
	trying to replace things of type &#1234; and &eacute; by the unicode chars
	"""
	codeHTML = re.sub("&.+?;",replacementHtmlUnicode,codeHTML)
	return codeHTML

def replacementHtmlUnicode(s):
		match = s.group()[1:-1] # get rid of & and ;

		if match[:2] == "#x" : # if of type &#xabcd;
			try :
			   return chr(int(match[2:], 16))
			except Exception as e:
				if debug: print("0. strange html like thing:",match,e)
		elif match[0] == "#" :
			i = int(match[1:])
			if i in windowsGarbage:
				return windowsGarbage[i].decode("utf-8")
			else:
				try :
					return chr(i)  # if of type &#1234;
				except Exception as e:
					if debug: print("1. strange html like thing:",match,e)
					return " "
		try :
			return chr(name2codepoint[match])
		except Exception as e:
				if debug: print("2. strange html like thing:",match,e)
				return " "


	

reNotGood=re.compile(r"[^\w\d\n\r ,;:§@#/\.\+\-\‒–—―\(\)\[\]\{\}\<\>\='\"‘’“”„”«»\%‰‱…≦≧·|√™°±≡′″‴]",re.I+re.U)

def checkChars(txt):
	badChars=[]
	for ng in reNotGood.finditer(txt):
		badChars+= [ng.group(0)+" (unicode character "+str(ord(ng.group(0)))+")"]
	return badChars

def markupChars(txt, badChars):
	#markupText=txt.replace("\n","<br/>")
	for bc in set(badChars):
		#print "ooo",bc
		txt=txt.replace(bc[0],'<span style="color:red" id="claimError">'+bc+"</span>")
	return txt

def suppressBadChars(txt):
	"""
	imported from creation.py, used to clean the seed claim
	"""
	return normalize(reNotGood.sub(" ",txt))


################### patent analysis


#reFurthercomprising=re.compile(r"(according to|of)( claim)? (\d+)\,? further comprising( the steps?( of)?)?",re.I+re.U)

#The analyte monitoring device of claim 1, wherein elements a and d ean be replaceably inserted into the analyte monitoring device as part of a cassette.
#The non-transitory computer-accessible medium as recited in claim 8 wherein the code portion for processing a mail item further comprises a code portion for encrypting the mail item.

#The method as recited in claim 1 wherein the redirectora
#reStep=re.compile(r"[;,.]( and)?$",re.I+re.U)

#The method according to claim 1 further comprising the steps of:
#according to claim 1 wherein

#print reStep.search("11. A method of synchronizing message information among a plurality of transceivers comprising the steps of:")

reClaimStart		=	re.compile(r"((i claim|we claim|what is claimed|claims?\s*\:?$|the [\w\-\']+ claimed is)\s*\:?)",re.I+re.U) # 2018 forced claims to be the only word of the line

reNumberstart	=	re.compile(r"^(\d+)[\.\)]")
reNumberedClaimStart	=	re.compile(r" (\d+\. (The|A) )")

reStepTrigger	=	re.compile(r"(comprises|comprising|includes|including|wherein|in which|whereby|further configured)", re.I+re.U)

#reComprising	=	re.compile(r"(?<=\, )?( (the|said|the said|each|every)( \w+)+)?( (additionally|further))? (comprises|comprising|includes|including)( the( following)? steps?( of)?)?\:?", re.I+re.U)

reWherein=		re.compile(r" ?(wherein|in which|whereby)( (the|said|the said|each|every)( [\w\-\']+)(( [\w\-\']+)*)( additionally|further| also)? comprises|includes)?\:?",re.I+re.U)
reATheComprising=	re.compile(r"(?<=\,)?( ?(a|an|the|said|the said|each|every)\b(( [\w\-\']+)+))[,:]?( (additionally|further|also))? (comprises|comprising|includes|including)( the( following)? steps?( of)?)?\:?", re.I+re.U)

#print reATheComprising.search("of items comprising a first plurality of items from the ").group(0)
#print reATheComprising.search("A process for displaying items to a user, comprising the steps of:").group(1)
#sys.exit()


reWhereinComprising=	re.compile(r"(?<=\, )?\b((wherein|in which|whereby)[,:]?( (the|said|the said|each|every)( [\w\-\']+)+ ?(additionally|further|also)? ?(comprises|includes))?|((a|an|the|said|the said|each|every)(( [\w\-\']+)+))[,:]? ?(additionally|further|also)? ?(comprises|includes|configured)|((a|an|the|said|the said|each|every)(( [\w\-\']+)+))?[,:]? ?(additionally|further|also)? ?(comprising|including|configured))( the( following)? steps?( of)?)?\:?|further configured", re.I+re.U)


#print reWhereinComprising.search("wherein said second portion of said connector member also includes a looped element").group(0)
#sys.exit()

reStepNumberstart=	re.compile(r"^(\(?(\w|ii|iii|iv)[).]|\-|[bcdefghijklmnopqrstuvwxyz] |a (?=\w+ing))",re.I+re.U)
reStepSeparate=		re.compile(r"; and|, and\;|; ",re.I+re.U)
reEnd=			re.compile(r"[\;\,\.]$",re.I+re.U)
reEndAnd=		re.compile(r"[\;\,\.]( and[\;\,\.]?)?$",re.I+re.U)
reSemiEndAnd=		re.compile(r"[\;\:\.]( and[\;\,\.]?)?$",re.I+re.U)
reStart=		re.compile(r"^[\;\,\.] ?",re.I+re.U)

#print reEndAnd.search(u'said first process generating events for controlling said user interface display while the second process remains as a foreground process and the first process is a background process, said events providing information regarding the operations performed by said first process for the second process; and')
#sys.exit()

#A method as claimed in any of claims 1 to 11, wherein 
#The system as defined in any one of claims 1 to 3, wherein said prescription medium is read by a computerized dispensary reader in communication with said centralized computer to authenticate each of said prescription medium and thereby authorize prescription filling at the dispensary.
reRef=re.compile(r"((as set forth in claim|as in claim|according to claim|according to any of claims?|as described in claim|as defined in claim|in accordance with claim|recited in claim|of claim|(claimed|defined)\,? in (any (one )?of )?claims?)|(system|method|process|device|tool|set|computer program product|computer program) (of|as( in)?)( claim)?) \(?(?P<ref>\d+)\)?\,?( above)?( to \d+)?([\d\-]*)?( or claims? \d+)?",re.I+re.U)

reRefBaseClaim=re.compile(r"according to claim|as set forth in claim|as in claim|as described in claim|as defined in claim|in accordance with claim|recited in claim|of claim|(as )?(claimed|defined),? in (any of )?claims?|according to (any of )?claims?",re.I+re.U)
#reAdditionally=re.compile(r" (additionally|further)",re.I+re.U)

reAfterBaseTerm=re.compile(r"\b(for|having)\b",re.I+re.U)

reIngBeforeBaseTerm=re.compile(r"\b(.+ing)\b",re.I+re.U)

#reIng=re.compile(r"^\w+ing,? |\, \w+ing,? ")
reIng=re.compile(r" \w+ing,? ")
reStrangeEnding=re.compile(r" (of|for|to|on|in|at|is|a|the|or|and|from|first|second|third)$")
reStrangeStart=re.compile(r"^(of|for|to|on|in|at|is|system|method|process|device|tool|set|item|items|mean|means|comprises|comprising|includes|including|computer program product|computer program) ")

#reBaseTerm1=re.compile(r"(according to claim|as recited in claim|of claim",re.I+re.U)
reSaidThe	=	re.compile(r"^(the|said|the said|each|every)",re.I+re.U)
reWhereInWhich	=	re.compile(r"^(wherein|in which|whereby|whereas|further configured)",re.I+re.U)
reWhereInWhichComma	=	re.compile(r"\b(wherein|in which|whereby|whereas|further configured)[ \t]*\,",re.I+re.U)
#reCompr	=	re.compile(r"^(comprising|comprises)",re.I+re.U)
reGoodBases	=	re.compile(r"^(apparatus|system|method|process|device|tool|set|circuit|computer program product|computer program)\b",re.I+re.U)
reAnywhereGoodBases	=	re.compile(r"\b(apparatus|system|method|process|device|tool|set|circuit|computer program product|computer program)\b",re.I+re.U)

reNotInformative	=	re.compile(r"(\b"+r"\b|\b".join("a the apparatus system method process device tool set of comprising".split())+r"\b)",re.I+re.U)

reClaims = re.compile(r"claims? \d",re.U+re.I)

maxsizeBaseterm	=  	5


def cleanupNewlines(parags):
	"""
	takes a list of paragraphs and combines those that look like they belong to the same claim
	"""
	newps=[]
	for i,p in enumerate(parags):
		#print (i,p)
		if reNumberstart.search(p) or reStepNumberstart.search(p):
			newps+=[p]
			#print "***",newps
		elif reNumberstart.match(newps[-1]): # last line was just number
			newps[-1]+=" "+p
		elif i>0 and reStrangeEnding.search(parags[i-1]):
			newps[-1]+=" "+p
		elif reStrangeStart.search(p):
			newps[-1]+=" "+p
		else:
			newps+=[p]
		#print newps
	return newps		
				


def makeSteps(t,sdic,fdic,baseterm):
	#print "----makeSteps",t,sdic,baseterm
	
	sdic[baseterm]=sdic.get(baseterm,[])
	if not t.strip():return baseterm
	t,bb=findSubsteps(t,sdic,fdic, baseterm)
	
	for s in reStepSeparate.split(t):
		if reStepNumberstart.sub("",s.strip()).strip():
			#if sdic[baseterm] and 
			
			#else:
			sdic[baseterm]+=[reStepNumberstart.sub("",s.strip()).strip()]

def extractBaseterm(baseterms):
	if debug>1:print("extractBaseterm:baseterms from:",baseterms,reAfterBaseTerm.search(baseterms))
	
	# if starts with common base: take just the base
	if reGoodBases.search(baseterms):		baseterms=reGoodBases.search(baseterms).group(1)
	# if common term after baseterm: cut there
	elif reAfterBaseTerm.search(baseterms): 	baseterms=reAfterBaseTerm.split(baseterms)[0]
	
	#if " for " in baseterms: baseterms=baseterms.split(" for ")[0]
	
	# if short enough: take all
	if len(baseterms.split())<=maxsizeBaseterm:
		baseterm=baseterms
	# otherwise take the last word
	else: 
		baseterm=baseterms.split()[-1]
	
	return baseterm

def findSubsteps(t, sdic, fdic, lastbaseterm):
	"""
	takes a text t, step dictionary sdic, filler dictionary fdic, and the last base term
	gives back the remaining text t and the found baseterm
	"""
	#if debug: print "----findSubsteps",t, sdic,fdic
	wc=reWhereinComprising.search(t)
	if debug>1:print("___finding steps in:",t,wc)
	if wc: # contains something that indicates steps
		se=wc.group(0).strip()
		if debug>1:print("__matched:",wc.group(0),":::se:::",se)
		w=reWherein.search(se) # wherein search
		c=reATheComprising.search(se) # comprising search
		if debug>1:print("_reWherein,reATheComprising w,c:",w,c)
		secbase=None # second base (for "wherein X" case)
		if w:	# wherein search
			baseterms=w.group(1).strip() # wherein the X
			try:
				if w.group(4): secbase=w.group(4).strip()
			except:pass

		elif c:	# comprising search
			baseterms=c.group(3).strip()
			if debug>1:print("__reATheComprising: ----",baseterms)
		else:
			baseterms=t[:wc.start()].strip()
		
		#baseterm=extractBaseterm(baseterms)
		try:	
			baseterm=extractBaseterm(baseterms)
			if not baseterm:
				baseterm=lastbaseterm
		except:	baseterm=lastbaseterm
		
		if secbase:baseterm=baseterm+"__"+secbase
		
		#print "baseterm",baseterm
		
		fdic[baseterm]=wc.group(0).strip()
		#print "ooooooo",baseterm,"___"
		makeSteps(t[wc.end():].strip(),sdic,fdic,baseterm)
		t=t[:wc.start()].strip()
		if debug>1:print("__yyy",dict(sdic), dict(fdic))	
	else:
		t,baseterm=t,""
	return t,baseterm
	
#print findSubsteps(normalize("a processor, a display, a memory, a user input device, a first process operative in the computer system, a second process operative in the computer system as a foreground process and a user interface on said computer system display under the control of the second process, a method for the first process to perform operations for the second process and control a content of the user interface on said computer system display, said content under control of the foreground second process operative in said computer system, said first process controlling the content to display information regarding the operations performed by the first process for the second process, said d  qs qsd qsd method for qsdf qsldf comprising the following steps:"))
#sys.exit()

def analyzeClaim(txt, returnTree=False, skipReferenceErrors=False):
	"""
	takes the claim tree text,
	returns claimsBase , allFillers, allSteps, claimsOrig
	"""
		
	
	
	# get all non empty lines that are not starters (startes = I claim,...)
	parags=[p.strip() for p in txt.split("\n") if p.strip() and not reClaimStart.match(p.lower())]
	#print "\n".join(parags)
	parags=cleanupNewlines(parags)
	#print "\n".join(parags)
	#qsdf
	tree={}
	
	claimsOrig={}
	
	claimsBase={} # claim number --> list of lines that are not whereins nor steps
	
	allSteps={} # claim number --> { base term --> list of steps }
	allFillers={} # claim number --> { base term --> filler } example: allFillers OrderedDict([(u'apparatus', u'the apparatus comprising'), (u'means ', u'said means for coding including'), (u'wherein', u'wherein said means for coding further includes')])

	
	claimnum=1
	
	# separate claims
	for i, p in enumerate(parags):
		if debug>1: print("\nline:",i+1,'____'+ p+'___')
		
		if reNumberstart.search(p): 
			claimnum=int(reNumberstart.search(p).group(1))
		
		claimsOrig[claimnum]=claimsOrig.get(claimnum,[])+[p]
	
	# handle each claim
	for claimnum,ps in sorted(claimsOrig.items()):
		
		tree[claimnum]=None
		
		coolClaim=False
		lastpsemicolonend=False
		lastbaseterm=None
		## find if it's a well organized claim=coolClaim (each line ends well)
		#if reStepTrigger.search(ps[0]):
			#for p in ps[1:]:
				#if reEndAnd.search(p):
					#coolClaim=True
				#else:
					#coolClaim=False
					#break
			#if len(ps)==1:
				#coolClaim=True
		
		#if coolClaim and 1==0:
			#if debug>1:print "\n\n\n coolClaim",claimnum,ps
		#else:
			
		if True:	
			if debug>1:
				#print "\n\n\n\nooo coolClaim",coolClaim
		
				print("\n\n\n\n_____________claimnum:",claimnum,"number parags:",len(ps))
				for p in ps: print("---",p)
				print("\n\n")
			#break
			#thisp=[]
			for pn,p in enumerate(ps):
				if debug>1:
					print("\n\n...now handling parag number:",pn,"claimnum:",claimnum)
					print("... p:",p,"\n")
			
				numbered,stepnum,ref,baseterm=None,None,None,None
				fillers=OrderedDict()
				steps=OrderedDict()
				
				psemicolonend=reSemiEndAnd.search(p)
				
				# first part: discovering segments ###########################################
				if reNumberstart.search(p): 
					claimnum=int(reNumberstart.search(p).group(1))
					numbered=True
					p=p[reNumberstart.search(p).end():].strip()
					if debug>1:print("numbered",claimnum)
				elif reStepNumberstart.search(p): 
					stepnum=reStepNumberstart.search(p).group(0)
					if debug>1:print("stepnum",stepnum)
					p=p[reStepNumberstart.search(p).end():].strip()
					
				if numbered or not claimsBase:
					claimsBase[claimnum]=[]		
					allSteps[claimnum]=OrderedDict()
					allFillers[claimnum]=OrderedDict()
				
				
				p=reEnd.sub("",p.strip()).strip() # remove ; at the end of the line
				p=reStart.sub("",p.strip()).strip()
				#p=reEndAnd.sub("",p.strip()).strip()
				if reRef.search(p):	
					if debug>1:print(":::::::::has reference. reRefBaseClaim:",reRefBaseClaim.search(p))
					try:
						ref=int(reRef.search(p).group('ref'))
						claimsBase[ref]
						if ref >= claimnum:
							raise KeyError
						if debug>1: print("=== found reference: reRef", ref,"in this claim number",claimnum)
					except KeyError: 
						errorMessage = "Wrong reference: "+str(claimnum)+" in: "+p+". The claim was suppressed."
						if debug: print(errorMessage)
						if skipReferenceErrors: 
							del tree[claimnum]
							del claimsBase[claimnum]
							del allSteps[claimnum]
							del allFillers[claimnum]							
							open(skipReferenceErrors,"a").write(errorMessage+"\n")
							break
						else:	raise ReferenceError("Reference Error", p)
						
						
					if reRefBaseClaim.search(p) and p[:reRefBaseClaim.search(p).start()].strip(): # second case and case nothing before the match
						containsBaseTerm=p[:reRefBaseClaim.search(p).start()].strip()
						if " for " in containsBaseTerm: containsBaseTerm=containsBaseTerm.split(" for ")[0]
						baseterm=containsBaseTerm.split()[-1]
						if debug>1:print("!!!! found reference with this baseterm:",baseterm)
					else:
						if reRef.search(p).group(4):
							baseterm=reRef.search(p).group(4) 
							if debug>1:print("!!!! found reference with this baseterm:",baseterm)
						else:
							if debug>1:print(ref,baseterm)
							print(111,ref,baseterm)
							baseterm = baseterm if baseterm else 'no baseterm found'
							errorMessage = "Reference for which I can't find baseterm: "+baseterm+" in: "+p+". The claim was kept but errors are possible."
							print(errorMessage)
							baseterm=""
							if skipReferenceErrors: 
								open(skipReferenceErrors,"a").write(errorMessage+"\n")
								continue #  and False
							else:	raise ReferenceError("Reference Error: Can't find base term", p)
							
							
					#print "pppp",p,p[:reRef.search(p).start()]
					# case: using xxx to 	eg: using the method of claim 1 to produce...  --> using the method to produce...
					if reIngBeforeBaseTerm.search(p[:reRef.search(p).start()]) and p[reRef.search(p).end():].strip().startswith("to"):
						p=p[:reRef.search(p).start()].strip()+" "+baseterm+" "+p[reRef.search(p).end():].strip()
					else:
						p=p[reRef.search(p).end():].strip()
					#print "pppp",p
					
					tree[claimnum]=ref
				#thisp += [p]	
				
				if reClaims.search(p):
					errorMessage = "Reference could not be resolved: "+str(claimnum)+" in: "+p+". The claim was suppressed."
					if debug>1:print(errorMessage)
					if skipReferenceErrors: 
						del tree[claimnum]
						del claimsBase[claimnum]
						del allSteps[claimnum]
						del allFillers[claimnum]
						open(skipReferenceErrors,"a").write(errorMessage+"\n")
						break
					else:	raise ReferenceError("Reference Error", p)
			
				#p=" ".join(thisp)
				if debug>1:print("now searching for substeps in:",p)
					
				# finding substeps:	
				while reStepTrigger.search(p):
					if debug>1:
						print("vvvvvvvvvvvvvvvv reStepTrigger - found:",reStepTrigger.search(p).group(0),"\t\tin:::::",p)
						if claimnum in allSteps and allSteps[claimnum]: print("-----------------allSteps:",allSteps[claimnum])
						print("baseterm before findSubsteps", baseterm)
					if coolClaim and claimnum in allSteps and allSteps[claimnum]:break
					if not baseterm: #  in case the findSubsteps won't give any results, we need to provide the old or another baseterm, better than nothing.
						if reAnywhereGoodBases.search(p):baseterm = reAnywhereGoodBases.search(p).group(1)
						else: baseterm = lastbaseterm
					if debug>1:print("__xxxx",p, dict(steps),dict(fillers), baseterm)
					p,baseterm = findSubsteps(p, steps,fillers, baseterm) # baseterm is needed if the reRef took already the baseterm away
					if debug>1:print("__ùùùù",p,baseterm)
					if debug>1: print(p,"\t\t_::::::::::found that baseterm:",baseterm)
					if p.strip() and reStepTrigger.search(p) and not baseterm:
						p=p[reStepTrigger.search(p).end():].strip()
				
				if debug>1:	
					print("results_________________________:numbered,stepnum,ref,baseterm,fillers,steps")
					for x in numbered,stepnum,ref,baseterm,fillers,steps:
						print(".....",x)
				if not baseterm:
					#print "jjj",steps,fillers, baseterm
					#print "jjj,p",p
					if reAnywhereGoodBases.search(p):baseterm = reAnywhereGoodBases.search(p).group(1) # extractBaseterm(p)#, steps,fillers, baseterm)
					else: baseterm = lastbaseterm
					#print "jjj",steps,fillers, baseterm
					
				if debug>1:print("iii",p)	
				p=reEnd.sub("",p.strip()).strip()
				p=reStart.sub("",p.strip()).strip()
				if debug>1:
					print("finished analyzing______"+p+"___")	
					print("#######################################################")
				#############################################
				# second part: cleaning and recombining parts
				if ref:
					claimsBase[claimnum]=claimsBase[ref][:] # copy stuff from the refered claim
					for bt in allFillers[ref]:
						if debug>1:print("copy from allFillers and allSteps((((",bt)
						allFillers[claimnum][bt]=allFillers[ref][bt][:]
						allSteps[claimnum][bt]=allSteps[ref].get(bt,[])[:]
						
						
				if p: # what to do with the remainders? 
					
					
					# if we have steps in the original claim (before adding any new coreference from the current line), add the remainders to one of those lists
					if not numbered and len(allSteps[claimnum]) :
						if debug>1:print("case not numbered and len(allSteps[claimnum])")
						
						#print allSteps[claimnum].keys()[-1]
						
						# check of indentation level: 
						# if choice of existing baseterms
						# and ";" or "; and" in the end of previous paragraph, 
						# then go back to first level of indentation
						if baseterm and baseterm in allSteps[claimnum]:bt=baseterm # somehow this steps contains a reference, eg using the method of claim 1. then use this baseterm
						elif len(allSteps[claimnum])>1 and (lastpsemicolonend or stepnum):
							bt=list(allSteps[claimnum].keys())[0] # choose the first key
						else:	bt=list(allSteps[claimnum].keys())[-1] # choose the last key
						
						p=reEndAnd.sub("",p.strip()).strip()
						allSteps[claimnum][bt]+=[p]

						if debug>1:print("bt:",bt,"\tlist:",allSteps[claimnum][bt])
					##if we have a stepnum
					#elif 
					else: 
						claimsBase[claimnum]+=[p]

				#if ref:
					#for bt in allFillers[ref]:
						#if debug>1:print "allFillers((((",bt
						#allFillers[claimnum][bt]=allFillers[ref][bt][:]
						#allSteps[claimnum][bt]=allSteps[ref].get(bt,[])[:]+allSteps[claimnum][bt]
					
				
				# putting the steps and fillers at the right place in the big dictionaries: allSteps[claimnum],allFillers[claimnum]		
				for bt in fillers:
					if debug>1:print("fillers((((",bt)
					allFillers[claimnum][bt]=allFillers[claimnum].get(bt,[])
					allSteps[claimnum][bt]=allSteps[claimnum].get(bt,[])
					bbt=bt
					if bt and "__" in bt:
						if debug>1:print("______________",bt)
						parts=bt.split("__")
						if parts[1] in allFillers[claimnum]: 
							bbt=parts[1]
							allSteps[claimnum][bbt]=allSteps[claimnum].get(bbt,[])
						#else:
							
							
							#bbt =  parts[0]
					if bbt not in  allSteps[claimnum]: 	allSteps[claimnum][bbt]=[]
					if bbt not in  allFillers[claimnum]: 	allFillers[claimnum][bbt]=[]
					
					
					# same line as previous or newstep?
					# newstep if
					# 	no choice
					# 	or (wherein and previous line not strange)
					# 	or (not wherein and ing)
					# 	or numbered (first step in paragraph)
					#print allSteps[claimnum]
					#print 
					newstep	= 	(not allSteps[claimnum][bbt]) or ( (reWhereInWhich.search(bbt) and (not reStrangeEnding.search(allSteps[claimnum][bbt][-1]) ) ) ) or ( (not reWhereInWhich.search(bbt)) and (not reIng.search(" ".join(steps[bt])) ) )  or numbered
					for step in steps[bt]:	
						if debug>1:print("''''",step,reEndAnd.search(step))
						step=reEndAnd.sub("",step.strip()).strip()
						if newstep:	allSteps[claimnum][bbt] 	+=	[step]
						else:		allSteps[claimnum][bbt][-1]	+=	" "+step
						
						newstep	= (not allSteps[claimnum][bbt]) or ( (reWhereInWhich.search(bbt) and (not reStrangeEnding.search(allSteps[claimnum][bbt][-1]) ) ) ) or ( (not reWhereInWhich.search(bbt)) and  reIng.search(step)  )
						
					if not allFillers[claimnum][bbt]: allFillers[claimnum][bbt]=fillers[bt]
					
					#if bbt=="in which":
						#print allSteps[claimnum]
						#print allFillers[claimnum]
						#sys.exit()
				
					if numbered:
						
						if not allFillers[claimnum]: # no filler at all
							bt=extractBaseterm(p)
							allFillers[claimnum][bbt]=[]
				lastpsemicolonend=psemicolonend	
				lastbaseterm=baseterm
				if debug>1:
					print("___end: parag number:",pn,"claimnum:",claimnum)
					print("___claimsBase",claimsBase[claimnum])
					print("___allFillers",allFillers[claimnum])
					print("___allSteps",allSteps[claimnum])
					
			#else: # continues here if the paragraph loop wasn't broken		
	if debug:		
		for i in claimsBase:
			print()
			print("i",i)
			print("claimsBase[i]",claimsBase[i])
			print("allFillers[i]",allFillers[i])
			for bt in allSteps[i]:
				print(bt, allSteps[i][bt])
	if debug>1:		
		for i in claimsOrig:
			print("claimsOrig",i,claimsOrig[i])
	#if debug:print "claimsBase , allFillers, allSteps",claimsBase , allFillers, allSteps	
	if returnTree:	return claimsBase , allFillers, allSteps, claimsOrig, tree
	else:		return claimsBase , allFillers, allSteps, claimsOrig



reponct=re.compile(r'(\s*[\.;:\,!\(\)§"-]+)(?!\d)')
recolumncomma=re.compile(r'\:\s*\,')

def tokenize(text):
	text=reponct.sub(r" \1 ",text)
	text=recolumncomma.sub(":",text)
	return text

nospacebefore=re.compile(r'(\s*[.,\)]+)')
nospaceafter=re.compile(r'([\(]+\s*)')

def nicetext(text):
	text=nospacebefore.sub(r"\1",text)
	text=nospaceafter.sub(r"\1",text)
	text=recolumncomma.sub(":",text)
	return text

#def out(txt,outf,nl,readable):
	#if readable:outf.write(nicetext(txt)+nl)
	#else:outf.write(tokenize(txt)+nl)


def makeClaimAnalysis(claimsText, numbered=False, readable=False, combineinwhichwithnextline=False, returnTree=False, skipReferenceErrors=False):
	"""
	central class for individualization
	returns:  
		error (either None or True or list of bad characters)
		individualClaims dic: claim num --> couple(indiv text, numbered indiv text)
		claimsOrig dic: claim num --> text of original claim
	
	used in two different contexts:
		1. check the user input
		2. analyze claim text in mass cloemization
	
	"""
	
	try:	
		if returnTree: 	claimsBase, allFillers, allSteps, claimsOrig, tree 	= analyzeClaim(claimsText, returnTree=returnTree, skipReferenceErrors=skipReferenceErrors) # here it happens
		else:		claimsBase, allFillers, allSteps, claimsOrig 		= analyzeClaim(claimsText, skipReferenceErrors=skipReferenceErrors)
	except ReferenceError as e:
		if debug: print("wrong reference. Please correct:::",e.line)
		print("wrong reference. Please correct:::",e.line)
		markupText=claimsText.replace(e.line,'<span style="color:red" id="claimError">'+e.line+"</span>")
		return True,{0:(markupText,"-")},{0:markupText}
	
	#claimsOrig={} # claim number --> list of lines of the original not individualized claim
	#claimsBase={} # claim number --> list of lines that are not whereins nor steps	eg: {1: [u'1. A method for attracting, increasing, or retaining customer interest and ...
	#allSteps={} # claim number --> OrderedDict{ base term --> list of steps } 	eg: {1: OrderedDict([(u'method', [u'selecting a size of a group of packages that...
	#allFillers={} # claim number --> { base term --> filler } 			eg: {1: OrderedDict([(u'method', u'said method comprising:')]), 2: OrderedDict([(u'method', u'said method comprising:'), (u'wherein__method', [])]), ...
	
	#if debug:print "\n\n\n\n________________claimsBase",claimsBase
	#if debug:print "\n\n\n\n________________claimsOrig",claimsOrig
	#if debug:print "\n\n\n\n________________allSteps",allSteps			
	#if debug:print "\n\n\n\n________________allFillers",allFillers
	
	individualClaims={}	
	
	for claimnum in sorted(claimsBase):
		if debug:print("\n\n\n\nclaimnum:",claimnum)
		outtext, outtextnumbered = "",""
		
		if numbered:	outtext+="___"+str(claimnum)+"___\n"
		outtextnumbered+="___"+str(claimnum)+"___\n"
		
		if claimsBase[claimnum]: # if there are base lines:
			# char after base lines
			#if at least two steps in the claim base and something behind: char=","
			#if len(claimsBase[claimnum]) and 
			if len(allFillers[claimnum]): 	post=""
			else: 				post="."
			if len(claimsBase[claimnum])==1:	nl=" "
			else:				nl="\n"
			#print i,claimsBase,claimsBase[i]
			claimsBase[claimnum][-1]+=post # adding the post to the last claim base
			
			for p in claimsBase[claimnum]: 
				if readable:	outtext+=nicetext(p)+nl
				else:		outtext+="p:__" +tokenize(p)+nl
				outtextnumbered+="p:__" +tokenize(p)+nl
		# now the claim bases are done.
		# now to the steps:
		#continue
		nl="\n"
		for i,bt in enumerate(allFillers[claimnum]):
			#print "bt",bt
			if debug:print("**********i,bt,fillers:",i,bt,allFillers[claimnum][bt])
			if bt in allSteps[claimnum]:
				if len(allSteps[claimnum][bt])>1:	pre=" - "
				else:				pre=""
				newsteps=[]
				for step in allSteps[claimnum][bt][:-2]: newsteps+=[pre+step+","]	
				try: newsteps+=[pre+allSteps[claimnum][bt][-2]+", and"] # adding ,and to the second last step
				except:pass
				if i == len(allSteps[claimnum])-1:	char="."
				else: 					char=","
				if allSteps[claimnum][bt] and allSteps[claimnum][bt][-1]: newsteps+=[pre+allSteps[claimnum][bt][-1]+char]
			
			# add reference to the process/method (the process comprising...) to the filler? 
			# only if 
			# not the first bt and not wherein step and list of steps > 1 and not already contains the/step:
			if i>0 and (not reWhereInWhich.search(bt)) and (bt in allSteps[claimnum] and len(allSteps[claimnum][bt])>1) and (not reSaidThe.search(allFillers[claimnum][bt])):
				allFillers[claimnum][bt] =" ".join([ "the",bt,allFillers[claimnum][bt] ]) 
				
			if allFillers[claimnum][bt]:		
				if readable:	outtext+=nicetext(allFillers[claimnum][bt])+"\n"
				else:		outtext+=tokenize(allFillers[claimnum][bt])+"\n"
				outtextnumbered+=tokenize(allFillers[claimnum][bt])+"\n"
				#out(allFillers[claimnum][bt],outf,nl,readable)
			if debug:print("newsteps",newsteps,"ooo",outtext+"___********")
			if combineinwhichwithnextline:
				if reWhereInWhich.search(outtext.strip().split()[-1]):
					outtext=outtext.strip()+" "
			for p in newsteps: 	
				#print "zzzzz",p

				if readable:	
					if numbered: outtext+="s:_"+bt+"_:___"+p+"\n"
					else: outtext+=p+"\n"
				else:	
					if numbered: outtext+=tokenize("s:_"+bt+"_:___"+p)+"\n"
					else: outtext+=tokenize(p)+"\n"
				outtextnumbered+=tokenize("s:_"+bt+"_:___"+p)+"\n"
				#print "outtext",outtext
				#out("s:_"+bt+"_:"+p,outf,nl,readable)
		# ugly hack to get rid of those commas after wherein,...:
		outtext=recolumncomma.sub(":",reWhereInWhichComma.sub(r"\1",outtext))
		outtextnumbered=recolumncomma.sub(":",reWhereInWhichComma.sub(r"\1",outtextnumbered))
		individualClaims[claimnum]=(outtext,outtextnumbered)
	if returnTree: 	return None,individualClaims,claimsOrig, tree
	else:		return None,individualClaims,claimsOrig


###########################################################################################################################

def individualize(folder, indiclaimf=None, 
			claimfile="claims.txt",
			numbered=False,readable=True, 
			numExtension=".num", problemExtension=".problem.html",
			skipReferenceErrors=False):
	"""
	main class of this module
	called from cloemseries
	folder: containing claims.txt file
	indiclaimf: path to indifile if None: add .indi
	skipReferenceErrors either False or a file name to write error information into
	"""
	claimfilename = os.path.join(folder,claimfile)
	print("&&&&&&& claimin.py &&&&&&&&&&& individualize", claimfilename)
	
	if not indiclaimf:
		indiclaimf = claimfilename+".indi"
	#patcode=os.path.basename(infolder)
	#print patcode,infolder,"ooooooooo",os.path.split(infolder),os.path.dirname(infolder)
	#1/0
	#basedir, inclaimsText = makebase(claimfilename, outbasefolder, human, patcode, origExtension)
	#simpleipcs = readipcs(infolder+"/"+ipcfile,basedir)
	
	#outfilename=basedir+patcode+indivExtension	
	with codecs.open(os.path.join(folder,claimfile), "r", "utf-8") as inf:
		inclaimsText=inf.read()
		
	error, individualClaims, claimsOrig = makeClaimAnalysis(inclaimsText, numbered, readable, skipReferenceErrors=skipReferenceErrors)
	
	if error:	
		#outfilename=claimfilename+problemExtension # because of reference error, individualization failed
		with codecs.open(os.path.join(folder,claimfile+problemExtension), "w", "utf-8") as outf:
			outf.write("\n\n".join([individualClaims[i][0].strip() for i in sorted(individualClaims)]))
	else:
		with codecs.open(indiclaimf, "w", "utf-8") as outf:
			outf.write("\n\n".join([individualClaims[i][0].strip() for i in sorted(individualClaims)]))
		with codecs.open(indiclaimf+numExtension, "w", "utf-8") as outf:
			outf.write("\n\n".join([individualClaims[i][1].strip() for i in sorted(individualClaims)]))
	
	#if not error: # write also numbered individual file
		#outf = codecs.open(outfilename+numExtension, "w", "utf-8")
		
		#outf.close()
	return error

###########################################################################################################################

	
def makebase(infilename,outbasefolder,human,patcode,origExtension):
	"""
	DEPRECATED
	makes the base directory
	writes the indifile for reference
	returns the name of the base directory
	"""
	inclaimsText = codecs.open(infilename, "r", "utf-8").read()
	inclaimsText = suppressBadChars(inclaimsText) # either in case of mass cloem production or strange characters slipped thru the user input control
	if human:
		basedir= outbasefolder+human+"/"
	else:
		md5hex = hashlib.md5(inclaimsText.encode('utf-8')).hexdigest()
		basedir= outbasefolder+patcode+"--"+md5hex+"/"
	
	try:	os.mkdir(basedir)
	except:
		if debug:	print("dir exists",basedir)
	
	#indifile=codecs.open(basedir+"indiClaims.txt","w","utf-8")
	infile=codecs.open(basedir+os.path.basename(infilename)+origExtension,"w","utf-8")
	infile.write(inclaimsText)
	infile.close()
	
	return basedir,inclaimsText

def readipcs(infilename,outbasefolder):	
	#DEPRECATED
	simpleipcs=[]
	with codecs.open(infilename,"r","utf-8") as inf, codecs.open(outbasefolder+"simpleipcs.txt","w","utf-8") as outf:
		for line in inf:
			ipc=line[:4]
			if ipc not in simpleipcs: 
				simpleipcs+=[ipc]
				outf.write(ipc+"\n")

	return simpleipcs
	
	
#def transformClaimFolder(infolder, outfolder, numbered=False,readable=False):
	#counter=0
	#for infile in os.listdir(infolder):
		##print "iiiiii",infile,os.path.isdir(infolder+"/"+infile)
		#if infile.endswith("~"):continue
		#if os.path.isdir(infolder+infile):continue
		
		#error=transformClaimFile(infolder+infile, outfolder+infile,numbered,readable)
		#if not error:counter+=1
		
				
		#print "finished individualizing",infile
	#return counter

def getInformativeCamel(claimsText,maxi=30): # for filename creation in creation.py
	try: txt = reNotInformative.sub("", makeClaimAnalysis(normalize(claimsText), numbered=False,readable=True, combineinwhichwithnextline=False, returnTree=False, skipReferenceErrors="getInformativeCamel.ReferenceErrors.txt")[1][1][0])
	except : txt = normalize(claimsText)
	camel=""
	words=txt.split()
	while len(camel)<maxi:
		try:	camel+=words.pop(0).title()
		except:	break
	return camel

############################# end: main classes ###################################""




if __name__ == "__main__":
	"""
	code for producing unit testing results
	"""
	
	#claimsText=codecs.open("inClaims/chocolate.txt","r","utf-8").read()
	#claimsText=codecs.open("inClaims/test1.txt","r","utf-8").read()
	#claimsText=codecs.open("inClaims/heart.txt","r","utf-8").read()
	#claimsText=codecs.open("inClaims/Bouquet/IT - Litigation - Apple Motorola Photo - EP2059868.txt","r","utf-8").read()
	claimsText="""A method as claimed in any of claims 24 to 32, ink-jet printing a solvent on to localised regions of insulating layers of the devices so as to dissolve the insulating layers in the regions to leave voids extending through the layers, and depositing electrically conductive material in the voids."""
	claimsText="""A method as claimed in claim 32, ink-jet printing a solvent on to localised regions of insulating layers of the devices so as to dissolve the insulating layers in the regions to leave voids extending through the layers, and depositing electrically conductive material in the voids."""
	claimsText="""3D motion picture adaption system comprising
- a 3D motion picture device for displaying 3D motion pictures, and
- a sensor device for detecting the position of the eyes of a viewer; and an adaption device for adapting the position of the displayed 3D motion pictures to the detected position of the viewer's fish eyes."""
	
	claimsText="""CLAIMS What is claimed is: 1. A method of manufacturing a customized wearable article comprising: a) providing a subject; b) obtaining image data regarding the subject's body or portion thereof; c) creating a virtual image of the subject using the image data regarding the subject's body or portion thereof; d) selecting a virtual wearable article from an article set; e) customizing the virtual wearable article utilizing the virtual image of the subject; and f) printing the article using a three dimensional printer. 2. The method of claim 1, wherein the subject is a human. 3. The method of claim 1, wherein a camera or 3D scanner is utilized to obtain the image data regarding the subject's body or portion thereof. 4. The method of claim 3, wherein the image data regarding the subject's body or portion thereof comprises information selected from shape, size, scale and dimension. 5. The method of claim 1, wherein a 3D scanner is utilized to obtain the image data regarding the subject's body or portion thereof. 6. The method of claim 5, wherein the image data regarding the subject's body or portion thereof acquired by the 3D scanner is transferred to a computer aided design program. 7. The method of claim 6, wherein the CAD program is used to modify the image data of the virtual image. 8. The method of claim 7, wherein the modified image data of the virtual image is utilized to customize features of the virtual wearable article. 9. The method of claim 8, wherein the features of the virtual article are selected from size, shape and thickness. 10. The method of claim 1, wherein image data is collected using a camera and a design tool. 11. The method of claim 1, wherein the virtual image is a 3D surface image. 12. The method of claim 1, wherein the virtual image is used to provide custom sizing information regarding the subject. 13. The method of claim 1, wherein the article comprises a single type of material. 14. The method of claim 1, wherein the article comprises two or more types of material. 15. The method of claim 1, wherein the article comprises two or more layers. 16. The method of claim 1, wherein a creation tool is utilized to create a computer readable script that includes information regarding the virtual image. 17. The method of claim 16, wherein the computer readable script identifies the virtual wearable article from the article set. 18. The method of claim 16, wherein the computer readable script utilizes the image data of the virtual image to customize the virtual wearable article. 19. The method of claim 16, wherein the computer readable script encodes a graphical user interface through which a user can modify virtual wearable article data in the computer readable script. 20. The method of claim 16, wherein the computer readable script is stored in a memory component. A method of manufacturing a customized wearable article comprising a) providing a subject; b) obtaining image data regarding the subject's body or portion thereof; c) creating a virtual image of the subject using the image data; d) creating a virtual wearable article using a creation tool; e) customizing the virtual wearable article utilizing the creation tool and the virtual image; and f) printing the customized virtual wearable article using a three dimensional printer. 22. The method of claim 20, wherein a 3D scanner is utilized to obtain the image data regarding the subject's body or portion thereof. 23. The method of claim 22, wherein the image data regarding the subject's body or portion thereof comprises information selected from shape, size, scale and dimension. 24. The method of claim 23, wherein a CAD program is used to modify and/or store the image data regarding the subject's body or portion thereof acquired by the 3D scanner. 25. The method of claim 24, wherein modified image data of the virtual image stored by the CAD program is utilized to customize features of the virtual wearable article. 26. A method of creating a customized wearable article comprising: a) obtaining image data regarding a subject's body or portion thereof using a 3D scanner; b) creating a virtual image of the subject's body or portion thereof; c) creating a virtual customized wearable article using information encoded in the virtual image; and d) printing the virtual customized wearable article on a 3D printer to create the customized wearable article. 27. The method of claim 26, wherein the virtual customized wearable article is printed on a local 3D printer. 28. The method of claim 26, wherein the virtual customized wearable article is printed on a remote 3D printer accessed via the internet. 29. The method of claim 26, wherein the virtual image of the subject's body or portion thereof is stored on a remote data server. 30. The method of claim 26, wherein creating a virtual customized wearable article using information encoded in the virtual image comprises using software that modifies a virtual wearable article with information encoded within the virtual image. 31. The method of claim 30, wherein the information encoded within the virtual image comprises information selected from size, shape, scale and dimension. 32. The method of claim 30, wherein the software is located on a local computer. 33. The method of claim 30, wherein the software is located on a retailer's server accessible via the internet. 34. The method of claim 30, wherein information encoding the virtual wearable article is stored on a retailer's data server. 35. The method of claim 26, wherein printing the virtual customized wearable article comprises processing of a computer-readable script encoding the virtual customized wearable article by a print/order management server. 36. A customized wearable article generated by the method of claim 26. 37. A method of creating a customized wearable article comprising: obtaining a 3D virtual image of the surface of a subject's body or portion thereof using a 3D scanner; modifying the 3D virtual image in order to augment, reduce or otherwise change a feature of the subject's body or portion thereof; and utilizing the modified 3D virtual image to manufacture the customized wearable article. 38. The method of claim 37, wherein the feature of the subject's body or portion thereof is the size of the subject's waist. 39. The method of claim 38, wherein the customized wearable article reduces the apparent size of the subject's waist when worn by the subject. 40. The method of claim 37, wherein the feature of the subject's body or portion thereof is the size of the subject's chest. 41. The method of claim 40, wherein the customized wearable article augments the apparent size of the subject's chest when worn by the subject. 42. The method of claim 37, wherein the feature of the subject's body or portion thereof is the subject's posture. 43. The method of claim 42, wherein the customized wearable article treats idiopathic scoliosis of the spine. 44. The method of claim 37, wherein the feature of the subject's body or portion thereof is the subject's biometric state. 45. The method of claim 44, wherein the customized wearable article inhibits detection of the subject's biometric state."""
	
	#print "________________",normalize(claimsText)
	#print reRef.sub("", makeClaimAnalysis(normalize(claimsText), numbered=False,readable=True, combineinwhichwithnextline=False, returnTree=False, skipReferenceErrors=True)[1][1][0].lower())
	
	#print getInformativeCamel(claimsText)
	
	#txt="""determining the average night length (NLAVE) by averaging the night lengths (NL) between a night starting time (NST) as determined by a photosensor and a night ending time (NET) determined by a photosensor for each of a plurality of days estimating midnight to occur at the time that is one half of the average night length (NLAVE) after the night starting time (NST) for the given day,"""
	#print suppressBadChars(txt)
	
	#error, individualClaims,claimsOrig=makeClaimAnalysis(claimsText, numbered=False,readable=True)
	#print error
	#,individualClaims,claimsOrig
	
	#claimsBase, allFillers, allSteps, claimsOrig = analyzeClaim(claimsText)
	#print allSteps
	#print claimsOrig
	#transformClaimFiles("inClaims", "individualClaims")
	
	#individualize("cloemseries/H97242087.claims.cloem.SymmetricCryptographicCalledTrans.3f635f8e602bcdb1bdf57bc6a27968cb","parse/dcf4bf107e5c6fd11e904a56c394299f/claims.indi")
	individualize("cloemseries/H2013-US-14030925.cloem.MedicamentPrescriptionManagement.653ec8cc80680255afc785c85a31eca4")

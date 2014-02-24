#Michael Laning and Daniel Langer
#CIS 391-final project

import time
import glob
import random
import email
import sys
import math
from collections import defaultdict
import string
import pickle

class Predictor:
    '''
    Predictor which will do prediction on emails
    '''
    def __init__(self, spamFolder, hamFolder):
        self.__createdAt = time.strftime("%d %b %H:%M:%S", time.gmtime())
        self.__spamFolder = spamFolder
        self.__hamFolder = hamFolder
        # do training on spam and ham
        self.classes = [spamFolder, hamFolder]
        self.spamwords=0
        self.hamwords=0
        self.dicts= self.__train__() #contains the trained spam/ham dictionaries
			
    def __train__(self):
        '''train model on spam and ham'''
        vocab = defaultdict(int)
        for c in self.classes:
        	vocab.update(file2countdict(glob.glob(c+"/*")))
        category = []
        
        for c in self.classes:
        	countdict = defaultdict(int, vocab)
        	countdict.update(file2countdict(glob.glob(c+"/*"))) 
        	
        	sumAll = sum(countdict.values())#total words in spam/ham
        	for k in countdict.keys():
        		# Do not find the distributions of sender,#emails,#caps in subject
      			if not k.startswith('XXX') and k!="EMAILTRACKER" and k != "SUBJECT_CAP":
        			countdict[k] = (float(countdict[k] +1))/(float(sumAll) + float(len(vocab)))
        	
        	category.append((c,countdict))
        return category 
        	
    def predict(self, filename):

      answers=[]
      
			#strip headers on email
      stripped = stripHeaders(filename)
      
      #stripped contains the body of the email, the sender address, and the subject string
      payload = stripped[0] 
      sender = stripped[1]
      subject = stripped[2] 
      
      # All capital words in Subject
      capCount = 0
      
      # Boolean for when Subject contains >1 capital words
      capital = False
      
      # Check if subject contains >1 capital words
      if subject:
      	for w in subject.split():
      		if w.isupper():
      			capCount += 1
      			if capCount > 1:
      				capital = True
      				break
      
      
      for c in self.dicts:
      	# Probability score of spam/ham
        score = 0
        
        # number of upper case words
        upper = 0
        
        #iterate over each word in the body of the email
        for w in payload.split():
          if w.isupper():
          	upper+=1 #count the all upper case words
          w = w.lower()
          if w in c[1]:
            score += math.log(c[1][w]) #update score with word probabilites
            
        #probability of sender's address
        if c[1]['XXX' + sender.upper()] != 0:
          score += math.log(float(c[1]['XXX' + sender.upper()])/c[1]["EMAILTRACKER"])
          
        #probability of upper case word
        #if upper!=0 and c[1]['UP']!=0:
          	#score += math.log(upper*float(c[1]['UP']))
          	
        #probability of capital subject
        if capital and c[1]['SUBJECT_CAP'] != 0:
          score += math.log(float(c[1]['SUBJECT_CAP'])/c[1]["EMAILTRACKER"])
          
        answers.append((score,c[0]))
        
      # classify the email based on the probability scores
      if answers[0][0] > answers[1][0]:
      	if self.__spamFolder == answers[0][1]:
      		return True
      	else:
      		return False
      else:
      	if self.__spamFolder == answers[1][1]:
      		return True
      	else:
      		return False
      		
def file2countdict(files):

	d=defaultdict(int)
	for file in files:
		stripped = stripHeaders(file)
		payload = stripped[0]
		sender = stripped[1]
		subject = stripped[2]
		
		capCount = 0
		if subject:
			for w in subject.split():
				if w.isupper():
					capCount += 1
					if capCount > 1:
						d["SUBJECT_CAP"] += 1

		d["XXX" + sender.upper()] += 1
		for word in payload.split():
			if word.isupper():
				d['UP'] +=1
			d[word.lower()] += 1
		d["EMAILTRACKER"]+=1
		
	return d


def stripHeaders(file):
	'''Strips header of the email
		Returns the body of the email, the sender's address and the subject string
	'''
	
	data=open(file).read().replace('\n', '')
	msg = email.message_from_string(data)
	
	#Get sender of email
	sender = (email.utils.parseaddr(email.parser.HeaderParser().parsestr(data)['From'])[1])
	sender = sender[(sender.rfind(".")+1):]
	
	#Gets subject of email
	subject = email.parser.HeaderParser().parsestr(data)['Subject']
  
  #get only the body of the email
	p = ""
	if msg.is_multipart():
		for payload in msg.get_payload():
			if payload.get_content_type() == "text/plain":
				p += str(payload.get_payload())
	else:
		p = str(msg.get_payload())
	
	return (p,sender,subject)	


  	
p = Predictor('hw6-spamham-data/spam','hw6-spamham-data/ham')

spm=0
hm=0
for file in glob.glob('hw6-spamham-data/dev/*'):
	x=p.predict(file)
	if x:
		spm+=1
	else:
		hm+=1
print 'hm' ,hm
print 'spm' ,spm

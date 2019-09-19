#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Diana Rocha Botello
"""
import matplotlib.pyplot as plt
import networkx as nx
import nltk
import os.path as path
import re
import spacy
import sys
from spacy.lang.es.examples import sentences

class Relaciones():
	def __init__(self, keyWords):
		self.nlp = spacy.load("es_core_news_md")
		self.keyWords = keyWords # Palabras claves
		self.selectedLines = [] # Los abstracts seleccionados de acuerdo con determinadas keyWords
		#(las|los|la|el|un|una|unos|unas|este|esta|estos|estas)*\s*\w+
		#self.regex = ["(las|los|la|el|un|una|unos|unas|este|esta|estos|estas)*\s*\w+\s*(forma parte de)\s(las|los|la|el|un|una|unos|unas|este|esta|estos|estas)*\s*\w+","(las|los|la|el|un|una|unos|unas|este|esta|estos|estas)*\s*\w+\s*(son|es)\s[las|los|la|el|un|una|unos|unas|este|esta|estos|estas]*\s*\w+","\w+\s(perteneciente(s)*)\s(a|al)\s([las|los|la|el|un|una|unos|unas|este|esta|estos|estas])*\s*\w+","\w+(,)\s(como:|tal como:|por ejemplo:|por ejemplo,|como por ejemplo)\s([las|los|la|el|un|una|unos|unas|este|esta|estos|estas]*\s*\w+(,\s)*)*"]
		self.regex = {'forma parte de':[".*\sforma parte de\s.*",1], 
					' forman parte de ':[".*\sforma parte de\s.*",1], 
					' es ':[".*\ses\s.*",1],
					' son ':[".*\sson\s.*",1],  
					' perteneciente ':[".*\sperteneciente\s.*",1],
					' pertenecientes ':[".*\spertenecientes\s.*",1], 
					' tal como: ':[".*\stal como:\s.*",2],
					' como ':[".*\scomo\s.*",2],
					' por ejemplo: ':[".*\spor ejemplo:\s.*",2],
					' por ejemplo, ':[".*\spor ejemplo,\s.*",2],
					' como por ejemplo ':[".*\scomo por ejemplo\s.*",2]}
		self.relacionesHiponimia = [] #Aristas
		self.elementos = [] #Nodos

	def cleanFile(self):
		file = 'wikipedia_es_abstracts.txt'
		newFile = open("wikipedia_abstracts_clean.txt",'w', encoding='utf8')
		with open(file, encoding='utf8') as f:
			for count, line in enumerate(f):
				if line.endswith('.\n'):	
					text = line.replace('\t', '. ')
					text = text.replace('Wikipedia:', '')
					newFile.write(text)				
			f.close()
		newFile.close()
	
	def getAbstracts(self):
		file = 'wikipedia_abstracts_clean.txt'
		with open(file, encoding='utf8') as f:
			for count, line in enumerate(f):
				findAllKeyWords = True
				i = 0
				while findAllKeyWords and i < len(self.keyWords):
					if not re.match("(.*)"+self.keyWords[i].lower()+"(.*)", line.lower()):
						findAllKeyWords = False
					i+=1
				if findAllKeyWords and line.endswith('.\n'):	
					text = line.replace('\t', '. ')				
					self.selectedLines.append(text)
			f.close()
		#print(self.selectedLines)

	def tokenizeSentence(self, parrafo):
		regex = re.compile(".*?\((.*?)\)")
		result = re.findall(regex, parrafo)
		for r in result:
			parrafo = parrafo.replace('('+r+')', '')
		es_tokenizador_oraciones = nltk.data.load('tokenizers/punkt/spanish.pickle')
		oraciones = es_tokenizador_oraciones.tokenize(parrafo)
		return oraciones

	def defineHomonimia(self,key,typeRe,RegexFoundList):
		for sentence in RegexFoundList:
			#print("--------------------------------")
			#print(sentence)
			sentence = sentence.lower()
			twoParts = sentence.split(key)
			if len(twoParts) == 2:
				doc = self.nlp(twoParts[0])
				chunkPart1 = [c for c in doc.noun_chunks]
				doc = self.nlp(twoParts[1])
				chunkPart2 = [c for c in doc.noun_chunks]
				if len(chunkPart1) > 0 and len(chunkPart2) > 0:
					if typeRe == 1:
						self.relacionesHiponimia.append((str(chunkPart2[0]),str(chunkPart1[0])))
					else:
						for noun in chunkPart2:
							self.relacionesHiponimia.append((str(chunkPart1[0]),str(noun)))
		#print(self.relacionesHiponimia)

	def getNodes(self):
		for r in self.relacionesHiponimia:
			if r[0] not in self.elementos:
				self.elementos.append(r[0])
			if r[1] not in self.elementos:
				self.elementos.append(r[1])
		print(self.elementos)

	def printGraph(self):
		G = nx.DiGraph()
		G.add_nodes_from(self.elementos)
		aristas = self.relacionesHiponimia
		G.add_edges_from(aristas)
		pos=nx.spring_layout(G)
		nx.draw_networkx_labels(G, pos, labels=dict([(i,i) for i in self.elementos]))
		nx.draw(G,pos)
		plt.show()

	def getRelacionesHiponimia(self):
		self.getAbstracts()
		for abstract in self.selectedLines:
			sentences = self.tokenizeSentence(abstract)
			for key,value in self.regex.items():
				#print(value[0])
				r = re.compile(value[0])
				RegexFoundList = list(filter(r.match, sentences))
				#print(RegexFoundList)
				self.defineHomonimia(key,value[1],RegexFoundList)
		self.getNodes()
		print(self.relacionesHiponimia)
		print("Número de elementos: "+str(len(self.elementos)))
		print("Número de relaciones-. "+str(len(self.relacionesHiponimia)))
		self.printGraph()

if __name__ == "__main__":
	if len(sys.argv) > 1: 
		sys.argv.pop(0)
		keyWords = []
		for keyword in sys.argv:
			keyWords.append(str(keyword))
		r= Relaciones(keyWords)
		if not path.exists("wikipedia_abstracts_clean.txt"):
			r.cleanFile()
		r.getRelacionesHiponimia()
	else:
		print("ERROR: Este script requiere de al menos 1 argumento para filtrar los documentos.")

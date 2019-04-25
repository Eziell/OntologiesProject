# -*- coding: utf-8 -*-

from Bio import Entrez, Medline
import contextManager as cm
import requests
import os

#   returns an array containing title, authors(array), abstract, ontologis, and date (url still needs to ne added)
def getPubmedArticles(disease, ammount=10):
    Entrez.email = "fc44949@alunos.fc.ul.pt"
    handle = Entrez.esearch(db="pubmed", term=disease, retmax=ammount)
    record = Entrez.read(handle)
    handle.close()
    idlist = record["IdList"]

    handle = Entrez.efetch(db="pubmed", id=idlist, rettype="medline", retmode="text")

    records = Medline.parse(handle)
    records = list(records)

    filteredRecords = dict()
    
    for record in records:
        title = record.get("TI")
        author = record.get("AU")
        abstract = record.get("AB")
        ontologies = record.get("OT")
        date = record.get("EDAT")
        pmid = record.get("PMID")
        url = "https://www.ncbi.nlm.nih.gov/pubmed/" + pmid

        filteredRecords[title] = [author, abstract, ontologies, url, date]
    
    return filteredRecords

#   returns a dictionary containing the doid as key, and associated disease as values
def runMER(text, lexicon='doid'):
    r = requests.get('http://labs.fc.ul.pt/mer/api.php?lexicon=%s&text=%s' % (lexicon, text))
    
    #key = disease name, index 0 = doid, index 1 = count
    diseases = dict()

    for line in r.text.splitlines():
        s = line.split('\t')
        disease = s[2]
        doid = s[3].split('/')[-1]
        
        if not diseases.get(disease):
            diseases[disease] = [doid, 1]
        else:
            count = diseases.get(disease)[1] + 1
            diseases[disease] = [doid, count]
    
    return diseases
    

# returns the resnik distance between two terms in the doid lexicon
def runDiShIn(arg1, arg2, lexicon = "doid", full=True):
	with cm.cd("DiShIn"):
		cmd = "python dishin.py %s.db %s %s" % (lexicon, arg1, arg2)
		
		dishin = os.popen(cmd).read()
		
		if full:
			return dishin
		else:
			list_temp = []
			list_temp = dishin.split('\n')

			resnik = list_temp[0].strip().split('\t')
			resnik = str(resnik[3])

			return resnik

		


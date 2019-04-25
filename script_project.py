import ontologiesProcedures as wp
import requests
import sys

annotations=open("5.txt","r")
header = True

geneDict = dict()
for line in annotations:
    if header == True:
        header = False
        continue
    
    gene, phenotype, geneId, phenotypeId = line.strip().split(",")
    geneDict[gene] = [phenotype, geneId, phenotypeId]

# genePaper - gene > papers > titulo, abstract
genePaper = dict()
for gene in geneDict.keys():
    print('Retrieving PubMed papers for: %s' % gene)
    # we only want the title and the abstract for each paper (key and index 1)
    paperBuffer = []
    for title, values in wp.getPubmedArticles(gene, 10).items():
        # function has a tendency not to retrieve abstracts.
        # append papers with title and abstracts until reaches 2.
        abstract = values[1]
        if abstract != None and title != None and len(paperBuffer) < 2:
            paperBuffer.append([title, abstract])

    genePaper[gene] = paperBuffer

genePaperMER = dict()
for key, values in genePaper.items():
    print('Calculating MER for: %s' % key)
    # next we're going calculate the MER for any given title + paper
    merValues = []

    for value in values:
        try:
            titleAbstract = " ".join(value)
            merValues.append(wp.runMER(titleAbstract, "hpo"))
        
        except:
            print("Exception raised for %s, stating: %s" % (key, sys.exc_info()[0]))
            print("Probably no abstract found for: %s." % value[0])
            print("Proceeding...")
    
    genePaperMER[key] = merValues

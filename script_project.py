import ontologiesProcedures as wp
import requests
import sys

annotations=open("test.txt","r")
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
	    mer = wp.runMER(titleAbstract.lower(), "hp")
            merValues.append(mer)
        except:
            print("Exception raised for %s, stating: %s" % (key, sys.exc_info()[0]))
            print("Output for %s may be incomplete." % key)
            print("Proceeding...")
     
    genePaperMER[key] = merValues


dictGeneTerms = {}
with open("relatorio.txt", "w") as f:
	output = ""
	for gene in geneDict.keys():
		geneTerms = []
		output += "Gene: %s\n" % gene
		for i in range(2):		
			title = genePaper.get(gene)[i][0]
			abstract = genePaper.get(gene)[i][1]
			output += "Title: %s\nAbstract: %s\n\n" % (title, abstract)
			output += "Term \t\t\t HPID \t\t\t Count\n"			
			for key, value in genePaperMER.items():
				for line in value:
					for term, idcount in line.items():					
						output += "%s \t\t\t %s \t\t\t %i\n" % (term, idcount[0], idcount[1])
						geneTerms.append(idcount[0])
						dictGeneTerms[geneDict[gene][2]] = geneTerms
	f.write(output)

print(dictGeneTerms)	
for key, value in dictGeneTerms.items():
	for term in value:
		print(key)
		print(term)
		print(wp.runDiShIn(str(key), str(term), "hp"))		
		





		

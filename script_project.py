import ontologiesProcedures as wp
import requests
import sys


annotations=open("3.txt","r")
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

with open("relatorio.txt", "w") as f:
	output = ""
	# opens geneDict dictionary which contains gene: phenotype, geneID, phenotypeID.
	for gene in geneDict.keys():
		output += "#"*40 + "\n"
		output += "Gene: %s\n\n" % gene
		# captures the 2 papers given for each entry in genePaper.
		for i in range(2):		
			title = genePaper.get(gene)[i][0]
			abstract = genePaper.get(gene)[i][1]
			output += "Title: %s\n\nAbstract: %s\n\n\n" % (title, abstract)
			# captures the corresponding paper in genePaperMER which stores for each gene an array with annotations for 2 papers
			# each entry in the array stores a dict containing annotation: ID, count	
			for term, idcount in genePaperMER.get(gene)[i].items():
					# to track progress
					print("Similarity: %s(%s)<> %s(%s)\n" % (geneDict[gene][2], geneDict[gene][0], idcount[0], term))
					output += "Similarity: %s(%s)<> %s(%s)\n" % (geneDict[gene][2], geneDict[gene][0], idcount[0], term)
					dishinRes = wp.runDiShIn(geneDict[gene][2], str(idcount[0]), "hp")
					output += dishinRes + "\n\n"	
	f.write(output)
	


		

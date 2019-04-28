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
    
    # while cicle will only stop if set of paper for gene has 2 entries.
    # if by the end of the cicle it doesn't it widdens the pubmed query to +10 publications
    fetch = 10
    while len(paperBuffer) < 2:
        print('Searching for %i terms' % fetch)
        
        for title, values in wp.getPubmedArticles(gene, fetch).items():
            # function has a tendency not to retrieve abstracts.
            # append papers with title and abstracts until reaches 2.
            abstract = values[1]
            if abstract != None and title != None and len(paperBuffer) < 2:
                # mer is run over the combination of the title and abstract
                titleAbstract = title + abstract
                mer = wp.runMER(titleAbstract.lower(), "hp")
                # only append mer set of title, abstract and mer values if annotated mer terms are >= 5
                if len(mer) >= fetch:
                    paperBuffer.append([title, abstract, mer])
        fetch -= 1

    genePaper[gene] = paperBuffer


papers = ""
with open("relatorio.txt", "w") as f:
    output = ""
    # opens geneDict dictionary which contains gene: phenotype, geneID, phenotypeID.
    for gene, phenotype in geneDict.items():
        papers += "Papers for: %s\n\n\n" % phenotype[0]

        output += "#"*40 + "\n"
        output += "Gene: %s\tPhenotype: %s\n\n" % (gene, phenotype[0])
        treshold1 = 0.75
        treshold2 = 0.5
        treshold3 = 0.25
        output += "HP_Code\tResnik DiShIn\tResnik MICA\tLin DiShIn\tLin MICA\tJC DiShIn\tJC MICA\tRelation in Text\tRelation by Lin/DiShIn > %i\tRelation by Lin/DiShIn > %f\tRelation by Lin/DiShIn > %f\tEvaluation\n" % (treshold1,treshold2,treshold3)
		# captures the 2 papers given for each entry in genePaper.
        for pub in genePaper.get(gene):
            title = pub[0]
            abstract = pub[1]
            merDict = pub[2]

            papers +="Title: %s\nAbstract: %s\n\n" % (title, abstract)
            # captures the corresponding paper in genePaperMER which stores for each gene an array with annotations for 2 papers
            # each entry in the array stores a dict containing annotation: ID, count
            for term, idcount in merDict.items():
                dishinRes = wp.runDiShIn(geneDict[gene][2], str(idcount[0]), "hp")
                # dishin may not retrieve anything so its a good idea to have a try except block
                try:
                    ResnikDishin, ResnikMica, LinDishin, LinMica, JcDishin, JcMica = dishinRes.splitlines()
                except:
                    print("Couldn't retrieve Dishin for %s. Proceeding..." % term)
                    continue
                ResnikDishin = float(ResnikDishin.split('\t')[-1])
                ResnikMica = float(ResnikMica.split('\t')[-1])
                LinDishin = float(LinDishin.split('\t')[-1])
                LinMica = float(LinMica.split('\t')[-1])
                JcDishin = float(JcDishin.split('\t')[-1])
                JcMica = float(JcMica.split('\t')[-1])
                # Checking for treshold 1
                dishinEval1 = False
                if LinDishin >= treshold1:
                    dishinEval1 = True
                # Checking for treshold 2
                dishinEval2 = False
                if LinDishin >= treshold2:
                    dishinEval2 = True
                # Checking for treshold 3
                dishinEval3 = False
                if LinDishin >= treshold3:
                    dishinEval3 = True
                
                # Converting bool to str
                dishinEval1 = str(dishinEval1)
                dishinEval2 = str(dishinEval2)
                dishinEval3 = str(dishinEval3)
                output += "%s\t%f\t%f\t%f\t%f\t%f\t%f\t\t%s\t%s\t%s\t\t\n" % (term, ResnikDishin,ResnikMica,LinDishin,LinMica,JcDishin,JcMica,dishinEval1,dishinEval2,dishinEval3)
    f.write(output)

with open("papers.txt", "w") as f:
    f.write(papers)
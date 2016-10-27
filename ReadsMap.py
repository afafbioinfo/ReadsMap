#@author SAAIDI afaf 2016
#This program maps single end reads to reference genome using TMAP.
#The version required a version of TMAP  is 3.0
#The samtools program should be installed, the version for samtools tested is 0.1.19
#!/usr/bin/env python2.7.0
from ConfigParser import SafeConfigParser
import Functions as Fct
import os

#to run the program from the current working directory as
os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':
	#Connect to the configuration file
	config= SafeConfigParser()
	config.read("MapReads.Config")
	#Get the ensemble of folders path
	FastaFiles=config.get("Paths","PathFastaFiles")
	FastqFiles = config.get("Paths", "PathFastqFiles")
	SamFolder= config.get("Paths","PathSamFiles")
	BamFolder = config.get("Paths", "PathBamFiles")
	Alignedreads = config.get("Paths","Alignedreads")
	FastaFileExtension= config.get("Parameters", "FastaFileExtension")
	GlobalFastaFile= config.get("Parameters", "GlobalFastaFile")
	sudo_password=config.get("Parameters", "sudo_password")
	Quality=int(config.get("Parameters", "QualityalignThresh"))
	Analysis=(config.get("Parameters", "Generates_reads_analysis")).lower()

    #Create one fasta reference file
	Fct.ConcatenateFiles(FastaFiles, FastaFileExtension,GlobalFastaFile)
	#TMAP preprocessing, Index the refernce file using TMAP
	Fct.TMAPIndexSeq(GlobalFastaFile)
	#Extract the list of rnas identifiers
	listRnas=Fct.GetListFile(FastaFiles, FastaFileExtension)
	# Mapping reads
	Fct. TMAPmapping(FastqFiles,GlobalFastaFile, SamFolder,BamFolder,Alignedreads,sudo_password,Quality,listRnas)

	if Analysis=="true":
		Fct.ReadsAnalysis(BamFolder)
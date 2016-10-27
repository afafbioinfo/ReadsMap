import os, subprocess, time
from os.path import isfile, join


# Function gets the list of files with the extension FileExtension, in the specific folder PathFile
def GetListFile(PathFile, FileExtension):
    return [os.path.splitext(f)[0] for f in os.listdir(PathFile) if
            isfile(join(PathFile, f)) and os.path.splitext(f)[1] == '.' + FileExtension]


# Function creates a folder if does not exist
def CreateFold(Folders):
    for Folder in Folders:
        try:
            os.stat(Folder)
        except:
            os.mkdir(Folder)

def ConcatenateFiles(PathFile, FileExtension, Fileout):
    sort_out = open(Fileout, 'wb', 0)
    sort_in = PathFile + '/*.' + FileExtension
    subprocess.Popen("cat " + sort_in, stdin=subprocess.PIPE, stdout=sort_out, shell=True)

def TMAPIndexSeq(Referencesequence):
    subprocess.Popen('tmap index -f' + Referencesequence, shell=True).wait()
    print "Indexing reference sequence(s) done with success"


def CheckFastqfile(f):
    res = True
    if os.path.splitext(f)[1] != '.fastq':
        print "You are providing a non fastq extension file"
        res = False
    return res


def TMAPmapping(FastqFiles, Referencesequence, SamFolder, BamFolder,Alignedreads, sudo_password,Quality,listRnas):
    startime = time.time()
    CreateFold([SamFolder,BamFolder,Alignedreads])
    for Fastqfile in os.listdir(FastqFiles):
        # print  CheckFastqfile(Fastqfile)
        if CheckFastqfile(Fastqfile):
            filename = os.path.splitext(Fastqfile)[0]
            fastqfile=FastqFiles + "/" + Fastqfile
            samfile= SamFolder + "/" +filename+ ".sam"
            bamfile = BamFolder + "/" + filename + ".bam"

            command = " tmap mapall -n 24 -f  " + Referencesequence + " -r " + fastqfile + " -v -Y -u -a 3 -s " +samfile  + " -o O stage1 map4"
            p=subprocess.Popen( command, shell=True)
            # This command required the sudo approval through communicating the password
            p.communicate(sudo_password + '\n')[1]
            print "The mapping for", filename, "is achieved with success"
            # convert Sam file to Bam and  sort it
            CommandconvertSamBam='samtools view -bS '
            #print CommandconvertSamBam
            subprocess.call(CommandconvertSamBam +samfile,stdin=open(samfile ,'r'), stdout=open(bamfile ,'wb'),shell=True)

            print filename+":conversion to Bam  done with success"

            # sort Bam files
            sbamfile = BamFolder + "/" + filename + ".sort"
            CommandsortBam="samtools sort "
            subprocess.call(CommandsortBam+" " +bamfile+" " + sbamfile,stdin=open(bamfile,'r'), stdout=open(sbamfile,'wb'), shell=True)
            print "Sorting BAM file done"

            CommandindexBam="samtools index "+BamFolder + "/" + filename + ".sort.bam"
            print CommandindexBam
            subprocess.call(CommandindexBam, shell=True)

            ParseBamFile(BamFolder, Alignedreads,filename, Quality,listRnas)
            endtime = time.time()
            print (" %s  mapping done in %53f \t"% (filename, endtime - startime))

def ParseBamFile(BamFolder, Alignedreads,filename, QualityThresh,listRnas):
    # Extracting fields of interest from the indexed and sorted Bam file, with removing unmapped reads and fixing quality to 30

    Qualin=BamFolder + "/" +filename+'.sort.bam'
    commandfilterquality = "samtools view -F 0x04  -q " + str(QualityThresh)+" "+Qualin
    print ("p1 running")
    p1 = subprocess.Popen(commandfilterquality, stdin=open(Qualin,'r'),stdout=subprocess.PIPE, shell=True)
    #Pipe the result to p2 process
    print ("p2 runnig")
    p2 = subprocess.Popen(r'''awk '{print $3 "\t" $4 "\t" $5 "\t"$6 "\t"$10 "\t"$11 "\t" }' ''', stdin=p1.stdout,stdout= subprocess.PIPE, shell=True)
    for Rna in listRnas:
        p3 =subprocess.Popen("grep -i "+ Rna , stdin=p2.stdout,stdout=open(Alignedreads+"/"+Rna+'.'+filename + ".txt", 'w'), shell=True)

def ReadsAnalysis(BamFolder):
    for filee in os.listdir(BamFolder):
        if os.path.splitext(filee)[-1]==".bam":
            file=BamFolder+"/"+filee
            subprocess.call("echo " +file +"&&"+" samtools flagstat "+file +"&&"+ '''echo "In more details"'''+"&&"+ "samtools idxstats "+file , stdin=open(file,'r'), stdout= open("ReadsAnalysis.txt", 'a'), shell=True)

#User defined input. Spceify here the parameters used to run TFEA including full paths to all the necessary input files
#======================================================================================================================#
#Input bed file containing regions of interest to perform TFEA. This file is required to run TFEA. Ideally a list of eRNAs called by Tfit.
BED='/full/path/to/bed/file.bed'

#Input bam files as a list containing transcription data. Must specify at least two bam files. If multiple replicates, specify each as a full path in the appropriate list.
BAM1 = ['/full/path/to/bam1/rep1.bam','/full/path/to/bam1/rep2.bam','...']
BAM2 = ['/full/path/to/bam2/rep1.bam','/full/path/to/bam2/rep2.bam','...']

#Specify conditions for bam files
LABEL1 = 'Condition1'
LABEL2 = 'Condition2'

#Specify whether you want to run a single motif or a database. By default, TFEA runs on the latest version of HOCMOCO obtained through MEME.
#Default:False. Change to a motif name if you want to run TFEA on a single motif (make sure your single motif is in the specified database).
SINGLEMOTIF='P53_f2'
DATABASE='HOCOMOCOv9.meme'

#Specify full path to genome fasta file
GENOME = '/Users/joru1876/scratch_backup/hg19_reference_files/hg19_all.fa'

#Specify full path to MEME directory with motif databases. Make sure you have updated the motif databases in MEME using the following command (where MEMEDB is the full path to where MEME databases are located):
#update-sequence-db MEMEDB
MEMEDB = '/opt/meme/4.10.1_4/db/motif_databases/HUMAN/'

#Optional: If choosing deseqfile() option for ranking, provide deseq res.txt output file
DESEQFILE = '/Users/joru1876/scratch_backup/TFEA_grant_figure/Tfit_all_bidir_predictions.sorted.merge.count.bed.id.bed.DMSONutlinnascent.res.txt'
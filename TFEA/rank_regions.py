__author__ = 'Jonathan Rubin'

import math
import os
from config import FILEDIR,DESEQ_FILE

def deseqfile():
    #Parse a deseq file and obtain the exact middle of each region (for motif distance calc later) and pvalue (to rank)
    up = list()
    down = list()
    with open(DESEQ_FILE) as F:
        header = F.readline().strip('\n').split('\t')
        fc_index = [i for i in range(len(header)) if header[i] == '"fc"' or header[i] == '"foldChange"'][0]
        for line in F:
            line = line.strip('\n').split('\t')
            if line[fc_index] != 'NA':
                try:
                    pval = format(float(line[-2]),'.12f')
                except ValueError:
                    pval = format(1.0,'.12f')
                region = line[0].split(':')
                chrom = region[0]
                coordinates = region[1].split('-')
                start = coordinates[0]
                stop = coordinates[1]
                chrom = chrom.strip('"')
                stop = stop.strip('"')
                fc = float(line[fc_index])
                if fc < 1:
                    down.append((chrom,start,stop,pval,str(fc)))
                else:
                    up.append((chrom,start,stop,pval,str(fc)))

    #Save ranked regions in a bed file (pvalue included)
    outfile = open(FILEDIR + "ranked_file.bed",'w')
    r=1
    for region in sorted(up, key=lambda x: x[3]):
        outfile.write('\t'.join(region) + '\t' + str(r) + '\n')
        r += 1
    for region in sorted(down, key=lambda x: x[3], reverse=True):
        outfile.write('\t'.join(region) + '\t' + str(r) + '\n')
        r += 1
    outfile.close()

    #Get center base for each region
    outfile = open(FILEDIR+"ranked_file.center.bed",'w')
    with open(FILEDIR + "ranked_file.bed") as F:
        for line in F:
            line = line.strip('\n').split('\t')
            chrom,start,stop = line[:3]
            center = (int(start)+int(stop))/2
            outfile.write(chrom + '\t' + str(center) + '\t' + str(center+1) + '\t' + '\t'.join(line[3:]) + '\n')
    outfile.close()


    os.system("sort -k1,1 -k2,2n " + FILEDIR+"ranked_file.center.bed" + " > " + FILEDIR + "ranked_file.center.sorted.bed")
    # os.system("rm " + filedir + "combined_input.bed")
    # os.system("rm " + filedir + "combined_input.merge.bed")
    # os.system("rm " + filedir + "combined_input.sorted.bed")
    # #os.system("rm " + filedir + "count_file.bed")
    # os.system("rm " + filedir + "count_file.header.bed")
    # os.system("rm " + filedir + "ranked_file.bed")
    # os.system("rm " + filedir + "ranked_file.center.bed")




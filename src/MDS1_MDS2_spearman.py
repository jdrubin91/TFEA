__autor__ = 'Rutendo F. Sigauke'

import os
import numpy as np
import pandas as pd 
import scipy
from scipy import stats

def parent_dir(directory):
    pathlist = directory.split('/')
    newdir = '/'.join(pathlist[0:len(pathlist)-1])

    return newdir

##def sortTFEA(tfea_res):
def sortMDS1_MDS2(mds_res1, mds_res2, outfile, name):
    """
    take a tsv files for mds scores, sort by the pvalues and 
    use the rank of the both to calculate the spearman correlation.

    """
    with open(mds_res1) as mds1:

        tf1 = list()
        Y1 = list()
        pvals1 = list()
        tf_motif1 =list()

        for line1 in mds1:
            line1 = line1.strip('\n')
            tf1.append(line1.split('\t')[1])
            Y1.append(line1.split('\t')[3])
            pvals1.append(line1.split('\t')[4])
            tf_motif1.append(line1.split('\t')[5])

        MDSsum1 = zip(tf1, Y1, pvals1, tf_motif1)
        MDSsummary1 = pd.DataFrame(MDSsum1,columns=['TF','Y','pval', 'TF_motif'])
        MDSsummary21 = MDSsummary1.drop(MDSsummary1.index[:1])
        MDSsummary21['pvals'] =MDSsummary21['pval'].astype('float')

        ##split the NES into positive and negative values                                                                                                                                    ##now sort the two df by the pvalues                                                                                                                                          
        positive1 = MDSsummary21[(MDSsummary21['Y'].astype(float) >= 0.0)]
        negative1 = MDSsummary21[MDSsummary21['Y'].astype(float) < 0.0]
        positive_sort1 = positive1.sort_values(by=['pvals'])
        negative_sort1 = negative1.sort_values(by=['pvals'],ascending=False)

        dframes1 = [positive_sort1, negative_sort1]
        

        sorted_pval_mds1 = pd.concat(dframes1)
    

        sorted_pval_mds1.insert(0, 'Rank1', range(1, 1 + len(sorted_pval_mds1)))

        
    with open(mds_res2) as mds2:
        tf = list()
        Y = list()
        pvals = list()
        tf_motif =list()

        for line in mds2:
            line = line.strip('\n')
            tf.append(line.split('\t')[1])
            Y.append(line.split('\t')[3])
            pvals.append(line.split('\t')[4])
            tf_motif.append(line.split('\t')[5])

        MDSsum = zip(tf, Y, pvals, tf_motif)
        MDSsummary = pd.DataFrame(MDSsum,columns=['TF','Y','pval', 'TF_motif'])
        MDSsummary2 = MDSsummary.drop(MDSsummary.index[:1])
        MDSsummary2['pvals'] =MDSsummary2['pval'].astype('float')

    ##split the NES into positive and negative values                                                                                                                             
    ##now sort the two df by the pvalues                                                                                                                                          
        positive = MDSsummary2[(MDSsummary2['Y'].astype(float) >= 0.0)]
        negative = MDSsummary2[MDSsummary2['Y'].astype(float) < 0.0]
        positive_sort = positive.sort_values(by=['pvals'])
        negative_sort = negative.sort_values(by=['pvals'],ascending=False)
        
        dframes = [positive_sort, negative_sort]
        

        sorted_pval_mds2 = pd.concat(dframes)
        sorted_pval_mds2.insert(0, 'Rank2', range(1, 1 + len(sorted_pval_mds2)))
        

        df = pd.merge(sorted_pval_mds1, sorted_pval_mds2, on='TF_motif',how='inner')
        print df

        df.to_csv(outfile + name +'_MDS_Replicate_Ranks.tsv', sep='\t')

        spearman_corr = scipy.stats.spearmanr(df["Rank1"].values, df["Rank2"].values)
        ##spearman_corr = scipy.stats.pearsonr(df["Rank1"].values, df["Rank2"].values) 
        
        print spearman_corr


if __name__ == "__main__":
    
    # mds_res1 = '/scratch/Users/rusi2317/projects/rotation/output/MDS_compare/SRR1105739SRR1105737_MDSout.tsv'
    # mds_res2 = '/scratch/Users/rusi2317/projects/rotation/output/MDS_compare/SRR1105738SRR1105736_MDSout.tsv'
    mds_res1 = '/scratch/Users/rusi2317/projects/rotation/output/MDS_compare/SRR1015587SRR1015583_MDSout.tsv'
    mds_res2 = '/scratch/Users/rusi2317/projects/rotation/output/MDS_compare/SRR1015588SRR1015584_MDSout.tsv'
    outfile ='/scratch/Users/rusi2317/projects/rotation/output/spearman_ranks/'
    # name = 'Allen2014'
    name = 'Luo2014'
    sortMDS1_MDS2(mds_res1, mds_res2, outfile, name)



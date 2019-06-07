#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''This module calculates enrichment statistics for TF motifs across inputted
    regions of interest. This module takes as input the output of the SCANNER
    module. It outputs a list of lists with enrichment statistics including
    a p-value.
'''

#==============================================================================
__author__ = 'Jonathan D. Rubin and Rutendo F. Sigauke'
__credits__ = ['Jonathan D. Rubin', 'Rutendo F. Sigauke', 'Jacob T. Stanley',
                'Robin D. Dowell']
__maintainer__ = 'Jonathan D. Rubin'
__email__ = 'Jonathan.Rubin@colorado.edu'

#Imports
#==============================================================================
import os
import sys
import math
import time
import datetime
import traceback
import numpy as np
import math
from scipy.stats import norm
from scipy.stats import anderson_ksamp

from TFEA import config
from TFEA import multiprocess
from TFEA import plot

#Main Script
#==============================================================================
def main(use_config=True, motif_distances=None, md_distances1=None, 
            md_distances2=None, mdd_distances1=None, mdd_distances2=None, 
            enrichment=None, output_type=None, permutations=None, debug=None, 
            largewindow=None, smallwindow=None, md=None, mdd=None, cpus=None, 
            jobid=None, pvals=None, fcs=None, p_cutoff=None, figuredir=None, 
            plotall=False, fimo_motifs=None, meta_profile_dict=None, 
            label1=None, label2=None, dpi=None, motif_fpkm={}):
    '''This is the main script of the ENRICHMENT module. It takes as input
        a list of distances outputted from the SCANNER module and calculates
        an enrichment score, a p-value, and in some instances an adjusted 
        p-value for each motif.
    
    Parameters
    ----------
    use_config : boolean
        Whether to use a config module to assign variables.
    motif_distances : list of lists
        A list containing a list for each motif scanned. For each motif, the 
        list begins with the motif name as a string and is followed by int
        values corresponding to the motif distance for each region (ranked). A
        '.' value means the motif was not within the given region
    md_distances1 : list of lists
        A list containing a list for each motif scanned. For each motif, the 
        list begins with the motif name as a string and is followed by int
        values corresponding to the motif distance for each region (ranked). A
        '.' value means the motif was not within the given region
    md_distances2 : list of lists
        A list containing a list for each motif scanned. For each motif, the 
        list begins with the motif name as a string and is followed by int
        values corresponding to the motif distance for each region (ranked). A
        '.' value means the motif was not within the given region
    enrichment : str
        The type of enrichment analysis to perform
    output_type : str
        Determines what some functions will output. At this point, this is mostly
        intended for debug purposes.
    permutations : int
        Number of random shuffling permutations to perform to calculate a 
        p-value
    debug : boolean
        Whether to print debug statements specifically within the multiprocess
        module
    largewindow : int
        A distance cutoff value used within auc_bgcorrect
    smallwindow : int
        A distance cutoff value used within the md score analysis
    
    Returns
    -------
    results : list of lists
        A list of lists corresponding to enrichment statistics for each motif
    md_results : list of lists
        A list of lists corresponding to md-score statistics for each motif
    '''
    start_time = time.time()
    if use_config:
        motif_distances = config.vars['MOTIF_DISTANCES']
        md_distances1 = config.vars['MD_DISTANCES1']
        md_distances2 = config.vars['MD_DISTANCES2']
        mdd_distances1 = config.vars['MDD_DISTANCES1']
        mdd_distances2 = config.vars['MDD_DISTANCES2']
        enrichment = config.vars['ENRICHMENT']
        permutations = config.vars['PERMUTATIONS']
        debug = config.vars['DEBUG']
        largewindow = config.vars['LARGEWINDOW']
        smallwindow = config.vars['SMALLWINDOW']
        pvals = config.vars['PVALS']
        fcs = config.vars['FCS']
        md = config.vars['MD']
        mdd = config.vars['MDD']
        cpus = config.vars['CPUS']
        jobid = config.vars['JOBID']
        p_cutoff = config.vars['PADJCUTOFF']
        figuredir = config.vars['FIGUREDIR']
        plotall = config.vars['PLOTALL']
        fimo_motifs = config.vars['FIMO_MOTIFS']
        meta_profile_dict = config.vars['META_PROFILE']
        label1 = config.vars['LABEL1']
        label2 = config.vars['LABEL2']
        dpi = config.vars['DPI']
        output_type = config.vars['OUTPUT_TYPE']
        try:
            motif_fpkm = config.vars['MOTIF_FPKM']
        except:
            motif_fpkm = {}

    print("Calculating enrichment...", flush=True, file=sys.stderr)

    results = None
    md_results = None
    mdd_results = None

    if enrichment == 'auc':
        print('\tTFEA:', file=sys.stderr)
        auc_keywords = dict(permutations=permutations, use_config=use_config, 
                        output_type=output_type, pvals=pvals, plotall=plotall, 
                        p_cutoff=p_cutoff, figuredir=figuredir, 
                        largewindow=largewindow, fimo_motifs=fimo_motifs, 
                        meta_profile_dict=meta_profile_dict, label1=label1, 
                        label2=label2, dpi=dpi, fcs=fcs, motif_fpkm=motif_fpkm, 
                        tests=len(motif_distances))
        results = multiprocess.main(function=area_under_curve, 
                                    args=motif_distances, kwargs=auc_keywords,
                                    debug=debug, jobid=jobid, cpus=cpus)
        # results = list()
        # for motif_distance in motif_distances:
        #     results.append(area_under_curve(motif_distance, **auc_keywords))
        # padj_bonferroni(results)
    elif enrichment == 'anderson-darling':
        results = multiprocess.main(function=anderson_darling, 
                                        args=motif_distances, debug=debug, 
                                        jobid=jobid, cpus=cpus)

    elif enrichment == 'auc_bgcorrect':
        print('\tTFEA:', file=sys.stderr)
        auc_bgcorrect_keywords = dict(permutations=permutations)
        results = multiprocess.main(function=area_under_curve_bgcorrect, 
                                    args=motif_distances, 
                                    kwargs=auc_bgcorrect_keywords,
                                    debug=debug, jobid=jobid, cpus=cpus)

        padj_bonferroni(results)

    if md:
        print('\tMD:', file=sys.stderr)
        md_results = calculate_md(md_distances1=md_distances1, 
                                    md_distances2=md_distances2, 
                                    smallwindow=smallwindow, 
                                    jobid=jobid, cpus=cpus, debug=debug)
        if use_config:
            config.vars['MD_RESULTS'] = md_results
    if mdd:
        print('\tMDD:', file=sys.stderr)
        mdd_results =  calculate_md(md_distances1=mdd_distances1, 
                                        md_distances2=mdd_distances2, 
                                        smallwindow=smallwindow,
                                        jobid=jobid, cpus=cpus, debug=debug)
        if use_config:
            config.vars['MDD_RESULTS'] = mdd_results

    if use_config:
        config.vars['RESULTS'] = results

    total_time = time.time() - start_time
    if use_config:
        config.vars['ENRICHMENTtime'] = total_time
    print("done in: " + str(datetime.timedelta(seconds=int(total_time))), file=sys.stderr)

    if debug:
        multiprocess.current_mem_usage(jobid)

    return results, md_results, mdd_results

#==============================================================================
def calculate_md(md_distances1=None, md_distances2=None, smallwindow=None, 
                    jobid=None, cpus=None, debug=None):
    md_keywords = dict(smallwindow=smallwindow)
    md_results = multiprocess.main(function=md_score, 
                    args=list(zip(sorted(md_distances1),sorted(md_distances2))), 
                    kwargs=md_keywords,
                    debug=debug, jobid=jobid, cpus=cpus)

    md_results = md_score_p(md_results)

    return md_results

#Functions
#==============================================================================
def area_under_curve(distances, use_config=True, output_type=None, 
                        permutations=None, pvals=None,
                        plotall=None, p_cutoff=None, figuredir=None, 
                        largewindow=None, fimo_motifs=None, 
                        meta_profile_dict=None, label1=None, label2=None, 
                        dpi=None, fcs=None, tests=None, motif_fpkm=None):
    '''Calculates an enrichment score using the area under the curve. This
        method is not as sensitive to artifacts as other methods. It works well
        as an asymmetry detector and will be good at picking up cases where
        most of the motif localization changes happen at the most differentially
        transcribed regions.
    '''
    try:
        #sort distances based on the ranks from TF bed file
        #and calculate the absolute distance
        motif = distances[0]
        try:
            fpkm = motif_fpkm[motif]
        except KeyError:
            fpkm = 0
        distances = distances[1:]
        distances_abs = [abs(x)  if x != '.' else x for x in distances]

        hits = len([x for x in distances_abs if x != '.'])

        #Filter any TFs/files without any hits
        if hits == 0:
            return [motif, 0.0, 0, fpkm, 1.0]

        #Get -exp() of distance and get cumulative scores
        #Filter distances into quartiles to get middle distribution
        q1 = int(round(len(distances)*.25))
        q3 = int(round(len(distances)*.75))
        middledistancehist =  [x for x in distances_abs[int(q1):int(q3)] if x != '.']
        try:
            average_distance = float(sum(middledistancehist))/float(len(middledistancehist))
        except ZeroDivisionError:
            return [motif, 0.0, 0, fpkm, 1.0]
        
        score = [math.exp(-float(x)/average_distance) if x != '.' else 0.0 for x in distances_abs]
        total = sum(score)
        if output_type == 'score':
            return score

        binwidth = 1.0/float(len(distances_abs))
        normalized_score = [(float(x)/total)*binwidth for x in score]
        cumscore = np.cumsum(normalized_score)
        trend = np.append(np.arange(0,1,1.0/float(len(cumscore)))[1:], 1.0)
        trend = [x*binwidth for x in trend]

        #The AUC is the relative to the "random" line
        auc = np.trapz(cumscore) - np.trapz(trend)

        #Calculate random AUC
        sim_auc = permute_auc(distances=normalized_score, trend=trend, 
                                permutations=permutations)

        #Calculate p-value                                                                                                                                                          
        mu = np.mean(sim_auc)
        sigma = np.std(sim_auc)
        p = min(norm.cdf(auc,mu,sigma), 1-norm.cdf(auc,mu,sigma))
        if math.isnan(p):
            p = 1.0
        
        p = p*tests if p*tests <=1 else 1

        if output_type=='html' or plotall or p < p_cutoff:
            from TFEA import plot
            plotting_score = [(float(x)/total) for x in score]
            plotting_cumscore = np.cumsum(plotting_score)
            plot.plot_individual_graphs(motif=motif, distances=distances, 
                                        figuredir=figuredir, 
                                        fimo_motifs=fimo_motifs, 
                                        largewindow=largewindow, 
                                        score=plotting_score, 
                                        use_config=use_config, dpi=dpi, 
                                        pvals=pvals, fcs=fcs, 
                                        cumscore=plotting_cumscore, 
                                        sim_auc=sim_auc, auc=auc,
                                        meta_profile_dict=meta_profile_dict, 
                                        label1=label1, label2=label2)
    except Exception as e:
        # This prints the type, value, and stack trace of the
        # current exception being handled.
        print(traceback.print_exc())
        raise e
    return [motif, auc, hits, fpkm, p]

#==============================================================================
def area_under_curve_bgcorrect(distances, use_config=False, output_type=None, 
                        permutations=None, pvals=None,
                        plotall=None, p_cutoff=None, figuredir=None, 
                        largewindow=None, fimo_motifs=None, 
                        meta_profile_dict=None, label1=None, label2=None, 
                        dpi=None, fcs=None):
    try:
        #sort distances based on the ranks from TF bed file
        #and calculate the absolute distance
        motif = distances[0]
        distances = distances[1:]
        distances_abs = [abs(x)  if x != '.' else x for x in distances]

        hits = len([x for x in distances_abs if x != '.'])

        #Filter any TFs/files without any hits
        if hits == 0:
            return [motif, 0.0, 0, 1.0]

        #Get -exp() of distance and get cumulative scores
        #Filter distances into quartiles to get middle distribution
        q1 = int(round(len(distances)*.25))
        q3 = int(round(len(distances)*.75))
        middledistancehist =  [x for x in distances_abs[int(q1):int(q3)] if x != '.']
        try:
            average_distance = float(sum(middledistancehist))/float(len(middledistancehist))
        except ZeroDivisionError:
            return [motif, 0.0, 0, 1.0]
        
        score = [math.exp(-float(x)/average_distance) if x != '.' else 0.0 for x in distances_abs]
        total = sum(score)
        if output_type == 'score':
            return score

        #Normalize x-axis to be from 0 to 1
        binwidth = 1.0/float(len(distances_abs))
        normalized_score = [(float(x)/total)*binwidth for x in score]
        cumscore = np.cumsum(normalized_score)
        trend = np.append(np.arange(0,1,1.0/float(len(cumscore)))[1:], 1.0)
        trend = [x*binwidth for x in trend]

        #Calculate the backgroupnd AUC
        bg_cumscore = np.cumsum(normalized_score[q1:q3])
        bg_trend = np.append(np.arange(0,1,1.0/float(len(bg_cumscore)))[1:], 1.0)
        bg_trend = [x*binwidth for x in bg_trend]
        bg_auc = np.trapz(bg_cumscore) - np.trapz(bg_trend)


        #The AUC is the relative to the "random" line
        auc = np.trapz(cumscore) - np.trapz(trend)

        #Subtract background auc
        auc = auc - bg_auc

        #Calculate random AUC
        sim_auc = permute_auc(distances=normalized_score, trend=trend, 
                                permutations=permutations)

        #Calculate p-value                                                                                                                                                          
        mu = np.mean(sim_auc)
        sigma = np.std(sim_auc)
        p = min(norm.cdf(auc,mu,sigma), 1-norm.cdf(auc,mu,sigma))
        if math.isnan(p):
            p = 1.0

        if output_type == 'html' or plotall:
            #make individual plots and also individual html file
            from TFEA import plot
            plotting_score = [(float(x)/total) for x in score]
            plotting_cumscore = np.cumsum(plotting_score)
            plot.plot_individual_graphs(distances=distances, figuredir=figuredir, 
                            fimo_motifs=fimo_motifs, largewindow=largewindow, 
                            score=plotting_score, use_config=use_config,
                            dpi=dpi, pvals=pvals, fcs=fcs, 
                            cumscore=plotting_cumscore, sim_auc=sim_auc, auc=auc,
                            meta_profile_dict=meta_profile_dict, label1=label1, 
                            label2=label2)
            
        
        if output_type == 'lineplot_output':
            plotting_score = [0] + [(float(x)/total) for x in score]
            plotting_cumscore = np.cumsum(plotting_score)
            return plotting_cumscore
        
        if output_type == 'simulation_output':
            return auc, sim_auc
    except Exception as e:
        # This prints the type, value, and stack trace of the
        # current exception being handled.
        print(traceback.print_exc())
        raise e
    return [motif, auc, hits, p]

#==============================================================================
def max_GSEA(distances, use_config=False, output_type=None, cutoff=None,
                        permutations=None, pvals=None,
                        plotall=None, p_cutoff=None, figuredir=None, 
                        largewindow=None, fimo_motifs=None, 
                        meta_profile_dict=None, label1=None, label2=None, 
                        dpi=None, fcs=None):
    '''Takes the max of the enrichment curve. This method is good at detecting
        significant motif instances in a row. It is susceptible to instances
        where a motif appears generally throughout all regions.
    '''
    motif = distances[0]
    distances = [x if x != '.' else cutoff+1 for x in distances[1:]]
    hits = [1 if abs(x) < cutoff else -1 for x in distances]
    pos_total = float(sum([1 for x in hits if x != -1]))
    neg_total = float(sum([1 for x in hits if x == -1]))

    Eval = 0
    ES = list()
    for distance in hits:
        if distance == -1:
            Eval += -1.0/neg_total
            ES.append(Eval)
        else:
            Eval += 1.0/pos_total
            ES.append(Eval)
    
    actualES = max(ES, key=abs)

    #To get NES, first simulate 1000 permuations of region ranks
    simES = permute_max_GSEA(hits=hits, permutations=1000)

    #NES is the actualES divided by the mean ES of all permutations with the 
    # same sign as actualES p-value is caluclated empirically 
    # (i.e. (# of simulated ES scores larger than actualES)/(rest of simulated ES scores))
    if actualES < 0:
        simESsubset = [x for x in simES if x < 0]
        mu = np.mean(simESsubset)
        NES = -(actualES/mu)
        sigma = np.std(simESsubset)
        p = norm.cdf(actualES, mu, sigma)
    else:
        simESsubset = [x for x in simES if x > 0]
        mu = np.mean(simESsubset)
        NES = actualES/mu
        sigma = np.std(simESsubset)
        p = 1-norm.cdf(actualES, mu, sigma)

    if math.isnan(p):
        p = 1.0

    # if output_type == 'html':
    #     from TFEA import plot
    #     plotting_score = [(float(x)/total) for x in score]
    #     plotting_cumscore = np.cumsum(plotting_score)
    #     plot.plot_individual_graphs(distances=distances, figuredir=figuredir, 
    #                     fimo_motifs=fimo_motifs, largewindow=largewindow, 
    #                     score=plotting_score, use_config=use_config,
    #                     dpi=dpi, pvals=pvals, fcs=fcs, 
    #                     cumscore=plotting_cumscore, sim_auc=sim_auc, auc=auc,
    #                     meta_profile_dict=meta_profile_dict, label1=label1, 
    #                     label2=label2)
    
    if output_type == 'lineplot_output':
        return ES
    
    if output_type == 'simulation_output':
        return actualES, simES

    return [motif, actualES, NES, pos_total, p]

#==============================================================================
def permute_auc(distances=None, trend=None, permutations=None):
    '''Generates permutations of the distances and calculates AUC for each 
        permutation.

    Parameters
    ----------
    distances : list or array
        normalized distances 
        
    permutations : int
        number of times to permute (default=1000)
        
    Returns
    -------
    es_permute : list 
        list of AUC calculated for permutations 
       
    '''
    es_permute = []
    triangle_area = np.trapz(trend)
    for i in range(permutations):
        random_distances = np.random.permutation(distances)
        cum_distances = np.cumsum(random_distances)
        es = np.trapz(cum_distances)
        auc = es - triangle_area
        es_permute.append(auc)

    return es_permute

#==============================================================================
def permute_max_GSEA(hits=None, permutations=1000):
    import numpy as np
    #Simulate 1000 permuations of region ranks
    pos_total = float(sum([1 for x in hits if x != -1]))
    neg_total = float(sum([1 for x in hits if x == -1]))
    simES = list()
    for i in range(permutations):
        np.random.shuffle(hits)
        Eval = 0
        ES = list()
        for distance in hits:
            if distance == -1:
                Eval += -1.0/neg_total
                ES.append(Eval)
            else:
                Eval += 1.0/pos_total
                ES.append(Eval)
        simES.append(max(ES, key=abs))

    return simES

#==============================================================================
def padj_bonferroni(results, pvalindex=-1):
    '''This function iterates through TFEA results, removes TFs that returned 
        "no hits" and calculates a p-adj using the Bonferroni Correction for 
        each TF motif appending it to the given TFresults array

    Parameters
    ----------
    TFresults : list of lists
        contains calculated enrichment scores for all TFs of interest specified
        by the user
        
    Returns
    -------
    TFresults : list of lists
        same as input with an additional p-adjusted value appended to each TF
    '''
    for i in range(len(results)):
        PVAL = results[i][pvalindex]
        #Using Bonferroni Correction
        PADJ = 1 if PVAL*len(results) > 1 else PVAL*len(results)
        results[i].append(PADJ)

    return results

#==============================================================================
def anderson_darling(distances):
    #sort distances based on the ranks from TF bed file
    #and calculate the absolute distance
    motif = distances[0]
    distances = distances[1:]
    hits = sum([1 if x != '.' else 0 for x in distances])

    #Get -exp() of distance and get cumulative scores
    #Filter distances into quartiles to get middle distribution
    q1 = int(round(len(distances)*.25))
    q3 = int(round(len(distances)*.75))
    expected_distribution =  [x for x in distances[int(q1):int(q3)] if x != '.']
    observed_distribution = [x for x in distances if x != '.']

    stat, _, sig = anderson_ksamp([observed_distribution, expected_distribution])

    return [motif, stat, hits, sig]

#==============================================================================
def md_score(distances, smallwindow=None):
    '''Calculate md score
    '''
    distances1, distances2 = distances
    motif = distances1[0]
    distances1 = [abs(float(x)) for x in distances1[1:] if x != '.']
    distances2 = [abs(float(x)) for x in distances2[1:] if x != '.']
    d1_total = float(len(distances1))
    d2_total = float(len(distances2))
    # print(motif)
    # print("distances1: ", distances1[:100])
    # print("md1sum: ", sum([1.0 if d <= smallwindow else 0.0 for d in distances1]))
    # print("md1tot: ", d1_total)
    # print("distances2: ", distances2[:100])
    # print("md2sum: ", sum([1.0 if d <= smallwindow else 0.0 for d in distances2]))
    # print("md2tot: ", d2_total)
    try:
        md1 = sum([1.0 if d <= smallwindow else 0.0 for d in distances1])/d1_total
        md2 = sum([1.0 if d <= smallwindow else 0.0 for d in distances2])/d2_total
    except ZeroDivisionError:
        return [motif, 0, 0, 1, 1]

    return [motif, md1, md2, d1_total, d2_total]

#==============================================================================
def md_score_p(results):
    '''Calculate a p-value for md-score results
    '''
    mean = float(sum([x[2]-x[1] for x in results]))/float(len(results))
    for i in range(len(results)):
        motif = results[i][0]
        md1=float(results[i][1])
        md2=float(results[i][2])
        N1=float(results[i][3])
        N2=float(results[i][4])
        if (N1+N2)/2.0 != 0:
            p=((md1*N1)+(md2*N2))/(N1+N2)
            SE=(p*(1-p))*((1/N1)+(1/N2))
            try:
                z = (md2-md1-mean)/math.sqrt(SE)
            except ZeroDivisionError:
                z=0
            cdf=norm.cdf(z,0,1)
            p=min(cdf,1-cdf)*2
            md = md2-md1-mean
            total = (N1 + N2)/2.0
        
        results[i] = [motif, md, total, p]

    return results
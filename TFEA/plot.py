#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''This module only contains scripts that plot things in matplotlib. 
    All such scripts are in this module. No exceptions.
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
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
import subprocess

import numpy as np

from TFEA import exceptions

#Functions
#==============================================================================
def plot_individual_graphs(use_config=True, distances=None, figuredir=None, 
                            fimo_motifs=None, largewindow=1500, score=None, 
                            dpi=100, pvals=None, fcs=None, 
                            cumscore=None, sim_auc=None, auc=None,
                            meta_profile_dict=None, label1=None, label2=None, 
                            motif=None):
    '''This function plots all TFEA related graphs for an individual motif
    '''
    if use_config:
        from TFEA import config
        pvals = config.vars['PVALS']
        fcs = config.vars['FCS']
        figuredir=config.vars['FIGUREDIR']
        largewindow=config.vars['LARGEWINDOW']
        fimo_motifs = config.vars['FIMO_MOTIFS']
        dpi = config.vars['DPI']
        label1 = config.vars['LABEL1']
        label2 = config.vars['LABEL2']
        meta_profile_dict = config.vars['META_PROFILE']

    #Create MEME logos
    meme_logo(fimo_motifs, motif, figuredir)

    #Filter distances into quartiles for plotting purposes
    q1 = int(round(np.percentile(np.arange(1, len(distances),1), 25)))
    q2 = int(round(np.percentile(np.arange(1, len(distances),1), 50)))
    q3 = int(round(np.percentile(np.arange(1, len(distances),1), 75)))
    q1_distances = [x for x in distances[:q1] if x != '.']
    q2_distances = [x for x in distances[q1:q2] if x != '.']
    q3_distances = [x for x in distances[q2:q3] if x != '.']
    q4_distances = [x for x in distances[q3:] if x != '.']

    
    #Get log pval to plot for rank metric
    logpval = list()
    for x,y in zip(pvals,fcs):
        try:
            if y < 1:
                logpval.append(math.log(x,10))
            else:
                logpval.append(-math.log(x,10))
        except:
            logpval.append(0.0)


    #Set up plotting space
    plt.figure(figsize=(15.5,12))
    outer_gs = gridspec.GridSpec(2, 1, height_ratios=[2,1])
    enrichment_gs = gridspec.GridSpecFromSubplotSpec(4, 1, 
                                                    subplot_spec=outer_gs[0], 
                                                    height_ratios=[4, 1, 4, 2], 
                                                    hspace=.1)
    meta_gs = gridspec.GridSpecFromSubplotSpec(3, 4, subplot_spec=outer_gs[1], 
                                                    hspace=0.1, wspace=0.3)

    #Create Enrichment Plot
    xvals = np.linspace(start=0, stop=1, num=len(cumscore))
    xlimits = [0, 1]
    lineplot_ax = plt.subplot(enrichment_gs[0])
    barplot_ax = plt.subplot(enrichment_gs[1])
    scatterplot_ax = plt.subplot(enrichment_gs[2])
    figure_title = motif.split('.bed')[0] + ' Enrichment Plot'
    lineplot(title=figure_title, ax=lineplot_ax, xvals=xvals, yvals=cumscore, 
                xlimits=xlimits)
    
    barplot(ax=barplot_ax, xvals=xvals, colorarray=score, xlimits=xlimits)

    scatter_data = [(i,x) for i,x in zip(xvals, distances) if x != '.']
    scatter_x = [i for i,_ in scatter_data]
    scatter_y = [x for _,x in scatter_data]
    if len(logpval) != 0:
        scatterplot(ax=scatterplot_ax, xvals=scatter_x, yvals=scatter_y, 
                    xlimits=xlimits, largewindow=largewindow)
        fillplot_ax = plt.subplot(enrichment_gs[3])
        fillplot(ax=fillplot_ax, xvals=xvals, yvals=logpval, xlimits=xlimits)
    else:
        scatterplot(ax=scatterplot_ax, xvals=scatter_x, yvals=scatter_y, 
                    xlimits=xlimits, largewindow=largewindow, xlabel=True)

    #Create Meta Plot
    #Initiate meta plots
    if len(meta_profile_dict) != 0:
        ax3 = plt.subplot(meta_gs[:2, 0])
        ax4 = plt.subplot(meta_gs[:2, 1])
        ax5 = plt.subplot(meta_gs[:2, 2])
        ax6 = plt.subplot(meta_gs[:2, 3])
        xvals = range(-int(largewindow),int(largewindow))
        q1posprofile1 = meta_profile_dict['q1posprofile1']
        q1negprofile1 = meta_profile_dict['q1negprofile1']
        q1posprofile2 = meta_profile_dict['q1posprofile2']
        q1negprofile2 = meta_profile_dict['q1negprofile2']
        q2posprofile1 = meta_profile_dict['q2posprofile1']
        q2negprofile1 = meta_profile_dict['q2negprofile1']
        q2posprofile2 = meta_profile_dict['q2posprofile2']
        q2negprofile2 = meta_profile_dict['q2negprofile2']
        q3posprofile1 = meta_profile_dict['q3posprofile1']
        q3negprofile1 = meta_profile_dict['q3negprofile1']
        q3posprofile2 = meta_profile_dict['q3posprofile2']
        q3negprofile2 = meta_profile_dict['q3negprofile2']
        q4posprofile1 = meta_profile_dict['q4posprofile1']
        q4negprofile1 = meta_profile_dict['q4negprofile1']
        q4posprofile2 = meta_profile_dict['q4posprofile2']
        q4negprofile2 = meta_profile_dict['q4negprofile2']

        ylim = [min(q1negprofile1+q1negprofile2+q2negprofile1+q2negprofile2
                        +q3negprofile1+q3negprofile2+q4negprofile1+q4negprofile2),
                    max(q1posprofile1+q1posprofile2+q2posprofile1+q2posprofile2
                        +q3posprofile1+q3posprofile2+q4posprofile1+q4posprofile2)]

        metaplot(q1posprofile1, q1negprofile1, q1posprofile2, q1negprofile2, ax=ax3, 
                    xvals=xvals, label1=label1, label2=label2, title='Q1', ylim=ylim)
        ax3.legend(loc=2,fontsize='small')
        metaplot(q2posprofile1, q2negprofile1, q2posprofile2, q2negprofile2, ax=ax4, 
                    xvals=xvals, label1=label1, label2=label2, title='Q2', ylim=ylim)
        metaplot(q3posprofile1, q3negprofile1, q3posprofile2, q3negprofile2, ax=ax5, 
                    xvals=xvals, label1=label1, label2=label2, title='Q3', ylim=ylim)
        metaplot(q4posprofile1, q4negprofile1, q4posprofile2, q4negprofile2, ax=ax6, 
                    xvals=xvals, label1=label1, label2=label2, title='Q4', ylim=ylim)

    #Initiate heatmaps
    ax7 = plt.subplot(meta_gs[2, 0])
    ax8 = plt.subplot(meta_gs[2, 1])
    ax9 = plt.subplot(meta_gs[2, 2])
    ax10 = plt.subplot(meta_gs[2, 3])
    
    bins = 100
    xlim = [int(-largewindow), int(largewindow)]
    if len(meta_profile_dict) != 0:
        heatmap(q1_distances, ax=ax7, xlim=xlim, bins=bins)
        heatmap(q2_distances, ax=ax8, xlim=xlim, bins=bins)
        heatmap(q3_distances, ax=ax9, xlim=xlim, bins=bins)
        heatmap(q4_distances, ax=ax10, xlim=xlim, bins=bins)
    else:
        heatmap(q1_distances, ax=ax7, xlim=xlim, bins=bins, title='Q1')
        heatmap(q2_distances, ax=ax8, xlim=xlim, bins=bins, title='Q2')
        heatmap(q3_distances, ax=ax9, xlim=xlim, bins=bins, title='Q3')
        heatmap(q4_distances, ax=ax10, xlim=xlim, bins=bins, title='Q4')

    plt.tight_layout()
    plt.savefig(os.path.join(figuredir, motif + '_enrichment_plot.png'), 
                dpi=dpi, bbox_inches='tight')
    plt.close()

    #Simulation Plot
    F = plt.figure(figsize=(9,7.75))
    ax = F.add_subplot(111)
    bins=100
    maximum = max(sim_auc)
    minimum = min(sim_auc)
    ax.hist(sim_auc,bins=bins)
    width = (maximum-minimum)/100.0
    rect = ax.bar(auc,ax.get_ylim()[1],color='red',width=width*2)[0]
    height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., 1.05*height, 'Observed', 
            ha='center', va='bottom')

    ax.set_xlim([min(minimum,auc)-(width*40), max(maximum,auc)+(width*40)])

    ax.set_ylim([0,(1.05*height)+5])
    ax.tick_params(axis='y', which='both', left=False, right=False, 
                    labelleft=True)

    ax.tick_params(axis='x', which='both', bottom=False, top=False, 
                    labelbottom=True)

    ax.set_title('Distribution of Simulated AUC values', fontsize=14)
    ax.set_ylabel('Number of Simulations', fontsize=14)
    ax.set_xlabel('Area Under the Curve (AUC)', fontsize=14)

    plt.tight_layout()
    plt.savefig(os.path.join(figuredir, motif + '_simulation_plot.png'), 
                dpi=dpi, bbox_inches='tight')
    plt.close()

#==============================================================================
def plot_global_MA(results, p_cutoff=None, title=None, xlabel=None, 
                    ylabel=None, savepath=None, dpi=100):
    '''This function plots graphs that are displayed on the main results.html 
        filethat correspond to results relating to all analyzed TFs.

    Parameters
    ----------
    results : list of lists
        contains calculated enrichment scores for all TFs of interest specified
        by the user
    '''
    ylist = [i[1] for i in results]
    xlist = [math.log(i[2], 10) if i[2] != 0 else 0 for i in results]
    plist = [i[-1] for i in results]

    sigx = [x for x, p in zip(xlist, plist) if p < p_cutoff]
    sigy = [p for x, p in zip(ylist, plist) if p < p_cutoff]

    F = plt.figure(figsize=(7,6))
    ax = plt.subplot(111)
    ax.scatter(xlist, ylist, color='navy', edgecolor='', s=50)
    ax.scatter(sigx, sigy, color='red', edgecolor='', s=50)
    ax.set_title(title, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)

    ax.set_xlabel(xlabel, fontsize=14)
    # ax.tick_params(axis='y', which='both', left=False, right=False, 
    #                 labelleft=True)

    # ax.tick_params(axis='x', which='both', bottom=False, top=False, 
    #                 labelbottom=True)

    # plt.tight_layout()
    F.savefig(savepath, dpi=dpi) #, bbox_inches='tight')
    plt.close()

#==============================================================================
def plot_global_volcano(results, p_cutoff=None, title=None, xlabel=None, 
                        ylabel=None, savepath=None, dpi=100):
    '''This function plots graphs that are displayed on the main results.html 
        filethat correspond to results relating to all analyzed TFs.

    Parameters
    ----------
    results : list of lists
        contains calculated enrichment scores for all TFs of interest specified
        by the user
    '''
    xlist = [i[1] for i in results]
    ylist = [-math.log(i[-1], 10) if i[-1] != 0 else 0 for i in results]
    plist = [i[-1] for i in results]

    sigx = [x for x, p in zip(xlist, plist) if p < p_cutoff]
    sigy = [p for x, p in zip(ylist, plist) if p < p_cutoff]

    F = plt.figure(figsize=(7,6))
    ax = plt.subplot(111)
    ax.scatter(xlist, ylist, color='navy', edgecolor='', s=50)
    ax.scatter(sigx, sigy, color='red', edgecolor='', s=50)
    ax.set_title(title, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.axhline(-math.log(p_cutoff, 10), linestyle='--', color='black')
    # ax.tick_params(axis='y', which='both', left=False, right=False, 
    #                 labelleft=True)

    # ax.tick_params(axis='x', which='both', bottom=False, top=False, 
    #                 labelbottom=True)

    # plt.tight_layout()
    F.savefig(savepath, dpi=dpi) #, bbox_inches='tight')
    plt.close()

#==============================================================================
def meme_logo(motif_file, motif_ID, figuredir):
    '''Runs meme2images that creates logo images
    '''
    meme2images_command = ['meme2images', '-rc', '-eps', '-motif', motif_ID, 
                            motif_file, figuredir]
    motif_ID = motif_ID.replace('.', '_')
    imagemagick_command = ['convert', figuredir / ('logo'+motif_ID+'.eps'), 
                            figuredir / ('logo'+motif_ID+'.png')]
    imagemagick_rc_command = ['convert', figuredir / ('logo'+motif_ID+'.eps'), 
                            figuredir / ('logo_rc'+motif_ID+'.png')]
    try:
        subprocess.check_output(meme2images_command, stderr=subprocess.PIPE)
        subprocess.check_output(imagemagick_command, stderr=subprocess.PIPE)
        subprocess.check_output(imagemagick_rc_command, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise exceptions.SubprocessError(e.stderr.decode())

#==============================================================================
def metaplot(posprofile1, negprofile1, posprofile2, negprofile2, ax=None, 
                xvals=None, label1=None, label2=None, title=None, ylim=None):
    ax.plot(xvals,posprofile1,color='blue',label=label1)
    ax.plot(xvals,negprofile1,color='blue')
    ax.plot(xvals,posprofile2,color='red',label=label2)
    ax.plot(xvals,negprofile2,color='red')
    ax.set_title(title,fontsize=14)
    ax.tick_params(axis='y', which='both', left=False, right=False, 
                    labelleft=True)
    ax.tick_params(axis='x', which='both', bottom=False, top=False, 
                    labelbottom=False)
    ax.set_ylabel('Reads per Millions Mapped',fontsize=10)
    ax.set_ylim(ylim)

#==============================================================================
def heatmap(distances, ax=None, xlim=None, bins=None, title=None):
    counts, edges = np.histogram(distances, bins=bins)
    edges = (edges[1:]+edges[:-1])/2.0
    norm    = matplotlib.colors.Normalize(vmin=min(counts), 
                                            vmax=max(counts))
    cmap    = cm.YlOrRd
    m       = cm.ScalarMappable(norm=norm, cmap=cmap)
    colors  = [m.to_rgba(c) for c in counts] 
    
    ax.bar(edges,np.ones((len(edges),)), color=colors, 
                width=(edges[-1]-edges[0])/len(edges), edgecolor=colors)
    ax.set_ylim([0,1])
    ax.set_xlim(xlim)
    ax.tick_params(axis='y', which='both', left=False, right=False, 
                    labelleft=False) 
    ax.tick_params(axis='x', which='both', bottom=False, top=False, 
                    labelbottom=True)
    ax.set_xlabel('Motif Distance to Center (bp)')
    if title != None:
        ax.set_title(title, fontsize=14)

#==============================================================================
def lineplot(title=None, ax=None, xvals=None, yvals=None, xlimits=None):
    #This is the enrichment score plot (i.e. line plot)
    ax.plot(xvals,yvals,color='green')
    ax.plot([0, 1],[0, 1], '--', alpha=0.75)
    ax.set_title(title, fontsize=14)
    ax.set_ylabel('Enrichment Score (ES)', fontsize=10)
    ax.tick_params(axis='y', which='both', left=True, right=False, 
                    labelleft=True)
    ax.tick_params(axis='x', which='both', bottom=False, top=False, 
                    labelbottom=False)
    ax.set_ylim([0,1])
    ax.set_xlim(xlimits)

#==============================================================================
def scatterplot(ax=None, xvals=None, yvals=None, xlimits=None, largewindow=None, 
                xlabel=False):
    #This is the barplot right below the enrichment score line plot
    ax.scatter(xvals, yvals, edgecolor="", color="black", 
                    s=10, alpha=0.25)
    ax.tick_params(axis='y', which='both', left=True, right=False, 
                    labelleft=True) 
    if xlabel:
        ax.tick_params(axis='x', which='both', bottom=False, top=False, 
                    labelbottom=True)
        ax.set_xlabel('Relative Rank (n='+str(len(xvals))+')', fontsize=14)
    else:
        ax.tick_params(axis='x', which='both', bottom=False, top=False, 
                        labelbottom=False)

    plt.sca(ax)
    plt.yticks([-int(largewindow),0,int(largewindow)],
                [str(largewindow/-1000.0), '0', str(largewindow/1000.0)])
    ax.set_xlim(xlimits)
    ax.set_ylim([-int(largewindow),int(largewindow)])
    ax.set_ylabel('Distance (kb)', fontsize=10)

#==============================================================================
def barplot(ax=None, xvals=None, colorarray=None, xlimits=None):
    norm    = matplotlib.colors.Normalize(vmin=min(colorarray), 
                                            vmax=max(colorarray))
    cmap    = cm.Greys
    m       = cm.ScalarMappable(norm=norm, cmap=cmap)
    colors  = [m.to_rgba(c) for c in colorarray] 
    ax.bar(xvals, [1 for x in xvals], width=1.0/len(xvals), edgecolor="", color=colors)
    ax.tick_params(axis='y', which='both', left=False, right=False, 
                    labelleft=False) 
    ax.tick_params(axis='x', which='both', bottom=False, top=False, 
                    labelbottom=False)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_ylabel('Score', fontsize=10)

#==============================================================================
def fillplot(ax=None, xvals=None, yvals=None, xlimits=None, ylimits=None):
    #This is the rank metric fill plot
    ax.fill_between(xvals, 0, yvals,facecolor='grey',edgecolor="")
    ax.tick_params(axis='y', which='both', left=True, right=False, 
                    labelleft=True)
    ax.tick_params(axis='x', which='both', bottom=False, top=False, 
                    labelbottom=True)
    ylim = math.fabs(max([x for x in yvals if -500 < x < 500],key=abs))
    ax.yaxis.set_ticks([int(-ylim), 0, int(ylim)])
    ax.set_xlim(xlimits)
    ax.set_xlabel('Relative Rank (n='+str(len(xvals))+')', fontsize=14)
    ax.set_ylabel('Rank Metric', fontsize=10)
    # try:
    #     ax2.axvline(len(updistancehist)+1,color='green',alpha=0.25)
    # except ValueError:
    #     pass
    # try:
    #     ax2.axvline(len(xvals) - len(downdistancehist), color='purple', 
    #                 alpha=0.25)
    # except ValueError:
    #     pass

#==============================================================================
def plot_deseq_MA(deseq_file=None, label1=None, label2=None, figuredir=None, 
                    dpi=100):
    '''Plots the DE-Seq MA-plot using the full regions of interest and saves it
    to the figuredir directory created in TFEA output folder

    Parameters
    ----------
    deseqfile : string
        full path to the deseq file (specifically .res.txt)

    label1 : string
        the name of the treatment or condition corresponding to bam1 list

    label2 : string
        the name of the treatment or condition corresponding to bam2 list

    figuredir : string
        full path to figure directory in output directory (created by TFEA)

    Returns
    -------
    None
    '''
    up_x = list()
    up_y = list()
    up_p = list()
    dn_x = list()
    dn_y = list()
    dn_p = list()
    with open(deseq_file,'r') as F:
        header = F.readline().strip('\n').split('\t')
        basemean_index = header.index('"baseMean"')
        log2fc_index = header.index('"log2FoldChange"')
        for line in F:
            line = line.strip('\n').split('\t')
            try:
                log2fc = float(line[log2fc_index+1])
                basemean = math.log(float(line[basemean_index+1]),10)
                pval = float(line[-2])
                if log2fc > 0:
                    up_x.append(basemean)
                    up_y.append(log2fc)
                    up_p.append(pval)
                else:
                    dn_x.append(basemean)
                    dn_y.append(log2fc)
                    dn_p.append(pval)
            except:
                pass

    x = [x for _,x in sorted(zip(up_p,up_x))] \
        + [x for _,x in sorted(zip(dn_p,dn_x),reverse=True)]

    y = [y for _,y in sorted(zip(up_p,up_y))] \
        + [y for _,y in sorted(zip(dn_p,dn_y),reverse=True)]

    c = np.linspace(0, 1, len(x))

    #Creates an MA-Plot of the region expression
    F = plt.figure(figsize=(7,6))
    ax = plt.subplot(111)
    plt.scatter(x=x,y=y,c=c,edgecolor='', cmap="RdYlGn")
    ax.set_title("DE-Seq MA-Plot",fontsize=14)
    ax.set_ylabel("Log2 Fold-Change ("+label2+"/"+label1+")",fontsize=14)
    ax.set_xlabel("Log10 Average Expression",fontsize=14)
    # ax.tick_params(axis='y', which='both', left=False, right=False, 
    #                 labelleft=True)
    # ax.tick_params(axis='x', which='both', bottom=False, top=False, 
    #                 labelbottom=True)
    cbar = plt.colorbar()
    cbar.ax.invert_yaxis() 
    cbar.set_ticks([0, 0.25, 0.5, 0.75, 1], ['0', '0.25', '0.5', '0.75', '1'])
    cbar.set_label('Relative Rank (n=' + str(len(x)) + ')', rotation=270, 
                        labelpad=20)
    plt.savefig(os.path.join(figuredir, 'DESEQ_MA_Plot.png'), dpi=dpi)
                # bbox_inches='tight')
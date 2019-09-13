#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
'''This is the main script that runs when the TFEA package is run.
'''
#==============================================================================
__author__ = 'Jonathan D. Rubin and Rutendo F. Sigauke'
__credits__ = ['Jonathan D. Rubin', 'Rutendo F. Sigauke', 'Jacob T. Stanley',
                'Robin D. Dowell']
__maintainer__ = 'Jonathan D. Rubin'
__email__ = 'Jonathan.Rubin@colorado.edu'
__version__ = '4.0'

def run():
    #Imports
    #==============================================================================
    import sys
    import subprocess
    import shutil
    from pathlib import Path
    #Add TFEA srcdirectory into path
    srcdirectory = Path(__file__).absolute().parent
    sys.path.insert(0, srcdirectory)

    from TFEA import process_inputs

    #ARGUMENT PARSING
    #==============================================================================
    '''We begin by parsing user arguments. TFEA can be run in two ways and these
        are not mutually exclusive. TFEA has traditional command line flags that
        a user may specify. Additionally, a user may provide a configuration file
        (.ini) with all necessary inputs. Finally, a user may provide both a 
        configuration file and command line flags. In this case, the command line
        flags will overwrite any redundant options in the configuration file.
    '''
    #Process user inputs in a separate module
    parser = process_inputs.read_arguments()

    #Display help message when no args are passed.
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    #TEST module
    #==============================================================================
    '''If test flag specified, run unittests and exit.
    '''
    test_install = parser.parse_args().TEST_INSTALL
    if test_install:
        subprocess.call(["python3.7", srcdirectory / 'test' / 'test_install.py'])
        sys.exit()
        
    test_full = parser.parse_args().TEST_FULL
    if test_full:
        sbatch = parser.parse_args().SBATCH
        if not sbatch:
            subprocess.call(["python3.7", srcdirectory / 'test' / 'test_full.py'])
            sys.exit()
        else:
            error_file = str(srcdirectory / 'test' / 'test_files' / 'TFEA_test.err')
            output_file = str(srcdirectory / 'test' / 'test_files' / 'TFEA_test.out')
            subprocess.call(["sbatch", 
                                "--error=" + error_file, 
                                "--output=" +  output_file,
                                "--mail-user=" + sbatch,
                                srcdirectory / 'test' / 'test.sbatch'])
            print(("TFEA tests submitted as sbatch job. It can be "
                    "monitored using:\ntail -f " + error_file))
            sys.exit()

    #Rerun module
    #==============================================================================
    '''If rerun flag specified, rerun all rerun.sh files in specified directory
    '''
    rerun = parser.parse_args().RERUN
    if rerun:
        for path in rerun:
            for rerun_script in Path(path).glob('**/rerun.sh'):
                subprocess.call(["sh", rerun_script])
        sys.exit()

    #VERIFICATION OF USER INPUTS
    #==============================================================================
    '''This section of the code reads config file and user specified flags, makes
        sure these are complete and not conflicting and writes them to config.py
        within TFEA for global use across modules
    '''
    process_inputs.verify_arguments(parser=parser)

    #CREATING DIRECTORIES
    #==============================================================================
    '''TFEA creates the specified output directory if it doesn't exist. Within the
        output directory, 3 directories are created: 'temp_files', 'e_and_o', and
        'plots'. These contain temporary files, stderr and stdout files, and
        figures generated by TFEA. This is also the module where the special 
        --sbatch flag is handled
    '''
    process_inputs.create_directories(srcdirectory=srcdirectory)

    #==============================================================================
    #MAIN SCRIPT
    #==============================================================================

    #SECONDARY IMPORTS
    #==============================================================================
    import multiprocessing as mp

    from TFEA import config
    from TFEA import multiprocess

    #Print starting statements
    #==============================================================================
    print("TFEA start: ", file=sys.stderr)
    #Print multiprocessing information to stderr
    if config.vars['DEBUG']:
        mp.log_to_stderr()
        multiprocess.current_mem_usage(config.vars['JOBID'])

    #COMBINE module
    #==============================================================================
    '''This module is a pre-processing step where a user may specify how to handle
        multiple bed file inputs. The goal is to arrive at a single bed file to
        input into subsequent modules.
    '''
    if config.vars['COMBINE'] != False:
        from TFEA import combine
        combine.main()

    #RANK module
    #==============================================================================
    '''This module decides how to rank regions within the bed files. If genome
        hits specified then the ranked output will only contain the center of each
        region (since we will perform bedtools closest later)
    '''
    if config.vars['RANK'] != False:
        from TFEA import rank
        rank.main()

    #SCANNER module
    #==============================================================================
    '''This module returns motif distances to regions of interest. This is
        accomplished either by scanning regions on the fly using fimo or homer, or 
        by running bedtools closest on region centers compared to a database of
        motif hits across the genome.
    '''
    from TFEA import scanner
    scanner.main()
        
    #ENRICHMENT module
    #==============================================================================
    '''Where the bulk of TFEA analysis occurs. Some components of plotting module 
        are contained within this enrichment module
    '''
    from TFEA import enrichment
    enrichment.main()
        
    #OUTPUT module
    #==============================================================================
    '''A module to write output to either a txt or html file
    '''
    from TFEA import output
    output.main()

    print("TFEA done. Output in:", config.vars['OUTPUT'], file=sys.stderr)

    #Delete temp_files directory
    #==============================================================================
    if not config.vars['DEBUG']:
        shutil.rmtree(config.vars['TEMPDIR'])

    #==============================================================================
    #END OF MAIN SCRIPT
    #==============================================================================
import argparse
import ROOT

import find_json
import find_newest
import find_range
import histograms
import produce_ratio
import produce_responses
import produce_time_evolution
import produce_vetomaps
# from plotting import produce_plots
import skim
import met

def parse_arguments():
    parser = argparse.ArgumentParser(description='JEC4PROMPT Toolkit: \
            https://github.com/toicca/dijet_rdf/tree/main')

    subparsers = parser.add_subparsers(dest='subparser_name')

    # Histogram config: Histogram producer from skimmed files
    hist_parser = subparsers.add_parser('hist', help='Produce histograms from skimmed files.')
    hist_files = hist_parser.add_mutually_exclusive_group(required=True)
    hist_files.add_argument('-c', '--config', type=str, help='Path to the config file. If set, \
            overrides all other options.')
    hist_files.add_argument('-fp', '--filepaths', type=str, help='Comma separated list of \
            text files containing input files (one input file per line).')
    hist_files.add_argument('-fl', '--filelist', type=str, help='Input files separated by commas.')
    hist_triggers = hist_parser.add_mutually_exclusive_group()
    hist_triggers.add_argument("--triggerlist", type=str, help="Comma separated list of \
            triggers")
    hist_triggers.add_argument("--triggerpath", type=str, help="Path to a file containing \
            a list of triggers")
    hist_parser.add_argument('-loc', '--is_local', action='store_true', help='Run locally. If not \
            set will append root://cms-xrd-global.cern.ch/ \
            to the start of file names.')
    hist_parser.add_argument('-pbar', '--progress_bar', action='store_true',
            help='Show progress bar.')
    hist_parser.add_argument('-hconf', '--hist_config', type=str, help='Path to the histogram \
            config file.')
    hist_parser.add_argument("--run_range", type=str, help="Run range of the given input files \
            (run_min and run_max separated by a comma)")
    hist_parser.add_argument("--run_tag", type=str, help="Run tag")
    hist_parser.add_argument("--nThreads", type=int, help="Number of threads to be used \
            for multithreading")
    hist_parser.add_argument("--out", type=str, required=True, default="", help="Output path \
            (output file name included)")

    # Find JSON config
    find_json_parser = subparsers.add_parser('find_json', help='Find JSON File appropriate for given run')
    find_json_parser.add_argument("--json_files", required=True, type=str, help="Comma separated \
            list of json files")
    find_json_parser.add_argument("--run_range", required=True, type=str, help="Run number")
    find_json_parser.add_argument("--out", required=False, type=str, help="Output file")

    # Find newest config
    find_newest_parser = subparsers.add_parser('find_newest', help="Find newest output file in \
            the subdirectories of given root directory")
    find_newest_parser.add_argument("--root_directory", type=str, help="Directory to search for \
            files in")
    find_newest_parser.add_argument("--starts_with", type=str, help="Choose a prefix for the files \
            to search for")
    find_newest_parser.add_argument("--ends_with", type=str, help="Choose a suffix for the files \
            to search for")
    find_newest_parser.add_argument("--spaces", action="store_true", help="Use spaces instead of \
            commas to separate the file paths")
    find_newest_parser.add_argument("--max_depth", type=int, help="Depth of files to search for \
            in the directory tree (default: None)")

    # Find range config
    find_range_parser = subparsers.add_parser('find_range', help="Find run range of \
                                                given input files")
    find_range_files = find_range_parser.add_mutually_exclusive_group(required=True)
    find_range_files.add_argument("--filelist", type=str, help="Comma separated list of \
            input files")
    find_range_files.add_argument('-fp', '--filepaths', type=str, help='Comma separated list of \
            text files containing input files (one input file per line).')
    find_range_parser.add_argument("-loc", "--is_local", action="store_true", help='Run locally. \
            If not set will append root://cms-xrd-global.cern.ch/ \
            to the start of file names')
    find_range_parser.add_argument("--for_brilcalc", action="store_true", help='Prints the range \
            in a form compatible with the brilcalc command line tool')
    find_range_parser.add_argument("--nThreads", type=int, help="Number of threads to be used \
            for multithreading")
    find_range_parser.add_argument("--progress_bar", action="store_true", help="Show progress bar")

    # Produce ratio config
    ratio_parser = subparsers.add_parser("produce_ratio", help="Produce Data vs. MC comparisons")
    ratio_parser.add_argument("--data_files", type=str, required=True, help="A lsit of root files \
            containing skimmed run data")
    ratio_parser.add_argument("--mc_files", type=str, required=True, help="A list of root files \
            containing skimmed MC data")
    ratio_triggers = ratio_parser.add_mutually_exclusive_group()
    ratio_triggers.add_argument("--triggerlist", type=str, help="Comma separated list of \
            triggers")
    ratio_triggers.add_argument("--triggerpath", type=str, help="Path to a file containing \
            a list of triggers")
    ratio_parser.add_argument("--out", type=str, required=True, default="", help="Output path \
            (output file name included)")
    ratio_parser.add_argument("--data_tag", type=str, help="data tag")
    ratio_parser.add_argument("--mc_tag", type=str, required=True, help="MC tag")
    ratio_parser.add_argument("--nThreads", type=int, help="Number of threads to be used \
            for multithreading")
    ratio_parser.add_argument("--progress_bar", action="store_true", help="Show progress bar")
    ratio_parser.add_argument('-hconf', '--hist_config', required=True, type=str, help='Path to \
            the histogram config file.')
    ratio_parser.add_argument("--groups_of", type=int, help="Produce ratios for \
            groups containing given number of runs")

    # Produce responses config
    responses_parser = subparsers.add_parser("produce_responses", help="Produce responses \
            for files produced by JEC4PROMPT analysis")
    responses_files = responses_parser.add_mutually_exclusive_group(required=True)
    responses_files.add_argument("--filelist", type=str, help="Comma separated list of root files \
            produced by dijet_rdf")
    responses_files.add_argument('-fp', '--filepaths', type=str, help='Comma separated list of \
            text files containing input files (one input file per line).')
    responses_triggers = responses_parser.add_mutually_exclusive_group()
    responses_triggers.add_argument("--triggerlist", type=str, help="Comma separated list of \
            triggers for which plots will be produced \
            (default value 'all').")
    responses_triggers.add_argument("--triggerpath", type=str, help="Path to a file containing \
            a list of triggers for which plots will be produced")
    responses_parser.add_argument("--out", type=str, default="", help="Output path")
    responses_parser.add_argument("--config", type=str, default="", help="Path to config file")

    # Produce time evolution config
    time_evolution_parser = subparsers.add_parser("produce_time_evolution", help="Produce time \
            evolution for given input files")
    time_evolution_files = time_evolution_parser.add_mutually_exclusive_group(required=True)
    time_evolution_files.add_argument("--filelist", type=str, help="Comma separated list of \
            input files")
    time_evolution_files.add_argument('-fp', '--filepaths', type=str, help='Comma separated list of \
            text files containing input files (one input file per line).')
    time_evolution_triggers = time_evolution_parser.add_mutually_exclusive_group()
    time_evolution_triggers.add_argument("--triggerlist", type=str, help="Comma separated list of \
            triggers")
    time_evolution_triggers.add_argument("--triggerpath", type=str, help="Path to a file containing \
            a list of triggers")
    time_evolution_parser.add_argument("--out", type=str, required=True, default="", help="Output path \
            (output file name included)")
    time_evolution_parser.add_argument("--data_tag", type=str, help="data tag")
    time_evolution_parser.add_argument("--nThreads", type=int, help="Number of threads to be used \
            for multithreading")
    time_evolution_parser.add_argument("--progress_bar", action="store_true", help="Show progress bar")
    time_evolution_parser.add_argument('-hconf', '--hist_config', required=True, type=str, help='Path to the histogram \
            config file.')

    # Produce vetomaps config
    vetomaps_parser = subparsers.add_parser("produce_vetomaps", help="Produce VetoMaps for files \
            produced by JEC4PROMPT analysis")
    vetomaps_files = vetomaps_parser.add_mutually_exclusive_group(required=True)
    vetomaps_files.add_argument("--filelist", type=str, help="Comma separated list of root files \
            produced by dijet_rdf")
    vetomaps_files.add_argument('-fp', '--filepaths', type=str, help='Comma separated list of \
            text files containing input files (one input file per line).')
    vetomaps_triggers = vetomaps_parser.add_mutually_exclusive_group()
    vetomaps_triggers.add_argument("--triggerlist", type=str, help="Comma separated list of \
            triggers for which plots will be produced \
            (default value 'all')")
    vetomaps_triggers.add_argument("--triggerpath", type=str, help="Path to a file containing \
            a list of triggers for which plots will be produced")
    vetomaps_parser.add_argument("--out", type=str, default="", help="Output path")
    vetomaps_parser.add_argument("--config", type=str, default="", help="Path to config file")

    # Produce plots config
    plots_parser = subparsers.add_parser("produce_plots", help="Produce plots for given list of \
                                            input files")
    plots_files = plots_parser.add_mutually_exclusive_group(required=True)
    plots_files.add_argument("--filelist", type=str, help="Comma separated list of root files \
            produced by dijet_rdf")
    plots_files.add_argument('-fp', '--filepaths', type=str, help='Comma separated list of \
            text files containing input files (one input file per line).')
    plots_parser.add_argument("--out", required=True, type=str, help="Output path")
    plots_parser.add_argument("--config", type=str, default="", help="Path to config file")
    plots_parser.add_argument("--all", action="store_true",
                                help="Produce all plots in given .root files")

    # Skimming config
    skim_parser = subparsers.add_parser("skim", help="Perform skimming for\
            given list of input files")
    skim_files = skim_parser.add_mutually_exclusive_group(required=True)
    skim_files.add_argument("--filelist", type=str, help="Comma separated list of root files")
    skim_files.add_argument('-fp', '--filepaths', type=str, help='Comma separated list of \
            text files containing input files (one input file per line).')
    skim_parser.add_argument("--nsteps", type=int, help="Number of steps input files are grouped into.")
    skim_parser.add_argument("--step", type=int, help="Step to be processed.")
    skim_parser.add_argument("--progress_bar", action="store_true", help="Show progress bar")
    skim_parser.add_argument("--is_local", action="store_true", help='Run locally. If not set will \
            append root://cms-xrd-global.cern.ch/ to the start of file names')
    skim_triggers = skim_parser.add_mutually_exclusive_group()
    skim_triggers.add_argument('-tp', '--triggerpath', type=str, help='Path to the trigger list')
    skim_triggers.add_argument('-tl','--triggerlist', type=str,
            help='Input files separated by commas')
    skim_parser.add_argument("--out", type=str, required=True, default="", help="Output path")
    skim_parser.add_argument("--dataset", type=str,
            choices=["dijet", "zjet", "egamma", "multijet"],
            help="Dataset type: dijet, zjet, egamma or multijet")
    skim_parser.add_argument("--channel", type=str,
            choices=["dijet", "zmm", "photonjet", "multijet"],
            help="Channel type: dijet, zmm, photonjet or multijet")
    skim_parser.add_argument("--nThreads", type=int, help="Number of threads to be used \
            for multithreading")
    skim_parser.add_argument("--golden_json", type=str, help="Golden JSON for filtering")
    skim_parser.add_argument("--is_mc", action="store_true", help="Set if input files are MC data.")
    skim_parser.add_argument("--run_range", type=str, help="Run range of the given input files \
            (run_min and run_max separated by a comma)")
    skim_parser.add_argument("--mc_tag", type=str, help="MC tag of the given MC files")
    skim_parser.add_argument("--correction_json", type=str, help="Path to a JSON file defining \
                             JECs, vetomaps, etc.")
    skim_parser.add_argument("--correction_key", type=str, help="Key in the correction JSON file \
                             defining the corrections to be applied")

    met_parser = subparsers.add_parser('met', help = 'Perform MET analysis')
    met_parser.add_argument('-nt', '--n_threads', type = int,
                            help = 'How many threads for multithreading')
    met_parser.add_argument('-o', '--out', type = str, required = True, default = '',
                            help = 'Output path')
    met_parser.add_argument('-il', '--is_local', action = 'store_true',
                             help = 'Run locally. If not set, will append \
                             root://cms-xrd-global.cern.ch/ to filenames')
    met_parser.add_argument('-pb', '--progress_bar', action = 'store_true',
                           help = 'Show progress bar')
    met_parser.add_argument('-ns', '--n_steps', type = int,
                           help = 'Number of steps input files are grouped into')
    met_parser.add_argument('-s', '--step', type = int,
                           help = 'Step to be processed.')
    
    met_files = met_parser.add_mutually_exclusive_group(required = True)
    met_files.add_argument('-fl', '--filelist', type = str,
                           help = 'Comma-separated list of root files')
    met_files.add_argument('-fp', '--filepaths', type = str,
                           help = 'Comma-separated list of text files containing input files (one input file per line)')
    
    met_triggers = met_parser.add_mutually_exclusive_group()
    met_triggers.add_argument('-tp', '--trigger_path', type = str,
                              help = 'Path to trigger list')
    met_triggers.add_argument('-tl', '--trigger_list', type = str,
                              help = 'Input files separated by commas')

    # Parse command line arguments, overriding config file values
    args = parser.parse_args()

    if args.subparser_name == "skim":
        if not args.is_mc and args.mc_tag:
            raise ValueError("is_mc not set but mc_tag given")
        if args.is_mc and args.run_range:
            raise ValueError("run_range and is_mc both set")
        if (args.step is not None and args.nsteps is None) or \
                (args.nsteps is not None and args.step is None):
            raise ValueError("nsteps and step should be passed together")
        if (args.step is not None and args.nsteps is not None):
            if args.step > args.nsteps:
                raise ValueError("step should be less than nsteps")
        if args.dataset:
            print("--dataset is deprecated. Use --channel instead.")
            args.channel = args.dataset

    elif args.subparser_name == 'met':
        if not args.filelist and not args.filepaths:
            raise ValueError('Filelist or filepath required')

    return args


if __name__ == "__main__":
    args = parse_arguments()

    command = args.subparser_name
    
    # One day when Python version >= 3.10.0
    # is used implement match here instead.
    if command == "find_json":
        find_json.run(args)
    elif command == "find_newest":
        find_newest.run(args)
    elif command == "find_range":
        find_range.run(args)
    elif command == "hist":
        histograms.run(args)
    elif command == 'met':
        met.run(args)
    elif command == "produce_ratio":
        produce_ratio.run(args)
    elif command ==  "produce_responses":
        produce_responses.run(args)
    elif command == "skim":
        skim.run(args)
    elif command == "produce_time_evolution":
        produce_time_evolution.run(args)
    elif command == "produce_plots":
        produce_plots.run(args)
    elif command == "produce_vetomaps":
        produce_vetomaps.run(args)

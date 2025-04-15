import matplotlib.pyplot as mp
import mplhep as hep
import os
import uproot

from ROOT import gPad, EnableImplicitMT, RDataFrame, RDF, TChain, TCanvas, TFile, TEfficiency
from processing_utils import file_read_lines
from typing import List

def get_met(category, files, triggers, args, step = None):
    events_chain = TChain('Events')
    for file in files:
        if args.is_local: events_chain.Add(file)
        else:
            try: events_chain.Add(f'root://hip-cms-se.csc.fi//{file}')
            except Exception as ex: print(f'Skipping problematic run: {ex}')
    events_rdf = RDataFrame(events_chain)
    if args.progress_bar: RDF.Experimental.AddProgressBar(events_rdf)
    details, target = ('temp', category, 150, 0, 3000), 'PuppiMET_pt'
    pt_initial = events_rdf.Histo1D(details, target).Clone(f'{target} 0')
    hists = {'pt': [pt_initial], 'eff': []}
    TCanvas('', '', 300, 300).cd()
    for t, trigger in enumerate(triggers):
        pt_hist = events_rdf.Filter(trigger).Histo1D(details, target).Clone(f'{target} {t + 1}')
        hists['pt'].append(pt_hist)
        eff_hist = TEfficiency(pt_hist, pt_initial)
        eff_hist.Draw('')
        gPad.Update()
        hists['eff'].append(eff_hist.GetPaintedGraph().Clone())
    outfiles = {}
    for key, value in hists.items():
        outfile = f'{args.out}/{category}/{key}.root'
        with TFile.Open(outfile, 'RECREATE') as hist_out:
            hist_out.cd()
            for hist in value: hist.Write()
        outfiles[key] = outfile
    hist_params = {'eff': {'title': f"'{category.replace('_', ' ')}'",
                           'ylabel': "'Efficiency'", 'xlim': '0, 3000', 'xlabel': "r'$p_T$ [GeV]'"}}
    hist_params['pt'] = hist_params['eff'].copy()
    hist_params['pt']['ylabel'] = "'Events'"
    hist_params['pt']['yscale'] = "'log'"
    return outfiles, hist_params

def plot_met(hist_filepath, hist_params):
    file = uproot.open(hist_filepath)
    for hist_name in file:
        if 'eff' in hist_name:
            hist_label = 'Efficiency ' + hist_name[-1]
            (x_values, y_values) = file[hist_name].values()
            y_low = file[hist_name].errors('low', 1)
            y_high = file[hist_name].errors('high', 1)
            mp.errorbar(x_values, y_values, [y_low, y_high],
                        color = f'C{hist_label[-1]}', label = hist_label)
        else:
            hist_label = hist_name[:-2]
            hep.histplot(file[hist_name],
                         color = f'C{hist_label[-1]}', label = hist_label)
    for key, value in hist_params.items(): exec(f'mp.{key}({value})')
    mp.legend()
    mp.savefig(hist_filepath.replace('root', 'png'))
    mp.close()

def run(args):
    hep.style.use('CMS')
    if args.n_threads: EnableImplicitMT(args.n_threads)
    files: List[str] = []
    if args.filepaths:
        paths = [p.strip() for p in args.filepaths.split(',')]
        for path in paths: files.extend(file_read_lines(path))
        category = args.filepaths.split('/')[-1].replace('.txt', '')
    else:
        files = [l.strip() for l in args.filelist.split(',')]
        category = '_'.join([l.split('/')[-1].replace('.root', '')
                             for l in args.filelist.split(',')])
    if args.n_steps is not None and args.step is not None:
        files = files[args.step::args.n_steps]
    triggers: List[str] = []
    if args.trigger_list: triggers = args.trigger_list.split(',')
    elif args.trigger_path: triggers = file_read_lines(args.trigger_path)
    for dir in [args.out, f'{args.out}/{category}']:
        if not os.path.exists(dir): os.makedirs(dir)
    hist_files, hist_params = get_met(category, files, triggers, args, args.step)
    for key, value in hist_files.items(): plot_met(value, hist_params[key])
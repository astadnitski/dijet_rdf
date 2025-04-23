import matplotlib.pyplot as mp
import mplhep as hep
import os, uproot

from ROOT import gPad, EnableImplicitMT, RDataFrame, RDF, TChain, TCanvas, TFile, TEfficiency
from processing_utils import file_read_lines
from typing import List

def get_met(sample, files, triggers, args, step = None):
    events_chain = TChain('Events')
    for file in files:
        if args.is_local: events_chain.Add(file)
        else:
            try: events_chain.Add(f'root://hip-cms-se.csc.fi//{file}')
            except Exception as ex: print(f'Skipping problematic run: {ex}')
    events_rdf = RDataFrame(events_chain)
    if args.progress_bar: RDF.Experimental.AddProgressBar(events_rdf)
    events_rdf = get_pure_single_muon(events_rdf)
    details, target = ('temp', sample, 150, 0, 3000), 'PuppiMET_pt'
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
        outfile = f'{args.out}/{sample}/{key}.root'
        with TFile.Open(outfile, 'RECREATE') as hist_out:
            hist_out.cd()
            for hist in value: hist.Write()
        outfiles[key] = outfile
    return outfiles

def get_pure_single_muon(events_rdf):
    return events_rdf.Filter('HLT_IsoMu24').Filter('nMuon == 1')

def plot_met(hist_files, sample, triggers):
    pt, eff = uproot.open(hist_files['pt']), uproot.open(hist_files['eff'])
    fig, (ax_eff, ax_pt) = mp.subplots(1, 2)

    for hist_name in eff:
        hist_label = 'Efficiency ' + hist_name[-1]
        (x_values, y_values) = eff[hist_name].values()
        y_errors = [eff[hist_name].errors('low', 1), eff[hist_name].errors('high', 1)]
        ax_eff.errorbar(x_values, y_values, y_errors, color = f'C{hist_label[-1]}', label = hist_label)
    ax_eff.set_title('Trigger efficiency')
    ax_eff.set(xlabel = r'$p_T$ [GeV]', ylabel = 'Efficiency', xlim = [0, 1000])
    ax_eff.set_box_aspect(1)
    ax_eff.legend()

    for hist_name in pt:
        hist_label = hist_name[:-2]
        hep.histplot(pt[hist_name], color = f'C{hist_label[-1]}', label = hist_label)
    mp.yscale('log')
    ax_pt.set_title(r'PuppiMET $p_T$')
    ax_pt.set(xlabel = r'$p_T$ [GeV]', ylabel = 'Events', xlim = [0, 3000])
    ax_pt.set_box_aspect(1)
    ax_pt.legend()

    fig.suptitle(sample.replace('_', ' '))
    for t, trigger in enumerate(triggers):
        mp.figtext(0.5, 0.1 - (t * 0.028), f'Trigger {t + 1}: {trigger}', horizontalalignment = 'center', fontsize = 18, c = f'C{t + 1}')
    fig.set_size_inches(12, 9)
    fig.tight_layout()
    mp.savefig(f'out_met/{sample}/efficiency.png')


def run(args):
    hep.style.use('CMS')
    if args.n_threads: EnableImplicitMT(args.n_threads)
    files: List[str] = []
    if args.filepaths:
        paths = [p.strip() for p in args.filepaths.split(',')]
        for path in paths: files.extend(file_read_lines(path))
        sample = args.filepaths.split('/')[-1].replace('.txt', '')
    else:
        files = [l.strip() for l in args.filelist.split(',')]
        sample = '_'.join([l.split('/')[-1].replace('.root', '')
                             for l in args.filelist.split(',')])
    if args.n_steps is not None and args.step is not None:
        files = files[args.step::args.n_steps]
    triggers: List[str] = []
    if args.trigger_list: triggers = args.trigger_list.split(',')
    elif args.trigger_path: triggers = file_read_lines(args.trigger_path)
    for dir in [args.out, f'{args.out}/{sample}']:
        if not os.path.exists(dir): os.makedirs(dir)
    hist_files = get_met(sample, files, triggers, args, args.step)
    plot_met(hist_files, sample, triggers)
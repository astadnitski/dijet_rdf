import os
from ROOT import gStyle#, gErrorIgnoreLevel, kWarning
from ROOT import EnableImplicitMT, RDataFrame, RDF, TCanvas, TChain, TLegend
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
    bin_count, bin_min, bin_max = 150, 0, 3000
    target = 'PuppiMET_pt'
    pt_initial = events_rdf.Histo1D(('a_pt', f'{category} {target}', bin_count, bin_min, bin_max), target).Clone(category)
    pt_cut, efficiency = [pt_initial], []
    for trigger in triggers:
        events_rdf_cut = events_rdf.Filter(trigger)
        pt_hist = events_rdf_cut.Histo1D(('b_pt', f'{category} efficiency', bin_count, bin_min, bin_max), target)
        pt_hist = pt_hist.Clone(trigger)
        pt_cut.append(pt_hist)
        eff_hist = pt_hist.Clone(trigger)
        eff_hist.Divide(pt_initial)
        efficiency.append(eff_hist)
    colors = [1, 2, 3]
    canvas_style = {'SetTitle': "'new_title'", 'SetLogx': 'False', 'SetLogy': 'True'}
    hist_style = {'GetXaxis().SetRangeUser': '0, 3000',
                  'GetXaxis().SetTitle': "'pT [GeV]'",
                  'GetYaxis().SetTitle': "'events'"}
    make_plot(pt_cut, f'{args.out}/{category}', 'test_plot.png', canvas_style, hist_style, colors)
    canvas_style = {'SetTitle': "'new_title_1'", 'SetLogy': 'False'}
    hist_style = {'GetYaxis().SetTitle': "'efficiency'"}
    make_plot(efficiency, f'{args.out}/{category}', 'efficiency.png', canvas_style, hist_style, colors[1:])

def make_plot(hists, out_dir, out_name, canvas_style, hist_style, colors):
    gStyle.SetOptStat(0)
    canvas = TCanvas('canvas', '', 750, 750)
    legend = TLegend(0.2, 0.8, 0.9, 0.9)
    for h, hist in enumerate(hists):
        for key, value in hist_style.items(): exec(f'hist.{key}({value})')
        hist.SetLineColor(colors[h])
        hist.Draw('SAME')
        short = hist.GetName().split('&&')[-1].strip()
        legend.AddEntry(hist, short, 'l')
    for key, value in canvas_style.items(): exec(f'canvas.{key}({value})')
    legend.Draw()
    canvas.SaveAs(f'{out_dir}/{out_name}')

def run(args):
    #gErrorIgnoreLevel = kWarning
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
        n = args.n_steps
        i = args.step
        files = files[i::n]
    triggers: List[str] = []
    if args.trigger_list: triggers = args.trigger_list.split(',')
    elif args.trigger_path: triggers = file_read_lines(args.trigger_path)
    if not os.path.exists(args.out): os.makedirs(args.out)
    get_met(category, files, triggers, args, args.step)

# def add_columns(rdf, columns):
#     for column in columns: rdf = rdf.Define(column, '0.0')
#     return rdf
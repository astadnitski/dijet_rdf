import os
from ROOT import EnableImplicitMT, RDataFrame, RDF, TCanvas, TChain
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
    make_plot(category, events_rdf, ['PuppiMET_pt'], args.out, 'png')
    # print('PuppiMET_pt max:', events_rdf.Max('PuppiMET_pt').GetValue())

def add_columns(rdf, columns):
    for column in columns: rdf = rdf.Define(column, '0.0')
    return rdf

def make_plot(category, rdf, columns, output_dir, ext):
    canvas = TCanvas('canvas', '', 750, 750)
    canvas.SetLogy(True)
    for column in columns:
        histogram = rdf.Histo1D(column)
        histogram.SetTitle(f'{category} {column}')
        histogram.Draw()
        histogram.GetXaxis().SetRangeUser(0, 3000)
        histogram.GetXaxis().SetTitle('pT [GeV]')
        histogram.GetYaxis().SetTitle('events')
        canvas.SaveAs(f'{output_dir}/{category}/{column}.{ext}')
        # WHEN TIME ALLOWS: make mkdir work
        # try: canvas.SaveAs(f'{output_dir}/{category}/{column}.{ext}')
        # except:
        #     os.mkdir(f'{output_dir}/{category}')
        #     canvas.SaveAs(f'{output_dir}/{category}/{column}.{ext}')

def run(args):
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
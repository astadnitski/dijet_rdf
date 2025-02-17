import ROOT

def init_dijet(rdf, jet_columns):
    ROOT.gInterpreter.Declare("""
    #ifndef DIJET_IDXS
    #define DIJET_IDXS
                                
    std::pair<std::pair<int, int>, int> findTagProbeIdxs(ROOT::RVec<float> Jet_eta, ROOT::RVec<float> Jet_pt,
                        ROOT::RVec<float> Jet_phi, ROOT::RVec<int> Jet_jetId) {

        int idx1 = (int(Jet_phi[0]) * 100) % 2;
        int idx2 = -1;

        // Check that the tag is in barrel
        if (abs(Jet_eta[idx1]) > 1.3 || Jet_pt[idx1] < 15 || Jet_jetId[idx1] < 4) {
            return std::make_pair(std::make_pair(-1, -1), -1);
        }
                                
        // Find the probe jet as:
        // leading jet back-to-back with the tag jet
        for (int i = 0; i < Jet_pt.size(); i++) {
            if (i == idx1 || Jet_pt[i] < 12 || Jet_jetId[i] < 4) {
                continue;
            }
            if (abs(ROOT::VecOps::DeltaPhi(Jet_phi[i], Jet_phi[idx1])) > 2.7 &&
                Jet_pt[i] > 12 && Jet_jetId[i] >= 4) {
                idx2 = i;
                break;
            }
        }

        // Find the activity jet
        int idx3 = -1;
        for (int i = 0; i < Jet_pt.size(); i++) {
            if (i != idx1 && i != idx2 && Jet_pt[i] > 12 && Jet_jetId[i] >= 4) {
                idx3 = i;
                break;
            }
        }

        return std::make_pair(std::make_pair(idx1, idx2), idx3);
    }
                                
    #endif
    """)

    rdf = (rdf.Define("TnP_idx_temp", "findTagProbeIdxs(Jet_eta, Jet_pt, Jet_phi, Jet_jetId)")
            .Filter("TnP_idx_temp.first.first >= 0 && TnP_idx_temp.first.second >= 0",
                "Tag and probe found")
            .Define("Tag_idx_temp", "TnP_idx_temp.first.first")
            .Define("Probe_idx_temp", "TnP_idx_temp.first.second")
            .Define("Tag_pt", "Jet_pt[Tag_idx_temp]")
            .Define("Tag_eta", "Jet_eta[Tag_idx_temp]")
            .Define("Tag_phi", "Jet_phi[Tag_idx_temp]")
            .Define("Tag_mass", "Jet_mass[Tag_idx_temp]")
            .Define("Tag_rawPt", "(1.0 - Jet_rawFactor[Tag_idx_temp]) * Tag_pt")
            .Define("Tag_label", "0")
            .Define("Activity_idx_temp", "TnP_idx_temp.second")
            .Define("Probe_isFirst", "Probe_idx_temp == 0")
    )

    # Create a probe jet collection
    for column in jet_columns:
        rdf = rdf.Define("Probe_"+column[4:], f"{column}[Probe_idx_temp]")

    return rdf

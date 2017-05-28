# FNAL-T1049-near-line-analysis

In May 2014, immediately after finishing a first draft of my Ph.D. thesis, I traveled to Fermilab to help test a prototype muon detector called a "small-strip Thin Gap Chamber" (sTGC).

The experimental setup is shown in `figures/TestBeamSetup.png`.  The sTGC device under test, shown in red, was placed in the Fermilab Test Beam between six pixel detector planes (three on each side) shown in blue.  The sTGC itself consists of four detector planes, as shown in `figures/sTGC_layers.png`. Channel mapping is shown in `figures/sTGC_sectors.png`.

One of the main goals of this test beam campaign was to determine the resolution of the sTGC for reconstructing the trajectory of charged particles crossing it.  The design specification was a position resolution of 100 microns or better in each plane.

My code performed the "near-line analysis" of sTGC data: it was developed over a period of 2 weeks during data-taking, to assess the quality of the data as they were collected.  Going beyond the original goals of a simple data visualization, I reconstructed the trajectory if charged particles in the sTGC, and was able to demonstrate that the sTGC design specifications were met.

This is my version of the near-line analysis code at the end of data-taking.  The analysis was then further developed by colleagues into a proper "offline analysis" framework available here (restricted access):  
svn+ssh://svn.cern.ch/reps/fnaltestbeam14

The test beam experiment at Fermilab, and a follow-up at CERN, resulted in this publication in NIM A:  
<http://www.sciencedirect.com/science/article/pii/S0168900216001285>


### Data format

Raw data from the detectors comes in binary format, so the first step is to decode it.  High-energy physicists typically use ROOT files to store decoded data, especially for large detasets which benefit from built-in compression, but for getting a first implementation as quickly as possible, I chose to use tab-separated txt files. One big advantage of having a human-readable data format in the early stages of a project is the ability to catch simple problems quickly.

Small samples of good data taken near the end of the test beam campaign (the first 256 events from run 323) are available in `data/May20`:
- `trackHitOutfileRun323_sample.txt` contains human-readable pixel track data.  At the beginning of the experiment, software was already available to decode pixel data, form clusters out of adjacent hits, fit tracks from the clusters in different planes, and report the intersection point of the track with each pixel detector plane.
- `vmm000323_sample.txt` is the sTGC data in the format available at the time of starting the experiment: simply a txt version of the raw data, with dashes inserted between the address of the detector layer (in run 323 the addresses were [18, 19, 25, 29]) and the rest of the data from this address.  "fafafafa" was used to separate between events.  While useful to spot major data acquisition problems, this format needed to be further decoded and analyzed.


### Near-line analysis code

To run the near-line analysis on the small samples provided from run 323:
```bash
source run_decoder_correlated.sh 323
source run_plot_correlated.sh 323 0
```

The first script compiles and runs `decoder_correlated.C`, a C++ ROOT macro converting the sTGC data to human-readable tab-separated txt format.  It will create `data/May20/vmm000323_decoded_sample.txt`, with the same information as `vmm000323_sample.txt` but organized with one line for each hit reported by the sTGC detectors.  The format is:

`counter   channel   timing   amplitude   address   ievent`

... where `ievent` is generally equal to `counter + 1`, but may not be in case of synchronization problems.  There are 64 channels in each sTGC layer (address).

The second script runs the actual near-line analysis `plot_correlated.py`, written in Python ROOT.  The structure of the script is essentially as follows:

- initialization
   - constants specifying the conditions of each run
   - sTGC input file reader
   - pixel input file reader
   - start of main program
   - parse options
   - initialize IPMap with the mapping between addresses and detector layers
   - read input files
   - prepare output directory for plots
   - prepare canvas

- sTGC data analysis part 1  (simpler analysis, implemented first)
   - declare histograms
      - hit profiles, un-weighted and weighted by signal amplitude
      - timing distributions
      - amplitude distributions
      - correlation histograms to quantify coincidence hits between layers
      - correlation graphs between hits from different layers
      - graphs for sine-wave correction fits
      - rotated correlation graphs for determining standalone sTGC resolution
   - loop over events from sTGC data to fill the first histograms
   - draw the first histograms
      - includes gaussian fits of hit profiles
      - output png files

- pixel data analysis
   - declare histograms
      - pixel track display
      - pixel track angles
   - loop over events from pixel data to fill the histograms
      - includes reconstructing the pixel tracks using linear fits
   - draw the histograms
      - includes a gaussian fit of the track angles histogram
      - output png files

- sTGC data analysis part 2
   - declare histograms
      - "cutflow": how many events pass each step of the event selection
      - event displays: channel outputs for single events
      - sTGC track displays
      - sTGC position measurement residuals
         - "unbiased residuals": wrt tracks fit without the layer of interest
         - "biased residuals": wrt tracks fit including the layer of interest
         - residuals wrt pixel tracks
   - loop over events from sTGC data
      - event selection
         - timing between 2300 and 3300 counts
         - 3 to 5 hits per cluster
         - mode of cluster not next to channel with zero amplitude
         - all cluster channels within 2 channels of mode
         - clusters in all 4 sTGC layers, if expected for this track
         - at most 2 clusters with only 3 hits
      - fit clusters with gaussians to determine particle position measurements
         - weighted average an alternative way to measure position
      - apply sine-wave correction, measured from data, to undo readout bias
      - fill position correlation graphs
      - reconstruct sTGC tracks using linear fits
      - calculate position residuals
   - draw the histograms
      - includes a gaussian fit of the track angles histogram (measure of sTGC resolution)
      - output png files
   - implementation of algorithm by Vladimir Petrovich to use rotated correlation graphs for determining standalone sTGC resolution
      - includes sinusoidal fits
         - on data for which no correction is available: figure out the corrections to apply
         - on data for which correction is available: check that the corrections are correct
   - draw the final histograms
      - includes gaussian fits of the position residuals (another measure of sTGC resolution)
      - output png files


In the end, all three methods for evaluating the sTGC resolution (sTGC track angles, rotated correlation graphs, sTGC position residuals) indicated that one of the main sTGC design specifications, a position resolution of 100 microns or better in each plane, was met by the sTGC prototype.



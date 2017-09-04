#!/usr/bin/env python

""" MultiQC submodule to parse output from deepTools estimateReadFiltering """

import logging
import re
from collections import OrderedDict

from multiqc import config
from multiqc.plots import table, linegraph

# Initialise the logger
log = logging.getLogger(__name__)

class estimateReadFilteringMixin():
    def parse_estimateReadFiltering(self):
        """Find estimateReadFiltering output. Only the output from --table is supported."""
        self.deeptools_estimateReadFiltering = dict()
        for f in self.find_log_files('deeptools/estimateReadFiltering'):
            parsed_data = self.parseEstimateReadFilteringFile(f['f'], f['fn'])
            for k, v in parsed_data.items():
                if k in self.deeptools_estimateReadFiltering:
                    log.warning("Replacing duplicate sample {}.".format(k))
                self.deeptools_estimateReadFiltering[k] = v

            if len(parsed_data) > 0:
                self.add_data_source(f, section='estimateReadFiltering')

        if len(self.deeptools_estimateReadFiltering) > 0:
            header = OrderedDict()
            header["M Entries"] = {'title': 'M entries', 'description': 'Number of entries in the file (millions)'}
            header["% Aligned"] = {'title': '% Aligned', 'description': 'Percent of aligned entries'}
            header["% Filtered"] = {'title': '% Tot. Filtered', 'description': 'Percent of alignment that would be filtered for any reason.'}
            header["% Blacklisted"] = {'title': '% Blacklisted', 'description': 'Percent of alignments falling (at least partially) inside a blacklisted region'}
            header["% MAPQ"] = {'title': '% MAPQ', 'description': 'Percent of alignments having MAPQ scores below the specified threshold'}
            header["% Missing Flags"] = {'title': '% Missing Flags', 'description': 'Percent of alignments lacking at least on flag specified by --samFlagInclude'}
            header["% Forbidden Flags"] = {'title': '% Forbidden Flags', 'description': 'Percent of alignments having at least one flag specified by --samFlagExclude'}
            header["% deepTools Dupes"] = {'title': '% deepTools Dupes', 'description': 'Percent of alignments marked by deepTools as being duplicates'}
            header["% Duplication"] = {'title': '% Duplication', 'description': 'Percent of alignments originally marked as being duplicates'}
            header["% Singletons"] = {'title': '% Singletons', 'description': 'Percent of alignments that are singletons (i.e., paired-end reads where the mates don\'t align as a pair'}
            header["% Strand Filtered"] = {'title': '% Strand Filtered', 'description': 'Percent of alignments arising from the wrong strand'}

            d = dict()
            for k, v in self.deeptools_estimateReadFiltering.items():
                d[k] = {'M Entries': v['total'] / 1000000.0,
                        '% Aligned': 100. * v['mapped'] / float(v['total']),
                        '% Filtered': 100. * v['filtered'] / float(v['total']),
                        '% Blacklisted': 100. * v['blacklisted'] / float(v['total']),
                        '% Below MAPQ': 100. * v['mapq'] / float(v['total']),
                        '% Missing Flags': 100. * v['required flags'] / float(v['total']),
                        '% Forbidden Flags': 100. * v['excluded flags'] / float(v['total']),
                        '% deepTools Dupes': 100. * v['internal dupes'] / float(v['total']),
                        '% Duplication': 100. * v['dupes'] / float(v['total']),
                        '% Singletons': 100. * v['singletons'] / float(v['total']),
                        '% Strand Filtered': 100. * v['strand'] / float(v['total'])}

            self.general_stats_addcols(d, header)

        return len(self.deeptools_estimateReadFiltering)

    def parseEstimateReadFilteringFile(self, f, fname):
        d = {}
        firstLine = True
        for line in f.splitlines():
            if firstLine:
                firstLine = False
                continue
            cols = line.strip().split("\t")

            if len(cols) != 12:
                # This is not really the output from estimateReadFiltering!
                log.warning("{} was initially flagged as the tabular output from estimateReadFiltering, but that seems to not be the case. Skipping...".format(fname))
                return dict()

            if cols[0] in d:
                log.warning("Replacing duplicate sample {}.".format(cols[0]))
            d[cols[0]] = dict()

            try:
                d[cols[0]]["total"] = int(cols[1])
                d[cols[0]]["mapped"] = int(cols[2])
                d[cols[0]]["blacklisted"] = int(cols[3])
                d[cols[0]]["filtered"] = float(cols[4])
                d[cols[0]]["mapq"] = float(cols[5])
                d[cols[0]]["required flags"] = float(cols[6])
                d[cols[0]]["excluded flags"] = float(cols[7])
                d[cols[0]]["internal dupes"] = float(cols[8])
                d[cols[0]]["dupes"] = float(cols[9])
                d[cols[0]]["singletons"] = float(cols[10])
                d[cols[0]]["strand"] = float(cols[11])
            except:
                # Obviously this isn't really the output from estimateReadFiltering
                log.warning("{} was initially flagged as the output from estimateReadFiltering, but that seems to not be the case. Skipping...".format(fname))
                return dict()
        return d

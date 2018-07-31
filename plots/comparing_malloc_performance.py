###############################################################################
# Load raw data
###############################################################################
import os
import sys
os.chdir(os.path.dirname(sys.argv[0]))

series = {
    'nautk': {
        'file': 'nautk_run_mem2.out',
        'color': 'blue',
        'label': 'nautk',
        'params': {
            0: [],
            1: [],
        },
        'ts': [],
        'interpolate': False,
    },
    'linux': {
        'file': 'linux_run_mem2.out',
        'color': 'red',
        'label': 'linux',
        'params': {
            0: [],
            1: [],
        },
        'ts': [],
        'interpolate': False,
    },
}

import re
data_pattern = re.compile(r'(\d*),(\d*),(\d*)')

import numpy as np
import csv
for seri in series.values():
    with open(seri['file']) as fil:
        for line in fil:
            m = data_pattern.match(line)
            if m:
                mem, chunks, time = map(int, m.groups())
                seri['params'][0].append(np.log2(mem))
                seri['params'][1].append(np.log2(chunks))
                seri['ts'].append(np.log10(time))

###############################################################################
# Compute differences
###############################################################################

import common
import graph_2d
graph_2d.prepare_data(series)

series['diff'] = {
    'color': 'black',
    'label': 'linux - nautk',
    'params': {
        0: series['linux']['params'][0],
        1: series['linux']['params'][1],
    },
    'ts': series['linux']['mean_ts'] - series['nautk']['mean_ts'],
    'std': np.sqrt(series['linux']['std_ts']**2 + series['nautk']['std_ts']**2),
    'interpolate': False,
    'fmin': lambda data: -np.max(np.fabs(data[~np.isnan(data)])),
    'fmax': lambda data: +np.max(np.fabs(data[~np.isnan(data)])),
}

labels = {0: 'mem', 1: 'chunks'}
graph_2d.prepare_data(series)
params = graph_2d.mk_params(series, labels)

###############################################################################
# Plot customizations
###############################################################################

import matplotlib.pyplot as plt
cbar = graph_2d.export_img(series['diff'], params)

plt.yticks([20, 25, 30], ['1Mb', '32Mb', '1Gb'])
plt.xticks([0, 5, 10, 15], ['$2^0$\n1', '$2^5$\n32', '$2^{10}$\n1024', '$2^{15}$\n32768'])
cbar.set_ticks([-1, 0, 1])
cbar.set_ticklabels(['Linux 10x\nfaster', 'parity', 'Nautilus 10x\nfaster'])
plt.ylabel('total size')
plt.title('malloc runtime in Linux vs Nautilus')

plt.savefig('malloc.png', bbox_inches='tight')

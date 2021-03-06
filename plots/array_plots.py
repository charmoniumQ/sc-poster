#!/usr/bin/env python3
import os
import sys
os.chdir(os.path.dirname(sys.argv[0]))

import csv
import common
import matplotlib.pyplot as plt
import numpy as np
import re
import os

version = 'array2'

data_file_names = {'linux': f'linux{version}.csv', 'nautk': f'nautk{version}.csv'}

plots = {}
headers = {}

def is_int(x):
    try:
        int(x)
    except ValueError:
        return False
    else:
        return True

for this_os, data_file_name in data_file_names.items():
    title = None
    with open(data_file_name) as data_file:
        this_data = csv.reader(data_file)
        for row in this_data:
            if row[-1] == 'title row':
                title = row[-2]
                header_row = row[:-2]
                if title not in plots:
                    plots[title] = {}
                plots[title][this_os] = [[] for col in header_row]
                headers[title] = header_row
            else:
                for col_no, data in enumerate(row):
                    if data:
                        try:
                            data = int(data)
                        except ValueError as e:
                            print(this_os)
                            print(header_row)
                            print(row)
                            raise e
                        if col_no >= len(plots[title][this_os]):
                            print(f'{col_no} for {title} ({this_os}) not defined')
                            print(list(enumerate(header_row)))
                        plots[title][this_os][col_no].append(data)

for title in plots.keys():
    for this_os in plots[title].keys():
        for col_no in range(len(plots[title][this_os])):
            plots[title][this_os][col_no] = np.array(plots[title][this_os][col_no])

def deduplicate(xs, ys):
    unique_xs = sorted(list(set(xs)))
    means = []
    stds = []
    for x in unique_xs:
        means.append(ys[xs == x].mean())
        stds.append(ys[xs == x].std())
    return np.array(unique_xs), np.array(means), np.array(stds)

colors = {'linux': 'r', 'nautk': 'b'}

for plot_no, plot_title in enumerate(sorted(plots.keys())):
    header_row = headers[plot_title]
    n_columns = len(list(plots[plot_title].values())[0])

    for col_no in range(n_columns):
        if col_no == 0:
            continue

        plt.figure(figsize=(9, 6))
        col_title = header_row[col_no]
        #title_addendum = f'({version}:{plot_no}:{col_no})'
        title_addendum = ''
        if col_title:
            plt.title(f'{plot_title} {col_title} {title_addendum}')
        else:
            plt.title(f'{plot_title} {title_addendum}')

        plt.xlabel(header_row[0])

        for this_os in plots[plot_title].keys():

            xs = plots[plot_title][this_os][0]
            ys = plots[plot_title][this_os][col_no]

            xs, means, stds = deduplicate(xs, ys)
            if this_os == 'linux':
                base_means = means
            else:
                factors = means / base_means
                for x, factor, mean in list(zip(xs, factors, means))[1::2]:
                    plt.text(x, mean, s=f'{factor:.1f}x')
                print(f'{version}:{plot_no}:{col_no} {this_os} {x} {mean:.0f} ({factor:.1f}x)')

            plt.plot(xs, means, color=colors[this_os])
            plt.fill_between(xs,
                             np.clip(means - stds, 1, None),
                             np.clip(means + stds, 1, None),
                             color=colors[this_os], alpha=0.5, label=fr"{this_os}'s time $\pm$ std. dev.")

        plt.legend(loc='upper left')
        plt.ylabel('time (cycles)')
        sanitized_col_title = (col_title.replace('(', '').replace(')', '').replace(' ', '_'))
        plt.savefig(f'{plot_title}_{sanitized_col_title}.png')
        print(f'{plot_title}_{sanitized_col_title}.png')

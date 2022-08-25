import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from matplotlib.ticker import StrMethodFormatter

#author: barry giesbrecht
#initial version date: aug 2, 2022
#for each lit search, get the files, read them in and concatenate into one big data frame
#search dir: directory with all the WoS searches. current version of the script assumes WoS searches are stored in a particular directory.
search_dir = "wos-searches"

#list_search_files = '*OSC*.txt'
#fig_title = '2000-2021 Oscillation Publications'
list_search_files = ["ERP","OSC","PC","MOBILE"]
fig_title = '2000-2021 EEG + Topic Publications'

#if you want to pass the file list and figure title as arguments comment lines 12-13 and uncomment these ones
#list_search_files = str(sys.argv[1])
#fig_title = str(sys.argv[2])

all_yearly_pubs = {}

#loop through each search
search_ctr = 0
for search in list_search_files:
    this_search_str = search_dir + "/*" + list_search_files[search_ctr] + "*.txt"

    these_files = glob.glob(this_search_str)

    i=0
    for file in these_files:

        if i==0:
            #first time through, dump data into master_search_table
            #files were stored as tab delimited
            master_search_table = pd.read_csv(file,sep='\t')
        else:
            #all other times, concatenate the new file with the master data frame
            master_search_table = pd.concat([master_search_table,pd.read_csv(file,sep='\t')])

        i=i+1

    #select years 2000-2021
    master_search_table = master_search_table[((master_search_table['PY']>1999) & (master_search_table['PY']<2022))]

    #get unique values and counts and store in new dataframe with two columns, one for year and one for unique counts.
    yearly_pubs = master_search_table.PY.value_counts().rename_axis('year').reset_index(name='counts')

    #sort
    yearly_pubs = yearly_pubs.sort_values("year")
    yearly_pubs["year"] = yearly_pubs["year"].astype(int)
    plt.plot(yearly_pubs.year, yearly_pubs.counts)

    
#   all_yearly_pubs[search_ctr]= yearly_pubs
    all_yearly_pubs[list_search_files[search_ctr]]= yearly_pubs

    search_ctr = search_ctr + 1
    #end search loop

#if totall eeg records are desirded, then uncomment this code
# eeg_count_file = "raweeg_counts.csv"
#tmp = pd.read_csv(eeg_count_file)
#plt.plot(tmp.Year, tmp.EEG)

#plot
#plt.plot(yearly_pubs.year, yearly_pubs.counts)
plt.ylabel('pub count')
plt.xlabel('year')
plt.gca().xaxis.set_major_formatter(StrMethodFormatter('{x:.0f}'))
plt.title(fig_title)
plt.legend(list_search_files)
plt.show()
#plt.savefig('erpPubs.pdf')
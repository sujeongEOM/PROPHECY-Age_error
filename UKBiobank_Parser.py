import time, os
from glob import glob
import xmltodict
import traceback
import numpy as np
import pandas as pd

import multiprocessing as mp
import parmap

from UKBiobankXMLParser import UKBiobankXMLParser, xml_parsing

#set variables
base_dir = '/home/ubuntu/uk-biobank-ecg_mount'
wave_save_dir = os.path.join(base_dir, '220408_uk-biobank-ecg_waveform')

uk_1_list = glob(os.path.join(base_dir, 'UKB_ECG_1st_20205_2_0_bulk_data/*.xml'))
uk_2_list = glob(os.path.join(base_dir, 'UKB_ECG_2nd_20205_3_0_bulk_data/*.xml'))
xml_list = uk_1_list + uk_2_list

def parallel_dataframe(xml_list, func, wave_save_dir, num_cores):
    xml_list_split = np.array_split(xml_list, num_cores)
    df = parmap.map(func, xml_list_split, wave_save_dir, pm_pbar=True, pm_processes=num_cores)
    return df

def main(num_cores=os.cpu_count()):
    start = int(time.time())
    
    uk_xml = np.array_split(xml_list, 10) #45610 to 4561 at one process
    df_list = []
    
    for x in uk_xml: #len(x) = 4561
        df = parallel_dataframe(x, xml_parsing, wave_save_dir, num_cores)    
        try:
            df_concat = pd.concat(df, ignore_index=True)
            df_list.append(df_concat)
        except:
            print(traceback.print_exc())
    
    master_df = pd.concat(df_list, ignore_index=True)
    master_df.to_csv(os.path.join(base_dir, '220408_uk-biobank-ecg_label.csv'), index=False)        

    print('df done')
        
    print("***run time(sec) :", int(time.time()) - start)

if __name__ == "__main__":
    main()
import time, os
from glob import glob
import xmltodict
import traceback
import numpy as np
import pandas as pd

class UKBiobankXMLParser :
    def __init__(self,path):
        try :
            with open(path, 'rb') as xml_original:
                self.xml_dic = xmltodict.parse(xml_original.read().decode('cp949'))['CardiologyXML']
            self.__ObservationType = self.xml_dic.get('ObservationType') #RestECG
            self.__ObservationDateTime = self.xml_dic.get('ObservationDateTime')
            self.__PatientInfo = self.xml_dic.get('PatientInfo')
            self.__Interpretation = self.xml_dic.get('Interpretation')
            self.__StripData = self.xml_dic.get('StripData')
        except :
            print(traceback.print_exc())

    def ObservationType_parser(self):
        ObservType = self.__ObservationType

        assert ObservType == 'RestECG', 'Not RestECG'
        
        return {'ObservationType': ObservType}

    def ObservationDateTime_parser(self):
        ObservYear = self.__ObservationDateTime.get('Year')
        ObservMonth = self.__ObservationDateTime.get('Month')
        ObservDay = self.__ObservationDateTime.get('Day')
        ObservDate = f'{ObservYear}-{ObservMonth}-{ObservDay}'
        return {'ObservationDate': ObservDate, 'ObservationYear':ObservYear}


    def PatientInfo_parser(self):
        PtID = self.__PatientInfo.get('PID')
        PtAge = self.__PatientInfo.get('Age').get('#text')
        PtBirthYear = self.__PatientInfo.get('BirthDateTime').get('Year')
        PtGender = self.__PatientInfo.get('Gender')
        return {'PatientID': PtID, 'PatientAge':PtAge, "BirthYear":PtBirthYear, "Gender":PtGender}

    def Interpretation_parser(self):
        try: Diagnosis = self.__Interpretation.get('Diagnosis')
        except: Diagnosis = None
        try: 
            Conclusion = self.__Interpretation.get('Conclusion')
            dx = []
            try: 
                for i in Conclusion:
                    dx.append(i['ConclusionText'])
            except:
                dx.append(Conclusion['ConclusionText'])
        except: 
            Conclusion = None
            dx = None

        return {'Diagnosis': dx}
    
    def StripData_parser(self):
        NumberOfLeads = self.__StripData.get('NumberOfLeads')
        SampleRate = self.__StripData.get('SampleRate').get('#text')
        ChannelSampleCountTotal = self.__StripData.get('ChannelSampleCountTotal')
        
        Lead_waveforms = {}
        for i in self.__StripData['WaveformData'] :
            lead_data = i['#text']
            lead_data = lead_data.replace('\n\t\t', '')
            lead_data = lead_data.split(',')
            Lead_waveforms[i['@lead']]= lead_data
            
        return {'NumberOfLeads':NumberOfLeads, 'SampleRate':SampleRate, 'ChannelSampleCountTotal':ChannelSampleCountTotal, 'WaveformData':Lead_waveforms}


def xml_parsing(xml_list, wave_save_dir):
    print(len(xml_list))
    master_df = pd.DataFrame()
    try:
        for f in xml_list:
            f = str(f)
            fname = f.split('/')[-1].split('.')[0]
            
            # label table
            parser = UKBiobankXMLParser(f)
            
            ob_type = parser.ObservationType_parser()
            ob_date= parser.ObservationDateTime_parser()
            pt_info = parser.PatientInfo_parser()
            dx = parser.Interpretation_parser()
            waveform = parser.StripData_parser()
            
            pt_info.update(ob_date)
            pt_info.update(dx)
            pt_info.update({'FileName':fname})
            
            df = pd.DataFrame.from_dict([pt_info])
            
            master_df = pd.concat([master_df, df], ignore_index=True)
            
            # waverform data (to single csv file)
            df_wave = pd.DataFrame.from_dict(waveform['WaveformData'])
            df_wave.to_csv(os.path.join(wave_save_dir, f'{fname}.csv'), index=False)
    except Exception as Argument:
        file = open('bug.txt', 'a')
        file.write(f'{f} : {str(Argument)} \n')
        print(f'{f} : {str(Argument)} \n')
        f.close()

    return master_df
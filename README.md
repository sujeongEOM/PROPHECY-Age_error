# PROPHECY-Age
project start on 2022.03	   
  
     
     
# Process of EKG projects
1. Extracting waveform, label table from XML or tsv; parsing and decoding
2. Data preprocessing (check waveform shape, label null etc.)
3. Model train, test
  
  
## 1. Extraction difference with Dataset
> 1. Sev MUSE EKG tsv (Train / Internal Validation)
-- Whole data in huge single tsv file (220GB)
- Each row equals one EKG file
- There are pt overlap (as single pt takes many EKGs)
- Label Table : Whole tsv file saved in csv only with WaveformData column deleted
- Waveform : WaveformData column needs base64 decoding; decoded and saved into a single csv file  



> 2. UK Biobank (External Validation)
- XML data
- Need to parse each XML file
- Single XML file equals one EKG file
- Parsing function on branch _**UK Biobank**_



## 2. Data Preprocessing


## 3. Model Train, Test
- Data Generator
- 1D CNN model (Ribeiro, Attia etc.)
- Test values : MSE, MAE, r2 score

from pickle import FALSE
import eel
from hrvanalysis import get_time_domain_features, get_frequency_domain_features, get_csi_cvi_features, get_sampen, get_poincare_plot_features
from scipy.signal import argrelextrema
import tkinter 
from tkinter import messagebox
from tkinter import filedialog
import pandas as pd
import numpy as np
import os, math
import json
from collections import deque
from kafka import KafkaConsumer
import scipy.signal as sg
import threading
import os
import csv
import matplotlib.pyplot as plt

base_path = os.path.abspath(".")
base_path = os.path.join(base_path, 'web')
eel.init(base_path)

class Test:
    def __init__(self):
        self.data = None
        self.first_curve = None
        self.second_curve = None
        self.thread = False
        self.II = deque([])
        self.PLETH = deque([], maxlen=500)
        self.RESP = deque([], maxlen=500)   
    def update_var(self, x):
        self.data = x
    def update_first_curve(self, x):
        self.first_curve = x
    def update_second_curve(self, x):
        self.second_curve = x
    def get_first_curve(self):
        return self.first_curve
    def get_second_curve(self):
        return self.second_curve
    def get_dataset(self):
        return self.data
    def stop_thread_state(self):
        return self.thread
    def stop_thread(self):
        self.thread = True
    def split_data(self, size):
        self.size = size
        self.k = int(len(self.data) / self.size) + 1
    def get_II(self):
        result = list(self.II)
        return result
    def get_PLETH(self):
        result = list(self.PLETH)
        return result
    def get_RESP(self):
        result = list(self.RESP)
        return result
    def add_II(self,value):
        self.II.append(value)
    def add_PLETH(self,value):
        self.PLETH.append(value)
    def add_RESP(self,value):
        self.RESP.append(value)
    def clear_II(self):
        self.II.clear()
    def clear_PLETH(self):
        self.PLETH.clear()
    def clear_RESP(self):
        self.RESP.clear()



file = Test()

@eel.expose
def selectFolder(nrow, choosefile):
    root = tkinter.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    ecg_datas = []
    temp_II=[]
    temp_Pleth=[]
    temp_Resp=[]
    n_row = int(nrow)
    file.clear_II()
    file.clear_PLETH()
    file.clear_RESP()
    
    if choosefile == True:
        
        directory_path = filedialog.askopenfilename(
        filetypes=(("CSV files", "*.csv"), ("Excel files", "*.xlsx") ),
        title='Select ONM file'
        )

        print('waiting')
        file.update_var(directory_path)
        df_read=pd.read_csv(directory_path)
        df_col=df_read.columns
        df_col=df_col.to_list()
        for i in range(0,len(df_col),1):
            if(df_col[i]=="II/" or df_col[i]=="L2"):
                df_col[i]="II"
        df_len = df_read.shape[0]
        for i in range(100):
            first_index = i*n_row
            if first_index + n_row > df_len:
                n_row = df_len - first_index
                ecg = pd.read_csv(directory_path, skiprows=first_index, nrows=n_row)
                ecg.columns = df_col
                file.add_II(ecg['II'])
                ecg_datas.append(ecg.to_json(orient="records"))
                break
                # pandas.errors.EmptyDataError: No columns to parse from file
            else:
                ecg = pd.read_csv(directory_path, skiprows=first_index, nrows=n_row)
                # ecg.columns = ["II", "ABP", "PLETH", "RESP"]
                ecg.columns = df_col
                file.add_II(ecg['II'])
                ecg_datas.append(ecg.to_json(orient="records"))
        # 搬移中
        ii = file.get_II()
        flat_list = []
        for sublist in ii:
            for item in sublist:
                flat_list.append(item)
        rawData = np.array(flat_list)
        print('ii')
        print(len(rawData))

         # =======新增中=============
        sampling_rate = 1000
        baseline = sg.medfilt(sg.medfilt(rawData, int(0.2 * sampling_rate) - 1), int(0.6 * sampling_rate) - 1)
        print(baseline)
        midData = rawData - baseline
        mid_interval=midData.tolist()


        #低通和高通滤波
        b, a =sg.butter(8, 0.3,'lowpass')
        ecg_1 = sg.filtfilt(b, a,mid_interval) 
        
        b, a = sg.butter(8, 0.007,'highpass')   #配置滤波器 8 表示滤波器的阶数
        hl_interval = sg.filtfilt(b, a, ecg_1)  #data为要过滤的信号

        # b, a = sg.butter(8, 0.002,'highpass')   
        # hl_1_interval = sg.filtfilt(b, a, ecg_1)  

        # b, a = sg.butter(8, 0.003,'highpass')   
        # hl_15_interval = sg.filtfilt(b, a, ecg_1) 
        
        # b, a = sg.butter(8, 0.004,'highpass')   
        # hl_2_interval = sg.filtfilt(b, a, ecg_1) 

        # b, a = sg.butter(8, 0.005,'highpass')   
        # hl_25_interval = sg.filtfilt(b, a, ecg_1) 

        # b, a = sg.butter(8, 0.006,'highpass')   
        # hl_3_interval = sg.filtfilt(b, a, ecg_1) 

        # b, a = sg.butter(8, 0.007,'highpass')   
        # hl_35_interval = sg.filtfilt(b, a, ecg_1) 

        # b, a = sg.butter(8, 0.008,'highpass')   
        # hl_4_interval = sg.filtfilt(b, a, ecg_1) 

        # b, a = sg.butter(8, 0.009,'highpass')   
        # hl_45_interval = sg.filtfilt(b, a, ecg_1) 

        # b, a = sg.butter(8, 0.0001,'highpass')   
        # hl_5_interval = sg.filtfilt(b, a, ecg_1) 
        

        plt.figure(figsize=(20,4))
        plt.subplot(6,1,1)
        plt.plot(flat_list)
        plt.title("RAW")
        plt.subplot(6,1,3)
        plt.plot(ecg_1)
        plt.title("Before Median filter")
        plt.subplot(6,1,5)
        plt.plot(hl_interval)
        plt.title("Before Median filter+High & Low Pass")
        # plt.subplot(8,1,5)
        # plt.plot(hl_4_interval)
        # plt.title("Before Median filter+High 4&Low Pass")
        # plt.subplot(8,1,7)
        # plt.plot(hl_45_interval)
        # plt.title("Before Median filter+High 4.5&Low Pass")
        # plt.subplot(6,1,3)
        # plt.plot(mid_interval)
        # plt.title("Before Median filter")
        
        plt.show()

        # =======新增中=============
        
        # =======施工中=============
        peaks = argrelextrema(midData, np.greater)[0]
        print(peaks)
        # filter
        var1, var2 = np.percentile(midData[peaks], (50, 75))
        bound = (var1+ var2) / 2
        peaks = [index for index, value in zip(peaks, midData[peaks]) if value >= bound]
            # create rr interval
        raw_rr_interval = []
        for i in range(len(peaks)):
            if i == len(peaks)-1:
                continue
            raw_rr_interval.append(peaks[i+1] - peaks[i])
        print("!!")
        print(len(raw_rr_interval))
        # =======施工中=============
        if len(raw_rr_interval) > 2:
            time_domain_features = get_time_domain_features(raw_rr_interval)
            frequency_domain_features = get_frequency_domain_features(raw_rr_interval)
            non_Linear1 = get_csi_cvi_features(raw_rr_interval)
            non_Linear2 = get_sampen(raw_rr_interval)
            non_Linear3 = get_poincare_plot_features(raw_rr_interval)

            # print(time_domain_features)
            # print(frequency_domain_features)
            # print(non_Linear1)
            # print(non_Linear2)
            # print(non_Linear3)
            
            for key, value in time_domain_features.items():
                if np.isinf(value) or np.isnan(value):
                    time_domain_features[key] = str(value)
                    continue
                value = math.floor(value * 100) / 100.0
                time_domain_features[key] = str(value)
            for key, value in frequency_domain_features.items():
                if np.isinf(value) or np.isnan(value):
                    frequency_domain_features[key] = str(value)
                    continue
                value = math.floor(value * 100) / 100.0
                frequency_domain_features[key] = str(value)
            for key, value in non_Linear1.items():
                if np.isinf(value) or np.isnan(value):
                    non_Linear1[key] = str(value)
                    continue
                value = math.floor(value * 100) / 100.0
                non_Linear1[key] = str(value)
            for key, value in non_Linear2.items():
                if np.isinf(value) or np.isnan(value):
                    non_Linear2[key] = str(value)
                    continue
                value = math.floor(value * 100) / 100.0
                non_Linear2[key] = str(value)
            for key, value in non_Linear3.items():
                if np.isinf(value) or np.isnan(value):
                    non_Linear3[key] = str(value)
                    continue
                value = math.floor(value * 100) / 100.0
                non_Linear3[key] = str(value)
           

        # 搬移中
        ecg_datas = json.dumps(
            {"ecg": ecg_datas,
             "time_domain_features" : {**time_domain_features},
            "frequency_domain_features" : {**frequency_domain_features},
            "non_Linear": {**non_Linear1, **non_Linear2, **non_Linear3}
             })
        print('complete')
        root.destroy()
        return ecg_datas
    # except:
        # messagebox.showinfo("警告", "沒有選擇指定檔案")
        # root.destroy()
    else:
        print('waiting')
        directory_path = file.get_dataset()
        df_read=pd.read_csv(directory_path)
        df_col=df_read.columns
        df_col=df_col.to_list()
        for i in range(0,len(df_col),1):
            if(df_col[i]=="II/" or df_col[i]=="L2"):
                df_col[i]="II"
        df_len = df_read.shape[0]
        for i in range(100):
            first_index = i*n_row
            if first_index + n_row > df_len:
                n_row = df_len - first_index
                ecg = pd.read_csv(directory_path, skiprows=first_index, nrows=n_row)
                ecg.columns = df_col
                ecg_datas.append(ecg.to_json(orient="records"))
                break
                # pandas.errors.EmptyDataError: No columns to parse from file
            else:
                ecg = pd.read_csv(directory_path, skiprows=first_index, nrows=n_row)
                ecg.columns = df_col
                ecg_datas.append(ecg.to_json(orient="records"))
        ecg_datas = json.dumps({"ecg": ecg_datas})
        print('complete')
        root.destroy()
        return ecg_datas
    
@eel.expose
def write_csv(data):

    if os.path.exists("generate_data\\outputData.csv"):
        try:
            with open("generate_data\\outputData.csv",mode='a',encoding='utf-8',newline='')as csvFile:
                writeCSV=csv.writer(csvFile)
                writeCSV.writerow(data)
                csvFile.close()
                return f'success'
        except:
            return f'fail'
    else:
        heads=['patientID','mean_nni','sdnn','sdsd','nni_50','pnni_50','nni_20','pnni_20','rmssd','median_nni','range_nni',
        'cvsd','cvnni','mean_hr','max_hr','min_hr','std_hr','lf','hf','lf_hf_ratio','lfnu','hfnu','total_power',
        'vlf','csi','cvi','Modified_csi','sampen','sd1','sd2','ratio_sd2_sd1']
        try:
            with open("generate_data\\outputData.csv",mode='w',encoding='utf-8',newline='')as csvFile:
                writeCSV=csv.writer(csvFile)
                writeCSV.writerow(heads)
                writeCSV.writerow(data)
                csvFile.close()
                return f'success'
        except:
            return f'fail'



@eel.expose
def start_realtime():
    ii = file.get_II()
    pleth = file.get_PLETH()
    resp = file.get_RESP()
    tmp = np.array(ii)
    print('ii')
    print(tmp)
    peaks = argrelextrema(tmp, np.greater)[0]
    # print(peaks)
    # filter
    var1, var2 = np.percentile(tmp[peaks], (50, 75))
    bound = (var1+ var2) / 2
    peaks = [index for index, value in zip(peaks, tmp[peaks]) if value >= bound]
    # create rr interval
    rr_interval = []
    for i in range(len(peaks)):
        if i == len(peaks)-1:
            continue
        rr_interval.append(peaks[i+1] - peaks[i])
    # rr_interval長度必須大於等於2
    if len(rr_interval) > 2:
        time_domain_features = get_time_domain_features(rr_interval)
        frequency_domain_features = get_frequency_domain_features(rr_interval)
        non_Linear1 = get_csi_cvi_features(rr_interval)
        non_Linear2 = get_sampen(rr_interval)
        non_Linear3 = get_poincare_plot_features(rr_interval)
        for key, value in time_domain_features.items():
            if np.isinf(value) or np.isnan(value):
                time_domain_features[key] = str(value)
                continue
            value = math.floor(value * 100) / 100.0
            time_domain_features[key] = str(value)
        for key, value in frequency_domain_features.items():
            if np.isinf(value) or np.isnan(value):
                frequency_domain_features[key] = str(value)
                continue
            value = math.floor(value * 100) / 100.0
            frequency_domain_features[key] = str(value)
        for key, value in non_Linear1.items():
            if np.isinf(value) or np.isnan(value):
                non_Linear1[key] = str(value)
                continue
            value = math.floor(value * 100) / 100.0
            non_Linear1[key] = str(value)
        for key, value in non_Linear2.items():
            if np.isinf(value) or np.isnan(value):
                non_Linear2[key] = str(value)
                continue
            value = math.floor(value * 100) / 100.0
            non_Linear2[key] = str(value)
        for key, value in non_Linear3.items():
            if np.isinf(value) or np.isnan(value):
                non_Linear3[key] = str(value)
                continue
            value = math.floor(value * 100) / 100.0
            non_Linear3[key] = str(value)
        
        return_obj = json.dumps({
            'ecg' : ii, 
            'pleth' : pleth,
            'resp' : resp,
            'time_domain_features' : {**time_domain_features},
            'frequency_domain_features' : {**frequency_domain_features},
            'non_Linear': {**non_Linear1, **non_Linear2, **non_Linear3}
        })
        return return_obj

    return_obj = json.dumps({
    'ecg': ii, 
    'time_domain_features': None, 
    'frequency_domain_features': None,
    'non_Linear': None
    })

    return return_obj

eel.start('main.html', mode='chrome')


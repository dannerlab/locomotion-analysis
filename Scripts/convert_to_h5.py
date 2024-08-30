#from Locoproc under GNU Lesser Public License
#Modifications made 8/13/2024 L. Schoenhals

import pandas as pd
import numpy as np
import neo.rawio
import scipy.io as scio
from optparse import OptionParser
import yaml
import os
import IPython

emgs = ['Left_TA','TA','LG','Left_GS','Right_TA','Right TA','Left GS','Right VL','GS','IP','ST','oTA', 'oST', 'oGS', 'oVL', 'oBF']

file_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(file_path,"naming.yaml"),'r') as f:
    naming = yaml.load(f,Loader=yaml.FullLoader)

trans = naming['kinematics']
trans2 = trans
for k in trans2.keys():
    trans2[k].append(k)

trans2 = {v:k for k,vs in trans2.items() for v in vs}

def load_spike2(fn):
    reader = neo.rawio.Spike2RawIO(filename=fn,ced_units=False,try_signal_grouping=False)
    reader.parse_header()

    def get_channel(i):
        sig = reader.get_analogsignal_chunk(stream_index=i)
        dt = reader.header['signal_channels'][i][3]
        #print(dt)
        if dt =='int32':
            sig = np.frombuffer(sig.tobytes(),dtype='float32')
        if dt =='int16':
            sig = sig.astype(np.float32)/6553.6
        return sig

    #print(reader.header['signal_channels'])
    ch_names=[c[0] for c in reader.header['signal_channels'] ]
    ev_ch_names=[c[0] for c in reader.header['event_channels'] ]
    print(ev_ch_names)
    print(ch_names)

    size = 9999999999999999999
    for key in trans2.keys():
        if key in ch_names:
            sr = reader.header['signal_channels'][ch_names.index(key)][2]
            t_start = reader._get_signal_t_start(block_index=0, seg_index=0,stream_index=ch_names.index(key))
            size_ = reader._get_signal_size(block_index=0, seg_index=0,stream_index=ch_names.index(key))
            if size_ < size:
                size = size_

    df_kinematics = pd.DataFrame({})
    df_kinematics['time'] = t_start+np.arange(size)/sr
    for k in list(ch_names):
        if k in trans2:
            #ADD CHECKS TO MAKE SURE SIGNALS ARE SYNCHRONIZED
            df_kinematics[trans2[k]] = get_channel(ch_names.index(k))[:size]
    size_emg = 9999999999999999999
    for e in emgs:
        if e in ch_names:
            sr_emg = reader.header['signal_channels'][ch_names.index(e)][2]
            t_start_emg = reader.get_signal_t_start(stream_index=ch_names.index(e),block_index=0, seg_index=0)
            size_emg_ = reader.get_signal_size(stream_index=ch_names.index(e),block_index=0, seg_index=0)
            #### MAKE SURE ALL CHANNELS START AT THE SAME; IF NOT PICK THE EARIEST TIME ALL CHANNELS ARE PRESENT
            if size_emg_ < size_emg:
                size_emg = size_emg_

    df_emg = pd.DataFrame({})
    df_emg['time'] = t_start_emg+np.arange(size_emg)/sr_emg
    for ch in ch_names:
        #if ch in ['Treadmill','Current']:
        #    continue
        if reader.header['signal_channels'][ch_names.index(ch)][2] == sr_emg:
            sz = reader.get_signal_size(stream_index=ch_names.index(ch),block_index=0, seg_index=0)
            sig = get_channel(ch_names.index(ch))
            if sig.shape[0]>size_emg:
                sig=sig[0:size_emg]
            if sig.shape[0]==df_emg.time.shape[0]:
                df_emg[ch] = sig
            else:
                print("channel "+ ch + " " + str(ch_names.index(ch)) + " not loaded")


    df_emg = df_emg[(df_emg.time >= df_kinematics.time.iloc[0])&(df_emg.time <= df_kinematics.time.iloc[-1])]

    ev_chs={}
    for ch in ev_ch_names:
        print(ch)
        tst, dur, labels= reader.get_event_timestamps(event_channel_index=ev_ch_names.index(ch))
        tst=tst/5e5
        tst-=t_start
        labels = labels.astype(dtype="<U11")
        labels[labels == ""] = '32'
        #import IPython;IPython.embed()
        ev=list(zip([chr(int(x)) for x in labels],tst))
        in_=np.where(np.diff([e[1] for e in ev])>1.5)[0]

        in_=np.append(0,in_+1)
        ins_=[(s,e) for s,e in zip(np.append(in_,len(ev)-1),np.append(in_[1:],[len(ev)-1,len(ev)]))]

        ev_out=[]

        for in_ in ins_:
            if -1 in in_:
                continue
            ev_out.append(("".join([e[0] for e in ev[in_[0]:in_[1]]]),ev[in_[0]][1]))

        # change ev to ev_out for better formatting of the events. doesn't work well always though
        ev_chs[ch]=ev
        #ev_chs[ch]=ev_out
    return df_kinematics, df_emg, ev_chs

def load_matfile(fn):
    file = scio.loadmat(fn)

    df_kinematics = pd.DataFrame({})
    if 'Crx__cm_' not in file:
        print('no kinematics',fn)
        return 0,0
    interval = file['Crx__cm_']['interval'][0][0][0][0]
    len_ = file['Crx__cm_']['values'][0][0].shape[0]
    if len_==0:
        print('dur\t',0,'\t',fn)
        return 0,0
    df_kinematics['time'] = np.arange(len_)*interval
    if len_*interval<5.0:
        print('dur\t',len_*interval,'\t',fn)

    for k in list(file.keys()):
        if k in trans:
            df_kinematics[trans[k]]=file[k]['values'][0][0]
            if interval!=file[k]['interval'][0][0][0][0]:
                print('interval differs in ',k,trans[k])
        elif k in [it[1] for it in trans.items()]:
            df_kinematics[k]=file[k]['values'][0][0]
            if interval!=file[k]['interval'][0][0][0][0]:
                print('interval differs in ',k)
        else:
            print(k,'missing')
    df_emg = pd.DataFrame({})

    for e in emgs:
        if e in file.keys():
            interval_emg = file[e]['interval'][0][0][0][0]
            len_ = file[e]['values'][0][0].shape[0]
            break

    df_emg['time'] = np.arange(len_)*interval_emg
    for k in list(file.keys()):
        if isinstance(file[k],np.ndarray):
            if 'interval' in file[k].dtype.names:
                if interval_emg==file[k]['interval'][0][0][0][0]:
                    df_emg[k]=file[k]['values'][0][0]
                    #print('loaded emg',k)
    return df_kinematics, df_emg

def save_h5(fn,df_kinematics, df_emg):
    print('kinematic channels',df_kinematics.columns.values)
    print('====')
    print('\tmissing kinematic values',{v for v in trans.keys()}-{v for v in df_kinematics.columns.values})
    print('====')
    print('EMG channels',df_emg.columns.values)
    df_kinematics.to_hdf(fn, key='df_kinematics', mode='w',complevel=9)
    df_emg.to_hdf(fn, key='df_emg',complevel=9)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--filename", dest="filename",default='',
              help="SMR file to be converted", metavar="FILE")
    parser.add_option("-u", "--units_han", dest="convert_units",action="store_true",default=False,
              help="convert units to mm and degrees (from dm and radians)")
    options, args = parser.parse_args()

    file_ending = options.filename.split('.')[-1]
    parent_folder = os.path.dirname(os.path.dirname(options.filename)) #locomotion-analysis/Sample_data/V3Off_Levelwalk/smr/gp3m4_1.smr
    save_folder = os.path.join(parent_folder, "h5")
    if not os.path.exists(save_folder):
        os.makedirs(save_folder, exist_ok=True)
    save_name = os.path.join(save_folder, os.path.split(options.filename)[-1][:-4] +'.h5')

    if file_ending == 'smr':
        df_kinematics, df_emg, ev_chs = load_spike2(options.filename)

        ev_chs_toe_touch = []
        ev_chs_toe_off = []
        df_ev_chs = pd.DataFrame()
        if ('toetouch' in ev_chs.keys()) and ('toeoff' in ev_chs.keys()):
            for event in ev_chs['toetouch']: #'toetouch' should be changed so that it can update based on naming
                ev_chs_toe_touch.append(event[1])
            for event in ev_chs['toeoff']: #same thing for 'toeoff'
                ev_chs_toe_off.append(event[1])

            #pad lists to same length so they can be DFs
            max_len = max(len(ev_chs_toe_touch), len(ev_chs_toe_off))
            ev_chs_toe_touch += [None] * (max_len - len(ev_chs_toe_touch))
            ev_chs_toe_off += [None] * (max_len - len(ev_chs_toe_off))

            df_ev_chs = pd.DataFrame({
                'stance': ev_chs_toe_touch, #note: to work w/ locoproc as phase file, these must be called stance & swing
                'swing': ev_chs_toe_off
            })

        if options.convert_units:
            print('converting units to mm and degrees (from dm and radians)')
            for col in df_kinematics.columns.values:
                if "angle" in col:
                    df_kinematics[col] = df_kinematics[col]*180/np.pi
                if any(st in col for st in ['_x','_y']):
                    df_kinematics[col] = df_kinematics[col]*100
            if "Knee_x" not in df_kinematics.columns.values:
                df_kinematics["Knee_x"] = 0.
                df_kinematics["Knee_y"] = 0.

        # sort columns - stick figure plotting somehow depends on the correct sequence, this fixes it
        tcols = ['time', 'Hip_angle', 'Knee_angle', 'Ankle_angle', 'MTP_angle',
                 'IliacCrest_x', 'IliacCrest_y',
                 'Hip_x', 'Hip_y',
                 'Knee_x', 'Knee_y',
                 'Ankle_x', 'Ankle_y',
                 'Metatarsal_x', 'Metatarsal_y',
                 'ToeTip_x', 'ToeTip_y']
        tcols = tcols + list(set(df_kinematics.columns)-set(tcols))
        columns = []
        for v in tcols:
            if v in df_kinematics.columns.values:
                columns.append(v)
        df_kinematics = df_kinematics[columns]

        #print(df_kinematics)
        #print(df_emg)
        save_h5(save_name, df_kinematics, df_emg)
        if not df_ev_chs.empty:
            df_ev_chs.to_csv(options.filename[:-4] + '.phase', index=False)

    if file_ending == 'mat':
        try:
               df_kinematics, df_emg = load_matfile(options.filename)
        except:
            print('Filetype cannot be read as of now - will implement soon')
            exit()
        save_h5(save_name,df_kinematics,df_emg)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import json


class DataRetriever:
  ts_thresholds = {}

  def __init__(self):
    self.data_url = 'https://timeseriesvisual.firebaseio.com'

  def RetrieveRawData(self, data_name='/raw'):
    response = requests.get(self.data_url + data_name + '.json')
    raw_data = json.loads(response.text)
    
    start_time = self.ts_thresholds.setdefault(data_name, 0)
    raw_data = sorted([(obj['timestamp'], obj['data']) for obj in raw_data
                       if obj['timestamp'] > start_time])
    if raw_data:
      self.ts_thresholds[data_name] = raw_data[-1][0]
      return raw_data

  '''
  def PostProcessedData(self, serieses):
    for name,data in serieses.iteritems():
      result = self.firebaseRef.post('/processed', name, data)
      break
  '''

def GetMeasurementNames(raw_data_tuple):
  names = set()
  for data in raw_data_tuple:
    for k in data[1].keys():
      names.add(k)
  return names

def Resample(tss, values, ts_gap):
  stime = np.ceil(tss[0])
  etime = np.floor(tss[-1])
  tss_new = np.arange(stime, etime, ts_gap)
  return tss_new, np.interp(tss_new, tss, values)

def EstimateSampleRate(tss):
  if type(tss) is list:
    tss = np.array(tss)
  return np.round(np.mean(tss[1:] - tss[:-1])*1000)/1000

def RawToSeries(raw_data_tuple, resample_gap=None):
  ts_names = GetMeasurementNames(raw_data_tuple)
  serieses = {}
  tss = np.array([tu[0] for tu in raw_data_tuple])
  if resample_gap and resample_gap < 0:
    resample_gap = EstimateSampleRate(tss)
    # print('Use sample rate: %f'%resample_gap)
  for name in ts_names:
    ts_list = []
    measurement = []
    for data in raw_data_tuple:
      if name in data[1]:
        ts_list.append(data[0])
        measurement.append(data[1][name])
    if resample_gap:
      ts_list, measurement = Resample(ts_list, measurement, resample_gap)
    serieses[name] = pd.Series(measurement, index=pd.to_datetime(
        ts_list, unit='s'))
  return serieses

def RawToSeriesPandas(raw_data_tuple, resample_gap=None, how='mean',
                      fill_method='bfill'):
  ts_names = GetMeasurementNames(raw_data_tuple)
  serieses = {}
  for name in ts_names:
    ts_list = []
    measurement = []
    for data in raw_data_tuple:
      if name in data[1]:
        ts_list.append(data[0])
        measurement.append(data[1][name])
    series = pd.Series(measurement, index=pd.to_datetime(
        ts_list, unit='s'))
    if resample_gap:
      serieses[name] = series.resample(resample_gap, how=how,
                                       fill_method=fill_method)
    else:
      serieses[name] = series
  return serieses

def GetNormFactors(values):
  return np.mean(values), np.std(values)

def NormalizeValues(values, mean_value=None, std_value=None):
  if mean_value is None:
    mean_value = np.mean(values)
  if std_value is None:
    std_value = np.std(values)
  if std_value != 0:
    return (values - mean_value) / float(std_value)
  else:
    return values

def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.

    http://wiki.scipy.org/Cookbook/SignalSmooth

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett',
                'blackman'
                flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of
          a string
    NOTE: length(output) != length(input), to correct this:
          return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        print('check failed 1')
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        print("Input vector should be bigger than window size. Use 3 instead.")
        window_len = 3
    if window_len < 3:
        print('window_len too small')
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        print('method not recognized')
        return

    s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    #return y
    return y[(window_len/2-1):-(window_len/2)]

def SmoothValues(series, index):
  if type(series) is list:
    series = np.array(series)
  values_new = smooth(series)
  len_original = len(series)
  return pd.Series(values_new[:len_original], index=index), index

def ConvertTupleToSerieses(raw_tuple):
  serieses_rs = RawToSeries(raw_tuple, resample_gap=-1)
  '''
  for name,series in serieses_rs.iteritems():
    plt.figure()
    series.plot()
    plt.show()
  '''
  serieses_smoothed = {}
  for name,series in serieses_rs.iteritems():
    norm_factors = GetNormFactors(series.values)
    series_norm = NormalizeValues(series.values, norm_factors[0],
                                  norm_factors[1])
    s_smoothed, tss = SmoothValues(series, series.index)
    plt.figure()
    plt.subplot(211)
    series.plot()
    plt.title('%s (raw data)'%name)
    plt.subplot(212)
    s_smoothed.plot()
    plt.title('%s (after smoothing)'%name)
    plt.show()
    serieses_smoothed[name] = {
        'values': [v for v in s_smoothed.values],
        'mean': norm_factors[0],
        'std': norm_factors[1],
        'tss': [int(v) for v in tss.astype(np.int64)/1000000]}
  return serieses_smoothed

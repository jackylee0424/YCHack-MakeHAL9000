import matplotlib.pyplot as plt
import time
import ts_processor as tsp
reload(tsp)

data_retriever = tsp.DataRetriever()
max_run = 3
n_run_done = 0
name_ecg = 'bio_raspi-skfecg'
name_ppg = 'bio_raspi-ltfppg'
while n_run_done < max_run:
  raw_tuple = data_retriever.RetrieveRawData('/bio')
  print('Probe database')
  if raw_tuple:
    series = tsp.ConvertTupleToSerieses(raw_tuple)
    keys = series.keys()
    name = name_ecg
    tss = series[name]['tss']
    print 'Found %d %s measurement in (%s, %s)'%(
           len(tss), name, str(tss[0]), str(tss[-1]))
    plt.figure(); plt.plot(series[name]['tss'], series[name]['values'])
    plt.show()
  time.sleep(3)
  n_run_done += 1

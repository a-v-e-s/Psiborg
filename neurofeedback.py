"""
COMPUTE NEUROFEEDBACK METRICS
# These metrics could also be used to drive brain-computer interfaces

# Alpha Protocol:
# Simple redout of alpha power, divided by delta waves in order to rule out noise
alpha_metric = smooth_band_powers[Band.Alpha] / \
    smooth_band_powers[Band.Delta]

# Beta Protocol:
# Beta waves have been used as a measure of mental activity and concentration
# This beta over theta ratio is commonly used as neurofeedback for ADHD
beta_metric = smooth_band_powers[Band.Beta] / \
    smooth_band_powers[Band.Theta]

# Alpha/Theta Protocol:
# This is another popular neurofeedback metric for stress reduction
# Higher theta over alpha is supposedly associated with reduced anxiety
theta_metric = smooth_band_powers[Band.Theta] / \
    smooth_band_powers[Band.Alpha]
"""

import numpy as np  # Module that simplifies computations on matrices
import matplotlib.pyplot as plt  # Module used for plotting
from pylsl import StreamInlet, resolve_byprop  # Module to receive EEG data
import mlsl_utils  # Our own utility functions
from time import time
import pickle


class Band:
    Delta = 0
    Theta = 1
    Alpha = 2
    Beta = 3
    Gamma = 4


def feedback(name, start_time, child=None, lock=None):
    lock.acquire()

    """ EXPERIMENTAL PARAMETERS """
    # Modify these to change aspects of the signal processing

    # Length of the EEG data buffer (in seconds)
    # This buffer will hold last n seconds of data and be used for calculations
    BUFFER_LENGTH = 5

    # Length of the epochs used to compute the FFT (in seconds)
    EPOCH_LENGTH = 1

    # Amount of overlap between two consecutive epochs (in seconds)
    OVERLAP_LENGTH = 0.8

    # Amount to 'shift' the start of each next consecutive epoch
    SHIFT_LENGTH = EPOCH_LENGTH - OVERLAP_LENGTH

    # Index of the channel(s) (electrodes) to be used
    # 0 = left ear, 1 = left forehead, 2 = right forehead, 3 = right ear
    INDEX_CHANNEL = [0]

    """ 1. CONNECT TO EEG STREAM """

    # Search for active LSL streams
    print('Looking for an EEG stream...')
    streams = resolve_byprop('type', 'EEG', timeout=2)
    if len(streams) == 0:
        if child:
            child.send('Fail')
            lock.release()
        raise RuntimeError('Can\'t find EEG stream.')

    # Set active EEG stream to inlet and apply time correction
    print("Start acquiring data")
    inlet = StreamInlet(streams[0], max_chunklen=12)
    eeg_time_correction = inlet.time_correction()

    # Get the stream info and description
    info = inlet.info()
    description = info.desc()

    # Get the sampling frequency
    # This is an important value that represents how many EEG data points are
    # collected in a second. This influences our frequency band calculation.
    # for the Muse 2016, this should always be 256
    fs = int(info.nominal_srate())

    """ 2. INITIALIZE BUFFERS """

    # Initialize raw EEG data buffer
    eeg_buffer = np.zeros((int(fs * BUFFER_LENGTH), 1))
    filter_state = None  # for use with the notch filter

    # Compute the number of epochs in "buffer_length"
    n_win_test = int(np.floor((BUFFER_LENGTH - EPOCH_LENGTH) /
                              SHIFT_LENGTH + 1))

    # Initialize the band power buffer (for plotting)
    # bands will be ordered: [delta, theta, alpha, beta]
    band_buffer = np.zeros((n_win_test, 5))

    """ 3. GET DATA """

    # The try/except structure allows to quit the while loop by aborting the
    # script with <Ctrl-C>
    print('Press Ctrl-C in the console to break the while loop.')

    data = []
    try:
        # The following loop acquires data, computes band powers, and calculates neurofeedback metrics based on those band powers
        if child:
            child.send('Begin!')
            lock.release()
        while True:
            if child.poll():
                if child.recv() == 'Done!':
                    print('parent says Done!')
                    save_and_exit(name, start_time, data)
                    break

            """ 3.1 ACQUIRE DATA """
            # Obtain EEG data from the LSL stream
            eeg_data, timestamp = inlet.pull_chunk(
                timeout=1, max_samples=int(SHIFT_LENGTH * fs))

            # Only keep the channel we're interested in
            ch_data = np.array(eeg_data)[:, INDEX_CHANNEL]

            # Update EEG buffer with the new data
            eeg_buffer, filter_state = mlsl_utils.update_buffer(
                eeg_buffer, ch_data, notch=True,
                filter_state=filter_state)

            """ 3.2 COMPUTE BAND POWERS """
            # Get newest samples from the buffer
            data_epoch = mlsl_utils.get_last_data(eeg_buffer,
                                             EPOCH_LENGTH * fs)

            # Compute band powers
            band_powers = mlsl_utils.compute_band_powers(data_epoch, fs)
            band_buffer, _ = mlsl_utils.update_buffer(band_buffer,
                                                 np.asarray([band_powers]))
            # Compute the average band powers for all epochs in buffer
            # This helps to smooth out noise
            smooth_band_powers = np.mean(band_buffer, axis=0)

            timestamp = time()
            bands = {
                timestamp: [
                    [
                        band_powers[Band.Delta],
                        band_powers[Band.Theta],
                        band_powers[Band.Alpha],
                        band_powers[Band.Beta],
                        band_powers[Band.Gamma]
                    ],
                    [
                        smooth_band_powers[Band.Delta],
                        smooth_band_powers[Band.Theta],
                        smooth_band_powers[Band.Alpha],
                        smooth_band_powers[Band.Beta],
                        smooth_band_powers[Band.Gamma]
                    ]
                ]
            }
            data.append(bands)
            #yield data

    except KeyboardInterrupt:
        save_and_exit(name, start_time, data)


def save_and_exit(name, start_time, data):
    print('Saving and Closing!')
    pkl_name = 'EEGs/' + name.get().replace(' ', '_') + '/zener/' + start_time + '.pkl'
    with open(pkl_name, 'wb') as f:
        pickle.dump(data, f)
    exit()


if __name__ == '__main__':
    import tkinter
    from datetime import datetime
    name = tkinter.StringVar()
    name.set('Jon David')
    start_time = str(datetime.now()).replace(' ', '_')
    feedback(name, start_time)
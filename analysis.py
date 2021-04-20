# credit to https://github.com/mdeff/fma

import os


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn as skl
import sklearn.utils, sklearn.preprocessing, sklearn.decomposition, sklearn.svm
import librosa
import librosa.display
from collections import defaultdict
import pickle
 
from fma import utils

AUDIO_DIR = os.environ.get('AUDIO_DIR')

# Load metadata and features.
tracks = utils.load('fma/data/fma_metadata/tracks.csv')
genres = utils.load('fma/data/fma_metadata/genres.csv')
features = utils.load('fma/data/fma_metadata/features.csv')
echonest = utils.load('fma/data/fma_metadata/echonest.csv')

small = tracks['set', 'subset'] <= 'small'
sub = tracks.loc[small, ('track', 'genre_top')]

small_subset = echonest.loc[small]


filtered_cols = [('echonest', 'audio_features', 'acousticness'), 
    ('echonest', 'audio_features', 'danceability'),
    ('echonest', 'audio_features', 'energy'),
    ('echonest', 'audio_features', 'instrumentalness'),
    ('echonest', 'audio_features', 'liveness'),
    ('echonest', 'audio_features', 'speechiness'),
    ('echonest', 'audio_features', 'tempo'),
    ('echonest', 'audio_features', 'valence'),
    ('track', 'genre_top')]


filtered = small_subset.join(sub.to_frame(), how='inner')[filtered_cols]
filtered.to_csv('filtered.csv')

# Generate the dictionary with melspectogram information

aggregate = defaultdict(list)
aggregate2 = defaultdict(list)
for track in filtered.iterrows():
    filename = utils.get_audio_path('fma/data/fma_small', track[0])
    genre = track[1][('track', 'genre_top')]

    x, sr = librosa.load(filename, sr=None, mono=True)

    stft = np.abs(librosa.stft(x, n_fft=2048, hop_length=512))
    mel = librosa.feature.melspectrogram(sr=sr, S=stft**2)
    log_mel = librosa.power_to_db(mel, ref=np.max)

    chroma = librosa.feature.chroma_stft(x, sr=sr)
    aggregate[genre].append(log_mel)
    aggregate2[genre].append(chroma)

with open('test.pickle', 'wb') as file, open('test2.pickle', 'wb') as file2:
    pickle.dump(aggregate, file)
    pickle.dump(aggregate2, file2)
        
# Save spectrogram median values

with open('test.pickle', 'rb') as file, open('test2.pickle', 'rb') as file2:
    aggregate = pickle.load(file)
    aggregate2 = pickle.load(file2)

returned = {}
returned2 = {}
for key in aggregate:
    mi = min([p.shape[1] for p in aggregate[key]])
    mi2 = min([p.shape[1] for p in aggregate2[key]])
    returned[key] = np.median(np.array([a[..., :mi] for a in aggregate[key][::int(mi/10)]]), axis=0)
    returned2[key] = np.median(np.array([a[..., :mi2] for a in aggregate2[key][::int(mi/10)]]), axis=0)

with open('spectogram.pickle', 'wb') as file, open('chroma.pickle', 'wb') as file2:
    pickle.dump(returned2, file2)
    pickle.dump(returned, file)

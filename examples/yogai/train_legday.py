#!/usr/bin/env python3
import argparse
import numpy as np
import pandas as pd
from multiprocessing import cpu_count
from sklearn.model_selection import train_test_split

import keras
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.optimizers import RMSprop


window = 5
epochs = 10
batch_size = 16
pose_vec_dim = 28
cores = cpu_count()

class_names = ['squat', 'deadlift', 'stand']
num_class = len(class_names)
lbl_dict = {class_name:idx for idx, class_name in enumerate(class_names)}


def load_data(fl):
    dataset = pd.read_csv(fl,  index_col=None)
    y = dataset.pop('y')
    X = dataset.values  
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2) 

    y_train = keras.utils.to_categorical(list(map(lbl_dict.get, y_train)), num_class)
    y_test = keras.utils.to_categorical(list(map(lbl_dict.get, y_test)), num_class)

    X_test = X_test.reshape(X_test.shape[0], pose_vec_dim, window)
    X_train = X_train.reshape(X_train.shape[0], pose_vec_dim, window)
    return X_train, X_test, y_train, y_test


def lstm_model():
    model = Sequential()
    model.add(LSTM(32, dropout=0.2, recurrent_dropout=0.2, input_shape=(pose_vec_dim, window)))
    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(len(class_names), activation='softmax'))
    print(model.summary())
    return model


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Training for LegDay application')
    parser.add_argument('--data', type=str, default='./data/legday/squats_deadlifts_stand5.csv')
    parser.add_argument('--out_file', type=str, default='./models/lstm.h5')
    args = parser.parse_args()

    model = lstm_model()
    model.compile(loss='categorical_crossentropy',
                  optimizer=RMSprop(),
                  metrics=['accuracy'])

    X_train, X_test, y_train, y_test = load_data(args.data)

    history = model.fit(X_train, y_train,
                        batch_size=batch_size,
                        epochs=epochs,
                        verbose=1,
                        validation_data=(X_test, y_test))

    score = model.evaluate(X_test, y_test, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])


    model.save(args.out_file)
    print("Saved model to disk")


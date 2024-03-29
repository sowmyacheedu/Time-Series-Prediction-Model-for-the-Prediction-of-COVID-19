import pandas as pd
import os
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,f1_score,precision_score,recall_score
import seaborn as sns
from datetime import date
from datetime import timedelta
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from sklearn.metrics import mean_squared_error

def preprocess_data(data):

    data=data.loc[:,["ObservationDate","Confirmed","Recovered","Deaths"]]

    # print(type(data),data)

    grouped_data=data.groupby(["ObservationDate"]).sum()

    grouped_data["date"]=grouped_data.index

    print("grouped_data ",grouped_data,sep="\n")

    b=grouped_data.reset_index(drop=True)

    b["Date"] = pd.to_datetime(b["date"])

    b=b.sort_values(by="Date")

    return b

def getDates():

    sdate=date(2021,5,3)

    edate=date.today()

    x=pd.date_range(sdate,edate)

    return x.date


def predict(X,n_steps,model):

    global future_confirmed_list,num_days

    last_row=X[X.shape[0]-1]

    last_date=date(2021,5,2)
    curr_date=date.today()
    num_days=(curr_date-last_date).days
    # print("num of days",num_days)

    tmp_list=list(last_row)
    future_confirmed_list=list()

    for i in range(num_days):
        x_input=np.asarray(tmp_list,dtype="object").astype(np.float32).reshape(1,n_steps,1)
        # print(x_input)
        yhat=model.predict(x_input,verbose=0)
        # print(yhat,type(yhat))
        tmp_list.append(yhat[0][0])
        tmp_list=tmp_list[1:]
        #temp list is used to store the next input and output for this input will be predicted
        # print(tmp_list)
        future_confirmed_list.append(yhat[0][0])

    return future_confirmed_list

def prepare_data(seq,n_steps):
    x=list()
    y=list()                        #[2,3,4,5,6,7]= [2,3] -> [4], [3,4] -> [5]
    for i in range(len(seq)):
        end_idx=i+n_steps
        if end_idx>=len(seq):
            break
        seq_x,seq_y=seq[i:end_idx],seq[end_idx]
        x.append(seq_x)
        y.append(seq_y)
    return np.array(x),np.array(y)


def getAllLists(data):
    global cured_list,future_confirmed_list
    b=data
    date_list=b.date.values
    confirmed_list=b.Confirmed.values
    cured_list=b.Recovered.values
    death_list=b.Deaths.values
    active_cases=[]

    for i in range(len(cured_list)):
        active_cases.append(confirmed_list[i]-cured_list[i]-death_list[i])

    return np.array(date_list),np.array(confirmed_list),np.array(death_list),np.array(cured_list),np.array(active_cases)

def loadModel(x_train,y_train):
    # model=Sequential()
    # model.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(n_steps,1)))
    # model.add(LSTM(50, activation='relu'))
    # model.add(Dense(1))
    # model.compile(optimizer='adam', loss='mse')
    # model.fit(x_train, y_train, epochs=300, verbose=1)
    model = keras.models.load_model('saved_model')
    return model

def displayAccuracy(pred,actual):
    n=len(pred)
    #print("length: ",n)
    sum=0
    for i in range(n):
        x=pred[i]
        y=actual[i]
        diff=abs(x-y)
        sum+=((y-diff)/y)*100
    #print("n: ",n," sum: ",sum)
    sum/=n
    return sum

def fun(confirmed_list):

    confirmed_x,confirmed_y=prepare_data(confirmed_list,n_steps)

    x_train,x_test,y_train,y_test=train_test_split(confirmed_x,confirmed_y,test_size=0.2) #splitting into training and testing data

    X_train=x_train.reshape(x_train.shape[0],x_train.shape[1],1)


    model=loadModel(X_train,y_train) ## Loading Model

    #model.save("saved_model")

    X_test=x_test.reshape(x_test.shape[0],x_test.shape[1],1)

    predicted_output_test=model.predict(X_test) ## Predicting the model for future

    actual_output_test=y_test

    print("predicted output: ",predicted_output_test[:,0])
    print("actual output",actual_output_test)

    accuracy=displayAccuracy(predicted_output_test[:,0],actual_output_test)
    print("\n\nAccuracy: ",accuracy,"\n\n")

    return confirmed_x , model


global n_steps,num_days

n_steps=5

data=pd.read_csv("covid_19_data.csv")
# print(data.head())

data=data[data["Country/Region"]=="India"]

data=preprocess_data(data) # Group confirmed cases, Recovered, Death cases data in the form of sorted order according to dates

# print("data after preprocessing:",data,sep="\n")
dates_list , confirmed_list, death_list , cured_list , active_list = getAllLists(data)

confirmed_x , confirmed_model =fun(confirmed_list)

future_confirmed_list=predict(confirmed_x,n_steps,confirmed_model)
"""
death_x ,death_model=fun(death_list)

future_death_list=predict(death_x,n_steps,death_model)

cured_x,cured_model=fun(cured_list)

future_cured_list=predict(cured_x,n_steps,cured_model)

"""

print("confirmed cases for future ")
print(future_confirmed_list)

future_dates_list=getDates()

plt.plot(future_dates_list,future_confirmed_list) ## Try to concatenate old dates with future_dates_list and plot a graph
plt.xlabel("Dates")
plt.ylabel("Total number of confirmed cases")
plt.show()
"""
plt.plot(future_dates_list,future_death_list)
plt.xlabel("Dates")
plt.ylabel("Total number of deaths")
plt.show()

"""

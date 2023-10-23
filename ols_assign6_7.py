#!/usr/bin/env python3
# ols.py                                                     SSimmons March 2018
"""
Uses a neural net to find the ordinary least-squares regression model. Trains
with batch gradient descent, and computes r^2 to gauge predictive quality.
"""
"""
Write a program that simulates choosing (with replacement) samples of size 20
(or, better, any sample size, k) from a population of size 2264 (or any population size, n).
Have your program keep track of which examples from the population have occurred in some sample.
At the moment when all the examples in the population have been seen,
have your program report the total number of samples that were drawn.
"""

import torch
import pandas as pd
import torch.nn as nn
print("loading data...")
# Read the named columns from the csv file into a dataframe.
names = ['SalePrice','1st_Flr_SF','2nd_Flr_SF','Lot_Area','Overall_Qual',
    'Overall_Cond','Year_Built','Year_Remod/Add','BsmtFin_SF_1','Total_Bsmt_SF',
    'Gr_Liv_Area','TotRms_AbvGrd','Bsmt_Unf_SF','Full_Bath']
df = pd.read_csv('AmesHousing.csv', names = names)
data = df.values # read data into a numpy array (as a list of lists)
data = data[1:] # remove the first list which consists of the labels
data = data.astype(float) # coerce the entries in the numpy array to floats
data = torch.FloatTensor(data) # convert data to a Torch tensor

data.sub_(data.mean(0)) # mean-center
data.div_(data.std(0))  # normalize

xss = data[:,1:]
yss = data[:,:1]

# specify test percentage
test_percentage = 0.2

# calculate number of test samples
num_test_samples = int(test_percentage * len(data))

# randomize data to get random datapoints
indices = torch.randperm(len(data))

# specify train and test indicies
train_indices = indices[:-num_test_samples]
test_indices = indices[-num_test_samples:]

# create tensors for test/train xss and yss
x_train = torch.FloatTensor(xss[train_indices])
y_train = torch.FloatTensor(yss[train_indices])
x_test = torch.FloatTensor(xss[test_indices])
y_test = torch.FloatTensor(yss[test_indices])


# define a model class
class NonLinearModel(nn.Module):

  def __init__(self):
    super(NonLinearModel, self).__init__()
    self.layer1 = nn.Linear(13, 10)
    self.layer2 = nn.Linear(10,1)

  def forward(self, xss):
    xss = self.layer1(xss)
    xss = torch.relu(xss)
    return self.layer2(xss)


# create and print an instance of the model class
model = NonLinearModel()
print(model)
#for name, param in model.named_parameters():
  #print(name, param.size())
#quit()
z_parameters = []
for param in model.parameters():
  z_parameters.append(param.data.clone())
for param in z_parameters:
  param.zero_()
  
criterion = nn.MSELoss()
num_examples = len(data)
batch_size = 30
learning_rate = 0.000355
epochs = 30
momentum = .899

model.train()
# train the model with momentum
for epoch in range(epochs):
    #accum_loss = 0
    model.train()
    for _ in range(num_examples // batch_size):
        indices = torch.randperm(num_examples)[:batch_size]

        #yss_mb = yss[indices]
        #yhatss_mb = model(xss[indices])
        outputs = model(x_train)
        loss = criterion(outputs, y_train)
        #loss = criterion(yhatss_mb, yss_mb)
        model.zero_grad()
        loss.backward()  
        #accum_loss=accum_loss+loss.item()

        for i, (z_param, param) in enumerate(zip(z_parameters, model.parameters())):
          z_parameters[i] = momentum * z_param + param.grad.data
          param.data.sub_(z_parameters[i] * learning_rate)
          
    with torch.no_grad():
      total_loss = criterion(model(xss), yss).item()
          #total_loss = criterion(model(xss), yss).item()
          
    print('epoch: {0}, loss: {1:11.8f}'.format(epoch+1,total_loss*batch_size/num_examples))

# compute R-squared for training data

with torch.no_grad():
    train_outputs = model(x_train)
    ss_residual = ((y_train - train_outputs) ** 2).sum()
    ss_total = ((y_train - y_train.mean()) ** 2).sum()
    r_squared_train = 1 - (ss_residual / ss_total)

print(f'R-squared (Training Data): {r_squared_train.item():.4f}')

model.eval() 
with torch.no_grad():
    test_outputs = model(x_test)
    test_loss = criterion(test_outputs, y_test)
    ss_residual = ((y_test - test_outputs) ** 2).sum()
    ss_total = ((y_test - y_test.mean()) ** 2).sum()
    r_squared_test = 1 - (ss_residual / ss_total)
    

print(f'R-squared (Test Data): {r_squared_test.item():.4f}')
print(f'Test Loss: {test_loss.item():.4f}')

print("total number of examples:", num_examples, end='; ')
print("batch size:", batch_size)
print("learning rate:", learning_rate)
print("momentum:", momentum)

# Compute 1-SSE/SST which is the proportion of the variance in the data
# explained by the regression hyperplane.
SS_E = 0.0
SS_T = 0.0
mean = yss.mean()
for xs, ys in zip(xss, yss):
    SS_E = SS_E + (ys - model(xs)) ** 2
    SS_T = SS_T + (ys - mean) ** 2
print(f"1-SSE/SST = {1.0 - (SS_E / SS_T).item():1.4f}")

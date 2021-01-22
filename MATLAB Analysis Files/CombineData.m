% ----------------------------------------------
%CombineData.m
%   Helper script to combine the output of SaveEigenFields.py into one .csv
%
%   Written in MATLAB 2019a
%
%   Written by Robert Davis
%   Applied Electromagnetics Lab, UCSD
%   If you use this code for research purposes, please cite the following:
%   (Insert the cite here)
%   Original: 2020-4-17
%   Last updated 2021-1-21
% -------------------------------------------------------------------------

baseFilename = 'myData'; %name of datafile (needs to be a .csv)
numFiles = 8; %number of files to combine

outputData = [];

for idx = 0:numFiles-1
    data = readmatrix(baseFilename+string(idx)+'.csv');
    outputData = [outputData, data];
end

writematrix(outputData,baseFilename+"_full.csv")
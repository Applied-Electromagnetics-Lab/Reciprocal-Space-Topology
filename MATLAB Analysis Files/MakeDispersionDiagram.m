% ----------------------------------------------
%MakeDispersionDiagram.m
%A simple plotting routine to plot a well-formatted dispersion diagram from
%a .csv (see GenerateDispersionData.py for format)
%
%User settings:
%1) cellPeriod : lattice periodicity, in m
%2) filename : corresponding to the .csv to use
%2) modes : number of modes to plot
%3) lattice : type of lattice, either 'tri' or 'square'
%4) scale : y axis scale to use, either 'norm' for normalized units or 
%           'GHz' for frequency
%Todo: 
%
%Written in MATLAB 2019a
%
%Written by Robert Davis
%Original: 2019-5-28
%Last updated 2020-12-23
% ----------------------------------------------

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%User Settings%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
cellPeriod = 20*10^-3; %lattice periodicity, in m
filename = 'file.csv';
modes = 4; %number of modes to plot
lattice = 'tri'; %either 'tri' or 'square'
scale = 'norm'; %either 'norm' for normalized units or 'GHz' for frequency
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

c = 3*10^8;

data = readmatrix(filename);
xpoints = [1:length(data)];
dispLength = (length(data))/3;

if strcmp(scale,'norm')
    data = data*cellPeriod/c;
    ylab = '\omegaa/2\pic';
elseif strcmp(scale,'GHz')
    data = data/10^9;
    ylab = 'Frequency (GHz)';
end

plot(xpoints,data(:,1:modes),'Linewidth',2)
xticks([1,dispLength,2*dispLength,3*dispLength])
ax = gca;
ax.XAxis.FontSize = 24;
xlim([1,size(data,1)])
ylabel(ylab,'FontSize',24)
ylim([0,max(data(:,modes))])

if strcmp(lattice,'square')
    xticklabels({'\Gamma','X','M','\Gamma'})
elseif strcmp(lattice,'tri')
    xticklabels({'\Gamma','M','K','\Gamma'})
end

line([dispLength, dispLength], [0, max(data(:,modes))],...
     'Color', 'black','LineStyle','--'); 
line([2*dispLength, 2*dispLength], [0, max(data(:,modes))],...
     'Color', 'black','LineStyle','--'); 

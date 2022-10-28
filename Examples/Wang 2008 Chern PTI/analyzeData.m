%% initial user configuration
numModes = 1; %number of modes to load in data from
%numReal = 187;
realPts = 10201;
%numK = 37;
kPts = 19^2;
filename_data = '/wangNonTrivfull'; %name of datafile (needs to be a .csv)
filename_grid = '/grid.pts';
filename_epsi = '/epsi.fld';
filename_mu = '/mu.fld';

currentFolder = pwd;
filename_base = [currentFolder];

%% read in E field data

if exist('data','var') == 0
    data = zeros(realPts,2*kPts,numModes);

    for fl = [1:numModes]
        data(:,:,fl) = readmatrix([filename_base,filename_data]+string(fl)+'.csv');
    end
    data = data(:,1:2:end,:) + i*data(:,2:2:end,:);
end

%% read in grids and material data (usually fast)
grid = readmatrix([filename_base,filename_grid],'FileType','text'); %read in the real grid
epsi = readmatrix([filename_base,filename_epsi],'FileType','text'); %read in the epsilon values
mu = readmatrix([filename_base,filename_mu],'FileType','text'); %read in the mu values

% read just the data points
epsi = epsi(:,4);
mu = mu(:,4);

%% plot a test field
numX = sqrt(realPts);
numY = sqrt(realPts);
figure(1)
Z = reshape(abs(data(:,1)),[numX,numY]);
surf(Z,'EdgeColor','none','FaceColor','interp')
colormap(jet)
xlabel('x','FontSize',24)
ylabel('y' ,'FontSize',24)
ax = gca;
ax.XAxis.FontSize = 18;
xlim([1,numY])
ax.YAxis.FontSize = 18;
ylim([1,numX])
pbaspect([1 1 1])
colorbar
view(0,90)

%% calculate Wilson loops and Berry curvatures
W = ComputeWilsonLoops(data,grid,epsi,mu);
F1 = ComputeBerryCurvature(data,grid,epsi,mu);

%% plot curvature for mode 1
figure(2)
surf(F1,'EdgeColor','none','FaceColor','interp')
colormap(jet)
ax = gca;
ax.XAxis.FontSize = 18;
xlim([1,size(F1,1)])
ax.YAxis.FontSize = 18;
ylim([1,size(F1,1)])
pbaspect([1 1 1])
title('Wang 2008: Berry Curvature for Mode 1')
colorbar
view(0,90)
C1 = sum(sum(F1))/(2*pi)

%% plot Wilson loops
figure
xVals = linspace(-1,1,length(W));
plot(xVals,W(1,:),'ro','LineWidth',2)
xlabel('k_x (\pi/a)')
ylabel('\theta (\pi)')
title('Wang 2008: Wilson Loop for Mode 1')
ylim([-1,1])

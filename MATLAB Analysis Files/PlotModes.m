function [] = PlotModes(data,mode,grid,realGridSize,kGridSize)
%PlOTMODES Plots high symmetry points of input data for square lattices
%   This function takes in a set of data of eigenmodes and plots the
%   various points of high symmetry (Gamma, M, X, etc.). Currently it
%   supports only square lattices. 
%
%   Inputs:
%   1) data : the input data. The format is R x K x N, where R is all spatial 
%   points to plot, K are all available k points, arranged in the order 
%   [k_x1,y1, kx2,y1...] (ie, kx first, followed by ky), and N is the
%   number of modes.
%   2) mode : The specific mode to plot (eg., 1, 2,...).
%   3) grid : the real space grid to use. This should be a .fld file.
%   4) realGridSize : size of the real space grid (N for an NxN grid)
%   5) kGridSize : number of k points in the k-space grid.
%   
%   Outputs:
%   Plots for Gamma, X, and M high symmetry points
%
%   Written by Robert J. Davis
%   Applied Electromagnetics Lab, UCSD
% 
%   If you use this code for research purposes, please cite the following:
%   D. Bisharat, R. Davis, Y. Zhou, P. Bandaru and D. Sievenpiper, 
%   "Photonic Topological Insulators: A Beginner's Introduction 
%   [Electromagnetic Perspectives]," in IEEE Antennas and Propagation 
%   Magazine, vol. 63, no. 3, pp. 112-124, June 2021, 
%   doi: 10.1109/MAP.2021.3069276.
% 
%   Original: 2020-4-17
%   Last updated 2022-2-15
% -------------------------------------------------------------------------


%extract the realspace grid info for plotting
x = grid(:,1);
y = grid(:,2);
Z = grid(1,3); %this should be a scalar

%reshape a bit to make surface plots
X = reshape(x,[realGridSize,realGridSize]);
Y = reshape(y,[realGridSize,realGridSize]);

%reshape a bit and extract the complex magnitudes of the high symmetry
%points
Gidx = (kGridSize+1)*((kGridSize-1)/2)+1; %assumes odd k points
Xidx = Gidx+(kGridSize-1)/2 + kGridSize+1;
Midx = length(data(1,:,mode));
kxy0_0 = abs(data(:,Gidx,mode));
kxy180_0 = abs(data(:,Xidx,mode));
kxy180_180 = abs(data(:,Midx,mode));

%plot the three high symmetry points
figure
Z = reshape(kxy0_0,[realGridSize,realGridSize])';
surf(X.*10^3,Y.*10^3,Z,'EdgeColor','none')
colormap(jet)
xlabel('x (mm)')
ylabel('y (mm)')
title('Mode ' + string(mode) + ' Mag(Ez) at Gamma (px=py=0deg)')
colorbar

figure
Z = reshape(kxy180_0,[realGridSize,realGridSize])';
surf(X.*10^3,Y.*10^3,Z,'EdgeColor','none')
colormap(jet)
xlabel('x (mm)')
ylabel('y (mm)')
title('Mode ' + string(mode) + ' Mag(Ez) at X (px=180deg, py=0deg)')
colorbar

figure
Z = reshape(kxy180_180,[realGridSize,realGridSize])';
surf(X.*10^3,Y.*10^3,Z,'EdgeColor','none')
colormap(jet)
xlabel('x (mm)')
ylabel('y (mm)')
title('Mode ' + string(mode) + ' Mag(Ez) at M (px=py=180deg)')
colorbar

end


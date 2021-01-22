function [F] = ComputeBerryCurvature(data,grid,epsi,mu)
%COMPUTEBERRYCURVATURE Computes the Berry curvature of the provided EM data
%   This function takes in a set of field data corresponding to all spatial
%   points for a set of points in the Brillouin zone, along with the
%   spatial grid and material grids, and calculates the Berry curvature. 
%   If the input data has more than one 1 mode included, the non-Abelian 
%   form is used, which gives the rigorous value for degenerate bands.
%
%   Inputs:
%   1) data : the input data. The format is R x K x N, where R is all spatial 
%   points to integrate over, K are all k points, arranged in the order 
%   [k_x1,y1, kx2,y1...] (ie, kx first, followed by ky), and N is the
%   number of modes.
%   2) grid : the real space grid to use. This should be a .fld file.
%   3) epsi : the values of epsilon relative for the real space grid. This
%   should also be a .fld (can be extracted from HFSS model directly).
%   4) mu : the values of mu relative for the real space grid. Not
%   currently used.
%   
%   Outputs:
%   1) F : Matrix containing all values of the Berry curvature. This will
%   be of size Sqrt(K)xSqrt(K), assuming the kx and ky are equal.
%
%   Example: for a real space grid of 101x101 points and a k space grid of 
%   51x51 points, the form of data should be a 10201x2601 
%   multidimensional array. The resulting output F will be a 51x51 matrix.
%
%
%   Known issues: 
%   1) At the moment, this only works for odd values of kx. Some problems 
%   may arise if kx (or ky) is not odd).
%
%   Written in MATLAB 2019a
%
%   Written by Robert Davis
%   Applied Electromagnetics Lab, UCSD
%   If you use this code for research purposes, please cite the following:
%   (Insert the cite here)
%   Original: 2020-6-24
%   Last updated 2021-1-21
% -------------------------------------------------------------------------

% fetch real and k space grid info
numK = sqrt(size(data,2));
numModes = size(data,3);

deltaS = abs(abs(grid(2,2))-abs(grid(1,2)))^2; %area of one plaquette of real space

%preallocate matrices
M = zeros(numModes^2,1); %overlap matrix
F = zeros(numK-1,numK-1); %Berry curvature matrix

%compute the Berry curvature. First kx is traversed, and a value of F is
%computed via the non-Abelian formulation. This is done by looping over ky,
%and building the overlap matrix of normalized inner products between 
%neighboring points in k space. The indexing is somewhat complicated, but
%all that is happening is <u_{ky,kx,n} | u_{ky,kx',n'}> is being computed 
%for every value of kx and n. 
for kx = 0:numK-2
    for ky = 1:numK:(numK-1)^2
        idx = 1;
        for np = 1:numModes
            for n = 1:numModes
                %compute the inner product and store to matrix
                kNorm = sum(conj(epsi.*data(:,kx+ky,n)).*data(:,kx+ky,n))*deltaS;
                kpNorm = sum(conj(epsi.*data(:,kx+ky+numK,np)).*data(:,kx+ky+numK,np))*deltaS;
                innerProduct1 = (kNorm.*kpNorm).^(-1/2).*sum(conj(epsi.*data(:,kx+ky,n)).*data(:,kx+ky+numK,np))*deltaS;
                
                kNorm = sum(conj(epsi.*data(:,kx+ky+numK,n)).*data(:,kx+ky+numK,n))*deltaS;
                kpNorm = sum(conj(epsi.*data(:,kx+ky+numK+1,np)).*data(:,kx+ky+numK+1,np))*deltaS;
                innerProduct2 = (kNorm.*kpNorm).^(-1/2).*sum(conj(epsi.*data(:,kx+ky+numK,n)).*data(:,kx+ky+numK+1,np))*deltaS;
                
                kNorm = sum(conj(epsi.*data(:,kx+ky+numK+1,n)).*data(:,kx+ky+numK+1,n))*deltaS;
                kpNorm = sum(conj(epsi.*data(:,kx+ky+1,np)).*data(:,kx+ky+1,np))*deltaS;
                innerProduct3 = (kNorm.*kpNorm).^(-1/2).*sum(conj(epsi.*data(:,kx+ky+numK+1,n)).*data(:,kx+ky+1,np))*deltaS;
                
                kNorm = sum(conj(epsi.*data(:,kx+ky+1,n)).*data(:,kx+ky+1,n))*deltaS;
                kpNorm = sum(conj(epsi.*data(:,kx+ky,np)).*data(:,kx+ky,np))*deltaS;
                innerProduct4 = (kNorm.*kpNorm).^(-1/2).*sum(conj(epsi.*data(:,kx+ky+1,n)).*data(:,kx+ky,np))*deltaS;
                
                M(idx) = innerProduct1*innerProduct2*innerProduct3*innerProduct4;
                idx = idx+1;
            end
        end
        M = reshape(M,[numModes,numModes]); %make into a matrix
        F(kx+1,(ky-1)/numK+1) = -imag(log(det(M))); %calculate the Berry curvature for the plaquette
    end
end
end


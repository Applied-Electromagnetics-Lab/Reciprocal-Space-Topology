function [W] = ComputeWilsonLoops(data,grid,epsi,mu)
%COMPUTEWILSONLOOPS Computes the Wilson loops for TM modes
%   This function takes in a set of field data corresponding to all spatial
%   points for a set of points in the Brillouin zone, along with the
%   spatial grid and material grids, and calculates the Wilson loop along a
%   fixed path in k space. 
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
%   1) W : the values of the Wilson loop for all modes in data. This will
%   be of size N x Sqrt(K), assuming the kx and ky are equal.
%
%   Example: for a real space grid of 101x101 points, a k space grid of 
%   51x51 points, and 4 modes, the form of data should be a 10201x2601x4 
%   multidimensional array. The resulting output W will be a 4x51 matrix.
%   Each row represents the Wilson loop for the each mode. 
%
%   Known issues: 
%   1) At the moment, this only works for odd values of kx. Some problems 
%   may arise if kx (or ky) is not odd).
%   2) Matlab's eig() does not always give the correct ordering. This only
%   happens when computing more than one mode at a time, and also only
%   happens for small values (usually right at the two extremes of W). Not
%   sure how to resolve this, but they are usually pretty obvious to see.
%
%   Written in MATLAB 2019a
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

% fetch real and k space grid info
numK = sqrt(size(data,2));
numModes = size(data,3);

deltaS = abs(abs(grid(2,2))-abs(grid(1,2)))^2; %area of one plaquette of real space

%preallocate matrices
M = zeros(numModes^2,numK); %overlap matrix
W = zeros(numModes,numK); %Wilson loop eigenvalues

%compute the Wilson loops. First kx is traversed, and a value of W is
%computed for every mode. This is done by looping over ky, and building the
%overlap matrix of normalized inner products between neighboring points in
%k space. The indexing is somewhat complicated, but all that is happening
%is <u_{ky,kx,n} | u_{ky,kx',n'}> is being computed for every value of kx
%and n. 
for kx = 0:numK-1
    idxM = 1;
    for ky = 1:numK:(numK-1)^2
        idx = 1;
        for np = 1:numModes
            for n = 1:numModes
                %compute the inner product and store to matrix
                kNorm = sum(conj(epsi.*data(:,kx+ky,n)).*data(:,kx+ky,n))*deltaS;
                kpNorm = sum(conj(epsi.*data(:,kx+ky+numK,np)).*data(:,kx+ky+numK,np))*deltaS;
                innerProduct = (kNorm.*kpNorm).^(-1/2).*sum(conj(epsi.*data(:,kx+ky,n)).*data(:,kx+ky+numK,np))*deltaS;
                M(idx,idxM) = innerProduct;
                idx = idx+1;
            end
        end
        idxM = idxM+1;
    end
    
    %the final value must be periodic, so that the inner product with the
    %last kx value is with the first kx value. So do this separately. 
    idx = 1;
    for np = 1:numModes
        for n = 1:numModes
            kNorm = sum(conj(epsi.*data(:,kx+ky+numK,n)).*data(:,kx+ky+numK,np))*deltaS;
            kpNorm = sum(conj(epsi.*data(:,kx+1,n)).*data(:,kx+1,np))*deltaS;
            innerProduct = (kNorm.*kpNorm).^(-1/2).*sum(conj(epsi.*data(:,kx+ky+numK,n)).*data(:,kx+1,np))*deltaS;
            M(idx,idxM) = innerProduct;
            idx = idx+1;
        end
    end
    
    %multiply all overlap matrices for every point (M will become NxN)
    M = reshape(prod(M,2),[numModes,numModes]);
    
    %compute the Wilson loop values, scaled by pi.
    W(:,kx+1) = -imag(log(eig(M)))/pi;
end
end


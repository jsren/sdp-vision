function coords = circles()
rgb = imread('images/empty_pitch/pitch0/bg0.png');
red = rgb(:,:,1);
blue = rgb(:,:,3);
[centers, radii] = imfindcircles(red + blue,[3 4],'ObjectPolarity', ...
    'bright','Sensitivity',0.976);
fid = fopen('circles.txt','wt');  % Note the 'wt' for writing in text mode
fprintf(fid,'%f\n',centers);  % The format string is applied to each element of a
fclose(fid);
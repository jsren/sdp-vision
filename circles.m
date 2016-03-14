function coords = circles()
rgb = imread('images/empty_pitch/pitch0/bg0.png');
red = rgb(:,:,1);
blue = rgb(:,:,3);
[centers, radii] = imfindcircles(red + blue,[3 4],'ObjectPolarity', ...
    'bright','Sensitivity',0.976);
imshow(rgb);
coords = viscircles(centers,radii);
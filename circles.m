
srcFiles =dir('images/empty_pitch/pitch0/*.png'); 
se = strel('disk',11,6);
for i = 1 : length(srcFiles)
    filename = strcat('images/empty_pitch/pitch0/',srcFiles(i).name);
    rgb = imread(filename);
    %rgb = imerode(rgb,se);
    red = rgb(:,:,1);
    green = rgb(:,:,2);
    blue = rgb(:,:,3);
    %imshow(blue);
    [centers, radii] = imfindcircles(red + blue,[3 4],'ObjectPolarity', ...
        'bright','Sensitivity',0.976);
    imshow(rgb);
    hold on
    h = viscircles(centers,radii);
    hold off
    pause(0.5);
    refresh;
end
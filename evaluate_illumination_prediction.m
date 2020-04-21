clc;

%% define data paths
gt_path='/Volumes/Samsung_T5/Courses/MachineLearning/Project/Data/MultiIllumWild/random/test/';
result_path='/Users/sebastian/sfuvault/Courses/MachineLearning/Project/Testing/results/';

img_path='pretrained_random/test_latest/images/';

%% allocate variables
err_1=zeros(30,1);
err_2=zeros(30,1);
err_total=zeros(30,1);

%% step through every test image
for i=1:30
    
    %% load ground truth
    gt1=load(strcat(gt_path,sprintf('%d.mat',i-1)),'img1');
    gt2=load(strcat(gt_path,sprintf('%d.mat',i-1)),'img2');

    %% load estimation
    img1=im2double(imread(strcat(result_path,img_path,sprintf('%d_est_im1.png',i-1))));
    img2=im2double(imread(strcat(result_path,img_path,sprintf('%d_est_im2.png',i-1))));
    
    %% calculate MSE
    err_1(i)=immse(img1,gt1.img1);
    err_2(i)=immse(img2,gt2.img2);
    err_total(i)=err_1(i)+err_2(i);
end

%% export results
t=table(err_total,err_1,err_2);
writetable(t,'pretrained_randomset_error.txt');


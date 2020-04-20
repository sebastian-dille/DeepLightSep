# Learning to separate Ambient and Flash Illuminants in a Single Image

This repository was created as part of the ML course at SFU, Burnaby in Spring 2020.

We have implemented a color-aware loss to address color shift in single image decomposition, especially targeted at seperating flash and ambient illuminantion in a single RGB image.

The code is a build upon the implementation described in the paper "Learning to Separate Multiple Illuminants in a Single Image, Zhuo Hui, Ayan Chakrabarti, Kalyan Sunkavalli, Aswin C. Sankaranarayanan, CVPR 2019" .

Website: https://huizhuo1987.github.io/learningIllum.html

Additionally, the code skeleton is based on "https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix" and "https://github.com/lixx2938/CGIntrinsics". If you use this code, please consider citing:

    @inproceedings{hui2019learning,
	  	title={Learning to Separate Multiple Illuminants in a Single Image},
	  	author={Hui, Zhuo and Chakrabarti, Ayan and Sunkavalli, Kalyan and Sankaranarayanan, Aswin C},
	  	booktitle={Computer Vision and Pattern Recognition (CVPR 2019)},
	  	year={2019}
	}
  

Our contribution consists of the following files:



### Pretrained model:
For the pretrained model, please refer to the original repository: https://huizhuo1987.github.io/learningIllum.html


### Train the network
To train your network, run the following command
```bash
    python train.py --dataroot {path_to_training_data} --model threelayers_color --name {your_training_name} 
    --lrA 0.0001 --lrB 0.0001 --niter 100 --niter_decay 100 --display_id -1 --gpu_ids {your_gpu_ids}
```

### Test image
To test the performance, run the following command
```bash
    python test.py --dataroot {path_to_test_data} --model threelayers_color --name {your_training_name} 
    --gpu_ids {your_gpu_ids}
```

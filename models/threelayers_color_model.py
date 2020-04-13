import torch
from util.image_pool import ImagePool
from .base_model import BaseModel
from . import networks


class ThreeLayersColorModel(BaseModel):
    def name(self):
        return 'ThreeLayersColorModel'

    @staticmethod
    def modify_commandline_options(parser, is_train=True):

        # changing the default values to match the pix2pix paper
        # (https://phillipi.github.io/pix2pix/)
        parser.set_defaults(pool_size=0, no_lsgan=True, norm='batch')
        parser.set_defaults(dataset_mode='aligned')
        parser.set_defaults(netG='unet_256')
        if is_train:
            parser.add_argument('--lambda_L1', type=float, default=100.0, help='weight for L1 loss')

        return parser

    def initialize(self, opt):
        BaseModel.initialize(self, opt)
        self.isTrain = opt.isTrain
        # specify the training losses you want to print out. The program will call base_model.get_current_losses
        self.loss_names = ['G_C']  # ['G_GAN', 'G_L1', 'D_real', 'D_fake']
        # specify the images you want to save/display. The program will call base_model.get_current_visuals

        # if self.isTrain:
        #     self.visual_names = ['rgb_img', 'img1', 'img2',  'im1', 'im2', 'chrom', 'predication', 'shading1', 'shading2', 'est_im1', 'est_im2']

        if self.isTrain:
            self.visual_names = ['rgb_img', 'img1', 'img2', 'predication', 'shading1', 'shading2', 'est_im1', 'est_im2']
        else:
            self.visual_names = ['rgb_img', 'predication', 'shading1', 'shading2', 'est_im1', 'est_im2']
        # specify the models you want to save to the disk. The program will call base_model.save_networks and base_model.load_networks

        if self.isTrain:
            self.model_names = ['G_A', 'G_B', 'G_C']
        else:  # during test time, only load Gs
            self.model_names = ['G_A', 'G_B', 'G_C']
        # load/define networks
        self.netG_A = networks.define_G(opt.input_nc, opt.output_nc, opt.ngf, "resnet_9blocks", opt.norm,
                                        not opt.no_dropout, "kaiming", opt.init_gain, self.gpu_ids)
        self.netG_B = networks.define_G(opt.output_nc, opt.input_nc, opt.ngf, "upunet_256", opt.norm,
                                        not opt.no_dropout, "kaiming", opt.init_gain, self.gpu_ids)
        self.netG_C = networks.define_G(opt.input_nc * 3, opt.output_nc * 2, opt.ngf, "render", opt.norm,
                                        not opt.no_dropout, "kaiming", opt.init_gain, self.gpu_ids)

        """
        if self.isTrain:
            use_sigmoid = opt.no_lsgan
            self.netD = networks.define_D(opt.input_nc + opt.output_nc, opt.ndf, opt.netD,
                                          opt.n_layers_D, opt.norm, use_sigmoid, opt.init_type, opt.init_gain, self.gpu_ids)
        """
        if self.isTrain:
            self.image_pool = ImagePool(opt.pool_size)
            self.image_pool1 = ImagePool(opt.pool_size)
            #self.image_pool2 = ImagePool(opt.pool_size)
            # define loss functions
            # self.criterionGAN = networks.GANLoss(use_lsgan=not opt.no_lsgan).to(self.device)
            # self.criterionL1 = torch.nn.L1Loss()
            self.loss = networks.JointColorLoss()
            self.sloss = networks.ShadingLoss()
            self.rloss = networks.ReconstructionLoss()
            #self.gloss = networks.L1Loss()
            # initialize optimizers
            self.optimizers = []
            # self.optimizer_G = torch.optim.Adam(self.netG_A.parameters(),
            #                                     lr=opt.lrA, betas=(opt.beta1, 0.999))

            # self.optimizer_G_B = torch.optim.Adam(self.netG_B.parameters(),
            #                                       lr=opt.lrB, betas=(opt.beta1, 0.999))

            self.optimizer_G_C = torch.optim.Adam(self.netG_C.parameters(),
                                                  lr=opt.lrB, betas=(opt.beta1, 0.999))

            # self.optimizers.append(self.optimizer_G)
            # self.optimizers.append(self.optimizer_G_B)
            self.optimizers.append(self.optimizer_G_C)

    def set_input(self, input):
        self.rgb_img = input['rgb_img'].to(self.device)
        self.image_paths = input['A_paths']
        if self.isTrain:
            #self.chrom = input['chrom'].to(self.device)
            # # self.gamma = input['gamma'].to(self.device)
            self.mask = input['mask'].to(self.device)

            #self.im1 = input['im1'].to(self.device)
            #self.im2 = input['im2'].to(self.device)

            self.img1 = input['img1'].to(self.device)
            self.img2 = input['img2'].to(self.device)
        # self.img_wb = input['img_wb'].to(self.device)

    def forward(self):
        self.predication = self.netG_A(self.rgb_img)
        inputG = torch.cat((self.predication, self.rgb_img), 1)
        self.shading1, self.shading2 = self.netG_B(inputG)

        input_ = torch.cat((self.rgb_img, self.shading1, self.shading2), 1)
        est_imgs = self.netG_C(input_)
        self.est_im1 , self.est_im2 = est_imgs[:,:3,:,:], est_imgs[:,3:,:,:]

    def L1Loss(self, prediction, gt, mask):
        num_valid = torch.sum( mask )
        diff = torch.mul(mask, torch.abs(prediction - gt))
        return torch.sum(diff)/num_valid

    def backward_G_C(self):
        input_G_C = self.image_pool1.query(torch.cat((self.rgb_img, self.shading1, self.shading2), 1))
        est_imgs = self.netG_C(input_G_C.detach())
        est_im1, est_im2 = est_imgs[:,:3,:,:], est_imgs[:,3:,:,:]

        #if self.L1Loss(self.shading1, self.im1, self.mask) < self.L1Loss(self.shading1, self.im2, self.mask):
        #    input_GT = torch.cat((self.rgb_img, self.im1, self.im2), 1)
        #else:
        #    input_GT = torch.cat((self.rgb_img, self.im2, self.im1), 1)

        #gt_imgs = self.netG_C(input_GT)
        #gt_im1, gt_im2 = gt_imgs[:,:3,:,:], gt_imgs[:,3:,:,:]
        img = est_im1 + est_im2

        #self.loss_G_C = .5 * self.rloss(self.img1, self.img2, est_im1, est_im2, self.mask) + \
        #                .5 * self.rloss(self.img1, self.img2, gt_im1, gt_im2, self.mask) + \
        #                .5 * self.loss(self.rgb_img, img, self.mask)

        #TODO: add color loss
        self.loss_G_C = .5 * self.loss(self.img1, est_im1, self.mask)

        self.loss_G_C.backward()

    # def backward_G_B(self):
    #     input_G_B = self.image_pool.query(torch.cat((self.predication, self.rgb_img), 1))
    #     input_G_T = torch.cat((self.chrom, self.rgb_img), 1)
    #     shading1, shading2 = self.netG_B(input_G_B.detach())
    #     gt_shading1, gt_shading2 = self.netG_B(input_G_T)

    #     # self.shading1, self.shading2 = self.netG_B(input_G_B.detach())

    #     self.loss_G_B = .5 * self.sloss(self.im1, self.im2, shading1, shading2, self.mask) \
    #                     +.5 * self.sloss(self.im1, self.im2, gt_shading1, gt_shading2, self.mask) \

    #     self.loss_G_B.backward()

    # def backward_G(self):
    #     # First, G(A) should fake the discriminator
    #     self.loss_G_A = self.loss(self.chrom, self.predication, self.mask)
    #     self.loss_G = self.loss_G_A
    #     self.loss_G.backward()

    def optimize_parameters(self):

        self.forward()
        # update G_C
        self.set_requires_grad(self.netG_C, True)
        self.optimizer_G_C.zero_grad()
        self.backward_G_C()
        self.optimizer_G_C.step()
        self.set_requires_grad(self.netG_C, False)

        # update G_B
        #self.set_requires_grad(self.netG_B, True)
        #self.optimizer_G_B.zero_grad()
        #self.backward_G_B()
        #self.optimizer_G_B.step()
        #self.set_requires_grad(self.netG_B, False)

        #self.optimizer_G.zero_grad()
        #self.backward_G()
        #self.optimizer_G.step()

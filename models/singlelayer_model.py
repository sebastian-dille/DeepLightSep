import torch
from util.image_pool import ImagePool
from .base_model import BaseModel
from . import networks


class SingleLayerModel(BaseModel):
    def name(self):
        return 'SingleLayerModel'

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
        self.loss_names = ['G_B']#['G_GAN', 'G_L1', 'D_real', 'D_fake']
        # specify the images you want to save/display. The program will call base_model.get_current_visuals
        self.visual_names = ['rgb_img', 'shading1', 'shading2', 'im1', 'im2']
        # specify the models you want to save to the disk. The program will call base_model.save_networks and base_model.load_networks



        if self.isTrain:
            self.model_names = ['G_B']
        else:  # during test time, only load Gs
            self.model_names = ['G_B']
        # load/define networks
        self.netG_B = networks.define_G(opt.output_nc, opt.input_nc, opt.ngf, "onenet_256", opt.norm,
                                      not opt.no_dropout, opt.init_type, opt.init_gain, self.gpu_ids)

        """
        if self.isTrain:
            use_sigmoid = opt.no_lsgan
            self.netD = networks.define_D(opt.input_nc + opt.output_nc, opt.ndf, opt.netD,
                                          opt.n_layers_D, opt.norm, use_sigmoid, opt.init_type, opt.init_gain, self.gpu_ids)
        """
        if self.isTrain:
            self.image_pool = ImagePool(opt.pool_size)
            # define loss functions
            #self.criterionGAN = networks.GANLoss(use_lsgan=not opt.no_lsgan).to(self.device)
            #self.criterionL1 = torch.nn.L1Loss()
            self.loss = networks.L1Loss()
            self.sloss = networks.ShadingLoss()
            # initialize optimizers
            self.optimizers = []

            self.optimizer_G_B = torch.optim.Adam(self.netG_B.parameters(),
                                                lr=opt.lrB, betas=(opt.beta1, 0.999))
            self.optimizers.append(self.optimizer_G_B)

    def set_input(self, input):

        self.rgb_img = input['rgb_img'].to(self.device)

        self.image_paths = input['A_paths']
        self.mask = input['mask'].to(self.device)

        self.im1 = input['img1'].to(self.device)
        self.im2 = input['img2'].to(self.device)



    def forward(self):
        self.shading1, self.shading2 = self.netG_B(self.rgb_img)

    def backward_G_B(self):
        self.loss_G_B = torch.min(self.loss(self.im1, self.shading1, self.mask) \
                                  + self.loss(self.im2, self.shading2, self.mask), \
                                  self.loss(self.im1, self.shading2, self.mask) \
                                  + self.loss(self.im2, self.shading1, self.mask))

                        #torch.min(self.loss(self.im1, self.shading1, self.mask) + \
                        #             self.loss(self.im2, self.shading2, self.mask),
                        #             self.loss(self.im2, self.shading1, self.mask) + \
                        #             self.loss(self.im1, self.shading2, self.mask))
                        #.5*torch.min(self.loss(self.im1, self.shading1, self.mask) + \
                        #             self.loss(self.im2, self.shading2, self.mask),
                        #             self.loss(self.im2, self.shading1, self.mask) + \
                        #             self.loss(self.im1, self.shading2, self.mask)) + \
                        #self.rloss(self.shading1, self.shading2, self.rgb_img, self.mask)

        self.loss_G_B.backward()

    def optimize_parameters(self):
        """
        self.forward()
        # update D
        self.set_requires_grad(self.netD, True)
        self.optimizer_D.zero_grad()
        self.backward_D()
        self.optimizer_D.step()

        # update G
        self.set_requires_grad(self.netD, False)
        self.optimizer_G.zero_grad()
        self.backward_G()
        self.optimizer_G.step()
        """
        self.forward()
        # update G_B
        self.optimizer_G_B.zero_grad()
        self.backward_G_B()
        self.optimizer_G_B.step()






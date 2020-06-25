from easydict import EasyDict as edict

from gans.trainers import cycle_gan_trainer


class CycleGAN:

    def __init__(
            self,
            input_params: edict,
            generators,
            discriminators,
            problem_type,
            continue_training,
    ):
        self.num_epochs = input_params.num_epochs
        self.cycle_gan_trainer = cycle_gan_trainer.CycleGANTrainer(
            batch_size=input_params.batch_size,
            generator=generators,
            discriminator=discriminators,
            dataset_type=problem_type,
            lr_generator=input_params.learning_rate_generator,
            lr_discriminator=input_params.learning_rate_discriminator,
            continue_training=continue_training,
            save_images_every_n_steps=input_params.save_images_every_n_steps,
        )

    def fit(self, dataset):
        self.cycle_gan_trainer.train(
            dataset=dataset,
            num_epochs=self.num_epochs,
        )

    def predict(self):
        pass
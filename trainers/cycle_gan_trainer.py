import numpy as np
import tensorflow as tf

from layers import losses
from trainers import gan_trainer
from utils import visualization

SEED = 0


class CycleGANTrainer(gan_trainer.GANTrainer):
    
    def __init__(
            self,
            batch_size,
            generator,
            discriminator,
            dataset_type,
            lr_generator,
            lr_discriminator,
            continue_training,
            checkpoint_step=10,
    ):
        super(CycleGANTrainer, self).__init__(
            batch_size,
            generator,
            discriminator,
            dataset_type,
            lr_generator,
            lr_discriminator,
            continue_training,
            checkpoint_step,
        )
    
    def train(self, dataset, num_epochs):
        train_step = 0
        test_seed = tf.random.normal([self.batch_size, 100])
        
        latest_checkpoint_epoch = self.regenerate_training()
        latest_epoch = latest_checkpoint_epoch * self.checkpoint_step
        num_epochs += latest_epoch
        for epoch in range(latest_epoch, num_epochs):
            for first_second_image_batch in dataset():
                train_step += 1
                print(train_step)
                gen_loss_b, dis_loss_b, gen_loss_a, dis_loss_a = self.train_step(
                    first_second_image_batch)
                with self.summary_writer.as_default():
                    tf.summary.scalar("generator_loss_b", gen_loss_b, step=train_step)
                    tf.summary.scalar("discriminator_loss_b", dis_loss_b, step=train_step)
                    tf.summary.scalar("generator_loss_a", gen_loss_a, step=train_step)
                    tf.summary.scalar("discriminator_loss_a", dis_loss_a, step=train_step)
                
                img_to_plot = visualization.generate_and_save_images(
                    generator_model=self.generator[0],
                    epoch=epoch + 1,
                    test_input=first_second_image_batch[0],
                    dataset_name=self.dataset_type + 'gen_a',
                    cmap='gray',
                    num_examples_to_display=1,
                )
                img_to_plot = visualization.generate_and_save_images(
                    generator_model=self.generator[1],
                    epoch=epoch + 1,
                    test_input=first_second_image_batch[1],
                    dataset_name=self.dataset_type + 'gen_b',
                    cmap='gray',
                    num_examples_to_display=1,
                )
            with self.summary_writer.as_default():
                tf.summary.image(
                    name='test_images',
                    data=np.reshape(img_to_plot, newshape=(1, 480, 640, 4)),
                    step=epoch,
                )
            
            if (epoch + 1) % self.checkpoint_step == 0:
                self.checkpoint.save(file_prefix=self.checkpoint_prefix)
    
    @tf.function
    def train_step(self, train_batch):
        first_dataset_batch, second_dataset_batch = train_batch
        generator_a, generator_b = self.generator
        discriminator_a, discriminator_b = self.discriminator
        with tf.GradientTape() as gen_tape_b, tf.GradientTape() as disc_tape_b, \
                tf.GradientTape() as gen_tape_a, tf.GradientTape() as disc_tape_a:
            fake_images_b = generator_b(first_dataset_batch, training=True)
            fake_images_a = generator_a(second_dataset_batch, training=True)
            
            real_output_b = discriminator_b(second_dataset_batch, training=True)
            fake_output_b = discriminator_b(fake_images_b, training=True)
            
            real_output_a = discriminator_a(first_dataset_batch, training=True)
            fake_output_a = discriminator_a(fake_images_a, training=True)
            
            generator_loss_b = losses.generator_loss(fake_output_b)
            discriminator_loss_b = losses.discriminator_loss(real_output_b, fake_output_b)
            
            generator_loss_a = losses.generator_loss(fake_output_a)
            discriminator_loss_a = losses.discriminator_loss(real_output_a, fake_output_a)
            
            # cycle losses
            cycle_image_a = generator_a(fake_images_b, training=True)
            cycle_image_b = generator_b(fake_images_a, training=True)
            
            cycle_loss_a = losses.cycle_loss(first_dataset_batch, cycle_image_a)
            cycle_loss_b = losses.cycle_loss(second_dataset_batch, cycle_image_b)
            
            total_cycle_loss = cycle_loss_a + cycle_loss_b
        
        gradients_of_generator_b = gen_tape_b.gradient(
            generator_loss_b + total_cycle_loss,
            generator_b.trainable_variables,
        )
        gradients_of_discriminator_b = disc_tape_b.gradient(
            discriminator_loss_b,
            discriminator_b.trainable_variables,
        )
        # gradients_of_cycle_b = disc_tape_b.gradient(
        #     total_cycle_loss,
        #     self.generator[1].trainable_variables,
        # )
        
        gradients_of_generator_a = gen_tape_a.gradient(
            generator_loss_a + total_cycle_loss,
            generator_a.trainable_variables,
        )
        gradients_of_discriminator_a = disc_tape_a.gradient(
            discriminator_loss_a,
            discriminator_a.trainable_variables,
        )
        # gradients_of_cycle_a = gen_tape_a.gradient(
        #     total_cycle_loss,
        #     self.generator[1].trainable_variables,
        # )
        
        self.generator_optimizer_b.apply_gradients(
            zip(gradients_of_generator_b, generator_b.trainable_variables))
        self.discriminator_optimizer_b.apply_gradients(
            zip(gradients_of_discriminator_b, discriminator_b.trainable_variables))
        
        self.generator_optimizer_a.apply_gradients(
            zip(gradients_of_generator_a, generator_a.trainable_variables))
        self.discriminator_optimizer_a.apply_gradients(
            zip(gradients_of_discriminator_a, discriminator_a.trainable_variables))
        
        return generator_loss_b, discriminator_loss_b, generator_loss_a, discriminator_loss_a
    
    def regenerate_training(self):
        latest_checkpoint_epoch = 0
        if self.continue_training:
            latest_checkpoint = tf.train.latest_checkpoint(self.checkpoint_path)
            if latest_checkpoint is not None:
                latest_checkpoint_epoch = int(latest_checkpoint[latest_checkpoint.index("-") + 1:])
                self.checkpoint.restore(latest_checkpoint)
            else:
                print('No checkpoints found. Starting training from scratch.')
        return latest_checkpoint_epoch

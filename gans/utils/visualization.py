import glob
import math
import os

import PIL
import imageio
import matplotlib.pyplot as plt
import numpy as np
from IPython import display

from gans.utils import constants


def make_gif_from_images(path, anim_file='dcgan.gif'):
    with imageio.get_writer(anim_file, mode='I') as writer:
        filenames = glob.glob(os.path.join(path, 'image*.png'))
        if not filenames:
            raise ValueError('Empty list of files to plot.')
        filenames = sorted(filenames, key=lambda s: int(s.split('_')[-1].replace('.png', '')))
        last = -1
        for i, filename in enumerate(filenames):
            frame = 2 * (i ** 0.5)
            if round(frame) > round(last):
                last = frame
            else:
                continue
            for _ in range(2):
                # frame = 2 * (i ** 0.5)
                # if round(frame) > round(last):
                #     last = frame
                # else:
                #     continue
                image = imageio.imread(filename)
                writer.append_data(image)
        image = imageio.imread(filename)
        writer.append_data(image)


def display_image(epoch_no):
    return PIL.Image.open('image_at_epoch_{:04d}.png'.format(epoch_no))


def generate_and_save_images(
        generator_model,
        epoch,
        test_input,
        dataset_name,
        cmap=None,
        num_examples_to_display=16,
):
    display.clear_output(wait=True)
    predictions = generator_model(test_input, training=False)
    if predictions.shape[0] < num_examples_to_display:
        raise ValueError("Input batch size cannot be less than number of example to display.")

    n = int(math.sqrt(num_examples_to_display))

    for i in range(num_examples_to_display):
        plt.subplot(n, n, i + 1)
        if generator_model.num_channels == 3:
            img_to_plot = predictions[i, :, :, :] * 127.5 + 127.5
        else:
            img_to_plot = predictions[i, :, :, 0] * 127.5 + 127.5
        plt.imshow(img_to_plot / 255, cmap=cmap)
        plt.axis('off')

    save_path = os.path.join(constants.SAVE_IMAGE_DIR, dataset_name)
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'image_at_epoch_{:04d}.png'.format(epoch)))
    im = np.asarray(
        PIL.Image.open(os.path.join(save_path, 'image_at_epoch_{:04d}.png'.format(epoch))))
    return im


def generate_and_save_images2(
        generator_model,
        epoch,
        test_input,
        dataset_name,
        cmap=None,
        num_examples_to_display=16,
):
    display.clear_output(wait=True)
    predictions = generator_model(test_input, training=False)
    import tensorflow as tf
    X1 = tf.random.uniform(shape=[5000], minval=-2, maxval=2)
    # X2 = X1 * X1
    X3 = X1 * X1 * X1
    # X4 = -(X1 * X1)
    X5 = -(X1 * X1 * X1)
    # DATA1 = tf.stack([X1, X2], axis=1)
    DATA2 = tf.stack([X1, X3], axis=1)
    # DATA3 = tf.stack([X1, X4], axis=1)
    DATA4 = tf.stack([X1, X5], axis=1)
    from matplotlib import pyplot as plt
    # plt.scatter(DATA1[:, 0], DATA1[:, 1])
    plt.scatter(DATA2[:, 0], DATA2[:, 1])
    # plt.scatter(DATA3[:, 0], DATA3[:, 1])
    plt.scatter(DATA4[:, 0], DATA4[:, 1])
    plt.scatter(predictions[:256, 0], predictions[:256, 1])
    plt.scatter(predictions[256:512, 0], predictions[256:512, 1])
    # plt.scatter(predictions[512:768, 0], predictions[512:768, 1])
    # plt.scatter(predictions[768:1024, 0], predictions[768:1024, 1])

    save_path = os.path.join(constants.SAVE_IMAGE_DIR, dataset_name)
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'image_at_epoch_{:04d}.png'.format(epoch)))
    im = np.asarray(
        PIL.Image.open(os.path.join(save_path, 'image_at_epoch_{:04d}.png'.format(epoch))))
    plt.clf()
    return im


def generate_images(
        generator_model,
        test_input,
        num_examples_to_display=16,
):
    predictions = generator_model(test_input, training=False)
    img_size = predictions.shape[1]
    if predictions.shape[0] < num_examples_to_display:
        raise ValueError("Input batch size cannot be less than number of example to display.")

    n = int(math.sqrt(num_examples_to_display))
    if generator_model.num_channels == 3:
        im = predictions[0, :, :, :] * 127.5 + 127.5
    else:
        im = predictions[0, :, :, 0] * 127.5 + 127.5
    for i in range(1, num_examples_to_display):
        if generator_model.num_channels == 3:
            img_to_plot = predictions[i, :, :, :] * 127.5 + 127.5
            im = np.concatenate([im, img_to_plot], axis=1)
        else:
            img_to_plot = predictions[i, :, :, 0] * 127.5 + 127.5
            im = np.concatenate([im, img_to_plot], axis=1)

    im = np.reshape(im, newshape=(1, 4 * img_size, 4 * img_size, -1))
    return im


def generate_and_save_images_in(
        generator_model,
        epoch,
        test_input,
        dataset_name,
        cmap=None,
        num_examples_to_display=16,
):
    display.clear_output(wait=True)
    predictions = generator_model(test_input, training=False)
    if predictions.shape[0] < num_examples_to_display:
        raise ValueError("Input batch size cannot be less than number of example to display.")

    n = int(math.sqrt(num_examples_to_display))

    for i in range(num_examples_to_display):
        plt.subplot(n, n, i + 1)
        if generator_model.num_channels == 3:
            img_to_plot = predictions[i, :, :, :] * 127.5 + 127.5
            img_to_plot = np.concatenate([test_input[i, :, :, :] * 127.5 + 127.5, img_to_plot],
                                         axis=1)
        else:
            img_to_plot = predictions[i, :, :, 0] * 127.5 + 127.5

        plt.imshow(img_to_plot / 255, cmap=cmap)
        plt.axis('off')

    save_path = os.path.join(constants.SAVE_IMAGE_DIR, dataset_name)
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, 'image_at_epoch_{:04d}.png'.format(epoch)))
    im = np.asarray(
        PIL.Image.open(os.path.join(save_path, 'image_at_epoch_{:04d}.png'.format(epoch))))
    return im


def plot_image_grid(generated_image):
    for i in range(generated_image.shape[0]):
        plt.subplot(4, 4, i + 1)
        plt.imshow(generated_image[i, :, :, 0] * 127.5 + 127.5, cmap='gray')
        plt.axis('off')
    plt.show()

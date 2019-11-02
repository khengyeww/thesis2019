import os
import torch
import argparse

from tqdm import tqdm

import time as date
from time import time as t

from model import HaoAndHuang2019
from spiking_neunet import Spiking
from utils import msg_wrapper


# Define dataset and number of input / output neurons.
dataset_name = 'MNIST'
n_inpt = 784
n_outpt = 10
# model_name = 'hao_2019'

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--n_neurons", type=int, default=100)
parser.add_argument("--n_epochs", type=int, default=1)
parser.add_argument("--n_train", type=int, default=None)
parser.add_argument("--n_test", type=int, default=None)
parser.add_argument("--n_workers", type=int, default=-1)
parser.add_argument("--exc", type=float, default=22.5)
parser.add_argument("--inh", type=float, default=120)
parser.add_argument("--norm_scale", type=float, default=0.1)
parser.add_argument("--theta_plus", type=float, default=0.05)
parser.add_argument("--time", type=int, default=350)
parser.add_argument("--dt", type=float, default=0.5)
parser.add_argument("--intensity", type=float, default=128)
parser.add_argument("--progress_interval", type=int, default=10)
parser.add_argument("--update_interval", type=int, default=3)#250)
parser.add_argument("--train", dest="train", action="store_true")
parser.add_argument("--test", dest="train", action="store_false") #TODO
parser.add_argument("--plot", dest="plot", action="store_true")
parser.add_argument("--gpu", dest="gpu", action="store_true")
parser.set_defaults(train=True, plot=False, gpu=False)

args = parser.parse_args()

seed = args.seed
n_neurons = args.n_neurons
n_epochs = args.n_epochs
n_train = args.n_train
n_test = args.n_test
n_workers = args.n_workers
exc = args.exc
inh = args.inh
norm_scale = args.norm_scale
theta_plus = args.theta_plus
time = args.time
dt = args.dt
intensity = args.intensity
progress_interval = args.progress_interval
update_interval = args.update_interval
train = args.train
plot = args.plot
gpu = args.gpu

# Setup pathnames for saving files.
datetime = date.strftime("%Y%m%d-%H%M%S")
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DIR_NAME = dataset_name.lower() + '-' + str(n_neurons) + '_' + datetime
RESULTS_PATH = os.path.join(ROOT_PATH, 'results')#, DIR_NAME)
# paths = [RESULTS_PATH]
# torch.set_printoptions(profile="full")

# Build network model.
network = HaoAndHuang2019(
    n_inpt=n_inpt,
    n_outpt=n_outpt,
    n_neurons=n_neurons,
    inh=inh,
    dt=dt,
    norm_scale=norm_scale,
    theta_plus=theta_plus,
    inpt_shape=(1, 28, 28),
)

# Setup network for training & testing.
snn = Spiking(
    network=network,
    n_outpt=n_outpt,
    results_path=RESULTS_PATH,
    dataset_name=dataset_name,
    seed=seed,
    n_workers=n_workers,
    time=time,
    dt=dt,
    intensity=intensity,
    update_interval=update_interval,
    plot=plot,
    gpu=gpu,
)

"""
    ### Training Session ###
"""
# Train the network.
msg = ["### Begin training. ###"]
msg_wrapper(msg, 1)
start = t()

for epoch in range(n_epochs):
    if epoch % progress_interval == 0:
        print("Progress: %d / %d (%.4f seconds)" % (epoch, n_epochs, t() - start))
        start = t()

    # Decide number of samples to use. Default to all samples.
    snn.train_network(n_train)
# snn.tryplot()
print("Progress: %d / %d (%.4f minutes)" % (epoch + 1, n_epochs, ((t() - start) / 60)))
print("Training complete.\n")

# ------------------------------------------------------------------------------- #

"""
    ### Testing Session ###
"""
# Test the network.
msg = ["### Begin testing. ###"]
msg_wrapper(msg, 1)
start = t()

# Decide number of samples to use. Default to all samples.
snn.test_network(n_test)

print("Testing complete. (%.4f minutes)\n" % ((t() - start) / 60))

# ------------------------------------------------------------------------------- #

# Print final train & test accuracy.
msg = snn.show_acc()
msg_wrapper(msg, 2)

# Save network & results.
snn.save_results()
snn.save_wrong_pred()
print("Saving network & results... ... ...done!\n")

import math
import argparse
import warnings

import flwr as fl
import tensorflow as tf
from tensorflow import keras as keras

parser = argparse.ArgumentParser(description="Flower Embedded devices")
parser.add_argument(
    "--server_address",
    type=str,
    default="0.0.0.0:8080",
    help=f"gRPC server address (deafault '0.0.0.0:8080')",
)
parser.add_argument(
    "--cid",
    type=int,
    required=True,
    help="Client id. Should be an integer between 0 and NUM_CLIENTS",
)
parser.add_argument(
    "--mnist",
    action="store_true",
    help="If you use Raspberry Pi Zero clients (which just have 512MB or RAM) use MNIST",
)

warnings.filterwarnings("ignore", category=UserWarning)
NUM_CLIENTS = 50


def prepare_dataset(use_mnist: bool):
    """Download and partitions the CIFAR-10/MNIST dataset."""
    if use_mnist:
        (x_train, y_train), testset = tf.keras.datasets.mnist.load_data()
    else:
        (x_train, y_train), testset = tf.keras.datasets.cifar10.load_data()
    partitions = []
    # We keep all partitions equal-sized in this example
    partition_size = math.floor(len(x_train) / NUM_CLIENTS)
    for cid in range(NUM_CLIENTS):
        # Split dataset into non-overlapping NUM_CLIENT partitions
        idx_from, idx_to = int(cid) * partition_size, (int(cid) + 1) * partition_size

        x_train_cid, y_train_cid = (
            x_train[idx_from:idx_to] / 255.0,
            y_train[idx_from:idx_to],
        )

        # now partition into train/validation
        # Use 10% of the client's training data for validation
        split_idx = math.floor(len(x_train_cid) * 0.9)

        client_train = (x_train_cid[:split_idx], y_train_cid[:split_idx])
        client_val = (x_train_cid[split_idx:], y_train_cid[split_idx:])
        partitions.append((client_train, client_val))

    return partitions, testset


class FlowerClient(fl.client.NumPyClient):
    """A FlowerClient that uses MobileNetV3 for CIFAR-10 or a much smaller CNN for
    MNIST."""

    def __init__(self, trainset, valset, use_mnist: bool):
        self.x_train, self.y_train = trainset
        self.x_val, self.y_val = valset
        # Instantiate model
        if use_mnist:
            # small model for MNIST
            self.model = model = keras.Sequential(
                [
                    keras.Input(shape=(28, 28, 1)),
                    keras.layers.Conv2D(32, kernel_size=(5, 5), activation="relu"),
                    keras.layers.MaxPooling2D(pool_size=(2, 2)),
                    keras.layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
                    keras.layers.MaxPooling2D(pool_size=(2, 2)),
                    keras.layers.Flatten(),
                    keras.layers.Dropout(0.5),
                    keras.layers.Dense(10, activation="softmax"),
                ]
            )
        else:
            # let's use a larger model for cifar
            self.model = tf.keras.applications.MobileNetV3Small(
                (32, 32, 3), classes=10, weights=None
            )
        self.model.compile(
            "adam", "sparse_categorical_crossentropy", metrics=["accuracy"]
        )

    def get_parameters(self, config):
        return self.model.get_weights()

    def set_parameters(self, params):
        self.model.set_weights(params)

    def fit(self, parameters, config):
        print("Client sampled for fit()")
        self.set_parameters(parameters)
        # Set hyperparameters from config sent by server/strategy
        batch, epochs = config["batch_size"], config["epochs"]
        # train
        self.model.fit(self.x_train, self.y_train, epochs=epochs, batch_size=batch)
        return self.get_parameters({}), len(self.x_train), {}

    def evaluate(self, parameters, config):
        print("Client sampled for evaluate()")
        self.set_parameters(parameters)
        loss, accuracy = self.model.evaluate(self.x_val, self.y_val)
        return loss, len(self.x_val), {"accuracy": accuracy}


def main():
    args = parser.parse_args()
    print(args)

    assert args.cid < NUM_CLIENTS

    use_mnist = args.mnist
    # Download CIFAR-10 dataset and partition it
    partitions, _ = prepare_dataset(use_mnist)
    trainset, valset = partitions[args.cid]

    # Start Flower client setting its associated data partition
    fl.client.start_client(
        server_address=args.server_address,
        client=FlowerClient(trainset=trainset, valset=valset, use_mnist=use_mnist).to_client(),
    )


if __name__ == "__main__":
    main()

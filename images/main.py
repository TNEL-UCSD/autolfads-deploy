import argparse
import os, pickle, shutil

# Don't log the TensorFlow info messages on imports
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"
import tensorflow as tf
from lfads_tf2.models import LFADS
from lfads_tf2.defaults import get_cfg_defaults
from lfads_tf2.tuples import BatchInput

from yacs.config import CfgNode as CN


def save_checkpoint_manual(model: LFADS, path: str):
    """
    Save model and optimizer weights. This is used to bootstrap a
    pretrained model instead of using the LFADS() built in
    checkpoint service (see Observation note in main)
    @param model LFADS
    @param path str
    """
    model_wts = [v.numpy() for v in model.trainable_variables]
    optim_wts = model.optimizer.get_weights()
    checkpoint = {"model": model_wts, "optimizer": optim_wts}
    with open(path, "wb") as fout:
        pickle.dump(checkpoint, fout)


def pprint(metrics: dict, fmt: str = "katib"):
    """
    Formatted print utility
    @param metrics dict
    @param fmt str - {"katib", None}
    """
    if fmt == "katib":
        # Format print to default Katib::StdOut to reduce need for additional user config
        # https://www.kubeflow.org/docs/components/katib/experiment/#metrics-collector
        print("epoch {}:".format(metrics["epoch"]))
        for k, v in metrics.items():
            if k == "epoch":
                continue
            print("{}={}".format(k, v))
        print()
    else:
        print(metrics)


# python3 main.py --data /share/data --checkpoint /share/output/lorenz --config-file /share/data/lorenz.yaml
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LFADS")
    parser.add_argument(
        "--data",
        nargs=1,
        type=str,
        dest="data_path",
        required=True,
        help="input data directory",
    )
    # Currently the checkpoints are written to $checkpoint_path/lfads_ckpts/most_recent/*
    parser.add_argument(
        "--checkpoint",
        nargs=1,
        type=str,
        dest="checkpoint_path",
        default="/var/log/katib/checkpoints/",
        help="checkpoint directory (resume and save)",
    )
    parser.add_argument(
        "--config-file",
        nargs=1,
        type=str,
        dest="config_file",
        required=False,
        help="config file to override defaults with",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
        help="number of epochs to train per generation (default: 50)",
    )
    # LFADS() currently combines checkpoint and summary writer outputs (nested)
    # parser.add_argument('--log-path', nargs=1, type=str, dest='log_dir',
    #                     default="/var/log/katib/tfevent/",
    #                     help="tfevent output path (default: /var/log/katib/tfevent/)")
    args, overrides = parser.parse_known_args()
    checkpoint_path = os.path.normpath(args.checkpoint_path[0])
    data_path = os.path.normpath(args.data_path[0])

    cfg = get_cfg_defaults()
    # Load overrides from file
    if args.config_file:
        cfg.merge_from_file(args.config_file[0])
    # Merge other overrides passed in via cli
    cfg.merge_from_list(overrides)
    # This is not recommended by yacs, but `--` is preferred for standard unix cli usage
    cfg.TRAIN.DATA.DIR = data_path
    cfg.TRAIN.MODEL_DIR = checkpoint_path
    cfg.TRAIN.TUNE_MODE = True
    cfg.TRAIN.PBT_MODE = True

    # Create the LFADS model
    model = LFADS(cfg_node=cfg)

    # Initialize the model weights and input shapes by passing noise
    mcfg = cfg.MODEL
    data_shape = (10, mcfg.SEQ_LEN, mcfg.DATA_DIM)
    output_seq_len = mcfg.SEQ_LEN - mcfg.IC_ENC_SEQ_LEN
    sv_mask_shape = (10, output_seq_len, mcfg.DATA_DIM)
    ext_input_shape = (10, output_seq_len, mcfg.EXT_INPUT_DIM)
    batch_of_noise = BatchInput(
        tf.random.uniform(shape=data_shape, dtype=tf.float32),
        tf.ones(shape=sv_mask_shape, dtype=tf.bool),
        tf.random.uniform(shape=ext_input_shape, dtype=tf.float32),
    )
    model.train_call(batch_of_noise)

    # Observation: loading from a checkpoint without having to mess with paths
    #              could be supported by LFADS(), though the usecase might only
    #              be for resuming training in modes like PBT.
    checkpoint_most_recent = os.path.join(checkpoint_path, "lfads_ckpts", "most_recent")
    resume_study = (
        os.path.exists(checkpoint_most_recent)
        and len(os.listdir(checkpoint_most_recent)) > 0
    )
    if resume_study:
        print("Resuming from manual checkpoint")
        ## Load Checkpoint (Manual)
        with open(
            os.path.join(checkpoint_most_recent, "manual_checkpoint.pkl"), "rb"
        ) as fin:
            checkpoint = pickle.load(fin)
        # Transfer the trainable weights
        for v, array in zip(model.trainable_variables, checkpoint["model"]):
            v.assign(array)

        # cur_epoch and cur_step need to be overridden
        last_row = model.train_df.iloc[-1:]
        model.cur_step.assign(last_row["step"].values[0])
        model.cur_epoch.assign(last_row.index.values[0])

        # use fake gradient to let optimizer init the weights
        grad_vars = model.trainable_weights
        zero_grads = [tf.zeros_like(w) for w in grad_vars]
        model.optimizer.apply_gradients(zip(zero_grads, grad_vars))
        # Copy the optimizer momentum terms
        model.optimizer.set_weights(checkpoint["optimizer"])

    num_epochs = args.epochs
    # The first generation always completes ramping
    if model.cur_epoch < model.last_ramp_epoch:
        num_epochs += model.last_ramp_epoch
    print("Target epochs: {}\n".format(num_epochs))

    for i in range(num_epochs):
        metrics = model.train_epoch()
        pprint(metrics)
        save_checkpoint_manual(
            model, os.path.join(checkpoint_most_recent, "manual_checkpoint.pkl")
        )

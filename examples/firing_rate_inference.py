import argparse
import logging
import warnings
import os

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({"font.size": 12})
import seaborn as sns

try:
    from nlb_tools import make_tensors, nwb_interface
except ModuleNotFoundError:
    print("nlb_tools not found." "Make sure that you have installed them.")
    os.kill(os.getpid(), 9)

PARAMS = {
    "mc_maze": {
        "spk_field": "spikes",
        "hospk_field": "heldout_spikes",
        "behavior_source": "data",
        "behavior_field": "hand_vel",
        "lag": 100,
        "make_params": {
            "align_field": "move_onset_time",
            "align_range": (-250, 450),
        },
        "eval_make_params": {
            "align_field": "move_onset_time",
            "align_range": (-250, 450),
        },
        "fp_len": 200,
        "psth_params": {
            "cond_fields": ["trial_type", "trial_version"],
            "make_params": {
                "align_field": "move_onset_time",
                "align_range": (-250, 450),
            },
            "kern_sd": 30,
        },
    }
}

def prep_mask(dataset, trial_split):
    """
    Converts trial split to boolean array and combines multiple splits if a list is provided
    
    Parameters
    ----------
    dataset: NWBDataset
        NWBDataset that trial mask is made for
    trial_split : {'train', 'val', 'test'}, array-like, or list, optional
        Trial splits to include in mask.

    Returns
    -------
    np.array
        Boolean array indicating which trials are within
        provided split(s)
    """
    split_to_mask = (
        lambda x: (dataset.trial_info.split == x) if isinstance(x, str) else x
    )
    if isinstance(trial_split, list):
        trial_mask = np.any([split_to_mask(split) for split in trial_split], axis=0)
    elif isinstance(trial_split, str):
        trial_mask = split_to_mask(trial_split)
    elif isinstance(trial_split, np.ndarray):
        trial_mask = np.isin(np.arange(len(dataset.trial_info.split)), trial_split)
    elif isinstance(trial_split, pd.Series):
        trial_mask = split_to_mask(trial_split)
    return trial_mask



if __name__ == "__main__":
    """
    Example script command:
        python3 firing_rate_inference.py
            --model_dir <model output data>
            --input_dir <model input data>
            --dataset_name mc_maze
            --dataset_dir <DANDI input data>
            --output_dir <>
            --ch_list 16 23 48
            --cond_list 83 96 7 35 56 61
    """
    parser = argparse.ArgumentParser(
        description="Generate firing rate figures"
    )
    parser.add_argument(
        "--model_dir",
        nargs=1,
        type=str,
        dest="model_dir",
        required=True,
        help="Directory for the trained model",
    )
    parser.add_argument(
        "--input_dir",
        nargs=1,
        type=str,
        dest="input_dir",
        required=True,
        help="Directory for the input data",
    )
    parser.add_argument(
        "--dataset_dir",
        nargs=1,
        type=str,
        dest="dataset_dir",
        required=True,
        help="Directory for the NWB dataset (DANDI download directory); Used for estimating the smoothed spikes and PSTH",
    )
    parser.add_argument(
        "--output_dir",
        nargs=1,
        type=str,
        dest="output_dir",
        required=True,
        help="Directory to save the generated figures",
    )
    parser.add_argument(
        "--dataset_name",
        nargs=1,
        type=str,
        dest="dataset_name",
        required=True,
        help="Reference name for the NWB dataset",
    )
    parser.add_argument(
        "--ch_list",
        nargs="*",
        type=int,
        dest="ch_list",
        required=True,
        help="List of channels / neurons to visualize ",
    )
    parser.add_argument(
        "--cond_list",
        nargs="*",
        type=int,
        dest="cond_list",
        required=True,
        help="List of conditions to visualize",
    )
    parser.add_argument(
        "--verbose",
        dest="is_verbose",
        action="store_true",
        default=False,
        help="Display debug messages",
    )
    args = parser.parse_args()

    # Construct Logger (stdio)
    console_handler = logging.StreamHandler()
    formatter = None
    if args.is_verbose:
        console_handler.setLevel(logging.DEBUG)
        # time - service_name - level - thread name[calling function] - message
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s -  %(message)s"
        )
    else:
        console_handler.setLevel(logging.INFO)
        # time - service_name - level - message
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    console_handler.setFormatter(formatter)
    # Add the log configurations to the root logger
    logging.getLogger("").setLevel(logging.DEBUG)
    logging.getLogger("").addHandler(console_handler)
    # Get the logger instantiation
    logger = logging.getLogger("autolfads_firing_rate_figs")
    logger.debug("Logger successfully initialized")
    logger.info("Runtime flags: " + str(vars(args)))

    model_dir = args.model_dir[0]
    input_dir = args.input_dir[0]
    dataset_name = args.dataset_name[0]
    dataset_dir = args.dataset_dir[0]
    output_dir = args.output_dir[0]
    ch_list = args.ch_list
    cond_list = args.cond_list

    data_loadpath = f"{input_dir}/{dataset_name}_train_lfads.h5"
    fr_loadpath = f"{model_dir}/{dataset_name}_autolfads_val_submission.h5"

    logging.info("Load in NWB dataset")
    # Generate the smoothed firing rate directly from the nlb_tools package
    datapath = f"{dataset_dir}/{dataset_name}/sub-Jenkins/"
    dataset = nwb_interface.NWBDataset(
        datapath, skip_fields=["joint_ang", "joint_vel", "muscle_len", "muscle_vel"]
    )

    logging.info("Obtain the train/val/test index from the input data")
    data_loadpath = f"{input_dir}/{dataset_name}_train_lfads.h5"
    h5file = h5py.File(data_loadpath, "r")
    train_inds = h5file["train_inds"][()].astype(np.int32)
    valid_inds = h5file["valid_inds"][()].astype(np.int32)

    logging.info("Smooth the spike train")
    params = PARAMS[dataset_name].copy()
    psth_params = params.get("psth_params", None)
    dataset.smooth_spk(
        psth_params["kern_sd"],
        signal_type=["spikes", "heldout_spikes"],
        overwrite=True,
        ignore_nans=True,
    )
    bin_width = 5
    dataset.resample(bin_width)
    smoothed_data_dict = make_tensors.make_train_input_tensors(
        dataset,
        dataset_name,
        ["train", "val"],
        save_file=False,
        include_forward_pred=False,
    )
    smoothed_rates = np.dstack(
        [
            smoothed_data_dict["train_spikes_heldin"],
            smoothed_data_dict["train_spikes_heldout"],
        ]
    )
    target_rates = smoothed_rates[valid_inds, :, :]

    logging.info("Compute the trial-averaged PSTH")
    train_val_mask = prep_mask(dataset, ["train", "val"])
    train_val_inds = np.where(train_val_mask)[0]
    train_inds_dataset = train_val_inds[train_inds]
    valid_inds_dataset = train_val_inds[valid_inds]
    train_mask = prep_mask(dataset, train_inds_dataset)
    eval_mask = prep_mask(dataset, valid_inds_dataset)
    ignore_mask = ~(train_mask | eval_mask)
    (train_cond_idx, eval_cond_idx), psths, good_comb = make_tensors._make_psth(
        dataset, train_mask, eval_mask, ignore_mask, **psth_params
    )

    logging.info("Obtain the LFADS inferred Firing Rate")
    fr_loadpath = f"{model_dir}/{dataset_name}_autolfads_val_submission.h5"
    h5file = h5py.File(fr_loadpath, "r")
    output_dict = make_tensors.h5_to_dict(h5file)
    # eval_rates: trials x bins x channels array of LFADS-inferred firing rates
    eval_rates_heldin = output_dict[dataset_name]["eval_rates_heldin"][()].astype(
        "float"
    )
    eval_rates_heldout = output_dict[dataset_name]["eval_rates_heldout"][()].astype(
        "float"
    )
    eval_rates = np.concatenate([eval_rates_heldin, eval_rates_heldout], axis=-1)

    logging.info("Plot the smoothed spike rate, PSTH, inferred firing rate")
    palette = [
        col
        for i, col in enumerate(
            sns.color_palette(palette="bright", n_colors=10, desat=0.9)
        )
        if i in [0, 1, 2, 4, 6, 8]
    ]
    # specify the channels and conditions to plot
    n_ch_plt = len(ch_list)  # number of channels to plot
    n_cond_plt = len(cond_list)  # number of conditions to plot
    fig, axes = plt.subplots(
        ncols=n_ch_plt, nrows=3, figsize=(n_ch_plt * 4, 12), sharey="row"
    )

    for i_ch, ch in enumerate(ch_list):
        for i_cond, cond in enumerate(cond_list):
            cond_trial = eval_cond_idx[cond]

            # Trial-averaged PSTH
            psth_cond = psths[cond, :, ch][~np.isnan(psths[cond, :, ch])]
            axes[1, i_ch].plot(
                np.array(range(len(psth_cond))) * bin_width,
                psth_cond * 1000,
                label=f"Cond {cond}",
                color=palette[i_cond],
                linewidth=2,
            )

            # Smoothing
            cond_smooth_rates = np.array(
                [target_rates[itrial] * 1000 for itrial in cond_trial]
            )
            axes[0, i_ch].plot(
                np.array(range(np.shape(cond_smooth_rates[:, :, ch])[1])) * bin_width,
                cond_smooth_rates[:, :, ch].T,
                color=palette[i_cond],
            )

            # LFADS inferred Firing Rate
            cond_rates = np.array([eval_rates[itrial] * 1000 for itrial in cond_trial])
            axes[2, i_ch].plot(
                np.array(range(np.shape(cond_rates[:, :, ch])[1])) * bin_width,
                cond_rates[:, :, ch].T,
                color=palette[i_cond],
            )

        axes[0, i_ch].set_title(f"Neuron {ch}")
        axes[0, i_ch].set_xlabel("")
        axes[1, i_ch].set_xlabel("")
        axes[2, i_ch].set_xlabel("Time (ms)")

    # Consistent ylim for PSTH and inferred firing rate
    ylim_u = 0
    ylim_l = 0
    ylim_ur = 0
    ylim_lr = 0
    for i_ch, ch in enumerate(ch_list):  # for each channel
        for i in range(1, 3):
            psth_ylim = axes[i, i_ch].get_ylim()
            ylim_u = max(ylim_u, psth_ylim[1])
            ylim_l = min(ylim_l, psth_ylim[0])
        rate_ylim = axes[0, i_ch].get_ylim()
        ylim_ur = max(ylim_ur, rate_ylim[1])
        ylim_lr = min(ylim_lr, rate_ylim[0])

    trial_offset = 0 - params["make_params"]["align_range"][0]
    for i_ch, ch in enumerate(ch_list):  # for each channel
        axes[0, i_ch].vlines(trial_offset, ylim_ur, ylim_lr, "k", linestyles="dashed")
        for i in range(1, 3):
            axes[i, i_ch].set_ylim([ylim_l, ylim_u])
            axes[i, i_ch].vlines(trial_offset, ylim_l, ylim_u, "k", linestyles="dashed")

    axes[1, 0].set_ylabel("Trial-Averaged PSTH (rates/s)")
    axes[0, 0].set_ylabel("Smoothing (rates/s)")
    axes[2, 0].set_ylabel("Inferred Firing Rates (rates/s)")
    plt.tight_layout()

    plt.savefig(f"{output_dir}/firing_rate_inference.pdf")
    plt.savefig(f"{output_dir}/firing_rate_inference.png", transparent=True)

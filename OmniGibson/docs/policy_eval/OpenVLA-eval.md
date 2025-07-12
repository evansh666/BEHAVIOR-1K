# Baseline Evaluation - OpenVLA-OFT


## Build Connection from Server Side

### Clone OpenVLA-OFT repo and install environment
Check https://github.com/moojink/openvla-oft/tree/main

### Deploy connection

Launch the VLA server on the machine that has the GPU you will use to run model inference (using the `openvla-oft` conda environment). Below is a sample command for this (change as needed):
```
python vla-scripts/deploy.py \
  --pretrained_checkpoint /PATH/TO/FINETUNED/MODEL/CHECKPOINT/DIR/ \
  --use_l1_regression True \
  --use_film True \
  --num_images_in_input 3 \
  --use_proprio True \
  --center_crop True \
  --unnorm_key NAME_OF_DATASET_USED_IN_CHECKPOINT
```

## Client Connection
install dependencies:

    pip install requests json-numpy

## Start evaluation
Note that if your server is not accessible on the open web, you can use ngrok, or forward ports to your client via ssh:
`ssh -L 8000:localhost:8000 ssh USERNAME@<SERVER_IP>`

Note that if you are using HPC GPU nodes to deploy server, and accessing outside the cluster
`ssh -L 8000:NODE_IP:8000 ssh USERNAME@<SERVER_IP>`

Specify host and port on `Omnigibson/omnigibson/learning/configs/policy/openvla.yaml`
Then, start evaluation on another terminal:
```
	cd Omnigibson/omnigibson/learning
    python eval.py --policy=openvla task=picking_up_trash
```

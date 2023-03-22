#!/bin/bash

VERSION=latest

nvidia-smi > /dev/null 2>&1;
if [[ $? -gt 0 ]]; then 
	docker run --rm -it -v $(pwd):/share ucsdtnel/autolfads:${VERSION} \
		--data /share/data \
		--checkpoint /share/container_output \
		--config-file /share/data/config.yaml
else 
	docker run --rm --runtime=nvidia --gpus='"device=0"' -it -v $(pwd):/share ucsdtnel/autolfads:${VERSION}-gpu \
		--data /share/data \
		--checkpoint /share/container_output \
		--config-file /share/data/config.yaml
fi

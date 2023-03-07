#!/bin/bash

docker run --rm -it -v $(pwd):/share ucsdtnel/autolfads:latest \
	--data /share/data \
	--checkpoint /share/container_output \
	--config-file /share/data/config.yaml

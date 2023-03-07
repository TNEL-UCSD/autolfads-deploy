#!/bin/bash

docker run --rm -it -v $(pwd):/share ucsdtnel/autolfads:$TAG \
	--data /share/data \
	--checkpoint /share/container_output \
	--config-file /share/data/config.yaml

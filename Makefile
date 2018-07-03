test:
	docker run -it --rm \
		-v $(PWD):/src \
		-e http_proxy=$(http_proxy) \
		-e https_proxy=$(https_proxy) \
		themattrix/tox-base \
		tox
		#/bin/sh

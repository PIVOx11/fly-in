MAP = maps/easy/01_linear_path.txt

run:
	uv run main.py ${MAP}

install_maps:
	wget https://cdn.intra.42.fr/document/document/53960/maps.tar.gz
	@tar -xf maps.tar.gz
	@rm maps.tar.gz

clean:
	rm -rf __pycache__

flake:
	flake8

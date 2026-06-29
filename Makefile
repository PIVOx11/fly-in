MAP = maps/easy/01_linear_path.txt

run:
	uv run __main__.py ${MAP}

install_maps:
	wget https://cdn.intra.42.fr/document/document/49913/maps.tar.gz
	@tar -xf maps.tar.gz
	@rm -rf maps.tar.gz

clean:
	rm -rf src/__pycache__

flake:
	flake8 __main__.py src/ 

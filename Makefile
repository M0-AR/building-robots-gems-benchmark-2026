.PHONY: setup run verify test fetch docker-up docker-verify clean
setup:
	pip install -r requirements.txt
fetch:
	python scripts/fetch_live_data.py
run:
	mkdir -p results/figures
	python scripts/run_all.py
verify:
	python scripts/verify.py
test:
	pytest -q
docker-up:
	docker compose up --build
docker-verify:
	docker compose run gems-verify
clean:
	rm -rf results/*.json results/figures/*.png __pycache__

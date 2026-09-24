.PHONY: install smoke regression test report clean lint

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

test:
	behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results -f pretty

smoke:
	behave --tags=@smoke -f allure_behave.formatter:AllureFormatter -o reports/allure-results -f pretty

regression:
	behave --tags=@regression -f allure_behave.formatter:AllureFormatter -o reports/allure-results -f pretty

users:
	behave features/users -f pretty

report:
	allure generate reports/allure-results -o reports/allure-report --clean
	allure open reports/allure-report

serve:
	allure serve reports/allure-results

lint:
	flake8 src config features --max-line-length=100

clean:
	rm -rf reports logs .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

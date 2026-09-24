# Capstone 3 — Python API Automation Framework (Requests + Behave BDD + Allure)


A production-shaped API automation framework for the User Management API of
[jsonplaceholder.typicode.com](https://jsonplaceholder.typicode.com/), built with
layered design so the same framework can point at any REST service by changing one
config file.

---


## 1. Architecture at a glance
```
Feature files (.feature)      <- business language, no code
        |
Step definitions              <- translate English to method calls, assert results
        |
Service objects (endpoints/)  <- one class per API resource, owns URLs & payloads
        |
APIClient (core/)             <- the only place that touches `requests`
        |
Config + Auth + Logger        <- environment switching, credentials, traceability
```
Rules that keep it maintainable:


- Step definitions never build a URL and never import `requests`.
- Service objects never assert — they return the `Response`.
- Only `APIClient` creates a session, so retries, timeouts, logging and Allure
  attachments are implemented once and apply everywhere.


---


## 2. File structure


```
api_test_framework/
├── behave.ini                      # Behave runner config (paths, formatters, userdata
├── requirements.txt
├── Makefile                        # make smoke / make regression / make report
├── .env                            # template for secrets (never commit .env)
├── .gitignore
│
├── config/
│   ├── config.yaml                 # qa / staging / prod blocks, ${ENV_VAR} placeholder
│   └── config_loader.py            # loads YAML, picks env, resolves env vars
│
├── src/
│   ├── core/
│   │   ├── api_client.py           # requests.Session wrapper: retries, timeout, logging, Allure
│   │   ├── auth.py                 # NoAuth / Bearer / Basic / ApiKey / OAuth2 strategies
│   │   ├── logger.py               # console + per-run file logging
│   │   └── exceptions.py           # framework-specific errors
│   │
│   ├── endpoints/
│   │   ├── base_endpoint.py        # URL joining helper, shared logger
│   │   ├── users_api.py            # get_all / get_by_id / search / create / update / patch / delete
│   │   
│   │
│   ├── models/
│   │   └── user.py                 # User dataclass + to_payload() / from_response()
│   │
│   ├── schemas/
│   │   ├── user_schema.json
│   │   ├── users_list_schema.json
│   │   
│   │
│   └── utils/
│       ├── assertions.py           # hard asserts + SoftAssert + dotted-path lookup
│       ├── json_schema_validator.py
│       ├── data_generator.py       # Faker-based unique payloads, invalid payload cat
│       └── file_utils.py           # static fixture loading
│
├── features/
│   ├── environment.py              # before_all / before_scenario / after_step hooks
│   ├── users/
│   │   ├── get_users.feature
│   │   ├── create_user.feature
│   │   ├── update_user.feature
│   │   └── delete_user.feature
│   ├── steps/
│   │   ├── common_steps.py         # status, schema, timing, field assertions
│   │   ├── user_steps.py           # user domain actions
│   └── test_data/
│       └── users.json
│
├── .github/workflows/api-tests.yml
├── reports/                        # allure-results, allure-report, junit
└── logs/                           # timestamped run logs
```

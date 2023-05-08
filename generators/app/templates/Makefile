# MAKEFILE META
APP_NAME ?= <%= packageName %>
FIR_PROJ ?= <%= firebaseProject %>
GCLOUD_ORG ?= <%= gcloudOrgIdentifier %>
GCLOUD_REGION ?= <%= gcloudRegion %>
GCLOUD_SQL_TIER ?= db-f1-micro
GCLOUD_BILLING_ACCOUNT ?= <%= gcloudBillingAccountIdentifier %>

# Create stamps directory
.stamps:
	@mkdir -p $@


# GENERIC

# Run pip install (both main and dev dependencies)
.PHONY: | pip
pip:
	. .venv/bin/activate; pip install -U -r requirements.txt && pip install -U -r requirements-dev.txt

.PHONY: | auth
auth:
	gcloud auth login
	firebase login
	echo "Authentication successful."


# PREPARE 

# Create Python virtualenv and install dependencies
.venv:
	python -m venv .venv
	@touch $@

node_modules:
	npm install

.PHONY: | prepare
prepare: | .venv pip node_modules
	echo "Codebase setup completed."


# INFRASTRUCTURE

# Create the Firebase project in a new Google Cloud project
.stamps/firebase-project.created.perm: | .stamps
	firebase projects:create $(FIR_PROJ) -n $(APP_NAME) -o $(GCLOUD_ORG) --non-interactive
	@touch $@

.stamps/gcloud-billing.linked.perm: | .stamps
	gcloud alpha billing accounts projects link $(FIR_PROJ) --billing-account $(GCLOUD_BILLING_ACCOUNT) --quiet
	@touch $@

# Enable Google Cloud sqladmin.googleapis.com API
.stamps/gcloud-apis.enabled.perm: | .stamps
	gcloud services enable sqladmin.googleapis.com secretmanager.googleapis.com --project $(FIR_PROJ) --quiet
	@touch $@

.stamps/gcloud-app-engine.created.perm: | .stamps
	gcloud app create --region $(GCLOUD_REGION) --project $(FIR_PROJ) --quiet
	@touch $@

# Create Google Cloud SQL Postgres database instance
.stamps/gcloud-cloud-sql-instance.created.perm: | .stamps .stamps/gcloud-apis.enabled.perm
	gcloud sql instances create $(FIR_PROJ)-postgres --project $(FIR_PROJ) --database-version POSTGRES_13 --tier $(GCLOUD_SQL_TIER) --region $(GCLOUD_REGION) --quiet
	@touch $@

# Create Postgres database on new instance
.stamps/gcloud-cloud-sql-database.created.perm: | .stamps .stamps/gcloud-cloud-sql-instance.created.perm
	gcloud sql databases create $(APP_NAME) --instance $(FIR_PROJ)-postgres --project $(FIR_PROJ) --quiet
	@touch $@

# Create Postgres database user on new instance
.stamps/gcloud-cloud-sql-database-user.created.perm: | .stamps .stamps/gcloud-cloud-sql-database.created.perm
	gcloud sql users create $(APP_NAME) --instance $(FIR_PROJ)-postgres --password $(DB_PASSWORD_PROD) --project $(FIR_PROJ) --quiet
	@touch $@

# Create secrets file (sensitive settings variables) in Google Cloud Secret Manager
.stamps/gcloud-secrets.created.perm: | .stamps
	fir_service_account_email := $(shell gcloud iam service-accounts list --project $(FIR_PROJ) --format="get(email)" --quiet | grep -Eo '^firebase-adminsdk-\w+@$(FIR_PROJ)\.iam\.gserviceaccount\.com$$')
	gcloud secrets create backend_settings --data-file .env-prod --project $(FIR_PROJ) --quiet
	gcloud secrets add-iam-policy-binding backend_settings --member serviceAccount:$(fir_service_account_email) --role roles/secretmanager.secretAccessor --project $(FIR_PROJ) --quiet
	@touch $@

.stamps/gcloud-firebase-admin-service-account-key.created.perm: | .stamps
	fir_service_account_email := $(shell gcloud iam service-accounts list --project $(FIR_PROJ) --format="get(email)" --quiet | grep -Eo '^firebase-adminsdk-\w+@$(FIR_PROJ)\.iam\.gserviceaccount\.com$$')
	gcloud iam service-accounts keys create firebase-admin-service-account.json --iam-account=$(fir_service_account_email) --quiet --project $(FIR_PROJ)
	gcloud secrets create firebase_admin_service_account_key --data-file firebase-admin-service-account.json --quiet --project $(FIR_PROJ)
	@touch $@

.stamps/infrastructure-setup.done: | .stamps .stamps/firebase-project.created.perm .stamps/gcloud-billing.linked.perm .stamps/gcloud-apis.enabled.perm .stamps/gcloud-cloud-sql-database-user.created.perm .stamps/gcloud-secrets.created.perm .stamps/gcloud-firebase-admin-service-account-key.created.perm
	@touch $@

.PHONY: check-password-in-env
check-password-in-env:
	test -n "$(DB_PASSWORD_PROD)"

.PHONY: | infrastructure
infrastructure: | check-password-in-env .stamps/infrastructure-setup.done
	echo "Infrastructure created"


# DEV

.PHONY: | secrets
secrets:
	echo "Getting latest environment settings and secrets from Google Cloud Secret Manager"
	gcloud secrets versions access latest --secret backend_settings > .env-prod --project=$(FIR_PROJ)
	gcloud secrets versions access latest --secret firebase_admin_service_account_key > firebase-admin-service-account.json  --project=$(FIR_PROJ)


# TEST

.PHONY: | test-backend
test-backend:
	echo "BE tests not implemented yet."

.PHONY: | test-rules
test-rules:
	npm test

.PHONY: | test
test: test-rules
	echo "All test suites ran successfully."


# DEPLOYMENT

.PHONY: | deploy
deploy:
	gcloud app deploy --project=$(FIR_PROJ)

.PHONY: | deploy-secrets
deploy-secrets:
	gcloud secrets versions add backend_settings --data-file .env-prod --project=$(FIR_PROJ)

.PHONY: | deploy-rules
deploy-rules:
	firebase deploy --only firestore:rules --project $(FIR_PROJ)

# <%= productName %> backend

Welcome to your latest backend project! This template contains everything you need to deploy a lightweight API service and task queue system that maintains a PostgreSQL database holding all of your important business data.

It also integrates with Firebase Auth and Firestore so you can:

- Populate and syncronize business data in Firestore so it can be consumed by the mobile app
- Sync user data from Firestore and Firebase auth to store valuable, non-ephemeral user data and aid product analytics.

The backend is your central point of integration with third-party services and data.

It is serverless so when API calls or tasks aren't running, the service scales to 0 and becomes zero-cost. Only the database instance remains running.

Although the backend service is lightweight, can evolved into microservices and is very scaleable; the database (especially at low-tier) is not. The backend is not meant to scale to your app's userbase growth. So, expose API endpoints to the app only when it's really needed (e.g. for transactional calls on things like account data. For the most part you should use the backend internally, for API integrations and background tasks that populate, transform and maintain your value business data. It is supposed to scale well as your business grows in complexity (think more background tasks and integrations).

At this level of scale, the backend remains incredibly low cost to run.

And this is part of the reason why we use Firestore as a mobile middleware for the mobile app clients. The mobile app doesn't usally communicate with the backend directly, it gets data from Firestore. Firestore will scale infinitely and there is no overhead cost to that scale. Also, clients will intelligently cache both reads and writes handling connection interruption seamlessly. It is a cheap, smart caching layer for emphemeral data.

![Startup factory architecture](doc_architecture.jpg 'Startup factory architecture')

## Cross-platform development

You don't need a mac or linux machine to develop here. We use the `.devcontainer` standard so you can load VS Code inside a disposable linux container which has all the environment tools you need. No configuration required!

## Getting started!

### Step one: download and install prerequisites

Download Docker Desktop for your platform here: https://www.docker.com/products/docker-desktop/

Inside VS Code, install the `Dev Containers` extension.

### Step two: open VS Code

Open the codebase in VS Code. A notification should pop up and ask if you want to `Reopen in container`. Do that and VS Code will build and start the dev container and then reopen the codebase inside the container environment.

If this prompt doesn't show you cna use the remote connection menu (bottom left on the toolbar with a `><` icon). In the menu select `Reopen in container`.

![Remote connection menu](docs_remote_connection_menu.jpg 'VS Code remote connection menu')

### Step three: open a VS Code terminal and run `make prepare`

Go `Terminal > New Terminal` and type

```
make prepare
```

This will authenticate the Firebase and Google Cloud SDKs service.

## Creating infrastructure post generation 🚀

**Skip this if the project and cloud services have already been created.**

Post-generation means you'll have just started a backend on a new project. You haven't created BE infrastructure in Google Cloud yet.

Even though you _can_ start development without creating cloud infrastructure (A Firebase / Google Cloud project, App Engine app, Cloud SQL Postgres database, secret storage etc...) you should create this immediately so you can get in the habit of deploying frequently and seeing progress in production.

The required cloud infrastructure can be created easily via a Makefile script, it takes care of running the exact `firebase` and `gcloud` CLI commands for you.

### Run `make infrastructure`

This will:

- Enable the required Google APIs
- Create a managed PostgreSQL database instance, database and user via Google Cloud SQL
- Create the required keys and secrets and store them in Secret Manager

Steps:

1. Set `DB_PASSWORD_PROD` in `src/backend/.env` and `src/backend/.env-prod`.
2. Run the infrastructure make target:

From a VS Code terminal run

```
make infrastructure
```

Ensure the script finishes. It can take a long while to create Cloud SQL instances, so be patient! If the script errors out or you `Ctrl + C` it half way through don't worry, if you run it again it will pick up where it left off thanks to the `.stamps/` created.

3. Commit the `*.perm` stamps created in `.stamps/`. This will indicate that a particular cloud service was created and/or configured.

#### ⚠️ Note

If you already have a Firebase project created (e.g. if you created one first via the app codebase) then you can specify to use that existing project.

_This shouldn't be used to integrate into a much larger existing Google Cloud project._

To do this:

1. Manually create the `.stamps/firebase-project.created.perm` stamp:

```
touch .stamps/firebase-project.created
```

2. Set `FIR_PROJ` in `src/backend/.env` to the ID of your existing Firebase project.

3. Run `make infrastructure`
4. Don't forget to commit the new stamps.

### Run `make deploy`

This will make the first deployment of the app to AppEngine

### Enable and configure Identity-Aware Proxy (IAP)

Go to the following page on the Google Cloud Console:

https://console.cloud.google.com/security/iap?serviceId=default&project=<%= firebaseProject %>

Enable IAP on the App Engine app.

## Getting started on an existing project 🙋‍♀️

If the project has already been created and you've just cloned this repo you'll need to download secrets (keys) so your local environment can access resources in the cloud.

Do this via:

```
make secrets
```

## Development 👩‍💻

## Testing ✅

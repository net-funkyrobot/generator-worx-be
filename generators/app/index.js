var Generator = require('yeoman-generator');
var path = require('path');
var passwordGenerator = require('generate-password');

module.exports = class extends Generator {
    async prompting() {
        const prompts = [
            {
                type: 'input',
                name: 'productName',
                message: "What is your product's name?",
                validate: (answer) =>
                    answer.match(
                        /^[A-Za-z]{1}[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$/
                    ) != null,
            },
            {
                type: 'input',
                name: 'orgIdentifier',
                message:
                    'Your organisation identifier, in reverse domain name notation',
                store: true,
            },
            {
                type: 'input',
                name: 'gcloudOrgIdentifier',
                message: 'Your Google Cloud organisation identifier',
                store: true,
            },
            {
                type: 'input',
                name: 'gcloudBillingAccountIdentifier',
                message: 'Your Google Cloud billing account identifier',
                store: true,
            },
            {
                type: 'list',
                name: 'gcloudRegion',
                message: 'Desired Google Cloud region',
                choices: [
                    'europe-west2',
                    'europe-west3',
                    'europe-central2',
                    'europe-west6',
                    'us-west1',
                    'us-west2',
                    'us-west3',
                    'us-west4',
                    'us-west4',
                    'northamerica-northeast1',
                    'us-east1',
                    'us-east4',
                ],
                store: true,
            },
            {
                type: 'password',
                name: 'prodDbPassword',
                message: 'Enter a secure production database user password',
            },
        ];

        this.answers = await this.prompt(prompts);

        this.packageName = this.answers.productName
            .toLowerCase()
            .replace(/ /g, '');
        this.log(`Package name: ${this.packageName}`);

        this.firebaseProject = `${this.answers.orgIdentifier
            .split('.')
            .join('-')}-${this.packageName}`;
        this.log(
            `Firebase / Google Cloud project identifier: ${this.firebaseProject}`
        );

        this.prodSecretKey = passwordGenerator.generate({
            length: 50,
        });

        this.devDbPassword = passwordGenerator.generate({
            length: 20,
            numbers: true,
        });
        this.devSecretKey = passwordGenerator.generate({
            length: 50,
        });

        this.context = {
            packageName: this.packageName,
            productName: this.answers.productName,
            firebaseProject: this.firebaseProject,
            gcloudOrgIdentifier: this.answers.gcloudOrgIdentifier,
            gcloudBillingAccountIdentifier:
                this.answers.gcloudBillingAccountIdentifier,
            gcloudRegion: this.answers.gcloudRegion,
            prodDbPassword: this.answers.prodDbPassword,
            prodSecretKey: this.prodSecretKey,
            devDbPassword: this.devDbPassword,
            devSecretKey: this.devSecretKey,
        };

        // Set destination root to create project dir with the new app's name
        this.destinationRoot(
            path.join(this.destinationRoot(), this.packageName)
        );
    }

    async _gitAddAndCommit(commitMessage) {
        await this.spawnCommand('git', ['add', '-A']);
        await this.spawnCommand('git', ['commit', '-m', commitMessage]);
    }

    async install() {
        await this.spawnCommand('git', ['init']);
        await this._gitAddAndCommit('Initial commit');
    }

    writing() {
        this.fs.copyTpl(
            this.templatePath(),
            this.destinationPath(),
            this.context
        );

        // Dot files need to be copied explicitly
        this.fs.copyTpl(
            this.templatePath('.devcontainer'),
            this.destinationPath('.devcontainer'),
            this.context
        );
        this.fs.copyTpl(
            this.templatePath('.dockerignore'),
            this.destinationPath('.dockerignore'),
            this.context
        );
        this.fs.copyTpl(
            this.templatePath('.env'),
            this.destinationPath('.env'),
            this.context
        );
        this.fs.copyTpl(
            this.templatePath('.env-dist'),
            this.destinationPath('.env-dist'),
            this.context
        );
        this.fs.copyTpl(
            this.templatePath('.env-prod'),
            this.destinationPath('.env-prod'),
            this.context
        );
        this.fs.copyTpl(
            this.templatePath('.flake8'),
            this.destinationPath('.flake8'),
            this.context
        );
    }

    end() {
        this.log("Success! You're all ready to go.");
    }
};

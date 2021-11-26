# **Time-tracker-api V2 Architecture**
Architecture
The application follows a DDD approach with a hexagonal clean architecture. BIG WORDS!, what does it mean? it means the following:

We have a directory for each domain entitiy (i.e. time entries, technologies, activities, etc)
Inside each entity directory we have other 3 directories (application, domain and infrastructure)
I'll leave this drawing to understand how these three folders work and what logic should be included in these directories

![ddd.png](https://raw.githubusercontent.com/eguezgustavo/time_tracker_app_skeleton/master/ddd.png)
More information  [Here](https://github.com/eguezgustavo/time_tracker_app_skeleton)

## **Stack Technologies**
  - [Serverless](https://serverless.com/framework/docs/providers/azure/guide/intro/)
  - Python
  - Pytest
  - Docker Compose
 
Recommended link [tdd_dojo](https://github.com/eguezgustavo/tdd_dojo)

## **Setup environment**

### **Requeriments**

- Install python 3.6 or 3.7 (recommendation to install python [pyenv](https://github.com/pyenv/pyenv))
- Install node (recommendation to install node [nvm](https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-20-04-es#:~:text=de%20Node.js.-,Opci%C3%B3n%203%3A%20Instalar%20Node%20usando%20el%20administrador%20de%20versiones%20de%20Node,-Otra%20forma%20de))

### **Add variables**
In the root directory /time-tracker-backend create a file .env with these values

```
export MS_AUTHORITY=XXX
export MS_CLIENT_ID=XXX
export MS_SCOPE=XXX
export MS_SECRET=XXX
export MS_ENDPOINT=XXX
export DATABASE_ACCOUNT_URI=XXX
export DATABASE_MASTER_KEY=XXX
export DATABASE_NAME=XXX
export FLASK_APP=XXX
export FLASK_ENV=XXX
export AZURE_APP_CONFIGURATION_CONNECTION_STRING=XXX
export USERID=XXX
export FLASK_DEBUG=True
export PYTHONPATH=XXX
export DB_CONNECTION=XXX
export ENVIRONMENT=XXX
```

In the  directory /V2 create a file .env with these values
```
DB_USER=XXX
DB_PASS=XXX
DB_NAME=XXX
```

### **Install dependencies**
In the Directory /V2
```
make install
```

## **Start Project**
In the directory /V2
```
npm run offline 
docker compose up or make start-local
```


## **Makefile to run a locally CI**

Execute the next command to show makefile help:

```shell
$ make help
```

- To install the dependencies type the command ```make install```
- To test the project type the command ```make test```
- To run the local database type the command ```make start-local```

## **How to contribute to the project**
Clone the repository and from the master branch create a new branch for each new task.
### **Branch names format**
For example if your task in Jira is **TT-48 implement semantic versioning** your branch name is:
```
   TT-48-implement-semantic-versioning
```
### **Commit messages format**


  Below there are some common examples you can use for your commit messages [semantic version](https://semver.org/) :

  - **feat**: A new feature.
  - **fix**: A bug fix.
  - **perf**: A code change that improves performance.
  - **build**: Changes that affect the build system or external dependencies (example scopes: npm, ts configuration).
  - **ci**: Changes to our CI or CD configuration files and scripts (example scopes: Azure devops, github actions).
  - **docs**: Documentation only changes.
  - **refactor**: A code change that neither fixes a bug nor adds a feature.
               It is important to mention that this key is not related to css styles.
  - **test**: Adding missing tests or correcting existing tests.

  ### Example
    fix: TT-48 implement semantic versioning

    Prefix to use in the space fix:
    `(fix: |feat: |perf: |build: |ci: |docs: |refactor: |style: |test: )`
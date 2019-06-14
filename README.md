# riclibre

**master** 

[![Build Status](https://travis-ci.org/tomlemeuch/riclibre.svg?branch=master)](https://travis-ci.org/tomlemeuch/riclibre)

**develop**

[![Build Status](https://travis-ci.org/tomlemeuch/riclibre.svg?branch=development)](https://travis-ci.org/tomlemeuch/riclibre)

Supported versions of python : **3.7**


## What is Riclibre ?

Following the demonstrations of yellow vests ("les gilets jaunes") in France and inspiring their claims, i decided to 
write this web application. I thougth this was an interesting topic to conclude my python development learning as 
port of a 2 years online training.

This web application allows citizens to create and plan referendum. They also can vote after providing a proof they 
are citizens (only french id card is supported for now).  


## Getting Started



### Prerequisites

Posgresql is used as database engine. 
Redis is used à message broker.
Required python libraries are listed in requirements.txt

You don't need to install them if you use docker-compose deployment.

### Installing

Copy [ric_libre_env_file_sample/.env](ric_libre_env_file_sample/.env) in project root.

Change environment variables values according to your environment.
example:
```.env
# Base config
DJANGO_SETTINGS_MODULE=riclibre.settings
DJANGO_SECRET_KEY=my_secret_key
DEBUG=True
DOMAIN_NAME=domain_ip
MAIL_DOMAIN=riclibre.fr.nf

# Database config
POSTGRES_DB=test
POSTGRES_USER=test
POSTGRES_PASSWORD=test
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Logging mail config
SENDGRID_API_KEY=send_grid_api_key
ADMINS=admin1@mail.fr;admin2@mail.fr

# Celery broker config
BROKER_URL=redis://<IP_BROKER>:6379


# Logging config
NEW_RELIC_KEY=<NEW_RELIC_LICENCE_KEY>
#SENTRY_DSN=https://<SENTRY_PUBLIC_KEY>@sentry.io/<SENTRY_PROJECT_ID>

# reCaptcha
RECAPTCHA_PUBLIC_KEY = 'public_key'
RECAPTCHA_PRIVATE_KEY = 'private_key'
DESACTIVATE_RECAPTCHA=True
```

Then run:

```
make docker-deploy
```

## Running the tests

Define all environment variables in your test environment.
example:
```shell
export DJANGO_SETTINGS_MODULE=riclibre.settings.test
```


Then run:

```shell
make test
```


### And coding style tests

Run command

```
make pylint
```

## Deployment



## Built With

* [Django](https://www.djangoproject.com/): python web framework
* [Passporteye](https://github.com/konstantint/PassportEye): Id card mrz extraction
* [Celery](http://www.celeryproject.org/): - Task queue

## Contributing

Because this project must be presented in conclusion of a learning path, i can't allow any contribution for now.

## Versioning

I use [SemVer](http://semver.org/) for versioning. For the versions available, see the 
[tags on Riclibre repository](https://github.com/your/project/tags). 

## Authors

* **Tom Gabrièle** - [RicLibre](https://github.com/tomlemeuch/riclibre)

See also the list of [contributors](https://github.com/tomlemeuch/riclibre/graphs/contributors) who participated in this project.

## License

This project is licensed under the GNU GPL V3 - see the [LICENSE](LICENSE) file for details


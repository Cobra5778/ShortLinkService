# What is ShortLinkService?

An application for implementing short links.
If you have your own domain (for example mysite.com )

You will be able to generate short links like: "mysite.com\Rer34rer" to any Internet resources.

The link length is limited to 2048 characters.

The length of the short link is no more than 15 characters, which consist of letters and numbers.

The project is based on Django Framework. Uses Redis and MySQL which are run from Docker containers using docker-compose.

For correct display of static files, ngnix is used. The settings for the external port are in the file "docker-compose.yml". In the ports section. You can choose a port other than 1334 for yourself.

## All the settings that you may need are in the config/config.cfg file.

### The [client] section contains all the data to connect to the database.

### The [app] section:  Web application settings.

`title`: Web page title

`our-damain-name`: Your domain name

`url-valid-days`: The duration of the service link. (number of days before its removal)

`shortlink-length`: The number of characters of the short link. (Maximum value 15)

### The [clearscrpit] section:  Settings for the Script for cleaning outdated links

`clear-interval-hours`: The interval for checking outdated links in hours. Real type values are allowed (for example 1.5)

> The storage duration of each link is unique and is recorded in the database when creating a short link.

### The [redis] section: Contains settings for REDIS.

# Install Compose on Linux systems
## Install `docker-compose` using pip

```console
$ pip3 install docker-compose
```

If you are not using virtualenv,

```console
$ sudo pip install docker-compose
```

> pip version 6.0 or greater is required.

# HOW TO USE

## START PROJECT from docker-compose.yml

Go to the project folder and run:

```console
$ sudo docker-compose build
```

After the project is built, you can run it:
```console
$ sudo docker-compose up
```
>During the first launch of the project, a database is created, it is stored in the project folder "mysql_data". Due to the fact that the database is not ready, the project may not start the first time. Therefore, you may need to stop and start the project again.


## RUN PROJECT
```console
$ sudo docker-compose start
```

## Project folders
```
.
├── mysql_data
├── log
├── nginx
├── static_volume
├── web_django
├── config
└── clearscript
```

FOLDER        | DESCRIPTION
------------- | -------------
`mysql_data`  | Project database files
`log` | Project logs
`nginx` | Web Server
`static_volume` | Static project files
`web_django` | Django project. Web interface.
`config` | Project Settings
`clearscript` | Script for clearing outdated records



> In order for the changes to the projects to be applied after configuration, the projects must be restarted.

> The storage duration of each link is unique and is recorded in the database when creating a short link.

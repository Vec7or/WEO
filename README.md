# WEO - WSL Environment Orchestrator

<div align="center">
  <img width="350" src="./assets/weo_logo.png">
</div>

## General

The wsl environment orchestrator helps you in provisioning new WSL containers. It allows you to create containers based
on docker images or on dockerfiles.

## Prerequisites

In order to use the WEO the following steps need to be done:
1. Activate the wsl windows features:
   - Virtual Machine Platform
   - Windows Subsystem for Linux
2. Restart your computer
3. Update wsl by doing the following:
   - Open a terminal and run `wsl --set-default-version 2`
   - Open a terminal and run `wsl --update`
4. Install WEO by using the `.msi` file provided in the GitHub release

## Usage

### Create

```bash
WEO.exe create [OPTIONS]

  Creates a new wsl environment

Options:
  -d, --docker-image TEXT         The name of the docker image to use as
                                  environment base  [required]
  -e, --environment-name TEXT     The name of the new environment that will be
                                  created  [required]
  -l, --local [FILE|DIR]          If this is set the option "-d" will be
                                  interpreted as a local path to a dockerfile
                                  or to a directory containing a dockerfile
                                  and it\'s build assets dependent on the
                                  value.
  -p, --environment-password TEXT
                                  The password of the user within the new
                                  environment  [default: WEO; required]
  -u, --user TEXT                 The user that should be used within the
                                  environment. This user needs to exist in the
                                  image.
```

### Remove

```bash
Usage: WEO.exe remove [OPTIONS]

  Removes an existing wsl environment

Options:
  -e, --environment-name TEXT  The name of the new environment that will be
                               removed  [required]
  --help                       Show this message and exit.
```
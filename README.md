SNARE
=====

⚠️ $\color{red}\Large\textsf {Important}$

**Deviation from original code from mushorg**

- Added capability for https request.
- Aditional steps need to be configured in the original snare Dockerfile.
    - Adjusting github url and checkout.
    - Mapping certificate, key from `/your/directory`. Files in `/your/directory` are copied to your $\color{SteelBlue}\textsf{snare container path of choice.}$ 
- Port 443 needs to be added into docker-compose file.
- Two additional parameters were added into snare initialization file `--ssl-cert` and `--ssl-key`. These parameters need to be included in Dockerfile as flags this tells snare initialization file to look for certificate and key at particular $\color{SteelBlue}\textsf{path inside snare container}$ (`e.q. CMD --ssl-cert /path/ssl/<certificate_name> --ssl-key /path/ssl/<key_name>`). <span style="color:red; font-size:large;">ℹ</span>




**Recomended settings**

- Adjust docker daemon and create `etc/docker/daemon.json`. That way you limit your ip address pool to have less impact on your system  (e.q. `192.168.1.1/28`). The more important reason is to avoid routing conflicts with your host default gatway ip adress. This pool only applies to containers on a bridge network. Custom networks have their own subnets created automaticaly (this process is random, docker however tries to avoid conflicts with your host machine network) if you don't specify them in docker-compose.
    - Adjust `/usr/local/bin/adjust-routing-table.sh`. In case you made changes to ip routing table manualy or via daemon.json you need to put those changes to `adjust-routing-table.sh`. This code automaticaly flushes ip route table and makes a default update. Another option is to simply stop this service from running. <span style="color:red; font-size:large;">ℹ</span>
- Change `/etc/crontab`. Comment out image update. If you leave your image names the same in your custom configuration they will get replaced/updated by pulling of original images. <span style="color:red; font-size:large;">ℹ</span>

**Additional info**

HTTPS usage is hardcoded in server.py aswell as its port. 
- Therefore you don't need to specify `--443` port flag in CMD line in your Dockerfile (part of tpotice, on your host machine).
  
As of right now modified snare supports both http and https.
- If you want more flexibility meaning you want to use `--443` flag you would need to adjust server.py.
    + If you decide to do that you can chose on what port/protocol snare listens in your Dockerfile (CMD line).

**P.S.** Another way to manipulate http or https availability is in your docker-compose file with port mapping (`e.q. 443:433`).

--------------


[![Documentation Status](https://readthedocs.org/projects/snare/badge/?version=latest)](http://snare.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/mushorg/snare.svg?branch=master)](https://travis-ci.org/mushorg/snare)
[![Coverage Status](https://coveralls.io/repos/github/mushorg/snare/badge.svg?branch=master)](https://coveralls.io/github/mushorg/snare?branch=master)

_**Super Next generation Advanced Reactive honEypot**_

About
-----

SNARE is a web application honeypot sensor attracting all sort of maliciousness from the Internet.

Documentation
--------------

The documentation can be found [here](http://snare.readthedocs.io).

Basic Concepts
--------------

- Surface first. Focus on the attack surface generation.
- Sensors and masters. Lightweight collectors (SNARE) and central decision maker (tanner).

Getting started
---------------

- You need Python3.6 to run SNARE
- This was tested with a recent Ubuntu based Linux.

#### Steps to setup

1. Get SNARE: `git clone https://github.com/mushorg/snare.qit` and `cd snare`
2. [Optional] Make virtual environment: `python3 -m venv venv`
3. [Optional] Activate virtual environment: `. venv/bin/activate`

**Note:** Do not use sudo with below commands if you're running snare in virtual environment.

4. Install requirements: `sudo pip3 install -r requirements.txt`
5. Setup snare: `sudo python3 setup.py install`
6. Clone a page: `sudo clone --target http://example.com --path <path to base dir>`
7. Run SNARE: `sudo snare --port 8080 --page-dir example.com --path <path to base dir>`
8. Test: Visit http://localhost:8080/index.html
9. (Optionally) Have your own [tanner](https://github.com/mushorg/tanner) service running.

[Note : Cloner clones the whole website, to restrict to a desired depth of cloning add `--max-depth` parameter]

#### Docker build instructions

1. Change current directory to `snare` project directory
2. `docker-compose build`
3. `docker-compose up`
4. Snare will start on 0.0.0.0 with port 80.
More information about running `docker-compose` can be found [here.](https://docs.docker.com/compose/gettingstarted/)

In case of an error while running `docker-compose up`, check the availability of port 80, if it is occupied then refer to Docker documentation to change the default port.

You obviously want to bind to 0.0.0.0 and port 80 when running in _production_.

## Testing

In order to run the tests and receive a test coverage report, we recommend running `pytest`:

```
    pip install pytest pytest-cov
    sudo pytest --cov-report term-missing --cov=snare snare/tests/
```

## Sample Output

```shell

    # sudo snare --port 8080 --page-dir example.com

       _____ _   _____    ____  ______
      / ___// | / /   |  / __ \/ ____/
      \__ \/  |/ / /| | / /_/ / __/
     ___/ / /|  / ___ |/ _, _/ /___
    /____/_/ |_/_/  |_/_/ |_/_____/


    privileges dropped, running as "nobody:nogroup"
    serving with uuid 9c10172f-7ce2-4fb4-b1c6-abc70141db56
    Debug logs will be stored in /opt/snare/snare.log
    Error logs will be stored in /opt/snare/snare.err
    ======== Running on http://127.0.0.1:8080 ========
    (Press CTRL+C to quit)
    you are running the latest version

```

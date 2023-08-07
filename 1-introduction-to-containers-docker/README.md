# Week 1 - Introduction to Contaienrs and Docker
This lab walks you through 
- installing a container runtime
- installing python to test a web application written in python
- containerizing the python web application
- running the containerized web application

## 0 - Clone Repo
1. Open a terminal
2. Clone the workshop repository with the command below
  
    `git clone https://github.com/kordaralabs/free-containers-workshop.git`
    
    Alternatively, download the [ZIP here](https://github.com/kordaralabs/free-containers-workshop/archive/refs/heads/main.zip) if you don't have git installed. Then, navigate to the directory of the unzipped file in the terminal
    
3. Change directory to `1-introduction-to-containers-docker`

    `cd 1-introduction-to-containers-docker`

## 1 - Dependencies
### 1.1 - Install a container runtime 
- Linux
  - [Docker](https://github.com/docker/docker-install#dockerdocker-install)
- Windows:
  - [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)
  - [Rancher Dekstop](https://docs.rancherdesktop.io/getting-started/installation/#windows) - Select `dockerd (moby)` as Container Engine during installation
- Mac
  - [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)

### 1.2 - Install Python 3
- Linux and Mac typically has python3 pre-installed
- [Windows](https://www.python.org/downloads/windows/)

## 2 - Run and Test Flask Python Application
Change the directory to `flask-application` using the command below

`cd flask-application`

### 2.1 - Create a Python Virtual Environment 
- Run the command below to create a python virtual environment
  
  `python -m venv venv` or `python3 -m venv venv`

### 2.2 - Activate Virtual Environment
- Activate the virtual environment so new packages do not get installed on the system wide python
  - Linux and Mac: `source ./venv/bin/activate`
  - Windows Powershell: `.\venv\Scripts\activate`

### 2.3 - Install Python Packages
- Install python packages requied by the Python web application
 
  `pip install -r requirements.txt`

### 2.4 - Start Python App
- Start the Python Application
  
  `python app.py`

### 2.5 - Test Application
- Use any of the following methods to test the application
  - Web browser: `http://localhost:8080`
  - Linux and Mac: `curl -i http://localhost:8080`
  - Windows Powershell:  `Invoke-WebRequest http://localhost:8080` 
- Stop the Python Application by pressing `Ctrl + C` on the terminal window that it was started


## 3 - Build Container Image
 Build the container image using the `Dockerfile` file in the `flask-application` directory. The `docker build` command by default looks for a `Dockerfile` in the directory passed. Here `'` is passed to used the current directory. 
  
  `docker build -t flask-app .`

## 4 - Run Container Image
  
`docker run -it -p 8080:8080 --name web-app flask-app`

- `-it` denotes that we want an interactive session. So application logs/outputs are written out to the terminal  
- `-p 8080:8080` exposes port 8080 (application port) to port 8080 on the machine the container is running on
- `--name web-app` names the container, this can be sued to retrieve information about the container after it is started. 

## 5 - Test Containerized Application
- Linux and Mac: `curl -i http://localhost:8080`
- Windows Powershell:  `Invoke-WebRequest http://localhost:8080` 
- Web browser: `http://localhost:8080`

## 6 - Stop the Container
- Since the `-it` interactive flag was passed, the current terminal window will be unusable. Press `Ctrl + C` to stop the Python application running in the container. Once the main application in a container is stopped, the container stops automatically
- Remove the container with
  - Remove gracefully: `docker remove web-app`
  - Remove forcefully: `docker remove web-app -f`
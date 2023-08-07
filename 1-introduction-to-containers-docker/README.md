## 0 - Dependencies
### 0.1 - Install a container runtime 
- Linux
  - [Docker](https://github.com/docker/docker-install#dockerdocker-install)
- Windows
  - [Docker](https://docs.docker.com/desktop/install/windows-install/)
  - [Rancher Dekstop](https://docs.rancherdesktop.io/getting-started/installation/#windows)
- Mac
  - [Docker](https://docs.docker.com/desktop/install/mac-install/)

### 0.2 - Install Python 3
- [Windows](https://www.python.org/downloads/windows/)

## 1 - Run and Test Flask Python Application
Working Dir: `flask-application`

### 1.1 - Create a Python Virtual Environment 
- `python -m venv venv` or `python3 -m venv venv`

### 1.2 - Activate Virtual Environment
- Linux and Mac: `source ./venv/bin/activate`
- Windows Powershell: `.\venv\Scripts\activate`

### 1.3 - Install required Python packages
- `pip install -r requirements.txt`

### 1.4 - Start Python App
- `python app.py`

### 1.5 - Test Application
- Linux and Mac: `curl -i http://localhost:8080`
- Windows Powershell:  `Invoke-WebRequest http://localhost:8080` 
- Web browser: `http://localhost:8080`

## 2 - Build Container Image
- `docker build -t flask-app .`

## 3 - Run Container Image
- `docker run -it -p 8080:8080 flask-app`
    
## 4 - Test Application
- Linux and Mac: `curl -i http://localhost:8080`
- Windows Powershell:  `Invoke-WebRequest http://localhost:8080` 
- Web browser: `http://localhost:8080`
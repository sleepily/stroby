# stroby
### a fast and accurate digital strobe tuner

note: since stroby is still in early stages of development, the pitch detection accuracy is currently limited by the FFT resolution and thus the audio buffer size. this will be fixed in a near future update.

## installation
as of now, there is no release available (yet).  
to use stroby, do as follows:  

1. clone repo  
2. set up a virtual environment for python
```python -m venv <venv-path>```
4. activate the environment  
```. ./<venv-path>/bin/activate```
5. install dependencies  
```pip install -r requirements.txt```
6. run stroby  
```python main.py```

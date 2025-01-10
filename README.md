# stroby
### a fast and accurate digital strobe tuner

![stroby_screenshot](https://github.com/user-attachments/assets/92b0dac4-7d58-4623-b6b7-046a6835d4c7)

note: since stroby is still in early stages of development, the pitch detection accuracy is currently limited by the FFT resolution and thus the audio buffer size. this will be fixed in a near future update.

## run source

1. clone repo  
2. set up a virtual environment for python
```python -m venv <venv-path>```
4. activate the environment  
```. ./<venv-path>/bin/activate```
5. install dependencies  
```pip install -r requirements.txt```
6. run stroby  
```python main.py```

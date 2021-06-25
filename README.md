# ALPHA PEOPLE COUNTER

This is an artificial intelligence surveillance system that counts people moving in and out of a building, using cameras positioned at the various entrances and exits of the building.

## SYSTEM ARCHITECTURE

- ##### Desktop Application

  ![](https://github.com/Owiredu/trestle-telnova-hack-2021/blob/main/images/alpha_home.jpg)

- ##### Web client (website)

  ![](https://github.com/Owiredu/trestle-telnova-hack-2021/blob/main/images/webpage.jpg)

## HOW TO RUN

1. Download and install [Visual C++ build tools](https://support.microsoft.com/en-us/topic/the-latest-supported-visual-c-downloads-2647da03-1eea-4433-9aff-95f26a218cc0)

2. Download and install [CMake](https://cmake.org/download/) and add it to the environment variables.

3. Navigate to the project's base directory.

4. Install the required python 3 modules using the command:

   `python -m pip install -r requirements.txt`

   *NB:  The system has been tested using Python 3.7.4 to 3.8.5*

5. To start the web server, navigate to the `/website/` directory and run the command: 

   `flask run`

6. To start the desktop application, navigate the `/final-desktop-app/` directory and run the command: 

   `python alpha_main.py`

   
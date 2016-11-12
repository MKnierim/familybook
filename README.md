# The familybook - like facebook, but for your family only

## Description
My personal facebook clone just for my family to communicate news and document family events 
without publishing information to the general public. It is a responsive web-app and can be set 
up via Google App Engine.

![Screenshot 1 familybook](/imgs/screenshots/screenshot1.jpg "screenshot 1 familybook")
![Screenshot 2 familybook](/imgs/screenshots/screenshot2.jpg "screenshot 2 familybook")

## Version information
It is an early alpha version that includes basic 
functionality such as user input for dates/events, password, e-mail, and design setting changes. 

## Getting Started
### Prerequisites on the server side
* Python 2.7
* Google App Engine SDK 1.9.24
* webapp2 2.5.2
* jinja2 2.6

## Running Instructions
* Either create an application instance in Google App Engine on [Google Cloud Platform]
(https://cloud.google.com/appengine/) or run a local server by calling dev_appserver.py which is 
included in the AppEngine SDK. For more instructions see this Google reference: [Python AppEngine
 Quickstart](https://cloud.google.com/appengine/docs/python/quickstart)
* During the inital setup, an admin account will be instantiated automatically (Username: 
"Admin", Password: "admin"). You can use it to login and get going immediately. 

# Known Issues
* There is currently a bug with delivering the error message to the user after date event input 
validation. This works for user setting changes though (e.g. e-mail or password).
* If you find some German words in there, please ignore them...

## Authors
This project was created by [Michael Knierim](https://github.com/MKnierim).

## Licensing
* This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for 
details.
* Profile stand-in images are integrated by the courtesy (CC0) of [Ryan McGuire](http://www.gratisography.com)
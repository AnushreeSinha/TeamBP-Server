# teambp-server

### An app for supporting recognition of pediatric hypertension

This app is based on a sample app [`flask_app.py`][flask_app] which comes with the [python fhir client][client-py]. 

The app has two app launch URI's:

[_localhost:8000/launchdoc.html_](http://localhost:8000/launchdoc.html) presents a graphical representation of blood pressure history and BMI for review by a clincian evaluating blood pressure trends.

[_localhost:8000/launchnurse.html_](http://localhost:8000/launchnurse.html) presents a smart vital signs entry panel that screens for elevated BP as data is collected and gives the opportunity to retake the blood pressure after assuring baseline (sitting, calm, etc) conditions.

The client is written in python 2.7 and has been run in Windows and Mac environments.

To host the app on localhost, clone the __teambp-server__ repository, (optionally) create and activate an environment, and install requirements with pip:

    git clone https://github.gatech.edu/teambp-server.git
    cd teambp-server
    virtualenv -p python2 env
    . env/bin/activate
    pip install -r requirements.txt
    python Flask_App.py
    
To test the apps, we used the sandbox at [Smart Sandbox] to emulate an EMR with launchable Smart on FHIR apps.
We are hopeful that any SMART on FHIR protocol compatible EMR or sandbox that has pediatric patients with 
Patient resouces and Observation resources with vital signs could be used to demo the app.

The parameters for the "Doctor" entry point are:

Parameter|Value
---------|-----
App Name|BP Presentation for Doctor
Client Id|e6b67cc5-200e-4264-b8ad-980b3e32abda
App Launch URI|http://localhost:8000/launchdoc.html
App Redirect URIs|http://localhost:8000/fhir-app/
Scopes|launch patient/*.* openid profile offline_access

The parameters for the "Nurse" entry point are:

Parameter|Value
---------|-----
App Name|BP Presentation for Nurse
Client Id|ec6df8f5-f1e8-4fff-93b8-7c0af18d7980
App Launch URI|http://localhost:8000/launchnurse.html
App Redirect URIs|http://localhost:8000/fhir-app/
Scopes|launch patient/*.* openid profile offline_access

Note:  This server is expecting to pull data from a DSTU2 FHIR server and uses version 1.0.6 of the python fhir client.
The software was tested using the [SMART Sandbox] which has announced plans to switch from DSTU2 to STU3 in the near future.  
When that occurs, the app will not be compatible until the requirements file is changed to reflect the latest version of 
fhirclient (currently 3.0.0 on pypi.python.org).

[client-py]: [https://github.com/smart-on-fhir/client-py]
[flask_app]: https://github.com/smart-on-fhir/client-py/blob/master/flask_app.py
[SMART Sandbox]:[https://sandbox.smarthealthit.org]

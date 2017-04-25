# -*- coding: utf-8 -*-

import logging
from fhirclient import client
from fhirclient.models.medication import Medication
from fhirclient.models.medicationorder import MedicationOrder
import pprint

from flask import Flask, request, redirect, session

# app setup
smart_defaults = {
##    'app_id': '4d328327-b2af-4539-a683-99898974b4ee',
##    'app_secret': 'AN0lzeYcj74MeBcF429lND7hu_DdCObcAgRXhXnvzxt-EwRoysmsmDMoKBj7hHZVpkyI4ZModgN8XJ1DIVImTs4',
    'app_id': '9c4adaf6-5f54-4f33-8465-3ee770339d1d',
    'api_base': 'https://sb-fhir-dstu2.smarthealthit.org/api/smartdstu2/data',
    'redirect_uri': 'http://localhost:8000/fhir-app/'
}

app = Flask(__name__)

def _save_state(state):
    session['state'] = state

def _get_smart():
    state = session.get('state')
    if state:
        return client.FHIRClient(state=state, save_func=_save_state)
    else:
        return client.FHIRClient(settings=smart_defaults, save_func=_save_state)

def _logout():
    if 'state' in session:
        smart = _get_smart()
        smart.reset_patient()

def _reset():
    if 'state' in session:
        del session['state']

def _get_prescriptions(smart):
    bundle = MedicationOrder.where({'patient': smart.patient_id}).perform(smart.server)
    pres = [be.resource for be in bundle.entry] if bundle is not None and bundle.entry is not None else None
    if pres is not None and len(pres) > 0:
        return pres
    return None

def _med_name(prescription):
    if prescription.medicationCodeableConcept and prescription.medicationCodeableConcept.coding[0].display:
        return prescription.medicationCodeableConcept.coding[0].display
    if prescription.text and prescription.text.div:
        return prescription.text.div
    return "Unnamed Medication(TM)"


# views

@app.route('/')
@app.route('/index.html')
def index():
    """ entry point for standalone launch - cannot get authorization to work.
    """
    _reset()
    smart = _get_smart()
    body = "<h1>Hello</h1>"
    if smart.ready and smart.patient is not None:       # "ready" may be true but the access token may have expired, making smart.patient = None
        name = smart.human_name(smart.patient.name[0] if smart.patient.name and len(smart.patient.name) > 0 else 'Unknown')

        # generate simple body text
        body += "<p>You are authorized and ready to make API requests for <em>{0}</em>.</p>".format(name)
        pres = _get_prescriptions(smart)
        if pres is not None:
            body += "<p>{0} prescriptions: <ul><li>{1}</li></ul></p>".format("His" if 'male' == smart.patient.gender else "Her", '</li><li>'.join([_med_name(p) for p in pres]))
        else:
            body += "<p>(There are no prescriptions for {0})</p>".format("him" if 'male' == smart.patient.gender else "her")
        body += """<p><a href="/logout">Change patient</a></p>"""
    else:
        auth_url = smart.authorize_url
        if auth_url is not None:
            logging.debug('Requesting Authorize with URL: '+auth_url)
            body += """<p>Please <a href="{0}">authorize</a>.</p>""".format(auth_url)
        else:
            body += """<p>Running against a no-auth server, nothing to demo here. """
        body += """<p><a href="/reset" style="font-size:small;">Reset</a></p>"""
    return body

@app.route('/after_token.html')
def after_token():
    # this generates the app output display of a single patient Med list
    smart = _get_smart()
    body = "<h1>Hello</h1>"
    name = smart.human_name(smart.patient.name[0] if smart.patient.name and len(smart.patient.name) > 0 else 'Unknown')
    body += "<p>You are authorized and ready to make API requests for <em>{0}</em>.</p>".format(name)
    pres = _get_prescriptions(smart)
    if pres is not None:
        body += "<p>{0} prescriptions: <ul><li>{1}</li></ul></p>".format("His" if 'male' == smart.patient.gender else "Her", '</li><li>'.join([_med_name(p) for p in pres]))
    else:
        body += "<p>(There are no prescriptions for {0})</p>".format("him" if 'male' == smart.patient.gender else "her")
    body += """<p><a href="/logout">Change patient</a></p>"""
    return body

@app.route('/launch.html')
def launch():
    """ The entry point for an emr launch
    """
    global smart_defaults
    _reset()
    smart_defaults = {
              'api_base': request.args['iss'],
              'launch_token': request.args['launch'],
    ##              'app_id': '4d328327-b2af-4539-a683-99898974b4ee',  #app_id for public app
              'app_id': '9c4adaf6-5f54-4f33-8465-3ee770339d1d', # app_id for confidential app
              'redirect_uri': 'http://localhost:8000/fhir-app/'
              }
    smart = _get_smart()
    return redirect(smart.authorize_url)


@app.route('/fhir-app/')
def callback():
    """ OAuth2 callback interception.
        Gets a token
    """
    logging.debug('In callback')
    logging.debug(request.args)
    logging.debug('Request url:'+request.url)
    smart = _get_smart()
    logging.debug('After get smart')
    try:
        smart.handle_callback(request.url)
    except Exception as e:
        return """<h1>Authorization Error</h1><p>{0}</p><p><a href="/">Start over</a></p>""".format(e)

    return redirect('after_token.html')


@app.route('/logout')
def logout():
    _logout()
    return redirect('/')


@app.route('/reset')
def reset():
    _reset()
    return redirect('/')

@app.route('/bp')
def bp_check():
    return "bp check here"


# start the app
if '__main__' == __name__:
    import flaskbeaker
    flaskbeaker.FlaskBeaker.setup_app(app)
    logging.basicConfig(level=logging.DEBUG,filename='myapp.log',filemode='w')
    app.run(debug=True, port=8000)
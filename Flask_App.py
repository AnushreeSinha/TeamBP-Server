# -*- coding: utf-8 -*-

import logging
from fhirclient import client
from fhirclient.models.medication import Medication
from fhirclient.models.medicationorder import MedicationOrder
from fhirclient.models.observation import Observation
import fhirclient.models.bundle as b
import pprint
from flask import jsonify

from flask import Flask, request, redirect, session

def iterentries(qry,smart):
    """ Generator to provide the entries in a paged bundle. Hides the
        process of pages being passed.
        input:
            qry is the portion of the REST URL after the server
        yields:
            a tuble containing
            entry - a single entry from the bundle
            blob - the most recent portion of the bundle downloaded
        Note:  had trouble nesting loops, probably because of
            a timeout between page fetches.
    """
    bund = b.Bundle.read_from(qry,smart.server)
    have_page = bund.entry
    while have_page:
        for item in bund.entry:
            yield item,bund
        next_link = next((item.url for item in bund.link if item.relation == 'next'),None)
        if next_link:
            qry = next_link.rpartition('?')[2]
            bund = b.Bundle.read_from('?'+qry,smart.server)
        else:
            have_page = False


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

def _get_smart(new_settings={}):
    state = session.get('state')
    settings = smart_defaults  #the global defaults
    settings.update(new_settings) #specific overriding defaults
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

def _vitals_iterator(smart):
    return iterentries('Observation?patient='+pat.resource.id+'&category=vital-signs&_format=json',smart)


# views

@app.route('/')
@app.route('/index.html')
def index():
    """ entry point for standalone launch - cannot get authorization to work.
    """
    body = "<h1>Hello</h1>"
    body += "Not a stand alone app"
    return body

@app.route('/launch.html')
def launch():
    """ The entry point for an emr launch
    """
    _reset()
    settings = {
              'api_base': request.args['iss'],
              'launch_token': request.args['launch'],
              'app_id': '9c4adaf6-5f54-4f33-8465-3ee770339d1d',
              'redirect_uri': 'http://localhost:8000/fhir-app/after_token'
              }
    smart = _get_smart(settings)
    return redirect(smart.authorize_url)

@app.route('/launchdoc.html')
def launchdoc():
    _reset()
    settings = {
              'api_base': request.args['iss'],
              'launch_token': request.args['launch'],
              'app_id': 'e6b67cc5-200e-4264-b8ad-980b3e32abda',
              'redirect_uri': 'http://localhost:8000/fhir-app/after_token2'
              }
    smart = _get_smart(settings)
    return redirect(smart.authorize_url)

@app.route('/fhir-app/after_token')
@app.route('/fhir-app/after_token2')
def callback():
    """ OAuth2 callback interception.
        Gets a token
    """
    logging.debug('In callback')
    logging.debug(request.args)  #args are state and code
    logging.debug('Request url:'+request.url)
    smart = _get_smart()
    logging.debug('After get smart')
    try:
        smart.handle_callback(request.url)
    except Exception as e:
        return """<h1>Authorization Error</h1><p>{0}</p><p><a href="/">Start over</a></p>""".format(e)
    newurl = r'/' + request.url.rpartition('?')[0].rpartition(r'/')[2]
    logging.debug('redirecting to: '+ newurl)
    return redirect(newurl)

@app.route('/after_token')
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

@app.route('/after_token2')
def after_token2():
    smart = _get_smart()
    id = smart.patient.id
    name = smart.patient.name
    birthDate = smart.patient.birthDate
    gender = smart.patient.gender
    # get all the observation resource in the category 'vital-signs' for this patient in a list of observation resources called vitals
    vitals = [result[0].resource for result in iterentries('Observation?patient='+ id +'&category=vital-signs&_format=json',smart)]
    body = smart.human_name(smart.patient.name[0] if smart.patient.name and len(smart.patient.name) > 0 else 'Unknown')
    for vital in vitals:
        edtiso = vital.effectiveDateTime.isostring
        if vital.component:
            comps = vital.component
        else:
            comps = [vital]
        for comp in comps:
            body += ('<br>'+ edtiso +' : ' +
                    comp.code.coding[0].display +' : ' +
                    str(comp.valueQuantity.value) +' : ' +
                    comp.valueQuantity.unit)
    return body






@app.route('/logout')
def logout():
    _logout()
    return redirect('/')


@app.route('/reset')
def reset():
    _reset()
    return redirect('/')

@app.route('/bp')
def bp():
    age = request.args.get('age')
    height = request.args.get('height')
    gender = request.args.get('gender')
    systolic = request.args.get('systolic')
    diastolic = request.args.get('diastolic')
    return jsonify(gender)

@app.route('/bpreadings', method=['POST'])
def bpreadings():
    newdiastolic = request.form('diastolic')
    newsystolic = request.form('systolic')
    patient_id = request.form('patient_id')







# start the app
if '__main__' == __name__:
    import flaskbeaker
    flaskbeaker.FlaskBeaker.setup_app(app)
    logging.basicConfig(level=logging.DEBUG,filename='myapp.log',filemode='w')
    app.run(debug=True, port=8000)
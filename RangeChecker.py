import json
import sys
from get_percentile import get_percentile as gp

# assuming age in years, height in cms, gender as male or female, BP readings in mmHg
def check_bp(height, age, gender, systolic, diastolic):
    patient_data = {"age": age, "height": height / 100, "sex": gender, "systolic": systolic, "diastolic": diastolic}
    percentiles = gp.bp_percentiles(patient_data)
    percentiles['systolic'] = float("{0:.2f}".format(percentiles['systolic']))
    percentiles['diastolic'] = float("{0:.2f}".format(percentiles['diastolic']))
    print(percentiles)
    if percentiles['systolic'] >= 95 or percentiles['diastolic'] >= 95:
        percentiles['bpstatus'] = 'hypertension'
    elif percentiles['systolic'] >= 90 or percentiles['diastolic'] >= 90:
        percentiles['bpstatus'] = 'prehypertension'
    else:
        percentiles['bpstatus'] = 'normal'

    toReturn = {}
    toReturn['systolic'] = percentiles['systolic']
    toReturn['diastolic'] = percentiles['diastolic']
    toReturn['bpstatus'] = percentiles['bpstatus']

    if toReturn['bpstatus'] != 'normal':
        toReturn['cards'] = getCards()
    else:
        toReturn['cards'] = []

    #print toReturn
    return toReturn

def getCards():
    card1 = '''Is the patient fully rested?
    Measurements should not be taken immediately after patient has been running around.
    Please make sure they are calm.'''
    card2 = 'Do they have the right size cuff on? Please ensure that you are using the proper equipment.'
    card3 = 'Please wait for 5/10 minutes in between each blood pressure reading.'

    data = []
    data.append(card1)
    data.append(card2)
    data.append(card3)
    json_data = json.dumps(data)

    return json_data
'''
    normalSystolicPressureLower=0
    normalSystolicPressureHigher=0
    normalDiastolicPressureLower=0
    normalDiastolicPressureHigher=0

    if age>=0 and age<1:
        normalSystolicPressureLower=75
        normalSystolicPressureHigher=100
        normalDiastolicPressureLower=50
        normalDiastolicPressureHigher=70
    elif age>=1 and age<5:
        normalSystolicPressureLower=80
        normalSystolicPressureHigher=110
        normalDiastolicPressureLower=50
        normalDiastolicPressureHigher=80
    elif age>=5 and age<13:
        normalSystolicPressureLower=85
        normalSystolicPressureHigher=120
        normalDiastolicPressureLower=55
        normalDiastolicPressureHigher=80
    elif age>=13 and age<=18:
        normalSystolicPressureLower=95
        normalSystolicPressureHigher=140
        normalDiastolicPressureLower=60
        normalDiastolicPressureHigher=90


    if systolic<normalSystolicPressureLower:
        bpstatus='low'
    elif  systolic>normalSystolicPressureHigher:
        bpstatus = 'high'
    else:
        bpstatus = 'normal'

    data = {}
    data['normalSystolicPressureLower'] = normalSystolicPressureLower
    data['normalSystolicPressureHigher'] = normalSystolicPressureHigher
    data['normalDiastolicPressureLower'] = normalDiastolicPressureLower
    data['normalDiastolicPressureHigher'] = normalDiastolicPressureHigher
    data['bpstatus'] = bpstatus
    json_data = json.dumps(data)

    return json_data

check_bp(100,10,'M',100,65)
'''

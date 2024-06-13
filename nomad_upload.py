import json
from Nomad_API import *
import yaml
import zipfile


def _getPoweredAxes(arr):
    axes = []
    for i in range(len(arr)):
        if arr[i]:
            axes.append(str(i+1))
    return axes


def _getYamlMagnetrons(dic, power_axes):
    axes = _getPoweredAxes(power_axes)
    return [_getYamlMagnetron(dic, axis) for axis in axes]


def _getYamlMagnetron(dic, axis):
    magnetron = {
        'name' : dic['Material Ax' + axis],
        'material' : {
            'name' : dic['Material Ax' + axis],
            'lab_id' : None
        },
        'vapor_source' : {
            'setpoints' : {
            'set_power' : dic['Power_Ax' + axis + '_setpoint_[W]'],
            'set_voltage' : None,
            'set_current' : None
            },
            'power' : {
                'values' : dic['Actual_Power_Ax' + axis + '_[W]'],
                'times' : dic['Time_[s]'],
                'mean' : dic['Actual_Power_Ax' + axis + '_[W]_Mean'],
                'error' : dic['Actual_Power_Ax' + axis + '_[W]_STD']
            },
            'voltage' : {
                'values' : dic['Voltage_Ax' + axis + '_[V]'],
                'times' : dic['Time_[s]'],
                'mean' : dic['Voltage_Ax' + axis + '_[V]_Mean'],
                'error' : dic['Voltage_Ax' + axis + '_[V]_STD'],
            },
            'current' : {
                'values' : [],
                'times' : dic['Time_[s]'],
                'mean' : None,
                'error' : None
            },
            'power_supply' : {
                'instrument_id' : "Power Supply Ax" + axis,
                'frequency' : None
            }
        },
        'position' : {
            'center_xyz' : None,
            'center_normal' : None,
            'rotation' : None
        }
    }
    return magnetron


def _getYamlQCM(dictionary, i):
    prefix = 'QCM_' + str(i) + '_'
    yamlQCM = {
            'crystal_info' : {
                'info' : None,
                'resonant_frequency' : None
            },
            'sensor_data' : {
                'values' : dictionary[prefix + 'frequency_[Hz]'],
                'mean' : None,
                'error' : None,
                'slope' : dictionary[prefix + 'rate_[df/dt]']
            },
            'remaining_lifetime' : {
                'value' : dictionary[prefix + 'xtal_lifetime_[%]']
            },
            'mass_deposition_rate' : {
                'value' : None,
                'error' : None
            }
        }
    return yamlQCM


def _getYamlEnv(dictionary):
    environment = {
        'gas_flow' : {
            'values' :  dictionary['Gas_flow_[sccm]'],
            'mean' : dictionary['Gas_flow_[sccm]_Mean'],
            'error' : dictionary['Gas_flow_[sccm]_STD'],
            'gas' : 'Here we do the pubchem thing'
        },
        'setpoints' : {
            'pressure' : dictionary['Pressure_setpoint_[mTorr]'],
            'flow' : None,
        },
        'pressure' : {
            'values' : dictionary['Actual_pressure_[mTorr]'],
            'mean' : dictionary['Actual_pressure_[mTorr]_Mean'],
            'error' : dictionary['Actual_pressure_[mTorr]_STD']
        },
        'sensors' : [_getYamlQCM(dictionary, i+1) for i in range(3)]
    }
    return environment
    


def data_to_zip(data : dict, activated_axes : list):
    '''
    Turns the experiment dictionary that we have into a yaml file, dumps it, then zips it.
    
    data: the experiment dictionary
    activated axes: array of booleans indicating which magnetron axes are activated during the experiment
    '''
    
    data = {'data' : {
            'm_def' : "../uploads/1WE7CfSoQbS8LidbT0XLfw/raw/automate-solar_schema.archive.yaml#/definitions/section_definitions/AutomateSolarSputterDeposition",
            'quantity' : None,
            'name' : data['Run_ID'],
            'lab_id' : "Uppsala University Åutomate-Solar",
            'description' : f'{data["Campaign description"]}, {data["Campaign code"]}, {data["Series_description"]}',
            'steps' : [
                {
                    'sources' : _getYamlMagnetrons(data, activated_axes),
                    'environment' : _getYamlEnv(data)
                }
            ]
        }
    }
    
    with open('data/data.archive.yaml', 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)
        
    with zipfile.ZipFile('data/data.zip', 'w') as zipped_f:
        zipped_f.writestr("data/data.archive.yaml", yaml.dump(data, default_flow_style=False))


def upload_zip():
    
    file = '/Users/emiresenov/secret.txt'
    password = ""
    with open(file, "r") as text:
        for line in text:
            password = line 
            
    username = 'emiresenov'
    nomad_url = 'http://localhost/nomad-oasis/api/v1/' 
    token = get_authentication_token(nomad_url, username, password)
    upload_id = upload_to_NOMAD(nomad_url, token, 'data/data.zip')
    
    last_status_message = check_upload_status(nomad_url, token, upload_id)
    print(last_status_message)
    
    response = publish_upload(nomad_url, token, upload_id)
    
    last_status_message = check_upload_status(nomad_url, token, upload_id)
    print(last_status_message)
    

if __name__ == "__main__":
    
    with open('data/data.json') as f:
        data = json.load(f)
    
    dic = data[0]
    
    # Dump dict to yaml and zip
    data_to_zip(dic, [True, True, True])
    
    # Upload via NOMAD API
    upload_zip()
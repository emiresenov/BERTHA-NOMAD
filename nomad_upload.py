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
        'name' : dic['source_' + axis + '_material'],
        'material' : {
            'name' : dic['source_' + axis + '_material'],
            'lab_id' : None
        },
        'vapor_source' : {
            'setpoints' : {
            'set_power' : dic['source_' + axis + '_set_power_[W]'],
            'set_voltage' : None,
            'set_current' : None
            },
            'power' : {
                'values' : dic['source_' + axis + '_act_power_[W]'],
                'times' : dic['time_[s]'],
                'mean' : dic['source_' + axis + '_act_power_[W]_mean'],
                'error' : dic['source_' + axis + '_act_power_[W]_mean']
            },
            'voltage' : {
                'values' : dic['source_' + axis + '_voltage_[V]'],
                'times' : dic['time_[s]'],
                'mean' : dic['source_' + axis + '_voltage_[V]_mean'],
                'error' : dic['source_' + axis + '_voltage_[V]_std'],
            },
            'current' : {
                'values' : [],
                'times' : dic['time_[s]'],
                'mean' : None,
                'error' : None
            },
            'power_supply' : {
                'instrument_id' : dic['source_' + axis + '_supply'],
                'supply_type' : dic['source_' + axis + '_mode'],
                'ramp_rate' : dic['source_' + axis + '_ramp_rate_[W/s]']
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
    prefix = 'qcm_' + str(i) + '_'
    yamlQCM = {
            'crystal_info' : {
                'info' : None,
                'resonant_frequency' : None
            },
            'sensor_data' : {
                'values' : dictionary[prefix + 'frequency_[Hz]'],
                'mean' : dictionary[prefix + 'frequency_[Hz]_mean'],
                'error' : None,
                'slope' : dictionary[prefix + 'frequency_rate_[/s2]'],
                'slope_error': dictionary[prefix + 'frequency_rate_[/s2]_error']
            },
            'remaining_lifetime' : {
                'value' : dictionary[prefix + 'lifetime_[%]']
            },
            'mass_deposition_rate' : {
                'value' : dictionary[prefix + 'mass_rate_[g/cm2s]'],
                'error' : dictionary[prefix + 'mass_rate_[g/cm2s]_error']
            }
        }
    return yamlQCM


def _getYamlEnv(dictionary):
    environment = {
        'gas_flow' : {
            'values' :  dictionary['flow_[sccm]'],
            'mean' : dictionary['flow_[sccm]_mean'],
            'error' : dictionary['flow_[sccm]_std'],
            'gas' : 'Here we do the pubchem thing'
        },
        'setpoints' : {
            'pressure' : dictionary['set_pressure_[mTorr]'],
            'flow' : None,
        },
        'pressure' : {
            'values' : dictionary['act_pressure_[mTorr]'],
            'mean' : dictionary['act_pressure_[mTorr]_mean'],
            'error' : dictionary['act_pressure_[mTorr]_std']
        },
        'sensors' : [_getYamlQCM(dictionary, i+1) for i in range(3)] if dic['qcms_active'] else []
    }
    return environment
    


def data_to_zip(data : dict, activated_axes : list):
    '''
    Turns the experiment dictionary that we have into a yaml file, dumps it, then zips it.
    
    data: the experiment dictionary
    activated axes: array of booleans indicating which magnetron axes are activated during the experiment
    '''
    
    data = {'data' : {
            'm_def' : "../uploads/M6lUZptaRcmSe76HUNRt4A/raw/automate-solar_schema.archive.yaml#/definitions/section_definitions/AutomateSolarSputterDeposition",
            'quantity' : None,
            'name' : dic['series_id'],
            'lab_id' : "Uppsala University Åutomate-Solar",
            'datetime' : dic['datetime']['$date'],
            'location' : "Uppsala, Sweden",
            'method' : 'Magnetron Sputtering',
            'description' : f'{dic["campaign_description"]}, {dic["campaign_id"]}, {dic["series_description"]}',
            'steps' : [
                {
                    'name' : f'{dic["series_id"]}, Step 1', # Change this to dynamic when we have more steps
                    'duration' : dic['dwell_time_[s]'],
                    'start_time' : dic['datetime']['$date'],
                    'creates_new_thin_film' : dic['samples_produced'],
                    'sources' : _getYamlMagnetrons(dic, [True,False,False,False,False,False]),
                    'environment' : _getYamlEnv(dic)
                }
            ]
        }
    }
    
    with open('data/data.archive.yaml', 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)
        
    with zipfile.ZipFile('data/data.zip', 'w') as zipped_f:
        zipped_f.writestr("data/data.archive.yaml", yaml.dump(data, default_flow_style=False))


def upload_zip():
    '''
    Upload the zipped file to NOMAD Oasis via API 
    '''
    
    file = '/Users/emiresenov/secret.txt'
    password = ""
    with open(file, "r") as text:
        for line in text:
            password = line 
            
    username = 'emiresenov'
    nomad_url = 'http://localhost/nomad-oasis/api/v1/' 
    token = get_authentication_token(nomad_url, username, password)
    upload_id = upload_to_NOMAD(nomad_url, token, 'data/data.zip')
    publish_upload(nomad_url, token, upload_id)
    
    

if __name__ == "__main__":
    
    with open('data/data.json') as f:
        data = json.load(f)
    
    dic = data[0]
    
    # Dump dict to yaml and zip
    data_to_zip(dic, [True, False, False, False, False, False])
    
    # Upload via NOMAD API
    upload_zip()
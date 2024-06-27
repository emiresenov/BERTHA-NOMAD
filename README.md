# Documentation for Jens & Co

This repo shows how we incorporated NOMAD in our self-driving magnetron sputtering lab setup. You can use this repository as an example to supplement the [NOMAD documentation](https://link-url-here.org](https://nomad-lab.eu/prod/v1/staging/docs/)).


## The setup

Our self-driving lab (SDL) runs in a loop. In each iteration, the following occurs:

1. The computer-controlled magnetron sputtering equipment outputs experiment data: [data.json](data/data.json).
2. We translate the output data to a YAML file and then zip it. The YAML file references a YAML schema already uploaded to NOMAD via: 
`'m_def' : "../uploads/vI_FnRuhR8Seh1nGrXttWw/raw/automate-solar_schema.archive.yaml#/definitions/section_definitions/AutomateSolarSputterDeposition"`.
See `data_to_zip` in [nomad_upload.py](nomad_upload.py).
3. We upload the zipped file to NOMAD. See `upload_zip` in [nomad_upload.py](nomad_upload.py).


## How to get things up and running

### 1. Access NOMAD

First, you need access to a NOMAD instance. You can either upload directly to the central NOMAD servers or set up a private instance, which becomes a NOMAD Oasis. 
The [NOMAD documentation](https://link-url-here.org](https://nomad-lab.eu/prod/v1/staging/docs/)) should tell you everything you need to know.

### 2. Define a schema (optional)

A schema adds functionality to an ELN (the thing that displays the NOMAD entry). If there is no schema, there won't be much more than raw data in your uploads.

You can use predefined schemas provided by NOMAD or create your own. In this project, we created a schema that inherits properties from a more general physical vapor deposition schema provided by NOMAD. 
You can find it in [automate-solar_schema.archive.yaml](schema/automate-solar_schema.archive.yaml). 

If the section references give you a headache, I created the following...

# TBC

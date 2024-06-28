# Documentation for Jens & Co

This repo shows how we incorporated NOMAD in our self-driving magnetron sputtering lab setup. You can use it as an example to supplement the [NOMAD documentation](https://link-url-here.org](https://nomad-lab.eu/prod/v1/staging/docs/)).


## The setup

Our self-driving lab runs in a loop. In each iteration, the following occurs:

1. The computer-controlled magnetron sputtering equipment outputs experiment data: [data.json](data/data.json).
2. We translate the output data to a YAML file and then zip it. The YAML file references a YAML schema already uploaded to NOMAD via: 
`'m_def' : "../uploads/vI_FnRuhR8Seh1nGrXttWw/raw/automate-solar_schema.archive.yaml#/definitions/section_definitions/AutomateSolarSputterDeposition"`.
See `data_to_zip` in [nomad_upload.py](nomad_upload.py).
3. We upload the zipped file to NOMAD. See `upload_zip` in [nomad_upload.py](nomad_upload.py).


Note that this repo is a standalone, offline mockup of the actual lab setup. In the sputtering lab, all of this happens in real time during experimentation, with small deviations from what is shown here. 


## Getting started

### 1. Access NOMAD

First, you need access to a NOMAD instance. You can either upload directly to the central NOMAD servers or set up a private instance, which becomes a NOMAD Oasis. 
The [NOMAD documentation](https://link-url-here.org](https://nomad-lab.eu/prod/v1/staging/docs/)) should tell you everything you need to know.

### 2. Define a schema (optional)

A schema adds functionality to an ELN (the thing that displays the NOMAD entry). The schema defines the structure of your data files. If there is no schema, there won't be much more than raw data in your uploads.

You can use predefined schemas provided by NOMAD or create your own. In this project, we created a schema that inherits properties from a more general physical vapor deposition schema provided by NOMAD. 
You can find it in [automate-solar_schema.archive.yaml](schema/automate-solar_schema.archive.yaml). 

If the nested section references give you a headache, I created the following image:

<p align="center">
  <img src="doc/hierarchy.png" />
</p>


Again, the NOMAD docs are best for understanding data structures and creating custom schemas. Ours is just an example.

### 3. Upload data

Now you're ready to upload, see NOMAD docs.

In our case, we're building a self-driving lab, meaning uploads are processed automatically. We also have a custom schema separate from our data files. 
Therefore, we first manually publish the schema to NOMAD and use its upload ID as a static reference in our generated upload files, as mentioned in point 2 of [The setup](#the-setup).
I included the schema in this repository to show it, but it is not used in any of our scripts.

If you're using a schema, the uploaded data files must match the descriptive fields in the schema. Furthermore, NOMAD has rather strict requirements for file formatting and throws very cryptic error messages
when files are invalid (something they intend to fix). Therefore, I would suggest starting with small, simple files and scaling up the complexity iteratively.

## Navigating this repository

To get a quick overview of what the files are doing:

- [Nomad_API.py](Nomad_API.py) This is copied from the [NOMAD programmating tutorial](https://nomad-lab.eu/prod/v1/staging/docs/howto/programmatic/publish_python.html).
- [nomad_upload.py](nomad_upload.py) This file translates our raw experiment data to the required YAML format defined by our schema. The two functions `data_to_zip` and `upload_zip` are the only entry points. The rest are helper functions.
Note that nothing special is going on in `data_to_zip`, so don't fixate on figuring out the meaning of the function and its subfunctions. This is just a hardcoded way to generate valid NOMAD files in YAML format as defined by our schema. To see the output, look at [data.archive.yaml](data/data.archive.yaml).
- [/schema](/schema) Contains our schema for you to look at. As stated, we upload this schema separately from the data and use its upload ID provided by NOMAD after publishing as a static reference in our generated data files. None of our scripts here use this file.
- [/notebooks](/notebooks) Contains two standalone notebooks demonstrating how to download our data files once they have been published to NOMAD.
- [/doc](/doc) Ignore.
- [/data](/data) Contains our raw output data from sputtering experiments ([data.json](data/data.json)) and serves as a stash for different scripts to dump their temporary files.


## Remarks
- Dumping the upload files locally before uploading is unnecessary/superfluous. Ideally, we would like to push data directly to NOMAD via the API. Uploading a ZIP file
was the only thing that worked for us given NOMAD's documentation. Consider improving this.
- Since we are deploying a self-driving lab, we are taking extra steps to automate the upload process. Specifically, in the setup we have in the lab, we automatically publish an entry via code in each experiment iteration.
If this is not your intended use case, consider using NOMAD's drag-and-drop functionality and cutting out the automation steps.
- In the notebooks folder, I cover how data uploaded to NOMAD can be retrieved. While I was developing this, we transitioned from using a local database to NOMAD in our setup, and we only automated NOMAD publishing.
We were not ready to automate data processing with NOMAD at the time, so I left the notebooks as examples of how to download our uploaded entries.
NOMAD offers Python packages for parsing data, which might be worth investigating depending on your data processing demands.
- NOMAD is currently in development, so you're not working with a finished product. It can be useful to [join their discord](https://discord.gg/Gyzx3ukUw8) for any issues that are not addressed by their documentation.
They are very helpful and quick to respond. 











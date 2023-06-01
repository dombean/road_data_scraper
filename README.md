# Road Data Scraper

![Tests](https://github.com/dombean/road_data_scraper/actions/workflows/road_scraper.yml/badge.svg)

The Road Data Scraper is a comprehensive Python tool designed to extract and process data from the WebTRIS Traffic Flow API. It is a complete rewrite of the [ONS Road Data Pipeline](https://github.com/datasciencecampus/road-data-dump/tree/r-pipeline) originally written in R. You can refer to the documentation of the ONS Road Data Pipeline [here](https://datasciencecampus.github.io/road-data-pipeline-documentation/) and to the WebTRIS Traffic Flow API [here](https://webtris.highwaysengland.co.uk/api/swagger/ui/index).

# Developer Usage

To get started with the Road Data Scraper, ensure Python 3.9 is installed on your machine. If you're using Anaconda or Miniconda, you can create a virtual environment with Python 3.9 using: `conda create --name py39 python=3.9`

1) Clone the repository: `git clone https://github.com/dombean/road_data_scraper.git`
2) Navigate into the cloned repository: `cd road_data_scraper/`
3) Install the package in editable mode: `pip install -e .`
4) Change directory into the package folder: `cd src/road_data_scraper/`
5) Adjust the config.ini file according to your requirements
6) Execute the script: `python main.py` or `python3 main.py`

# Project Structure

The Road Data Scraper project has the following structure:

```
├── config.ini
├── main.py
├── setup.cfg
├── setup.py
├── pyproject.toml
├── api_main.py
├── Dockerfile
├── src
│ ├── road_data_scraper
│ │ ├── steps
│ │ │ ├── download.py
│ │ │ ├── file_handler.py
│ │ │ └── metadata.py
│ │ └── report
│ │ ├── report.py
│ │ └── road_data_report_template.ipynb
├── tests
├── requirements.txt
├── requirements_dev.txt
├── tox.ini
└── README.md
```

The project directory contains the following components:

- `config.ini`: Configuration file for the Road Data Scraper pipeline.
- `main.py`: Main script to run the Road Data Scraper pipeline.
- `setup.cfg` & `setup.py` & `pyproject.toml`: Configuration file for the Python package.
- `api_main.py`: Main script for running the Road Data Scraper as a FastAPI application.
- `Dockerfile`: Dockerfile for building a Docker image of the Road Data Scraper.
- `src`: Directory containing the source code of the Road Data Scraper.
  - `road_data_scraper`: Package directory.
    - `steps`: Module directory containing the main modules for data scraping.
      - `download.py`: Module for scraping data from the WebTRIS Highways England API.
      - `file_handler.py`: Module for handling files and directories in the data scraping process.
      - `metadata.py`: Module for generating metadata for the road traffic sensor data scraping pipeline.
    - `report`: Module directory for generating HTML reports.
      - `report.py`: Module for generating HTML reports based on a template Jupyter notebook.
      - `road_data_report_template.ipynb`: Template Jupyter notebook for generating the HTML report.
- `requirements.txt`: File listing the required Python packages for the project.
- `requirements_dev.txt`: File listing additional development-specific requirements for the project.
- `tox.ini`: Configuration file for running tests using the Tox testing tool.
- `tests`: Directory containing test files for the project.
- `README.md`: Documentation file providing an overview and instructions for using the Road Data Scraper.

The main functionality of the Road Data Scraper resides in the `src/road_data_scraper/steps` directory, where the core modules for data scraping, file handling, metadata generation, and report generation are located. The `road_data_report_template.ipynb` file, which serves as the template for generating HTML reports, is placed inside the `src/road_data_scraper/report` directory.

The additional component, `Dockerfile`, is located in the root directory. It is used for building a Docker image of the Road Data Scraper, allowing for easy deployment and containerization of the application.


# Adjusting the Config File (config.ini)

There are several configurable options in the config.ini file:

- __start_date__: Specify a start date in the format __%Y-%m-%d__, e.g, "2021-01-01".
- __end_date__: Specify an end date in the format __%Y-%m-%d__, e.g, "2021-01-31".
- __test_run__: Set to __True__ for testing the pipeline (runs on a subset of available URLs) and __False__ for a complete data download.
- __generate_report__: Set to __True__ to generate a HTML report showcasing the Active and Inactive IDs for each road sensor -- MIDAS, TMU, and TAME.
- __output_path__: Provide a path to save the outputs generated by the Road Data Scraper Pipeline; for example, "/home/user/Documents/"
- __rm_dir__: Set to __True__ if you're using a Google Cloud VM Instance and you don't want to store the data on the VM (assuming you set __gcp_storage=True__).

## Google Cloud (GCP) Storage Options

To save output data to a Google Cloud bucket, adjust the following settings:

- __gcp_storage__: Set to __True__ to save the data generated by the pipeline to a Google Cloud bucket.
- __gcp_credentials__: Provide the path to your GCP credentials json file, e.g., "/home/user/gcp_credentials.json".
- __gcp_bucket_name__: Provide the name of your GCP bucket, e.g., "road_data_scraper_bucket".
- __gcp_blob_name__: Provide the name of the folder in the GCP bucket where you want the pipeline to save the data, e.g., "landing_zone".

# Google Cloud VM Instance Setup

Follow the below steps to set up the Road Data Scraper on a Google Cloud VM instance:

1) Login to __Google Cloud Platform__ and click on __Compute Engine__ in the left side-bar.
2) Then, in the left side-bar, click on __Marketplace__ and search for __Ubuntu 20.04 LTS (Focal)__, then, click __LAUNCH__.
3) Name the instance appropriately; click __COMPUTE-OPTIMISED__ (note: leave the defaults -- 4 vCPU, 16 GB memory); under __Firewall__, click __Allow HTTPS traffic__; and finally __CREATE__ the VM instance.
4) SSH into the VM instance.
5) Run the following commands: `sudo apt-get update && sudo apt-get dist-upgrade -y && sudo apt-get install python3-pip -y && sudo apt-get install wget -y`
6) Pip install the road_data_scraper Package using the command: `pip install road_data_scraper`
7) Upload GCP json credentials file.
8) Download the __config.ini__ file using the command: `wget https://raw.githubusercontent.com/dombean/road_data_scraper/main/src/road_data_scraper/config.ini`
9) Download the __runner.py__ file using the command: `wget https://raw.githubusercontent.com/dombean/road_data_scraper/main/runner.py`
10) Open __runner.py__ and put in the absolute path to the __config.ini__ file.
11) Change config.ini parameters accordingly, see README section: __Adjusting the Config File (config.ini)__.
12) Run the Road Data Scraper Pipeline using the command: `python3 runner.py`


1) Login to __Google Cloud Platform__ and click on __Compute Engine__ in the left side-bar.
2) Click on __Marketplace__ and search for __Ubuntu 20.04 LTS (Focal)__. Click LAUNCH__.
3) Name your instance, select __COMPUTE-OPTIMISED__ (default settings are recommended), enable HTTPS traffic under __Firewall__, and __CREATE__ the VM instance.
4) SSH into the created VM instance.
5) Update your instance and install necessary packages: `sudo apt-get update && sudo apt-get dist-upgrade -y && sudo apt-get install python3-pip -y && sudo apt-get install wget -y`
6) Install the road_data_scraper Package: `pip install road_data_scraper`
7) Upload your GCP json credentials file.
8) Download the `config.ini` file: `wget https://raw.githubusercontent.com/dombean/road_data_scraper/main/src/road_data_scraper/config.ini`
9) Download the `runner.py` file: `wget https://raw.githubusercontent.com/dombean/road_data_scraper/main/runner.py`
10) Update the path to the `config.ini` file in `runner.py`.
11) Adjust the parameters in the `config.ini` file as per your requirements. Refer to the README section on __Adjusting the Config File__ for more information.
12) Run the Road Data Scraper Pipeline: `python3 runner.py`

# Google Cloud Run Setup

Ensure Docker and Google Cloud SDK are installed locally. You will also need to authenticate Google Cloud and Docker.

- Login to Google Cloud on the command line: ```gcloud auth login```
- Configure Google Cloud Project on the command line: ```gcloud config set project <project-name>```
- Configure Docker and Google Cloud Credentials: ```gcloud auth configure-docker```

1) Clone the repository: `git clone https://github.com/dombean/road_data_scraper.git`
2) Change directory into the cloned repository: `cd road_data_scraper/`
3) Download your Google Cloud __JSON Credentials__ into the repository.
4) Build the Docker Image: `docker build -t road-data-scraper -f Dockerfile .`
5) Test the Docker Image: `docker run -it --env PORT=80 -p 80:80 road-data-scraper`
6) Tag the Docker Image: `docker tag road-data-scraper eu.gcr.io/<project-name>/road-data-scraper`
7) Push the Docker Image: `docker push eu.gcr.io/<project-name>/road-data-scraper`
8) Deploy the Docker Image on Google Cloud Run: `gcloud run deploy road-data-scraper --image eu.gcr.io/<project-name>/road-data-scraper --platform managed --region europe-west2 --timeout "3600" --cpu "4" --memory "16Gi" --max-instances "3"`
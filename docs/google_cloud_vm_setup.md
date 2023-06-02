# Google Cloud VM Instance Setup

Follow the steps below to set up the Road Data Scraper on a Google Cloud VM instance:

1) Login to your Google Cloud Platform (GCP) account and navigate to the __Compute Engine__ section in the left sidebar.
2) Click on __Marketplace__ in the left sidebar, and search for __Ubuntu 20.04 LTS (Focal)__. Click on __LAUNCH__.
3) Provide an appropriate name for the instance and select __COMPUTE-OPTIMISED__ as the machine type. Leave the default settings for 4 vCPUs and 16 GB memory. Under __Firewall__, make sure to click __Allow HTTPS traffic__. Finally, click __CREATE__ to create the VM instance.
4) SSH into the VM instance using a suitable method for your setup.
5) Update the VM instance and install necessary packages by running the following commands:
   ```
   sudo apt-get update
   sudo apt-get dist-upgrade -y
   sudo apt-get install python3-pip -y
   sudo apt-get install wget -y
   ```
6) Install the `road_data_scraper` package by running the command: `pip install road_data_scraper`
7) Upload your GCP JSON credentials file to the VM instance.
8) Download the `config.ini` file using the following command:
   ```
   wget https://raw.githubusercontent.com/dombean/road_data_scraper/main/src/road_data_scraper/config.ini
   ```
9) Download the `runner.py` file using the following command:
   ```
   wget https://raw.githubusercontent.com/dombean/road_data_scraper/main/runner.py
   ```
10) Open the `runner.py` file and update the absolute path to the `config.ini` file.
11) Adjust the parameters in the `config.ini` file according to your requirements. Refer to the README section on __Adjusting the Config File (config.ini)__ for more information.
12) Run the Road Data Scraper Pipeline by executing the following command:
   ```
   python3 runner.py
   ```

Please note that these instructions assume some prior knowledge of working with Google Cloud VM instances. 
Make sure to adapt the steps as necessary based on your specific environment and requirements.
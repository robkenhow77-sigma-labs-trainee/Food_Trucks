# Food Trucks Data Pipeline

## Description

This project is for a food truck company who own six food trucks, each operating independently. The stakeholders want to change the way they use and visualise their data. The stakeholders wanted a data pipeline to collect and process the data, an interactive dashboard to visualise how the trucks are performing individually and as a collective as well as scheduled daily report to summaries the previous days performance.

## Contents
- [System Architecture](#system-architecture)
- [Requirements](#requirements)
- [Repository Structure](#repository-structure)
    - [dashboard](#dashboard)
    - [database](#database)
    - [pipeline](#pipeline)
    - [report](#report)
    - [terraform](#terraform)


### System Architecture 
An image of the system architecture is available [here](system_architecture.png). All cloud resources are AWS.

The trucks data is uploaded to an S3 bucket. Where it is then extracted, transformed and loaded into an AWS MySQL RDS, this is triggered using an EventBridge schedule.  An interactive streamlit dashboard is run as an ECS service using Fargate to visualise the data. A daily report is generated using a Lambda function and sent to the stakeholders using SES, also scheduled using EventBridge.

## Requirements

To use this repository you must have:
- An AWS account with the following resources shown in the systems architecture diagram
- Python
- Docker
- Streamlit

## Repository Structure

### Usage
Each file must be run in their respective directory.\
See each folder for requirements.txt\
When creating containers using `docker build` you must be in the folder with the Dockerfile.\
Similarly when making AWS resources using terraform you must be in the terraform folder.\
Each folder contains useful shell scripts.\

#### Enviroment Variables
Each folder must contain a .env file (or .tfvars for terraform), the folder breakdown below will provide the relevant details for each file.

The contents of each folder is broken down below, in order of appearance:

### dashboard

#### `dashboard.py`

This file creates the streamlit dashboard. It queries the data base to get the relevant information and then creates graphs using altair and streamlit.

#### shell scripts

`source docker_build.sh` used the dashboard image run 
 `source docker_run.sh` used to view the dashboard at: http://0.0.0.0:8501/

#### `Dockerfile`

Used to create the docker image.

#### `food_truck_wireframe.png`

A wireframe visualisation of the dashboard.

#### `.env`
The .env must include the following for the MySQL database:
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD

### database

#### shell scripts

- `create_tables.sh` used to create the tables in the database. **Using this command will DELETE all data in the tables before creating them.**
- `delete_transactions.sh` used to delete all the transaction data
- `open_tables.sh` used to open the MySQL database in the terminal

#### `schema.sql`

The file has the relevant code to create the tables and insert the basic data such as payment type and the name of the food trucks.

#### `truck_erd.png`

An entity relationship diagram of the food truck database.

#### `.env`

The .env must include the following for the MySQL database:
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD


### pipeline

#### `truck_data`

This folder is used for temporarily storing the csvs when extracting the data. Once the data is uploaded the files are deleted (only when running `pipeline.py`, if running just the `extract.py` script the files will remain in the folder).

#### `Dockerfile`

Used to create the docker image.

#### `extract.py`

Used to extract the csv files from the s3 bucket.

CLI options:
- `-a` extracts all the files. Defaults to only the files not uploaded.
- `-s` to be used when running the file not as part of the `pipeline.py` script, to load in environment variables.

#### `pipeline.py`

Used to extract the relevant data from the s3 bucket, transform it and upload it to the MySQL database.

CLI options:
- `-a` extracts all the files.

#### `transform.py`

Used to transform the data from the extracted csv files and create a pandas DataFrame with the data to be uploaded.

#### `.env`

The .env must include the following for the AWS account and MySQL database:

- ACCESS_KEY
- SECRET_KEY
- BUCKET
- FOLDER
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD

### report

#### `Dockerfile`

Used to create the docker image.

#### `report.html`

A copy of html that will be uploaded for sending out the daily report email. The file is saved for previewing. It is not included in the docker image as the script only creates the html file when being run locally.

#### `report.py`

The script used to generate the html for the daily report. Script queries the database to get the relevant data then generates the html to present the insights.

#### `.env`
The .env must include the following for the MySQL database:
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD

### terraform

**WORK IN PROGRESS**

#### `terraform.tf`

All the terraform code to generate the following:
- 

#### `variables.tf` 

Teh neccesary varibales for the `terraform.tf` file.

#### `terraform.tfvars`

This file must be created with the following:

- ACCESS_KEY
- SECRET_KEY
- PIPELINE_IMAGE_URI
- BUCKET
- FOLDER -> s3 bucket folder
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD

## Testing

Relevant tests.

**WORK IN PROGRESS**
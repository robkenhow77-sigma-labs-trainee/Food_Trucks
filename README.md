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
Each file should be run in their respective directory.\
See each folder for requirements.txt\
When creating containers using `docker build` you must be in the folder with the Dockerfile.\
Similarly when making AWS resources using terraform you must be in the terraform folder.\
Each folder contains useful shell scripts.\

#### Enviroment Variables
Each folder must contain a .env file (or .tfvars for terraform), the folder breakdown below will provide the relevant details for each file.

The contents of each folder is broken down below, in order of appearance:

### dashboard

#### dashboard.py
This file creates the streamlit dashboard. It queries the data base to get the relevant information and then creates graphs using altair and streamlit.

#### shell scripts

To build the dashboard image run `source docker_build.sh`.\
To view the dashboard run `source docker_run.sh`, then go to http://0.0.0.0:8501/

#### Dockerfile
Used to create the docker image.

#### food_truck_wireframe.png
A wireframe visualisation of the dashboard.

#### .env
The .env should include the following for the MySQL database:
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD


### database

#### shell scripts
- create_tables.sh -> used to create the tables in the database. **Using this command will DELETE all data in the tables before creating them.**
- delete_transactions.sh -> used to delete all the transaction data
- open_tables.sh -> used to open the MySQL database in the terminal

#### schema.sql
The file has the relevant code to create the tables and insert the basic data such as payment type and the name of the food trucks.

### truck_erd.png
An entity relationship diagram of the food truck database.


### pipeline


### report


### terraform


## Testing
# Food Trucks Data Pipeline

## Description

This project is for a food truck company who own six food trucks, each operating independently. The stakeholders want to change the way they use and visualise their data. The stakeholders wanted a data pipeline to collect and process the data, an interactive dashboard to visualise how the trucks are performing individually and as a collective as well as scheduled daily report to summaries the previous days performance.

## Contents
- [System Architecture](#system-architecture)
- [Requirements](#requirements)
- [Repository Structure](#repository-structure)
    - [dashboard](#dahboard)
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
Each file should be run in their respective directory.\
For example to run `pipeline.py` you must be in the pipeline folder.\
See each folder for requirements.txt\
When creating containers using `docker build` you must be in the folder with the Dockerfile.\
Similarly when making AWS resources using terraform you must be in the terraform folder. 
Each folder contains useful shell scripts.

### dashboard

#### dahboard.py


### database


### pipeline


### report


### terraform

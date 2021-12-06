# Kubernetes Scheduler Simpy
This is the source code of the kubernetes default scheduler (kubescheduler) simulated application, created using simpy.
A thesis project of *University of Pisa* and *CNR-ISTI*.

## Team

#### Supervisor

|Name and Surname            | Email                       |
|----------------------------|-----------------------------|
|Dr. Patrizio Dazzi, Ph.D.   |patrizio.dazzi@isti.cnr.it   |
|Dr. Emanuele Carlini, Ph.D. |emanuele.carlini@isti.cnr.it |

#### Student Details

|Name and Surname  | Email                         |
|------------------|-------------------------------|
|Usman Shahzad     |u.shahzad1@studenti.unipi.it   |


## Instructions

### Initialization

To setup the project initially you have to run these commands
inside the project's root.

`python3 -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

### Run the project

To run the project for first time execute the following command:

`python code/app.py`

Later you can use the following command:

`bash run.sh`

Reason: the application creates a test.log file at every execution, and
the bash file (run.sh) removes the log file to obtain fresh result everytime.
It may cause a **file not found error** if we execute this command first time,
or if we delete the test.log file manually.

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

### Input Files

Before running the project we need to provide some input files to run the application:
- Pod deployment files (YAML) in the pods directory
- Input file (YAML) in the src directory with the following format

Some of the files are already provided for demo purpose.

### Plugins

The input file contains an item in the pods section which is used to provide a custom plugin for each pod:

`plugin: 10110000000010000001000`

The plugin is a combination of 23 bits where the first bit is always 1 (because YAML dosen't support binary number system).

The rest of the bits can be set according to the following order of predicates and priorites:

|Predicates               | Priorites                      |
|-------------------------|--------------------------------|
|PodFitsHostPorts         |SelectorSpreadPriority          |
|PodFitsHost              |InterPodAffinityPriority        |
|PodFitsResources         |LeastRequestedPriority          |
|MatchNodeSelector        |MostRequestedPriority           |
|NoVolumeZoneConflict     |RequestedToCapacityRatioPriority|
|noDiskConflict           |BalancedResourceAllocation      |
|MaxCSIVolumeCount        |NodePreferAvoidPodsPriority     |
|PodToleratesNodeTaints   |NodeAffinityPriority            |
|CheckVolumeBinding       |TaintTolerationPriority         |
|                         |ImageLocalityPriority           |
|                         |ServiceSpreadingPriority        |
|                         |EqualPriority                   |
|                         |EvenPodsSpreadPriority          |


### Run the project

To run the project for first time execute the following command:

`python code/app.py`

Later you can use the following command:

`bash run.sh`

Reason: the application creates a test.log file at every execution, and
the bash file (run.sh) removes the log file to obtain fresh result everytime.
It may cause a **file not found error** if we execute this command first time,
or if we delete the test.log file manually.

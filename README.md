# Kubernetes Scheduler Simulation

This is the source code of a simulation application for the kubernetes default scheduler "kubescheduler", created using python simulation package 'simpy'.

A thesis project of *University of Pisa* and *CNR-ISTI*.

## Team

### Supervisor

|Name and Surname            | Email                       |
|----------------------------|-----------------------------|
|Dr. Patrizio Dazzi, Ph.D.   |patrizio.dazzi@isti.cnr.it   |
|Dr. Emanuele Carlini, Ph.D. |emanuele.carlini@isti.cnr.it |

### Student Details

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

Before running the project we need to provide the following input files to run the application:

- Pod deployment files (YAML) in the **pods** directory
- Input file (YAML) in the **src** directory

Some of the files are already provided for demo purpose.

### Plugins

The input file contains an item named *plugin* in the pods section which is used to provide a custom plugin for each pod.

For example: `plugin: '0110000000010000001000'`

The plugin is basically a **22 bit** combination where the bits can be set to 0 or 1 according to the following order of predicates and priorites:

|Predicates                | Priorites                          |
|--------------------------|------------------------------------|
|1. PodFitsHostPorts       |10. SelectorSpreadPriority          |
|2. PodFitsHost            |11. InterPodAffinityPriority        |
|3. PodFitsResources       |12. LeastRequestedPriority          |
|4. MatchNodeSelector      |13. MostRequestedPriority           |
|5. NoVolumeZoneConflict   |14. RequestedToCapacityRatioPriority|
|6. noDiskConflict         |15. BalancedResourceAllocation      |
|7. MaxCSIVolumeCount      |16. NodePreferAvoidPodsPriority     |
|8. PodToleratesNodeTaints |17. NodeAffinityPriority            |
|9. CheckVolumeBinding     |18. TaintTolerationPriority         |
|                          |19. ImageLocalityPriority           |
|                          |20. ServiceSpreadingPriority        |
|                          |21. EqualPriority                   |
|                          |22. EvenPodsSpreadPriority          |

### Run the Project

To run the project for first time execute the following command:

`python code/app.py`

Later you can use the following command:

`bash run.sh`

**Reason:** the application creates a test.log file at every execution, and
the bash file (run.sh) removes the log file to obtain fresh result everytime.
It may cause a **file not found error** if we execute *bash run.sh* command first time, or if we delete the test.log file manually.

# Ansible Collection - knightsg.dkron

This collection packages Ansible modules and roles for automating installation, configuration, querying and administration of a Dkron cluster.

## Included content
- Connection Plugins:
- Filter Plugins:
- Inventory Source:
- Callback Plugins:
- Lookup Plugins:
- Modules:
  - dkron_cluster_info
  - dkron_job_info
  - dkron_job

## Supported Dkron versions
This collection has only been tested with Dkron version 3.x.

## Installation and Usage
### Installing from Ansible Galaxy
This module is a work in progress and has not yet been submitted to Ansible Galaxy.

### Installing manually from this repository (using Ansible Galaxy)
The Ansible Galaxy command line utility can be used to install the collection directly from this repo using the following command:

`ansible-galaxy collection install git+https://github.com/knightsg/ansible-dkron.git,stable`
 
The above command can be adjusted to install from other branches, tags or commits as required according to your needs. Just replace 'stable' with your chosen branch or tag name. 

The following list shows each major branch and its purpose:
- stable: Latest tested code.
- stable-x: Latest tested code for a specific version. 
- devel: Latest untested code.

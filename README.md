

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

## Tested with Ansible
- 2.9

## Tested with Dkron
- 3.x

## Installation and Usage
**Installing from Ansible Galaxy**
`ansible-galaxy collection install knightsg.dkron`

**Install via requirements.yml**
Include collection in a `requirements.yml` and install via `ansible-galaxy collection install -r requirements.yml`. The requirements format is as follows:

    --- 
    collections:
      - name: knightsg.dkron

**Installing manually from source using ansible-galaxy**
The Ansible Galaxy command line utility can be used to install the collection directly from the source repo using the following command:

`ansible-galaxy collection install git+https://github.com/knightsg/ansible-dkron.git,stable`
 
The above command can be adjusted to install from other branches, tags or commits as required according to your needs. Just replace 'stable' with your chosen branch or tag name.

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

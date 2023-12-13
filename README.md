# pulumi-proxmox-boilerplate

Create Virtual Machines on Proxmox using the [Proxmox Virtual Environment (Proxmox VE) Provider](https://www.pulumi.com/registry/packages/proxmoxve/) ([GitHub](https://github.com/muhlba91/pulumi-proxmoxve)).

## Prerequisites

- Python 3
- pip

## Usage

| :warning: Warning |
|:-----------------------------------------------------------|
| The proposed code may not fulfill all needs. Modifications may be required. |

### Proxmox VE

You need to add role (let's say "Pulumi") and assign this role to a group (prefered) or to a user. Your user will also need a token.

```bash
# Create role
pveum role add Pulumi -privs "VM.Allocate VM.Clone VM.Config.CDROM VM.Config.CPU VM.Config.Cloudinit VM.Config.Disk VM.Config.HWType VM.Config.Memory VM.Config.Network VM.Config.Options VM.Monitor VM.Audit VM.PowerMgmt Datastore.AllocateSpace Datastore.Audit SDN.Use"
# Assign to a group
pveum aclmod / -group <group name> -role Pulumi
# Assign to a user
pveum aclmod / -user <username> -role Pulumi
# Generate a token for your user
pveum user token add <username> <token name> -expire 0 -privsep 0 -comment "<comment>"
```

### Pulumi project

1. You need to edit the `.env` file with your information.
2. You need to edit the vms template to match your needs.

Then, run the following commands:

```bash
# Store your stack's state where you want (use --local or any other object storage backends (s3://, gs://, azblob://)) (default: Pulumi Cloud backend)
pulumi login
# Create a project and and a new stack
pulumi new python --name <project name> --stack <stack name> --description "<description>" --force
# Or add a stack in your project
pulumi stack init <stack name>
# Replace the generated __main__.py file and add the vms folder
# Replace the generated requirements.txt file
pip install -r requirements.txt
source .env
pulumi preview
pulumi up
```

To destroy everything:

```bash
pulumi destroy
```

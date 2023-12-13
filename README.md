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

### Role

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

### Template

In order to clone, you need to create a template. The following script can be used to create a Ubuntu GNU/Linux template:

```bash
mkdir -p /root/cloudinit-images/
cat <<EOF > /root/cloudinit-templates/ubuntu_templates.sh
#!/bin/bash

WORKSPACE="/root/cloudinit-images/"
readonly WORKSPACE

STORAGE_DST="FIXME"
readonly STORAGE_DST

QCOW2_FILENAME="ubuntu22.04-ci.qcow2"
readonly QCOW2_FILENAME

URL="https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img"
readonly URL

USERNAME="FIXME"
readonly USERNAME

PASSWORD="FIXME"
readonly PASSWORD

SSH_KEY="FIXME_SSH_PUBKEY"
readonly SSH_KEY

SSH_KEY_FILE="${WORKSPACE}FIXME.pub"
readonly SSH_KEY_FILE

declare -A template1=(
	[ID]=9000
	[Name]="ubuntu22.04-ci.small"
	[vCPU]=2
	[RAM]=2048
	[Disk]=20
	[User]="${USERNAME}"
	[Password]="${PASSWORD}"
	[SSHKeyFile]="${SSH_KEY_FILE}"
)

specs=("${!template1@}")
declare -n specs_ref

mkdir -p "${WORKSPACE}"
cd "${WORKSPACE}"

echo "${SSH_KEY}" >| "${SSH_KEY_FILE}"

if ! test -f "${QCOW2_FILENAME}"; then
	wget -O "${QCOW2_FILENAME}" "${URL}"
fi

for specs_ref in "${specs[@]}"; do
	qm create "${specs_ref[ID]}" --name "${specs_ref[Name]}" --bios ovmf --net0 virtio,bridge=vmbr0,firewall=0 --net1 virtio,bridge=vmbr0,firewall=0 --scsihw virtio-scsi-pci --onboot 1 --machine q35
	qm set "${specs_ref[ID]}" --tags "Template;Ubuntu"

	qm set "${specs_ref[ID]}" -efidisk0 "${STORAGE_DST}":1,format=raw,efitype=4m,pre-enrolled-keys=1
	qm set "${specs_ref[ID]}" -tpmstate0 "${STORAGE_DST}":1,version=v2.0

	qm set "${specs_ref[ID]}" --scsi0 "${STORAGE_DST}":0,backup=off,discard=on,ssd=1,format=qcow2,import-from="${WORKSPACE}${QCOW2_FILENAME}"
	qm disk resize "${specs_ref[ID]}" scsi0 "${specs_ref[Disk]}"G
	qm set "${specs_ref[ID]}" --boot order=scsi0

	qm set "${specs_ref[ID]}" --cpu host --cores "${specs_ref[vCPU]}" --memory "${specs_ref[RAM]}"

	qm set "${specs_ref[ID]}" --ide2 "${STORAGE_DST}":cloudinit
	qm set "${specs_ref[ID]}" --ciuser "${specs_ref[User]}"
	qm set "${specs_ref[ID]}" --cipassword "${specs_ref[Password]}"
	qm set "${specs_ref[ID]}" --sshkeys "${specs_ref[SSHKeyFile]}"
	qm set "${specs_ref[ID]}" --ciupgrade 0
	qm set "${specs_ref[ID]}" --ipconfig0 "ip=dhcp"
	qm set "${specs_ref[ID]}" --ipconfig1 "ip=dhcp"

	qm cloudinit update "${specs_ref[ID]}"

	qm set "${specs_ref[ID]}" --agent enabled=1
	qm set "${specs_ref[ID]}" --serial0 socket --vga serial0

	qm template "${specs_ref[ID]}"
done

rm "${SSH_KEY_FILE}"

cd -

exit 0
EOF

chmod +x /root/cloudinit-templates/ubuntu_templates.sh
./root/cloudinit-templates/ubuntu_templates.sh
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

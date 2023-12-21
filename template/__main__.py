"""A Python Pulumi program"""

import pathlib

import pulumi
import pulumi_proxmoxve as proxmox
import yaml


def load_yaml_files_from_folder(folder: pathlib.Path):
    loaded_data = list()
    for item in (pathlib.Path().cwd() / pathlib.Path(folder)).glob("**/*.yaml"):
        with open(item, "r") as input_file:
            loaded_data.append(yaml.safe_load(input_file))

    return loaded_data


def create_sequence_from_list_of_dict(cls_name, objects_list):
    sequence = list()
    for objects in objects_list:
        for obj in objects:
            if (
                cls_name.__name__ == "VirtualMachineDiskArgs"
                and "speed" in objects[obj]
            ):
                objects[obj]["speed"] = proxmox.vm.VirtualMachineDiskSpeedArgs(
                    **objects[obj]["speed"]
                )

            sequence.append(cls_name(**objects[obj]))

    return sequence


def create_vms_from_list(vms_list: list):
    """
    See documentation:
        * https://github.com/muhlba91/pulumi-proxmoxve/blob/main/sdk/python/pulumi_proxmoxve/vm/_inputs.py
        * https://github.com/muhlba91/pulumi-proxmoxve/blob/main/sdk/python/pulumi_proxmoxve/vm/virtual_machine.py
        * https://registry.terraform.io/providers/bpg/proxmox/latest/docs/resources/virtual_environment_vm
    """
    for vms in vms_list:
        for vm in vms:
            virtual_machine = proxmox.vm.VirtualMachine(
                resource_name=vm["resource_name"],
                node_name=vm["node_name"],
                agent=proxmox.vm.VirtualMachineAgentArgs(
                    enabled=vm["agent"]["enabled"],
                    trim=vm["agent"]["trim"],
                    type=vm["agent"]["type"],
                ),
                bios=vm["bios"],
                cdrom=proxmox.vm.VirtualMachineCdromArgs(
                    enabled=vm["cdrom"]["enabled"],
                    file_id=vm["cdrom"]["file_id"],
                    interface=vm["cdrom"]["interface"],
                ),
                clone=proxmox.vm.VirtualMachineCloneArgs(
                    node_name=vm["clone"]["node_name"],
                    vm_id=vm["clone"]["vm_id"],
                    full=vm["clone"]["full"],
                ),
                cpu=proxmox.vm.VirtualMachineCpuArgs(
                    cores=vm["cpu"]["cores"],
                    sockets=vm["cpu"]["sockets"],
                    type=vm["cpu"]["type"],
                ),
                description=vm["description"],
                disks=create_sequence_from_list_of_dict(
                    proxmox.vm.VirtualMachineDiskArgs, vm["disks"]
                ),
                # efi_disk = proxmox.vm.VirtualMachineEfiDiskArgs(
                #     datastore_id = vm["efi_disk"]["datastore_id"],
                #     file_format = vm["efi_disk"]["file_format"],
                #     pre_enrolled_keys = vm["efi_disk"]["pre_enrolled_keys"],
                #     type = vm["efi_disk"]["type"]
                # ),
                initialization=proxmox.vm.VirtualMachineInitializationArgs(
                    type=vm["cloud_init"]["type"],
                    datastore_id=vm["cloud_init"]["datastore_id"],
                    dns=proxmox.vm.VirtualMachineInitializationDnsArgs(
                        domain=vm["cloud_init"]["dns"]["domain"],
                        server=vm["cloud_init"]["dns"]["server"],
                    ),
                    ip_configs=[
                        proxmox.vm.VirtualMachineInitializationIpConfigArgs(
                            ipv4=proxmox.vm.VirtualMachineInitializationIpConfigIpv4Args(
                                address=ip_config["ipv4"]["address"],
                                gateway=ip_config["ipv4"]["gateway"],
                            )
                            if ip_config.get("ipv4")
                            else None,
                            ipv6=proxmox.vm.VirtualMachineInitializationIpConfigIpv6Args(
                                address=ip_config["ipv6"]["address"],
                                gateway=ip_config["ipv6"]["gateway"],
                            )
                            if ip_config.get("ipv6")
                            else None,
                        )
                        for ip_config in vm["cloud_init"]["ip_configs"]
                    ],
                    user_account=proxmox.vm.VirtualMachineInitializationUserAccountArgs(
                        username=vm["cloud_init"]["user_account"]["username"],
                        password=vm["cloud_init"]["user_account"]["password"],
                        keys=[
                            ssh_key
                            for ssh_key in vm["cloud_init"]["user_account"]["keys"]
                        ],
                    ),
                ),
                keyboard_layout=vm["keyboard_layout"],
                machine=vm["machine"],
                memory=proxmox.vm.VirtualMachineMemoryArgs(
                    dedicated=vm["memory"]["dedicated"]
                ),
                name=vm["name"],
                network_devices=create_sequence_from_list_of_dict(
                    proxmox.vm.VirtualMachineNetworkDeviceArgs, vm["network_devices"]
                ),
                on_boot=vm["on_boot"],
                reboot=vm["reboot"],
                scsi_hardware=vm["scsi_hardware"],
                serial_devices=create_sequence_from_list_of_dict(
                    proxmox.vm.VirtualMachineSerialDeviceArgs, vm["serial_devices"]
                ),
                started=vm["started"],
                tags=vm["tags"],
                template=vm["template"],
                tpm_state=proxmox.vm.VirtualMachineTpmStateArgs(
                    datastore_id=vm["tpm_state"]["datastore_id"],
                    version=vm["tpm_state"]["version"],
                ),
                vga=proxmox.vm.VirtualMachineVgaArgs(
                    enabled=vm["vga"]["enabled"], type=vm["vga"]["type"]
                ),
                vm_id=vm["vm_id"],
            )
            pulumi.export(vm["name"], virtual_machine.id)


if __name__ == "__main__":
    create_vms_from_list(load_yaml_files_from_folder(pathlib.Path("vms")))

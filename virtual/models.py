from __future__ import unicode_literals
from django.db import models


class vCenterHosts(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=1000)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    address = models.CharField(max_length=200)
    url = models.URLField()
    thumbprint = models.CharField(max_length=64)
    department = models.CharField(max_length=8, null=True, default=None)


class Permissions(models.Model):
    class Meta:
        managed = False
        permissions = (
            ('view_vmware', 'Can view VMware objects'),
            ('view_proxmox', 'Can view Proxmox objects'),
            ('view_xen', 'Can view XenServer objects'),
            ('view_kvm', 'Can view KVM objects'),
            ('view_hyperv', 'Can view Hyper-V objects'),
            ('view_rhev', 'Can view RHEV objects'),
            ('add_vcenter', 'Can add VMware vCenter'),
            ('add_vmware', 'Can add VMware hosts'),
            ('add_proxmox', 'Can add Proxmox hosts'),
            ('add_xen', 'Can add XenServer hosts'),
            ('add_kvm', 'Can add KVM hosts'),
            ('add_hyperv', 'Can add Hyper-V hosts'),
            ('add_rhev', 'Can add RHEV hosts'),
            ('change_vcenter', 'Can edit VMware vCenter'),
            ('delete_vcenter', 'Can delete VMware vCenter'),
            ('list_vmware', 'Can list VMware guests'),
            ('list_vmware_hosts', 'Can list VMware ESX hosts'),
            ('list_proxmox', 'Can list Proxmox guests'),
            ('list_xen', 'Can list XenServer guests'),
            ('list_kvm', 'Can list KVM guests'),
            ('list_hyperv', 'Can list Hyper-V guests'),
            ('list_rhev', 'Can list RHEV guests'),
        )

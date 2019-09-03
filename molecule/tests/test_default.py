import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


@pytest.mark.parametrize('pkg', [
    'podman',
    # 'libselinux-python'
])
def test_telegraf_packages_installed(host, pkg):
    package = host.package(pkg)
    assert package.is_installed


def test_telegraf_config(host):
    for fname in ['/etc/telegraf', '/etc/telegraf/telegraf.conf',
                  '/etc/telegraf/env',
                  '/etc/systemd/system/telegraf-service.service']:
        data = host.file(fname)

        assert data.exists
        assert data.user == 'root'
        assert data.group == 'root'


def test_telegraf_running(host):
    service = host.service('telegraf-service')

    assert service.is_running
    assert service.is_enabled


def test_telegraf_ssl_certs(host):
    data = {
        '/etc/telegraf/telegraf.crt': {'mode': 0o644},
        '/etc/telegraf/telegraf.key.pem': {'mode': 0o600}
    }

    for fname in data.keys():
        cert_file = host.file(fname)

        assert cert_file.exists
        assert cert_file.mode == data[fname]['mode']

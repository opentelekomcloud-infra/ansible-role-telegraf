import os
import pytest

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


@pytest.fixture(scope='module')
def telegraf_user(host):
    ansible_vars = host.ansible.get_variables()
    user = ansible_vars.get('telegraf_os_user', 'telegraf')
    group = ansible_vars.get('telegraf_os_group', 'telegraf')

    return {'user': user, 'group': group}


@pytest.mark.parametrize('pkg', [
    'podman',
    # 'libselinux-python'
])
def test_telegraf_packages_installed(host, pkg):
    package = host.package(pkg)
    assert package.is_installed


def test_telegraf_systemd_config(host):
    data = host.file('/etc/systemd/system/telegraf-service.service')

    assert data.exists
    assert data.user == 'root'
    assert data.group == 'root'


def test_telegraf_user(host, telegraf_user):

    user = host.user(telegraf_user['user'])

    assert user.group == telegraf_user['group']


def test_telegraf_config(host, telegraf_user):

    for fname in ['/etc/telegraf',
                  '/etc/telegraf/env',
                  '/etc/telegraf/telegraf.conf']:
        data = host.file(fname)

        assert data.exists
        assert data.user == telegraf_user['user']
        assert data.group == telegraf_user['group']


def test_telegraf_running(host):
    service = host.service('telegraf-service')

    assert service.is_running
    assert service.is_enabled

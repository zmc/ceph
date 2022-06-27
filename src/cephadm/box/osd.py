import json
import os
import re
from typing import Dict

from util import (
    Config,
    Target,
    ensure_inside_container,
    ensure_outside_container,
    get_orch_hosts,
    inside_container,
    run_cephadm_shell_command,
    run_dc_shell_command,
    run_shell_command,
)


DEVICES_FILE="./devices.json"


def create_loopback_devices(osds: int) -> Dict:
    assert osds
    cleanup()
    osd_devs = dict()
    for i in range(osds):
        img_name = f'osd{i}'
        loop_dev = create_loopback_device(img_name)
        osd_devs[i] = dict(img_name=img_name, device=loop_dev)
    with open(DEVICES_FILE, 'w') as dev_file:
        dev_file.write(json.dumps(osd_devs))
    return osd_devs


def create_loopback_device(img_name, size_gb=5):
    loop_img_dir = Config.get('loop_img_dir')
    run_shell_command(f'mkdir -p {loop_img_dir}')
    loop_img = os.path.join(loop_img_dir, img_name)
    run_shell_command(f'rm -f {loop_img}')
    run_shell_command(f'dd if=/dev/zero of={loop_img} bs=1 count=0 seek={size_gb}G')
    loop_dev = run_shell_command(f'sudo losetup -f')
    if not os.path.exists(loop_dev):
        dev_minor = re.match(r'\/dev\/[^\d]+(\d+)', loop_dev).groups()[0]
        run_shell_command(f'sudo mknod -m777 {loop_dev} b 7 {dev_minor}')
        run_shell_command(f'sudo chown {os.getuid()}:{os.getgid()} {loop_dev}')
    if os.path.ismount(loop_dev):
        os.umount(loop_dev)
    run_shell_command(f'sudo losetup {loop_dev} {loop_img}')
    return loop_dev


def load_osd_devices():
    if not os.path.exists(DEVICES_FILE):
        return dict()
    with open(DEVICES_FILE) as dev_file:
        devs = json.loads(dev_file.read())
    return devs


@ensure_inside_container
def deploy_osd(data: str, hostname: str) -> bool:
    out = run_cephadm_shell_command(f'ceph orch daemon add osd "{hostname}:{data}" raw')
    return 'Created osd(s)' in out


def cleanup() -> None:
    loop_img_dir = Config.get('loop_img_dir')
    osd_devs = load_osd_devices()
    for osd in osd_devs.values():
        device = osd['device']
        if 'loop' in device:
            loop_img = os.path.join(loop_img_dir, osd['img_name'])
            run_shell_command(f'sudo losetup -d {device}', expect_error=True)
            if os.path.exists(loop_img):
                os.remove(loop_img)
    run_shell_command(f'rm -rf {loop_img_dir}')


def deploy_osds(count):
    if inside_container():
        print('xd')
        return
    osd_devs = load_osd_devices()
    hosts = get_orch_hosts()
    host_index = 0
    v = '-v' if Config.get('verbose') else ''
    for osd in osd_devs.values():
        deployed = False
        while not deployed:
            hostname = hosts[host_index]['hostname']
            deployed = run_dc_shell_command(
                f'/cephadm/box/box.py {v} osd deploy --data {osd["device"]} --hostname {hostname}',
                1,
                'seed'
            )
            deployed = 'created osd' in deployed.lower()
        host_index = (host_index + 1) % len(hosts)


class Osd(Target):
    _help = """
    Deploy osds and create needed block devices with loopback devices:
    Actions:
    - deploy: Deploy an osd given a block device
    - create_loop: Create needed loopback devices and block devices in logical volumes
    for a number of osds.
    """
    actions = ['deploy', 'create_loop']

    def set_args(self):
        self.parser.add_argument('action', choices=Osd.actions)
        self.parser.add_argument('--data', type=str, help='path to a block device')
        self.parser.add_argument('--hostname', type=str, help='host to deploy osd')
        self.parser.add_argument('--osds', type=int, default=0, help='number of osds')

    def deploy(self):
        data = Config.get('data')
        hostname = Config.get('hostname')
        if not hostname:
            # assume this host
            hostname = run_shell_command('hostname')
        if not data:
            deploy_osds(Config.get('osds'))
        else:
            deploy_osd(data, hostname)


    @ensure_outside_container
    def create_loop(self):
        osds = Config.get('osds')
        create_loopback_devices(int(osds))
        print('Successfully created loopback devices')

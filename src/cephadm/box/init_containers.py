from util import (
    Config,
    Target,
    get_boxes_container_info,
    inside_container,
    ensure_outside_container,
    run_cephadm_shell_command,
    run_dc_shell_command,
    run_shell_command,
)


class InitContainers(Target):
    _help = "Start and stop init containers"
    actions = ["start", "stop"]
    capabilities = [
        "SYS_ADMIN",
        "NET_ADMIN",
        "SYS_TIME",
        "SYS_RAWIO",
        "MKNOD",
        "NET_RAW",
        "SETUID",
        "SETGID",
        "CHOWN",
        "SYS_PTRACE",
        "SYS_TTY_CONFIG",
    ]

    def set_args(self):
        self.parser.add_argument("action", choices=self.__class__.actions)
        self.parser.add_argument("--osds", type=int, default=0, help="number of osds")
        self.parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Instead of performing actions, output a podman command",
        )

    @staticmethod
    def _run_shell_cmd(args, expect_error=False):
        dry_run = Config.get("dry_run")
        if isinstance(args, list):
            cmd = " ".join(args)
        else:
            cmd = args
        if not dry_run:
            return run_shell_command(cmd, expect_error=expect_error)
        else:
            print(cmd)

    @classmethod
    @ensure_outside_container
    def start(cls):
        cls._run_shell_cmd("podman network create box || true")
        cls._run_shell_cmd(cls._get_start_command("seed", 1))
        cls._run_shell_cmd(cls._get_start_command("hosts", 1))

    @classmethod
    @ensure_outside_container
    def stop(cls):
        cls._run_shell_cmd(
            f"podman container rm -f {cls.get_name('seed', 1)} {cls.get_name('hosts', 1)}",
            expect_error=True,
        )
        cls._run_shell_cmd(f"podman network rm -f box", expect_error=True)

    @staticmethod
    def get_name(type_, index):
        return f"box_{type_}_{index}"

    @classmethod
    def _get_start_command(cls, type_, index):
        cmd = ["podman", "run"]
        posargs = ["cephadm-box"]
        args = [
            "--rm",
            "-i",
            "-d",
            "--name",
            cls.get_name(type_, index),
            "--network",
            "box",
            "--cap-add",
            ",".join(cls.capabilities),
            "--security-opt",
            "unmask=/sys/dev/block",
            "-v",
            "../../../:/ceph:z",
            "-v",
            "..:/cephadm:z",
            "-v",
            "/run/udev:/run/udev",
            "-v",
            "/sys/dev/block:/sys/dev/block",
            "-v",
            "/sys/fs/cgroup:/sys/fs/cgroup",
            "-v",
            "/dev/fuse:/dev/fuse",
            "-v",
            "/dev/disk:/dev/disk",
        ]
        for i in range(int(Config.get("osds"))):
            args.extend(["--device", f"/dev/loop{i}"])
        if type_ == "seed":
            args.extend(
                [
                    "-p",
                    "2222:22",
                    "-p",
                    "3000:3000",
                    "-p",
                    "8888:8888",
                    "-p",
                    "8443:8443",
                    "-p",
                    "9095:9095",
                ]
            )
        return cmd + args + posargs

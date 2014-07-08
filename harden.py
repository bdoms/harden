import argparse
import subprocess


def createNewAdminUser():
    username = raw_input("What username would you like? ")
    available = True
    try:
        subprocess.call(["id", "-u", username])
    except subprocess.CalledProcessError:
        available = False
    assert available, "That username is already in use."

    subprocess.call(["sudo", "adduser", "--gecos", "", username]) # create user
    subprocess.call(["sudo", "adduser", username, "sudo"]) # add to sudo group


def disableRootLogin():
    with open("/etc/ssh/sshd_config", "r+") as sshd_config:
        content = sshd_config.read()
        content = content.replace("PermitRootLogin yes", "PermitRootLogin no")
        sshd_config.seek(0)
        sshd_config.write(content)
        sshd_config.truncate()

    subprocess.call(["sudo", "service", "ssh", "restart"])


def restrictPorts(open_ports, limit_ports, log_ports):
    if 22 not in open_ports:
        warning = "WARNING! 22 is not in the list of ports to keep open.\n"
        warning += "Without it, you will not be able to remotely login\n"
        warning += "unless you have SSH configured to use a different port."
        print warning
        response = raw_input("Are you sure you want to continue without port 22 (y|n)? ").lower()
        if response != "y" and response != "yes":
            return

    subprocess.call(["sudo", "apt-get", "install", "ufw"])

    for port in open_ports:
        command = ["ufw"]
        if port in limit_ports:
            command.extend(["limit", "in"])
        else:
            command.append("allow")
        if port in log_ports:
            command.append("log")
        command.append(str(port) + "/tcp")
        subprocess.call(command)

    subprocess.call(["ufw", "enable"])


def harden(skip_user, open_ports, limit_ports, log_ports):
    if not skip_user:
        createNewAdminUser()

    disableRootLogin()

    restrictPorts(open_ports, limit_ports, log_ports)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--ports", nargs="+", type=int, default=[22, 80, 443], help="list of ports to keep open (default: 22 80 443)")
    parser.add_argument("--limit_ports", nargs="+", type=int, default=[22], help="list of ports to limit access to (default: 22)")
    parser.add_argument("--log_ports", nargs="+", type=int, default=[22], help="list of ports to log access to (default: 22)")
    parser.add_argument("--skip_user", action="store_true", help="skip creating a separate non-root user account")
    args = parser.parse_args()

    harden(args.skip_user, args.ports, args.limit_ports, args.log_ports)

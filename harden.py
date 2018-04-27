import argparse
import os
import shutil
import subprocess

# support both Python 2 and 3
try:
    input = raw_input
except NameError:
    pass


def createNewAdminUser():
    root_keys = os.path.join(os.path.sep, "root", ".ssh", "authorized_keys")
    assert os.path.exists(root_keys), "Root has no SSH keys."

    username = input("What username would you like? ")
    available = False
    try:
        # note that call does not trigger the error, but check_output does
        subprocess.check_output(["id", "-u", username])
    except subprocess.CalledProcessError:
        available = True
    assert available, "That username is already in use."

    # create user and add to sudo group
    subprocess.call(["adduser", "--gecos", "", username])
    subprocess.call(["adduser", username, "sudo"])

    # copy SSH keys
    user_ssh = os.path.join(os.path.sep, "home", username, ".ssh")
    if not os.path.exists(user_ssh):
        os.mkdir(user_ssh)
    shutil.copyfile(root_keys, os.path.join(user_ssh, "authorized_keys"))

    # ensure keys are owned by the new user
    subprocess.call(["chown", "-R", username + ":" + username, user_ssh])


def disableRootLogin():
    with open("/etc/ssh/sshd_config", "r+") as sshd_config:
        content = sshd_config.read()
        content = content.replace("PermitRootLogin yes", "PermitRootLogin no")
        content = content.replace("PasswordAuthentication yes", "PasswordAuthentication no")
        sshd_config.seek(0)
        sshd_config.write(content)
        sshd_config.truncate()

    subprocess.call(["service", "ssh", "restart"])


def restrictPorts(open_ports, limit_ports, log_ports):
    if 22 not in open_ports:
        warning = "WARNING! 22 is not in the list of ports to keep open.\n"
        warning += "Without it, you will not be able to remotely login\n"
        warning += "unless you have SSH configured to use a different port."
        print(warning)
        response = input("Are you sure you want to continue without port 22 (y|n)? ").lower()
        if response != "y" and response != "yes":
            return

    subprocess.call(["apt", "install", "ufw"])

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

    restrictPorts(open_ports, limit_ports, log_ports)

    disableRootLogin()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--ports", nargs="+", type=int, default=[22, 80, 443], help="list of ports to keep open (default: 22 80 443)")
    parser.add_argument("--limit_ports", nargs="+", type=int, default=[22], help="list of ports to limit access to (default: 22)")
    parser.add_argument("--log_ports", nargs="+", type=int, default=[22], help="list of ports to log access to (default: 22)")
    parser.add_argument("--skip_user", action="store_true", help="skip creating a separate non-root user account")
    args = parser.parse_args()

    harden(args.skip_user, args.ports, args.limit_ports, args.log_ports)

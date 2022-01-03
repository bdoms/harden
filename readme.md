Copyright &copy; 2014-2020, [Brendan Doms](http://www.bdoms.com/)
Licensed under the [MIT license](http://www.opensource.org/licenses/MIT)

# Harden
This is a script to prepare an Ubuntu box intended to be used as a public web server.
Specifically, it:

 * Creates an admin group user for remote access
 * Disables logging in as root or with a password
 * Sets up a firewall to block most ports


## Quick Use
The script is designed to be used out of the box on a modern Ubuntu distro (12.04 and up).
You should have wget and some version of python by default, so there's nothing to install.
Simply make sure you have root privileges and then run:

```bash
wget https://raw.githubusercontent.com/bdoms/harden/master/harden.py
python3 harden.py
```

Once it finishes, log out (if that didn't happen automatically).
You should no longer be able to ssh as root, but your new user should work fine.


## Options

### Skip User Creation
If you already have a user setup for remote access you can skip that step with the `--skip_user` option.

### Define Ports
You can define which ports will be opened in the `-p` or `--ports` list (default: 22 80 443).

To rate limit access to an opened port include it in the `--limit_ports` list (default: 22).

To log access to an opened port include it in the `--log_ports` list (default: 22).

Harden uses [UFW](https://help.ubuntu.com/community/UFW) as its firewall.
You can continue to change its behavior after this script has run using its usual commands.

### Support HTTP3
By default only TCP is allowed on open ports.

Include the `--http3` option for UDP to also be allowed on both ports 80 and 443,
as this is required for HTTP3 to work.

No other ports will be affected.


## Other Considerations
The basic modern Ubuntu server image used does not include the following packages,
but if they are installed they should be removed:

 * vsftp
 * telnetd
 * rsh-server

This is just a list of commonly installed packages in many distributions and is obviously incomplete.
Any package that opens a port or allows for remote login should be suspect.

You can use `ufw status` to check the status of the firewall
and something like `netstat -ltunp` to confirm which ports are active for yourself.

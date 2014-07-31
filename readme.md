Copyright &copy; 2014, [Brendan Doms](http://www.bdoms.com/)  
Licensed under the [MIT license](http://www.opensource.org/licenses/MIT)

# Harden
This is a script to prepare an Ubuntu box intended to be used as a web server.
Specifically, it:

 * Creates an admin group user for remote access
 * Disables logging in as root
 * Sets up a firewall to block most ports

## Options

### Skip User Creation
If you already have a user setup for remote access you can skip that step with the `--skip_user` option.

### Define Ports
You can define which ports will be opened in the `-p` or `--ports` list.

To automatically rate limit access to an opened port include that port in the `--limit_ports` list.

To log access to an opened port include that port in the `--log_ports` list.

Harden uses [UFW](https://help.ubuntu.com/community/UFW) as its firewall.
You can continue to change its behavior after this script has run using its usual commands.

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

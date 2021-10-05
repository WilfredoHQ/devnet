import signal
from ipaddress import IPv4Address

from click import argument, command, group, secho


def sigint_handler(signum, frame):
    secho("\nEjecución finalizada", fg="yellow")
    exit(1)


signal.signal(signal.SIGINT, sigint_handler)


@group()
def cli():
    pass


@command()
@argument("number", type=int)
def port(number):
    known_ports = (0, 1023)
    registered_ports = (1024, 49151)
    private_ports = (49152, 65535)

    if number in range(known_ports[0], known_ports[1] + 1):
        secho("Puerto bien conocido", fg="cyan")
    elif number in range(registered_ports[0], registered_ports[1] + 1):
        secho("Puerto registrado", fg="cyan")
    elif number in range(private_ports[0], private_ports[1] + 1):
        secho("Puerto privado", fg="cyan")
    else:
        secho("Fuera de rango", fg="red")


@command()
@argument("ip", type=IPv4Address)
def ipadd(ip):
    if IPv4Address(ip).is_global:
        secho("IP Pública", fg="cyan")
    elif IPv4Address(ip).is_private:
        secho("IP Privada", fg="cyan")

    if IPv4Address(ip) >= IPv4Address("0.0.0.0") and IPv4Address(ip) <= IPv4Address("127.255.255.255"):
        secho("Clase A", fg="cyan")
    elif IPv4Address(ip) >= IPv4Address("128.0.0.0") and IPv4Address(ip) <= IPv4Address("191.255.255.255"):
        secho("Clase B", fg="cyan")
    elif IPv4Address(ip) >= IPv4Address("192.0.0.0") and IPv4Address(ip) <= IPv4Address("223.255.255.255"):
        secho("Clase C", fg="cyan")
    elif IPv4Address(ip) >= IPv4Address("224.0.0.0") and IPv4Address(ip) <= IPv4Address("239.255.255.255"):
        secho("Clase D", fg="cyan")
    elif IPv4Address(ip) >= IPv4Address("240.0.0.0") and IPv4Address(ip) <= IPv4Address("255.255.255.255"):
        secho("Clase E", fg="cyan")


cli.add_command(port)
cli.add_command(ipadd)

if __name__ == '__main__':
    cli()

''' Top level of CLI '''

import click
from sp import sp


@click.group("vtc")
def vtc():
    """vtc CLI"""
    pass


def main():
    ''' Add sp command and run '''
    vtc.add_command(sp)
    vtc()


if __name__ == '__main__':
    main()

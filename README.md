# aur_repo
Build repo from aur packages

I recommend running this in a container or VM to prevent installing unwanted packages. To install:

prereqs:
'''
pip install sh
pip install requirements
pacman -S darkhttpd
'''

then add a build user:
'''
useradd -m -G wheel build
'''

use visudo to uncomment the nopasswd line for wheel.
create a build and repo dir:
'''
mkdir /build
mkdir /repo
chown build /build
chown build /repo
'''

add packages you want to build in /etc/aur_repo/pkglist

then as the build user run aur_repo.py from wherever you cloned it. Once everything is built run:
'''
darkhttpd /repo
'''

then on any machine that you want to sync to your aur repo add the following to /etc/pacman.conf:
'''
[aur-local]
Server = http://[ip-of-your-container]
'''

eventually I plan to add multi-arch support so you can use this to build raspberrypi packages.

# aur_repo
Build repo from aur packages

I recommend running this in a container or VM to prevent installing unwanted packages. To install:

install:
```
git clone https://github.com/etrombly/aur_repo.git
cd aur_repo
makepkg -si
```

use visudo to uncomment the nopasswd line for wheel.

add packages you want to build in /etc/aur_repo/pkglist, one per line

then as the build user run aur_repo.

then on any machine that you want to sync to your aur repo add the following to /etc/pacman.conf:
```
[aur-local]
Server = http://[ip-of-your-container]
```

eventually I plan to add multi-arch support so you can use this to build raspberrypi packages.

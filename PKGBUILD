# Maintainer: etrombly <etrombly at gmail dot com>
pkgname=aur_repo-git
pkgver=10.a765258
pkgrel=1
epoch=
pkgdesc="Build local repo from aur packages"
arch=('any')
url="https://github.com/etrombly/aur_repo"
license=('GPL')
groups=()
depends=('sudo' 'python' 'python-requests' 'python-sh' 'darkhttpd')
makedepends=('git')
optdepends=()
checkdepends=()
provides=()
conflicts=()
replaces=()
backup=()
options=()
changelog=
install=aur_repo.install
source=("$pkgname::git+https://github.com/etrombly/aur_repo")
noextract=()
md5sums=('SKIP')

pkgver() {
  cd "$srcdir/$pkgname"
  printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package() {
  cd "$srcdir/$pkgname"
  python setup.py install --root="$pkgdir/" --optimize=1
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
  install -Dm544 aur_repo.service "$pkgdir/etc/systemd/system/aur_repo.service"
}

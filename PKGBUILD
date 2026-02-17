# Maintainer: Masoud Gholypour  Masoudgholypour2000@gmail.com
pkgname=ollama-webui
pkgver=0.1.0
pkgrel=1
pkgdesc="A beautiful web interface for Ollama with conversation management and markdown support"
arch=('any')
url="https://github.com/yourusername/ollama-webui"
license=('MIT')
depends=('python' 'python-flask' 'python-requests' 'ollama' 'python-werkzeug')
makedepends=('python-build' 'python-installer' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz::https://github.com/yourusername/ollama-webui/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$srcdir/$pkgname-$pkgver"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/$pkgname-$pkgver"
    python -m installer --destdir="$pkgdir" dist/*.whl
    
    # Create systemd service file
    install -Dm644 "$srcdir/$pkgname-$pkgver/ollama-webui.service" "$pkgdir/usr/lib/systemd/system/ollama-webui.service"
    
    # Create configuration directory
    install -dm755 "$pkgdir/etc/ollama-webui"
}
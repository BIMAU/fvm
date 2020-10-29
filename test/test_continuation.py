import continuation
import numpy

from fvm import plot_utils

def test_continuation(nx=4, interactive=False):
    dof = 4
    ny = nx
    nz = nx
    n = dof * nx * ny * nz

    parameters = {}
    interface = continuation.Interface(parameters, nx, ny, nz, dof)

    x0 = numpy.zeros(dof * nx * ny * nz)
    x0 = continuation.newton(interface, x0, 0)

    l = 0
    target = 100
    ds = 100
    maxit = 20
    x = continuation.continuation(interface, x0, l, target, ds, maxit)

    assert numpy.linalg.norm(x) > 0

    if not interactive:
        return

    print(x)

    x = plot_utils.create_create_state_mtx(x, nx, ny, nz, dof)
    plot_utils.plot_state(x[:,ny//2,:,0], x[:,ny//2,:,2], nx, nz)

def test_continuation_2D(nx=8, interactive=False):
    dof = 4
    ny = nx
    nz = 1
    n = dof * nx * ny * nz

    parameters = {}
    interface = continuation.Interface(parameters, nx, ny, nz, dof)

    x0 = numpy.zeros(dof * nx * ny * nz)
    x0 = continuation.newton(interface, x0, 0)

    l = 0
    target = 2000
    ds = 100
    maxit = 20
    x = continuation.continuation(interface, x0, l, target, ds, maxit)

    assert numpy.linalg.norm(x) > 0

    if not interactive:
        return

    print(x)

    x = plot_utils.create_state_mtx(x, nx, ny, nz, dof)
    plot_utils.plot_state(x[:,:,0,0], x[:,:,0,1], nx, ny)

if __name__ == '__main__':
    test_continuation(8, False)
    # test_continuation_2D(8, True)
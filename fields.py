import numpy as np
from astropy import units as u, constants as const


def expand2(*arrays):
    """Add two unity axes to all arrays."""
    return [np.reshape(array, np.shape(array)+(1, 1))
            for array in arrays]


# Construct the dynamic spectrum directly
def dynamic_field(theta_par, theta_perp, realization, d_eff, mu_eff, f, t):
    """Given a set of scattering points, construct the dynamic wave field.

    Parameters
    ----------
    theta_par : ~astropy.units.Quantity
        Angles of the scattering point in the direction parallel to ``mu_eff``
    theta_perp : ~astropy.units.Quantity
        Angles perpendiculat to ``mu_eff``.
    realization : array-like
        Complex amplitudes of the scattering points
    d_eff : ~astropy.units.Quantity
        Effective distance.  Should be constant; if different for
        different points, no screen-to-screen scattering is taken into
        account.
    mu_eff : ~astropy.units.Quantity
        Effective proper motion (``v_eff / d_eff``), parallel to ``theta_par``.
    t : ~astropy.units.Quantity
        Times for which the dynamic wave spectrum should be calculated.
    f : ~astropy.units.frequency
        Frequencies for which the spectrum should be calculated.

    Returns
    -------
    dynwave : array
        Delayed wave field array, with last axis time, second but last
        frequency, and earlier axes as given by the other parameters.
    """
    theta_par, theta_perp, realization, d_eff, mu_eff = expand2(
        theta_par, theta_perp, realization, d_eff, mu_eff)
    th_par = theta_par + mu_eff * t
    tau_t = (d_eff / (2*const.c)) * (th_par**2 + theta_perp**2)
    phase = (f[:, np.newaxis] * u.cycle * tau_t).to_value(
        u.one, u.dimensionless_angles())
    return realization * np.exp(-1j * phase)


def theta_theta(theta, d_eff, mu_eff, dynspec, f, t):
    dynwave = dynamic_field(theta, 0, 1., d_eff, mu_eff, f, t)
    # Get intensities by brute-force mapping.
    pairs = dynwave * dynwave[:, np.newaxis].conj()
    # Remove constant parts
    pairs -= pairs.mean((-2, -1), keepdims=True)
    return (dynspec * pairs).mean((-2, -1))


def clean_theta_theta(theta_theta, k=1, clean_cross=True):
    if k > 1:
        theta_theta = np.triu(theta_theta, k=k) + np.tril(theta_theta, k=-k)
    if clean_cross:
        i = np.arange(theta_theta.shape[0]-1)
        theta_theta[theta_theta.shape[0]-1-i, i+1] = 0
    return theta_theta

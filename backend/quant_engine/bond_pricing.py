import numpy as np
from .vasicek import VasicekParams, bond_price as vasicek_bond
from .cir import CIRParams, bond_price as cir_bond


def coupon_bond_price(
    face: float,
    coupon_rate: float,
    maturity: float,
    r: float,
    params: VasicekParams | CIRParams,
    frequency: int = 2,
) -> float:
    """
    Price a fixed-coupon bond using the closed-form zero-coupon formula.
    coupon_rate: annual coupon as a percentage (e.g. 7.0)
    maturity: years to maturity
    frequency: coupon payments per year (2 = semi-annual)
    r: current short rate as percentage
    """
    r_dec = r / 100.0
    coupon = face * (coupon_rate / 100) / frequency
    n_coupons = int(maturity * frequency)
    dt = maturity / n_coupons

    price = 0.0
    pricer = vasicek_bond if isinstance(params, VasicekParams) else cir_bond

    for i in range(1, n_coupons + 1):
        tau = i * dt
        cf = coupon + (face if i == n_coupons else 0)
        price += cf * pricer(r_dec, tau, params)

    return price


def duration(
    face: float,
    coupon_rate: float,
    maturity: float,
    r: float,
    params: VasicekParams | CIRParams,
    frequency: int = 2,
) -> tuple[float, float]:
    """Returns (modified_duration, convexity)."""
    price = coupon_bond_price(face, coupon_rate, maturity, r, params, frequency)
    if price <= 0:
        return 0.0, 0.0

    r_dec = r / 100.0
    coupon = face * (coupon_rate / 100) / frequency
    n_coupons = int(maturity * frequency)
    dt = maturity / n_coupons

    mac_dur = 0.0
    convexity = 0.0
    pricer = vasicek_bond if isinstance(params, VasicekParams) else cir_bond

    for i in range(1, n_coupons + 1):
        tau = i * dt
        cf = coupon + (face if i == n_coupons else 0)
        pv = cf * pricer(r_dec, tau, params)
        mac_dur += tau * pv
        convexity += tau**2 * pv

    mac_dur /= price
    convexity /= price
    modified_dur = mac_dur / (1 + r_dec / frequency)
    return modified_dur, convexity


def price_from_paths(
    terminal_rates: np.ndarray,
    face: float,
    coupon_rate: float,
    maturity: float,
    params: VasicekParams | CIRParams,
    frequency: int = 2,
) -> np.ndarray:
    """
    Compute bond prices for each terminal rate from a simulation.
    terminal_rates: shape (n_paths,), values in percentage
    Returns array of prices, shape (n_paths,).
    """
    pricer = vasicek_bond if isinstance(params, VasicekParams) else cir_bond
    r_dec = terminal_rates / 100.0
    coupon = face * (coupon_rate / 100) / frequency
    n_coupons = int(maturity * frequency)
    dt = maturity / n_coupons

    prices = np.zeros(len(terminal_rates))
    for i in range(1, n_coupons + 1):
        tau = i * dt
        cf = coupon + (face if i == n_coupons else 0)
        prices += cf * np.array([pricer(r, tau, params) for r in r_dec])

    return prices

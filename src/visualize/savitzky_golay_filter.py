from math import factorial

import matplotlib.pyplot as plt
import numpy as np


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    try:
        window_size = np.abs(int(window_size))
        order = np.abs(int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order + 1)
    half_window = (window_size - 1) // 2
    # precompute coefficients
    b = np.mat([[k ** i for i in order_range] for k in range(-half_window, half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate ** deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')


def run_sample(input_values):
    yhat = savitzky_golay(input_values, 11, 3)  # window size 51, polynomial order 3
    plt.plot(yhat, color='red')

    plt.plot(input_values)
    plt.show()


if __name__ == '__main__':
    values = np.array(
        [0.2974774900480471, 0.26166490051242947, 0.28157702839280585, 0.2834612307534857, 0.23739148714836875,
         0.08796952136816227, 0.15729411689157305, 0.14356136485063217, 0.15078179360649646, 0.12750521440342114,
         0.12442443004090388, 0.15504274574474403, 0.16099541595102768, 0.13141817765856229, 0.1524160540857883,
         0.20775363736857733, 0.1423425730369403, 0.2003659457085812, 0.2944301433639311, 0.24287230305198132,
         0.6304357999778554, 0.1942745356156688, 0.39226304950928226, 0.25030706747136233, 0.4548531076114601,
         0.15261458226067998, 0.19708244418206466, 0.06171647021955009, 0.13046805331248001, 0.06880848042748997,
         0.1318014144538509, 0.06875412752336937, 0.19232660465002957, 0.09550963441219383, 0.265385400061375,
         0.18896531697281468, 0.2126695552062585, 0.29426805924701915, 0.27042037030897625, 0.2721721904259807,
         0.5650173554790441, 0.29155174646175674, 0.5399656173645234, 0.2997483536248734, 0.4621646649180683,
         0.18903413808219374, 0.44069075353492365, 0.07166044119882334, 0.1250719572122876, 0.01306077698425678,
         0.09284149086333703, 0.09804564152120206, 0.16099029410229834, 0.06857410035570143, 0.1985873784579649,
         0.12376342633038775, 0.12057696173691006, 0.14573819828103518, 0.15420951350752365, 0.08984871686384684,
         0.24651127365205655, 0.1275023839798852, 0.08406395826824999, 0.25434575579539553, 0.3899212923644382,
         0.2659257388670917, 0.585107068323532, 0.2567294394669295, 0.37229821602874125, 0.3282683712231703,
         0.4024324182745553, 0.12368310238012388, 0.45266194697009543, 0.0935554082041884, 0.07861228295747591,
         0.16275624583048995, 0.12099858558954683, 0.18378317460966073, 0.10675078858145189, 0.18562380760251534,
         0.09943437876121156, 0.1940169334265087, 0.10712286756445523, 0.03649572834050981, 0.08722257928404548,
         0.11238729823008611, 0.17843944666255362, 0.19303109766350357, 0.3705205801038498, 0.21095727072534945,
         0.06505727380517248, 0.21058364012402123, 0.14421630436254904, 0.2024501394257053, 0.43648553353871045,
         0.11556953796195996, 0.2478735408699811, 0.05589579573529832, 0.091308591850473, 0.1011145193741646,
         0.10984132830519538, 0.12643008974233022, 0.10363171316960684, 0.12451680340989596, 0.09951606555672636,
         0.11006641495769867, 0.10974266055064537, 0.0705316234353229, 0.10661010620619774, 0.08449672649108618,
         0.11364370216418793, 0.0883187135225656, 0.09440759737449506, 0.14788121215989655, 0.09115108441761194,
         0.04698977984853716, 0.04175040933263083, 0.17744604892715612, 0.29550441571075, 0.1473588676625753,
         0.4401950226995507, 0.19894032836767284, 0.1373803261780288, 0.23062413774005808, 0.14583152889250744,
         0.20780383307636172, 0.13059423748279908, 0.19361621009531815, 0.11353781236752314, 0.16900937864376134,
         0.10937259489616309, 0.19390784816827666, 0.11761683030213285, 0.09001268815558566, 0.1354440082968187])

    run_sample(values)

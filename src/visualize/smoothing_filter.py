import numpy


def smooth(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s = numpy.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]
    # print(len(s))
    if window == 'flat':  # moving average
        w = numpy.ones(window_len, 'd')
    else:
        w = eval('numpy.' + window + '(window_len)')

    y = numpy.convolve(w / w.sum(), s, mode='valid')
    return y


from pylab import *


def test_smoothing():
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

    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']

    # for w in windows:
    #     plot(smooth(values, 21, w))


    y = smooth(values, 16, 'hanning')

    plt.plot(values, c="red")
    plt.plot(y, c="black")

    plt.ylabel('some numbers')
    plt.show()


def smooth_demo():
    t = linspace(-4, 4, 100)
    x = sin(t)
    xn = x + randn(len(t)) * 0.1
    y = smooth(x)

    ws = 31

    subplot(211)
    plot(ones(ws))

    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']

    # hold(True)
    for w in windows[1:]:
        eval('plot(' + w + '(ws) )')

    axis([0, 30, 0, 1.1])

    legend(windows)
    title("The smoothing windows")
    subplot(212)
    plot(x)
    plot(xn)
    for w in windows:
        plot(smooth(xn, 10, w))
    l = ['original signal', 'signal with noise']
    l.extend(windows)

    legend(l)
    title("Smoothing a noisy signal")
    show()


if __name__ == '__main__':
    # smooth_demo()
    test_smoothing()

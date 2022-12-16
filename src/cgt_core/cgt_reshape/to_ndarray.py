import numpy as np

arr = [
    [
        0,
        [
            0.45360007882118225,
            0.2710459232330322,
            -0.04389750957489014
        ]
    ],
    [
        1,
        [
            0.4487285315990448,
            0.20153209567070007,
            -0.0633302703499794
        ]
    ],
    [
        2,
        [
            0.44876205921173096,
            0.22322767972946167,
            -0.03736548125743866
        ]
    ],
    [
        3,
        [
            0.437217652797699,
            0.15410038828849792,
            -0.0409834198653698
        ]
    ],
]


def construct_matrix(arr):
    res = []

    for i, _landmark in arr:
        landmark = np.array([_landmark])
        rot_sca = np.zeros(6).reshape(2, 3)
        
        r = np.concatenate((landmark, rot_sca, landmark), axis=0)
        print(r)
        res.append(r)

    print(res)


construct_matrix(arr)

import numpy as np
import copy

initial_fibers = {
    "fibers_box_extent": np.array([4000.0, 2000.0, 2000.0]),
    "fibers": {
        "1": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 912.50000000, 1000.00000000]),
                np.array([3160.00000000, 912.50000000, 1000.00000000]),
            ],
        },
        "2": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 947.50000000, 939.37822174]),
                np.array([3160.00000000, 947.50000000, 939.37822174]),
            ],
        },
        "3": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 930.00000000, 969.68911087]),
                np.array([3160.00000000, 930.00000000, 969.68911087]),
            ],
        },
        "4": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 947.50000000, 1000.00000000]),
                np.array([3160.00000000, 947.50000000, 1000.00000000]),
            ],
        },
        "5": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 930.00000000, 1030.31088913]),
                np.array([3160.00000000, 930.00000000, 1030.31088913]),
            ],
        },
        "6": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 947.50000000, 1060.62177826]),
                np.array([3160.00000000, 947.50000000, 1060.62177826]),
            ],
        },
        "7": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 965.00000000, 909.06733260]),
                np.array([3160.00000000, 965.00000000, 909.06733260]),
            ],
        },
        "8": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 982.50000000, 939.37822174]),
                np.array([3160.00000000, 982.50000000, 939.37822174]),
            ],
        },
        "9": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 965.00000000, 969.68911087]),
                np.array([3160.00000000, 965.00000000, 969.68911087]),
            ],
        },
        "10": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 982.50000000, 1000.00000000]),
                np.array([3160.00000000, 982.50000000, 1000.00000000]),
            ],
        },
        "11": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 965.00000000, 1030.31088913]),
                np.array([3160.00000000, 965.00000000, 1030.31088913]),
            ],
        },
        "12": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 982.50000000, 1060.62177826]),
                np.array([3160.00000000, 982.50000000, 1060.62177826]),
            ],
        },
        "13": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 965.00000000, 1090.93266740]),
                np.array([3160.00000000, 965.00000000, 1090.93266740]),
            ],
        },
        "14": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1000.00000000, 909.06733260]),
                np.array([3160.00000000, 1000.00000000, 909.06733260]),
            ],
        },
        "15": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1017.50000000, 939.37822174]),
                np.array([3160.00000000, 1017.50000000, 939.37822174]),
            ],
        },
        "16": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1000.00000000, 969.68911087]),
                np.array([3160.00000000, 1000.00000000, 969.68911087]),
            ],
        },
        "17": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1017.50000000, 1000.00000000]),
                np.array([3160.00000000, 1017.50000000, 1000.00000000]),
            ],
        },
        "18": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1000.00000000, 1030.31088913]),
                np.array([3160.00000000, 1000.00000000, 1030.31088913]),
            ],
        },
        "19": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1017.50000000, 1060.62177826]),
                np.array([3160.00000000, 1017.50000000, 1060.62177826]),
            ],
        },
        "20": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1000.00000000, 1090.93266740]),
                np.array([3160.00000000, 1000.00000000, 1090.93266740]),
            ],
        },
        "21": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1035.00000000, 909.06733260]),
                np.array([3160.00000000, 1035.00000000, 909.06733260]),
            ],
        },
        "22": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1052.50000000, 939.37822174]),
                np.array([3160.00000000, 1052.50000000, 939.37822174]),
            ],
        },
        "23": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1035.00000000, 969.68911087]),
                np.array([3160.00000000, 1035.00000000, 969.68911087]),
            ],
        },
        "24": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1052.50000000, 1000.00000000]),
                np.array([3160.00000000, 1052.50000000, 1000.00000000]),
            ],
        },
        "25": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1035.00000000, 1030.31088913]),
                np.array([3160.00000000, 1035.00000000, 1030.31088913]),
            ],
        },
        "26": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1052.50000000, 1060.62177826]),
                np.array([3160.00000000, 1052.50000000, 1060.62177826]),
            ],
        },
        "27": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1035.00000000, 1090.93266740]),
                np.array([3160.00000000, 1035.00000000, 1090.93266740]),
            ],
        },
        "28": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1070.00000000, 969.68911087]),
                np.array([3160.00000000, 1070.00000000, 969.68911087]),
            ],
        },
        "29": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1087.50000000, 1000.00000000]),
                np.array([3160.00000000, 1087.50000000, 1000.00000000]),
            ],
        },
        "30": {
            "type_name": "Actin-Polymer",
            "points": [
                np.array([1000.00000000, 1070.00000000, 1030.31088913]),
                np.array([3160.00000000, 1070.00000000, 1030.31088913]),
            ],
        },
    },
}


def centered_initial_fibers():
    result = initial_fibers
    for fiber_id in initial_fibers["fibers"]:
        fiber_points = initial_fibers["fibers"][fiber_id]["points"]
        for point_index in range(len(fiber_points)):
            result["fibers"][fiber_id]["points"][point_index] = (
                fiber_points[point_index] - 0.5 * initial_fibers["fibers_box_extent"]
            )
    return result

def map_fibers(f, initial_fibers):
    result = copy.deepcopy(initial_fibers)
    for fiber_id in initial_fibers["fibers"]:
        fiber_points = initial_fibers["fibers"][fiber_id]["points"]
        for point_index in range(len(fiber_points)):
            result["fibers"][fiber_id]["points"][point_index] = (
                f(fiber_points[point_index], initial_fibers["fibers_box_extent"])
            )
    return result


def single_fiber():
    fiber = {
        "fibers_box_extent": np.array([4000.0, 2000.0, 2000.0]),
        "fibers": {
            '1': {
                "type_name": "Actin-Polymer",
                "points": [
                    np.array([-0.250, 0.000, 0.000]),
                    np.array([-0.240, 0.000, 0.000]),
                    np.array([-0.230, 0.000, 0.000]),
                    np.array([-0.220, 0.000, 0.000]),
                    np.array([-0.210, 0.000, 0.000]),
                    np.array([-0.200, 0.000, 0.000]),
                    np.array([-0.190, 0.000, 0.000]),
                    np.array([-0.180, 0.000, 0.000]),
                    np.array([-0.170, 0.000, 0.000]),
                    np.array([-0.160, 0.000, 0.000]),
                    np.array([-0.150, 0.000, 0.000]),
                    np.array([-0.140, 0.000, 0.000]),
                    np.array([-0.130, 0.000, 0.000]),
                    np.array([-0.120, 0.000, 0.000]),
                    np.array([-0.110, 0.000, 0.000]),
                    np.array([-0.100, 0.000, 0.000]),
                    np.array([-0.090, 0.000, 0.000]),
                    np.array([-0.080, 0.000, 0.000]),
                    np.array([-0.070, 0.000, 0.000]),
                    np.array([-0.060, 0.000, 0.000]),
                    np.array([-0.050, 0.000, 0.000]),
                    np.array([-0.040, 0.000, 0.000]),
                    np.array([-0.030, 0.000, 0.000]),
                    np.array([-0.020, 0.000, 0.000]),
                    np.array([-0.010, 0.000, 0.000]),
                    np.array([0.000, 0.000, 0.000]),
                    np.array([0.010, 0.000, 0.000]),
                    np.array([0.020, 0.000, 0.000]),
                    np.array([0.030, 0.000, 0.000]),
                    np.array([0.040, 0.000, 0.000]),
                    np.array([0.050, 0.000, 0.000]),
                    np.array([0.060, 0.000, 0.000]),
                    np.array([0.070, 0.000, 0.000]),
                    np.array([0.080, 0.000, 0.000]),
                    np.array([0.090, 0.000, 0.000]),
                    np.array([0.100, 0.000, 0.000]),
                    np.array([0.110, 0.000, 0.000]),
                    np.array([0.120, 0.000, 0.000]),
                    np.array([0.130, 0.000, 0.000]),
                    np.array([0.140, 0.000, 0.000]),
                    np.array([0.150, 0.000, 0.000]),
                    np.array([0.160, 0.000, 0.000]),
                    np.array([0.170, 0.000, 0.000]),
                    np.array([0.180, 0.000, 0.000]),
                    np.array([0.190, 0.000, 0.000]),
                    np.array([0.200, 0.000, 0.000]),
                    np.array([0.210, 0.000, 0.000]),
                    np.array([0.220, 0.000, 0.000]),
                    np.array([0.230, 0.000, 0.000]),
                    np.array([0.240, 0.000, 0.000]),
                    np.array([0.250, 0.000, 0.000]),
                ]}}}

    scaled = map_fibers(
        lambda fiber_points, box_extent: fiber_points * 1000,
        fiber)

    return scaled

if __name__ == '__main__':
    fiber = single_fiber()
    import ipdb; ipdb.set_trace()

from vivarium.core.composer import Composer
from vivarium.core.engine import Engine
from vivarium.processes.alternator import PeriodicEvent

from vivarium_cytosim import CytosimProcess
from vivarium_models.data.fibers import single_fiber

READDY_TIMESTEP = 0.0000001
ALTERNATOR_PERIODS = [2.0, READDY_TIMESTEP]


class BucklingSqueeze(Composer):
    defaults = {
        "periodic_event": {
            "periods": [1.0]},
        "cytosim_squeeze": {
            'model_name': 'buckling_squeeze'}
    }

    def __init__(self, config=None):
        super().__init__(config)

    def generate_processes(self, config):
        periodic_event = PeriodicEvent(config["periodic_event"])
        cytosim_squeeze = CytosimProcess(config['cytosim_squeeze'])

        return {
            "periodic_event": periodic_event,
            'cytosim_squeeze': cytosim_squeeze,
        }

    def generate_topology(self, config):
        return {
            "periodic_event": {
                "event_trigger": ("alternate_trigger",),
                "period_index": ("period_index",),
            },
            "cytosim_squeeze": {
                "fibers": ("fibers",),
                "fibers_box_extent": ("fibers_box_extent",),
            },
        }


def test_buckling_squeeze():
    initial_state = single_fiber()
    # initial_state['choices'] = 'N/A'
    cytosim_config = {
        'actin_segmentation': 0.01,
        "template_directory": "vivarium_models/templates/"}
    buckling_squeeze_config = {
        "cytosim_squeeze": cytosim_config}
    buckling_squeeze = BucklingSqueeze(buckling_squeeze_config)
    composite = buckling_squeeze.generate()
    composite["initial_state"] = initial_state
    engine = Engine(
        processes=composite["processes"],
        topology=composite["topology"],
        initial_state=composite["initial_state"],
        # emitter="simularium",
        emit_processes=True,
    )
    engine.update(5)

    output = engine.emitter.get_data()
    import ipdb; ipdb.set_trace()



if __name__ == "__main__":
    test_buckling_squeeze()

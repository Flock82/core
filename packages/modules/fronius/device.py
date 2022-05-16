#!/usr/bin/env python3
from typing import Dict, Optional, Union, List

from helpermodules import log
from helpermodules.cli import run_using_positional_cli_args
from modules.common.store import get_inverter_value_store
from modules.common.abstract_device import AbstractDevice
from modules.common.component_context import MultiComponentUpdateContext, SingleComponentUpdateContext
from modules.fronius import bat
from modules.fronius import counter_s0
from modules.fronius import counter_sm
from modules.fronius import inverter


def get_default_config() -> dict:
    return {
        "name": "Fronius",
        "type": "fronius",
        "id": 0,
        "configuration": {
            "ip_address": None
        }
    }


fronius_component_classes = Union[bat.FroniusBat, counter_sm.FroniusSmCounter,
                                  counter_s0.FroniusS0Counter, inverter.FroniusInverter]


class Device(AbstractDevice):
    COMPONENT_TYPE_TO_CLASS = {
        "bat": bat.FroniusBat,
        "counter_sm": counter_sm.FroniusSmCounter,
        "counter_s0": counter_s0.FroniusS0Counter,
        "inverter": inverter.FroniusInverter,
    }

    def __init__(self, device_config: dict) -> None:
        self._components = {}  # type: Dict[str, fronius_component_classes]
        try:
            self.device_config = device_config
        except Exception:
            log.MainLogger().exception("Fehler im Modul "+device_config["name"])

    def add_component(self, component_config: dict) -> None:
        component_type = component_config["type"]
        if component_type in self.COMPONENT_TYPE_TO_CLASS:
            self._components["component"+str(component_config["id"])] = self.COMPONENT_TYPE_TO_CLASS[component_type](
                self.device_config["id"], component_config, self.device_config["configuration"])
        else:
            raise Exception(
                "illegal component type " + component_type + ". Allowed values: " +
                ','.join(self.COMPONENT_TYPE_TO_CLASS.keys())
            )

    def update(self) -> None:
        log.MainLogger().debug("Start device reading " + str(self._components))
        if self._components:
            with MultiComponentUpdateContext(self._components):
                for component in self._components:
                    self._components[component].update()
        else:
            log.MainLogger().warning(
                self.device_config["name"] +
                ": Es konnten keine Werte gelesen werden, da noch keine Komponenten konfiguriert wurden."
            )


def read_legacy(
        component_type: str,
        ip_address: str,
        meter_id: int,
        variant: int,
        ip_address2: str = "none",
        num: Optional[int] = None) -> None:
    COMPONENT_TYPE_TO_MODULE = {
        "bat": bat,
        "counter_sm": counter_sm,
        "counter_s0": counter_s0,
        "inverter": inverter,
    }

    device_config = get_default_config()
    device_config["configuration"]["ip_address"] = ip_address
    dev = Device(device_config)
    if component_type in COMPONENT_TYPE_TO_MODULE:
        component_config = COMPONENT_TYPE_TO_MODULE[component_type].get_default_config()
        if component_type == "bat":
            component_config["configuration"]["meter_id"] = meter_id
        elif component_type == "counter_sm":
            component_config["configuration"]["variant"] = variant
            component_config["configuration"]["meter_id"] = meter_id
    else:
        raise Exception(
            "illegal component type " + component_type + ". Allowed values: " +
            ','.join(COMPONENT_TYPE_TO_MODULE.keys())
        )
    component_config["id"] = num
    dev.add_component(component_config)

    log.MainLogger().debug('Fronius IP-Adresse: ' + str(ip_address))

    if component_type == "bat" and component_type == "counter":
        dev.update()
    elif component_type == "inverter" and num:
        inverter1 = inverter.FroniusInverter(num, component_config, device_config)
        if ip_address2 != "none":
            device_config["configuration"]["ip_address"] = ip_address2
            inverter2 = inverter.FroniusInverter(num, component_config, device_config)
        with SingleComponentUpdateContext(inverter1.component_info):
            total_power = inverter1.read_power()
            if ip_address2 != "none":
                total_power += inverter2.read_power()
            get_inverter_value_store(num).set(inverter1.fill_inverter_state(total_power))
    else:
        raise Exception("illegal component num " + str(num) + ". Should be an int if it is an inverter.")


def main(argv: List[str]) -> None:
    run_using_positional_cli_args(read_legacy, argv)

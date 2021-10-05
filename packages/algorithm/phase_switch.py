""" Modul, das die Phasenumschaltung durchführt.
"""
import threading
import time
import RPi.GPIO as GPIO

from ..helpermodules import log
from ..helpermodules import pub
from ..modules.cp import ip_evse

phase_switch_threads = {}


def thread_phase_switch(cp_num, selected, config, phases_to_use, duration, charge_state):
    """ startet einen Thread pro Ladepunkt, an dem eine Phasenumschaltung durchgeführt werden soll. Die Phasenumschaltung erfolgt in Threads, da diese länger als ein Zyklus dauert.

    Parameter
    ---------
    cp_num: int
        Ladepunkt-Nummer
    selected: str
        Anbindungsmodul
    config: dict
        Konfiguration des Anbindungsmoduls
    phases_to_use: int
        Anzahl Phasen, die nach der Umschaltung verwendet werden sollen
    duration: int
        Pause vor und nach der Umschaltung
    charge_state: int
        Ladung aktiv/inaktiv
    """
    try:
        global phase_switch_threads
        # fertige Threads aus der Liste löschen:
        phase_switch_threads = {t: phase_switch_threads[t] for t in phase_switch_threads if phase_switch_threads[t].is_alive()}

        # prüfen, ob Thread in der Liste ist. Dann ist noch eine Phasenumschaltung aktiv und es darf keine neue gestartet werden.
        if "thread_cp"+str(cp_num) not in phase_switch_threads:
            # Thread zur Phasenumschaltung erstellen, starten und der Liste hinzufügen.
            phase_switch_threads["thread_cp"+str(cp_num)] = threading.Thread(target=_perform_phase_switch, args=(selected, config, phases_to_use, duration, charge_state))
            phase_switch_threads["thread_cp"+str(cp_num)].start()
            log.message_debug_log("debug", "Thread zur Phasenumschaltung an LP"+str(cp_num)+" gestartet.")
    except Exception as e:
        log.exception_logging(e)


def _perform_phase_switch(selected, config, phases_to_use, duration, charge_state):
    """ ruft das Modul zur Phasenumschaltung für das jeweilige Modul auf.
    """
    # Stoppen der Ladung wird in start_charging bei gesetztem phase_switch_timestamp durchgeführt.
    # Wenn gerade geladen wird, muss vor der Umschaltung eine Pause von 5s gemacht werden.
    try:
        if charge_state == True:
            time.sleep(5)
        # Phasenumschaltung entsprechend Modul
        if selected == "external_openwb":
            num = config["chargepoint"]
            ip_address = config["ip_address"]
            pub.pub_single("openWB/set/isss/U1p3p", phases_to_use, ip_address)
            time.sleep(6+duration-1)
        elif selected == "ip_evse":
            ip_address = config["ip_address"]
            id = config["id"]
            ip_evse.perform_phase_switch(ip_address, id, duration, phases_to_use)
        elif selected == "modbus_evse":
            num = config["chargepoint"]
            _phase_switch_internal(num, duration, phases_to_use)
        # Kurze Pause, bevor mit der Ladung gestartet wird.
        # Die Ladung wird in start_charging wieder gestartet, wenn phase_switch_timestamp wieder auf "0" gesetzt wird.
        if charge_state == True:
            time.sleep(1)
    except Exception as e:
        log.exception_logging(e)


def _phase_switch_internal(duo_num, duration, phases_to_use):
    """ Phasenumschaltung im Master
    """
    try:
        if phases_to_use == 1:
            # setup GPIOs
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            if duo_num == 1:
                GPIO.setup(22, GPIO.OUT)
                GPIO.setup(29, GPIO.OUT)
            else:
                GPIO.setup(15, GPIO.OUT)
                GPIO.setup(11, GPIO.OUT)
            # block CP
            if duo_num == 1:
                GPIO.output(22, GPIO.HIGH)
            else:
                GPIO.output(15, GPIO.HIGH)
            time.sleep(duration)
            # switch phases
            if duo_num == 1:
                GPIO.output(29, GPIO.HIGH)
            else:
                GPIO.output(11, GPIO.HIGH)
            time.sleep(2)
            if duo_num == 1:
                GPIO.output(29, GPIO.LOW)
            else:
                GPIO.output(11, GPIO.LOW)
            time.sleep(duration)
            # enable CP
            if duo_num == 1:
                GPIO.output(22, GPIO.LOW)
            else:
                GPIO.output(15, GPIO.LOW)

        else:
            # setup GPIOs
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            if duo_num == 1:
                GPIO.setup(22, GPIO.OUT)
                GPIO.setup(37, GPIO.OUT)
            else:
                GPIO.setup(15, GPIO.OUT)
                GPIO.setup(13, GPIO.OUT)
            # block CP
            if duo_num == 1:
                GPIO.output(22, GPIO.HIGH)
            else:
                GPIO.output(15, GPIO.HIGH)
            time.sleep(duration)
            # switch phases
            if duo_num == 1:
                GPIO.output(37, GPIO.HIGH)
            else:
                GPIO.output(13, GPIO.HIGH)
            time.sleep(2)
            if duo_num == 1:
                GPIO.output(37, GPIO.LOW)
            else:
                GPIO.output(13, GPIO.LOW)
            time.sleep(duration)
            # enable CP
            if duo_num == 1:
                GPIO.output(22, GPIO.LOW)
            else:
                GPIO.output(15, GPIO.LOW)
    except Exception as e:
        log.exception_logging(e)
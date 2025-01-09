# l: aankomstsnelheid                   arrival_speed
# m: verwerkingssnelheid                processing_speed
# T: totale tijd                        total_time
# W: wachttijd in de wachtrij           wait_time
# S: servicetijd                        service_time
# N: aantal personen in het systeem     total_person
# g: bezettingsgraad                    occupancy_rate

# l: input = N/T
# m: input
# T: N/l = 1/(m-l)
# W: T-S
# S: 1/m
# N: g/(1-g) = l/(m-l) = l*T
# g: l/m

# FIFO: First In First Out (queue)
# LIFO: Last In First Out (stack)
# Priority: Gesorteerdop prioriteit
# Processor Sharing: om de beurtrekentijd
# SIRO: Service In Random Order

# l < m: Stabiele wachtrij. Kan wellang worden want statistische processen. Soms komt niemand, soms een bulk
# l > m: Instabiele wachtrij. Loopt uit de hand


def calculate_l(total_person:int, total_time:int) -> int:
    arrival_speed:int = total_person / total_time
    return arrival_speed

def calculate_T(total_person:int, arrival_speed:int) -> int:
    total_time:int = total_person / arrival_speed
    return total_time

def calculate_T_diff(arrival_speed:int, processing_speed:int) -> int:
    total_time:int = 1/(processing_speed-arrival_speed)
    return total_time

def calculate_W(total_time:int, service_time:int) -> int:
    wait_time:int = total_time - service_time
    return wait_time

def calculate_S(processing_speed:int) -> int:
    service_time:int = 1 / processing_speed

    return service_time
def calculate_N(occupancy_rate:int) -> int:
    total_person:int = occupancy_rate / (1 - occupancy_rate)
    return total_person

def calculate_g(arrival_speed:int, processing_speed:int) -> int:
    occupancy_rate:int = arrival_speed / processing_speed
    return occupancy_rate


def calculate_Total(arrival_speed:int, processing_speed:int) -> int:
    wait_time:int = calculate_W(calculate_T(calculate_N(calculate_g(arrival_speed, processing_speed)), arrival_speed), calculate_S(processing_speed))
    return wait_time


def calculate_diff(arrival_speed:int, processing_speed:int) -> int:
    wait_time:int = calculate_W((calculate_T_diff(arrival_speed, processing_speed)), calculate_S(processing_speed))
    return wait_time
    
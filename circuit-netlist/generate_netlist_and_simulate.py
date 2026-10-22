import os
import matplotlib.pyplot as plt

# Import the skidl library.
create_pcb=True
if create_pcb:
    os.environ['KICAD_SYMBOL_DIR'] = os.path.join(os.path.dirname(__file__), '/usr/share/kicad/symbols')
    os.environ['KICAD_FOOTPRINT_DIR'] = os.path.join(os.path.dirname(__file__), '/usr/share/kicad/footprints')
    os.environ['KICAD6_SYMBOL_DIR'] = os.path.join(os.path.dirname(__file__), '/usr/share/kicad/symbols')
    os.environ['KICAD6_FOOTPRINT_DIR'] = os.path.join(os.path.dirname(__file__), '/usr/share/kicad/footprints')
    os.environ['KICAD7_SYMBOL_DIR'] = os.path.join(os.path.dirname(__file__), '/usr/share/kicad/symbols')
    os.environ['KICAD7_FOOTPRINT_DIR'] = os.path.join(os.path.dirname(__file__), '/usr/share/kicad/footprints')
    from skidl import *
    from skidl import KICAD7
from skidl.pyspice import *

set_default_tool(KICAD7)

vdc_in = Part("Device", "Battery", ref = 'vdc', value=5 @ u_V, footprint="Battery:BatteryHolder_Bulgin_BX0036_1xC")
r1 = Part("Device", "R", value=1 @ u_kOhm, footprint="Resistor_SMD:R_0603_1608Metric")
r2 = Part("Device", "R", value=2 @ u_kOhm, footprint="Resistor_SMD:R_0603_1608Metric")

vin_net, vout_net, gnd_net = Net("Vin"), Net("Vout"), Net("GND")

gnd_net & vdc_in["2 1"] & vin_net & r1 & vout_net & r2 & gnd_net

# Output the netlist to a file.
generate_netlist()
# generate_schematic()
generate_pcb()


vdc_in.convert_for_spice(V, {1: "p", 2: "n"})
r1.convert_for_spice(R, {1: "p", 2: "n"})
r2.convert_for_spice(R, {1: "p", 2: "n"})

set_default_tool(SPICE)
circ = generate_netlist()
print(circ)
sim = circ.simulator(temperature=25, nominal_temperature=25)
analysis = sim.dc(Vvdc=slice(0, 5, 0.5))  # DC sweep analysis. Note that Vvdc is the reference to the voltage source and a V is added to the name of the source.
# analysis = sim.operating_point()        # Operating point analysis.



dc_vin = analysis[node(vdc_in["p"])]  # or dc_vin = analysis.Vin
dc_vout = analysis[node(r2["p"])]     # or dc_vout = analysis.Vout
dc_ir1 = -analysis['Vvdc']

# generate the drc rules for the pcb. sample is shown below
'''
(version 1)

(rule "LoW cLeArAnce BeTWeen neTS of THe SAme HV potential"
	(constraint clearance (min 0.2mm))
	(condition " A.NetClass == B.NetClass && A.NetClass == 'HV*' " ))
'''
# make a file called the name of this file and ,kicad_dru and add the syntax above for dc_in net and dc_out net names
drc_rules_template = '''
(version 1)
'''
drc_rules = drc_rules_template

def find_rules(voltage, current):
    # this is a simple lookup table to determine the clearance and width based on the voltage. this can be expanded to include more complex rules
    if max(voltage.as_ndarray()) > 100:
        min_clearance = 0.5
        min_width = 3
    else:
        min_clearance = 0.3
        min_width = 2
    return min_clearance, min_width
    
vin_min_clearance, vin_min_width = find_rules(dc_vin, dc_ir1)
drc_rules += f'''
(rule "VIN clearance"
    (constraint clearance (min {vin_min_clearance}mm))
    (constraint track_width (min {vin_min_width}mm))
    (condition "A.NetName == '{vin_net.name}' " ))
'''
vout_min_clearance, vout_min_width = find_rules(dc_vout, dc_ir1)
drc_rules += f'''
(rule "VOUT clearance"
    (constraint clearance (min {vout_min_clearance}mm))
    (constraint track_width (min {vout_min_width}mm))
    (condition "A.NetName == '{vout_net.name}' " ))
'''

file_name = os.path.splitext(os.path.basename(__file__))[0]
drc_file_name = file_name + ".kicad_dru"
with open(drc_file_name, "w") as drc_file:
    drc_file.write(drc_rules)



print("{:^7s}{:^7s}".format("Vin (V)", " Vout (V)"))
print("=" * 15)
for v, i in zip(dc_vin.as_ndarray(), dc_vout.as_ndarray()):
    print("{:6.2f} {:6.2f}".format(v, i))

# Create a plot of the current (Y coord) versus the applied voltage (X coord).
# plot if length of dc_vin and dc_ir1 > 1 (i.e., not a single point).
if len(dc_vin) > 1:
    figure = plt.figure(1)
    plt.title('Resistor Current vs. Applied Voltage')
    plt.xlabel('Voltage (V)')
    plt.ylabel('Current (mA)')
    plt.plot(dc_vin, dc_ir1*1000) # Plot X=voltage and Y=current (in milliamps, so multiply it by 1000).
    plt.show()
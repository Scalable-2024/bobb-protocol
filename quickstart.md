# Bobb Protocol

This protocol and flask application were created for an assignment for Scalable Computing, CS7NS1, to simulate and design a P2P LEO (Low Earth Orbit) satellite network.

## How to Run

This code is designed to run distributed over a number of devices, which simulate the intended behaviour of satellites. Testing locally is supported, but is discussed more below.

When running on the standard Raspberry Pi in the provided SCSS network, just run the following:

```sh
sh multi-device.sh <COUNT> <DEVICE_FUNCTION> <RESET_RESOURCES> [START_PORT]
```
1. **COUNT:** Number of simulated devices to start up.
2. **DEVICE_FUNCTION:** The function of this device - eg basestation or any of the valid satellite functions (disaster-imaging, whale-tracking, windfarm-monitoring, post-flood-survivor-detection-aerialdrones)
3. **RESET_RESOURCES:** If running the code for the first time this iteration, set to true. Otherwise (generally), set to false.
4. **START_PORT:** Port to start running simulated devices on - when running on raspberry pis, must be in range 33000 to 34000.

If setting up a full network, start up at least one basestation and and least one satellite.

### Testing on Localhost

If testing locally and your IP address does not start with 10, run the code as normal, and simulated devices will communicate cross ports. Otherwise, modify the definition of `find_x_satellites` in `src/discovery/discovery.py` to set the default value of `ìps_to_check` to `["localhost"]`.

## Group 1 Specific

```sh
python3 -m src.whale.simulate --min_diving_time=5 --max_diving_time=10 --min_surface_time=2 --max_surface_time=5 --destination_ip="172.32.116.126" --destination_port=33002
```
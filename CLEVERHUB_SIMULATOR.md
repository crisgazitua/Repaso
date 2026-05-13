# CleverHub Simulator

Docker image: `secheverriag/cleverhub-sim:p1a`

This Python script simulates a smart home environment ("CleverHub") that interacts with a central platform using a custom TCP-based protocol. It models various house states like doors, lights, proximity sensors, alarm systems, and temperature control. The simulator also includes threads for user interaction and time-based house state updates.

-----

## Features

  * **House State Simulation:** Models the state of doors, lights, proximity sensors, alarm, heater, chiller, and temperature.
  * **User Interaction:** Allows manual toggling of door, light, and proximity sensor states through a command-line interface.
  * **Time-based Updates:** Simulates the passage of time, which can influence house parameters like temperature (heater/chiller).
  * **CleverHub Protocol Implementation:** Connects to a specified server, sends "hello" messages, and handles "get state" (GS) and "set state" (SS) requests.
  * **Random Error Simulation:** Optionally introduces random errors when setting the house state to simulate network or device failures.
  * **Automatic Reconnection:** Attempts to reconnect to the central platform if the connection is lost.

---

## Running

To run the CleverHub Simulator, you need to provide the server's IP address, port, a username, a password, and a home name as command-line arguments.

```bash
docker run --rm -it secheverriag/cleverhub-sim:p1a <platform_ip> <platform_port> <username> <password> <home_name>
```

### Arguments

| Argument | Description |
|----------|-------------|
| `platform_ip` | IP where your platform is listening. |
| `platform_port` | TCP port your platform is listening on. |
| `username` | Name credential the hub sends when connecting to your platform. |
| `password` | Password credential the hub sends when connecting to your platform. |
| `home_name` | Unique identifier/name the hub uses to identify itself. |

### Example

```bash
docker run --rm -it secheverriag/cleverhub-sim:p1a localhost 8888 myuser mypass MySweetHome
```

### Docker flags used above

| Flag | Meaning |
|------|---------|
| `--rm` | Delete the container when it stops. |
| `-i` | Keep stdin open so the container can read your keyboard input. |
| `-t` | Allocate a pseudo-TTY so the simulator's shell works interactively. |


### Environment Variables

Some parts of the simulator can be configured through environment variables. More specifically:

| Variable | Description |
|----------|-------------|
| `NUM_DOORS` | Number of doors (default: 3) |
| `NUM_LIGHTS` | Number of lights (default: 5) |
| `NUM_PROXIMITY` | Number of proximity sensors (default: 2) |
| `RANDOM_ERROR` | If set to any value, the simulator randomly rejects some set-state requests. |

**Example:**

```bash
docker run --rm -it -e NUM_LIGHTS=10 -e RANDOM_ERROR=1 secheverriag/cleverhub-sim:p1a localhost 8888 myuser mypass MySweetHome
```

Alternatively, you can use an ```.env``` file to store your environment variables more easily.


```bash
docker run --rm -it --env-file .env secheverriag/cleverhub-sim:p1a localhost 8888 myuser mypass MySweetHome
```

---

## Interactive Commands

Once the simulator is running and connected, you'll see the current state of the house printed periodically. You can also interact with the house state by entering commands in the terminal:

| Command | Action |
|---------|--------|
| `d` | Toggle a door state (prompts for door number) |
| `l` | Toggle a light state (prompts for light number) |
| `p` | Toggle a proximity sensor state (prompts for sensor number) |
| `Enter` | Print the current state immediately |

These commands simulate physical changes in the house so you can verify your platform reads updated states correctly.

**Example Interaction:**

```
Current state: DS0=1;DS1=1;DS2=1;LS0=1;LS1=1;LS2=1;LS3=1;LS4=1;PS0=1;PS1=1;TR=65;AS=0;AO=0;HS=1;CS=0

Enter a command: d=[toggle door], l=[toggle light], p=[toggle proximity], RET=[show current status]: d
Enter the door number: 0
door is now 0

Current state: DS0=0;DS1=1;DS2=1;LS0=1;LS1=1;LS2=1;LS3=1;LS4=1;PS0=1;PS1=1;TR=66;AS=0;AO=0;HS=1;CS=0

Enter a command: d=[toggle door], l=[toggle light], p=[toggle proximity], RET=[show current status]:
```

---

## Time Simulation

Every 5 seconds the simulator updates the house temperature:

- If heater is on, temperature increases by 1.
- If chiller is on, temperature decreases by 1.

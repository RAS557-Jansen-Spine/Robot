import argparse
import csv
import sys
import time
from collections import deque

import matplotlib.pyplot as plt

# Try importing serial, but don't fail yet (might be in file replay mode)
try:
    import serial
except ImportError:
    serial = None


def main():
    parser = argparse.ArgumentParser(
        description="Live-plot IMU data from Serial or CSV."
    )
    parser.add_argument(
        "--port", help="Serial port for live plotting (e.g. /dev/ttyUSB0)"
    )
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate")
    parser.add_argument("--file", help="CSV file for replay (e.g. imu_data.csv)")
    parser.add_argument("--window", type=float, default=20.0, help="Time window (s)")
    args = parser.parse_args()

    if not args.port and not args.file:
        parser.print_help()
        sys.exit(1)

    # Setup Plot Dashboard
    tbuf, hbuf, rbuf, pbuf = deque(), deque(), deque(), deque()
    xbuf, ybuf, zbuf = deque(), deque(), deque()

    plt.ion()
    # 2x2 Layout: Top=Orientation, BottomL=Trajectory, BottomR=Height
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 2)

    # 1. Orientation (Top span)
    ax_orient = fig.add_subplot(gs[0, :])
    (lh,) = ax_orient.plot([], [], label="Heading", color="blue")
    (lr,) = ax_orient.plot([], [], label="Roll", color="orange")
    (lp,) = ax_orient.plot([], [], label="Pitch", color="green")
    ax_orient.set_ylabel("Angle (deg)")
    ax_orient.set_title("Robot Orientation")
    ax_orient.legend(loc="upper right")
    ax_orient.grid(True)

    # 2. Trajectory (Bottom Left)
    ax_traj = fig.add_subplot(gs[1, 0])
    (lt,) = ax_traj.plot([], [], label="Path", color="purple")
    ax_traj.set_xlabel("X (m)")
    ax_traj.set_ylabel("Y (m)")
    ax_traj.set_title("Top-Down Trajectory")
    ax_traj.axis("equal")
    ax_traj.grid(True)

    # 3. Height (Bottom Right)
    ax_height = fig.add_subplot(gs[1, 1])
    (lz,) = ax_height.plot([], [], label="Z (Height)", color="red")
    ax_height.set_xlabel("Time (s)")
    ax_height.set_ylabel("Z (m)")
    ax_height.set_title("Vertical Motion")
    ax_height.grid(True)

    # Source Setup
    ser = None
    csv_iter = None
    start_time_ref = time.time()  # Real-world start time

    if args.port:
        if not serial:
            print("Error: pyserial not installed. Run 'pip install pyserial'")
            sys.exit(1)
        try:
            ser = serial.Serial(args.port, args.baud, timeout=0.1)
            print(f"Connected to {args.port} at {args.baud} baud.")
        except Exception as e:
            print(f"Error opening serial: {e}")
            sys.exit(1)

    elif args.file:
        print(f"Replaying from {args.file}...")
        try:
            f = open(args.file, "r")
            reader = csv.reader(f)
            # Skip header if present
            header = next(reader, None)
            if header and not header[0].replace(".", "", 1).isdigit():
                # It's a text header
                print(f"Skipped header: {header}")
            else:
                # It was data, put it back (trickier with iterator, so assumes header exists usually)
                pass
            csv_iter = reader
        except Exception as e:
            print(f"Error opening file: {e}")
            sys.exit(1)

    print("Plotting... Press Ctrl+C to stop.")

    try:
        while True:
            # 1. Fetch Data
            # Format: t, h, r, p, [x, y, z]
            data_row = None

            if ser:
                # LIVE MODE
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line and not line.startswith("#"):
                    parts = line.split(",")
                    if len(parts) >= 4:
                        try:
                            # Basic 4 columns
                            t_ms = int(parts[0])
                            h = float(parts[1])
                            r = float(parts[2])
                            p = float(parts[3])

                            # Optional Position cols
                            x, y, z = 0.0, 0.0, 0.0
                            if len(parts) >= 7:
                                x = float(parts[4])
                                y = float(parts[5])
                                z = float(parts[6])

                            data_row = (t_ms / 1000.0, h, r, p, x, y, z)
                        except ValueError:
                            pass

            elif csv_iter:
                # REPLAY MODE
                try:
                    row = next(csv_iter)
                    # Expected: time_ms, heading, roll, pitch, x, y, z
                    t_ms = float(row[0])
                    # Wait until real time catches up to recorded time
                    target_time = start_time_ref + (t_ms / 1000.0)
                    now = time.time()
                    if target_time > now:
                        time.sleep(target_time - now)

                    h = float(row[1])
                    r = float(row[2])
                    p = float(row[3])

                    x, y, z = 0.0, 0.0, 0.0
                    if len(row) >= 7:
                        x = float(row[4])
                        y = float(row[5])
                        z = float(row[6])

                    data_row = (t_ms / 1000.0, h, r, p, x, y, z)
                except StopIteration:
                    print("End of file.")
                    break
                except ValueError:
                    pass

            # 2. Update Plot
            if data_row:
                t, h, r, p, x, y, z = data_row

                # Append
                tbuf.append(t)
                hbuf.append(h)
                rbuf.append(r)
                pbuf.append(p)
                xbuf.append(x)
                ybuf.append(y)
                zbuf.append(z)

                # Prune history (Time window for time-series plots)
                while tbuf and tbuf[0] < t - args.window:
                    tbuf.popleft()
                    hbuf.popleft()
                    rbuf.popleft()
                    pbuf.popleft()
                    # We usually prune x/y/z too to keep arrays aligned for idx reference
                    xbuf.popleft()
                    ybuf.popleft()
                    zbuf.popleft()

                if len(tbuf) > 1:
                    # Generic list cast for matplotlib
                    ts = list(tbuf)

                    # Updates
                    lh.set_data(ts, list(hbuf))
                    lr.set_data(ts, list(rbuf))
                    lp.set_data(ts, list(pbuf))

                    lt.set_data(list(xbuf), list(ybuf))  # X vs Y
                    lz.set_data(ts, list(zbuf))  # Z vs Time

                    # Rescale
                    for ax in [ax_orient, ax_traj, ax_height]:
                        ax.relim()
                        ax.autoscale_view()

                plt.pause(0.001)
            else:
                plt.pause(0.01)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if ser:
            ser.close()
        if args.file:
            f.close()


if __name__ == "__main__":
    main()

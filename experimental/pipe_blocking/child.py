"""A subprocess to simulate progress bar from an fpga programmer."""
import time


for i in range(500):
    print(f"\r  {i:06d}", end="", flush=True)
    time.sleep(0.05)

print("\nAll done.")

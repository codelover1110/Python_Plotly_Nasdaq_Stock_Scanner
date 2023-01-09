import subprocess

process1 = subprocess.Popen(["python", "harvesting_ib/orderbook_ibapi.py"]) # pulling orderbook
process2 = subprocess.Popen(["python", "harvesting_ib/candles.py"]) # pulling candles
process3 = subprocess.Popen(["python", "plotly_ib_insync.py"]) # running plotly_ib_insync

process1.wait() # Wait for process1 to finish (basically wait for script to finish)
process2.wait()
process3.wait()
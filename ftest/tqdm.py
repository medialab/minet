import sys
import time
from minet.cli.utils import LoadingBar
from tqdm import tqdm

N = 1_000

bar = LoadingBar(desc="Range", total=1_000)

# for i in range(N):
#     bar.print('one')
#     bar.update()
#     time.sleep(1)
#     bar.die('dommage')

try:
    for i in range(N):
        bar.update()
        time.sleep(1)
except KeyboardInterrupt:
    for ref in list(tqdm._instances):
        ref.leave = False
        ref.close()
    sys.exit(0)

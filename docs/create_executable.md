# How to create a Minet executable file

Install PyInstaller from PyPI:
```bash
pip install pyinstaller
```

> Be sure to have all Minet's dependencies installed on your computer (in your virtual environment if you're using one). Run this command in `minet` root folder:
> ```bash
> pip install -r requirements.txt
> ```

Go to `minet` root folder, take a deep breathe and run:
```bash
pyinstaller minet/cli/__main__.py --hidden-import sklearn.neighbors.typedefs --hidden-import sklearn.neighbors.quad_tree --hidden-import sklearn.tree._utils --hidden-import scipy.ndimage --onefile
```
It will generate the executable in the `dist` folder.

## Troubleshooting

- If you encounter a problem with **Python library path**, like `TypeError: expected str, bytes or os.PathLike object, not NoneType`, add your Python path to the environment variable LD_LIBRARY_PATH before running pyinstaller. 
  
  Example if you're using *pyenv*:
  `export LD_LIBRARY_PATH=/home/YOUR_NAME/.pyenv/versions/3.7.0/lib/://home/YOUR_NAME/.pyenv/versions/3.7.0/envs/minet/lib/`
  (*pyenv* stores Python and the dependancies in two differents locations)


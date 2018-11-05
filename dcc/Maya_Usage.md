# How to use a ChromeGuiApp in Maya

## Example Usage

Launch Maya and open its Script Editor window. Using a Python command tab, enter the following and lines execute.

```python
import sys
import os

# statements below used to provide access to jinja2 package in Maya
sys.path.append(r'C:\Python27\Lib\site-packages')
os.environ['PYTHONPATH'] = os.path.pathsep.join( [os.getenv('PYTHONPATH'), r'C:\Python27\Lib\site-packages'] )

os.environ['PXLC_CHROMEGUI_ROOT'] = 'C:/Users/mike_/Dropbox/code/pxlc_github/ChromeGuiApp'
CHROMEGUI_ROOT = os.getenv('PXLC_CHROMEGUI_ROOT')

sys.path.append('%s/dcc' % CHROMEGUI_ROOT)

from maya_chromegui import launch_pychrome_maya_gui

launch_pychrome_maya_gui('%s/examples/maya_test/maya_test_app.py' % CHROMEGUI_ROOT)
```

Of course, you will need to write your app module and your HTML template file to run this with.

For the above example, create new objects in your Maya scene and select a few of them in whatever order, then click on the button on the Chrome GUI and look at the output that shows up in the DEBUG console window.

<br/>

**[end]**

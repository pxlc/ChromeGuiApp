# How to use a ChromeGuiApp in Maya

## Example Usage

Launch Maya and open its Script Editor window. Using a Python command tab, enter the following and lines execute.

```python
import sys
sys.path.append('C:/Users/pxlc/dev/ChromeGuiApp/dcc')

from maya_chromegui import launch_pychrome_maya_gui

launch_pychrome_maya_gui(
	'C:/Users/pxlc/dev/ChromeGuiApp/examples/maya_test/maya_test_app.py',
    'TEMPLATE_maya_test.html')
```

Of course, you will need to write your app module and your HTML template file to run this with.

For the above example, create new objects in your Maya scene and select a few of them in whatever order, then click on the button on the Chrome GUI and look at the output that shows up in the DEBUG console window.

<br/>

**[end]**

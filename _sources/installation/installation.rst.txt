.. _installation-label:

Installation
============

Download the most recent official release at `Github
<https://github.com/cgtinker/blendarmocap/releases>`_.
Don't unzip the downloaded zip.

To install the add-on, navigate to ``Edit > Preferences > Add-Ons``.
Then seach for *BlendArMocap* using the search bar.
Finally activate the add-on by pressing the checkbox.

.. warning::
   Running *Googles Mediapipe* within Blender requires external dependencies.
   Preferably install them via the add-ons preferences with elevated privileges.


Starting Blender with elevated permissions
------------------------------------------

Installing dependencies may requires elevated privileges.

Windows
    Right-click the blender application and choose: "Run as administrator"

Mac
    #. Start Blender as admin by using the terminal:
    #. Navigate to Blender: ``cd /Applications/Blender/Contents/MacOS``
    #. Run Blender as admin: ``sudo ./Blender``

    The Terminal request may be blocked even with
    elevated privileges, if that happens navigate to
    ``System Settings > Privacy and Security > Full Disk Access``
    then activate your Terminal.
    After doing so, the sudo tag shouldn't be required anymore.

Linux
    #. Start Blender as admin using the terminal:
    #. Navigate to Blender: ``cd /usr/bin``
    #. Run Blender as admin: ``sudo ./blender``


Install External Dependencies
-----------------------------

To run mediapipe, you need to install the required dependencies
opencv and mediapipe via the **add-ons preferences**.
Internet connection is required to install the required packages.
It's recommended to disable VPN's during the
installation processes. Blender may to started with elevated
privileges during the installation process.

Default
    Install dependencies within Blenders site-packages.

Local (Linux)
    Install dependencies to the local user and link local user site
    packages to blender.



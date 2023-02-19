Manual Installation
===================

In some cases, mainly due to any system related issues,
it may be required to install dependencies manually.

.. note::
    Before attempting to install dependencies manually, ensure
    that you've had the required permissions when trying to install
    the dependencies to run mediapipe.

Gather information
------------------

Fire up blender, navigate to the ``Scripting`` workspace and
gather some information in the ``interactive python console``.

1. Find blenders python executable

.. code-block:: python

    import sys
    sys.executable()

2. Find blenders site-packages

.. code-block:: python

    import site
    site.getusersitepackages()

Install via system console
--------------------------

Next up, start the terminal or powershell on windows to install
the dependencies manually.

Windows
    .. code-block:: bash

        `blenders python executable` -m ensurepip
        `blenders python executable` -m pip install mediapipe
        `blenders python executable` -m pip install opencv-contrib-python==4.7.0.68
        `blenders python executable` -m pip install protobuf==3.20.3

Apple-Silicone
    .. code-block:: bash

        `blenders python executable` -m ensurepip
        `blenders python executable` -m pip install mediapipe-silicon
        `blenders python executable` -m pip install opencv-contrib-python==4.7.0.68

Apple-Legacy
    .. code-block:: bash

        `blenders python executable` -m ensurepip
        `blenders python executable` -m pip install mediapipe==0.8.10
        `blenders python executable` -m pip install opencv-contrib-python==4.5.5.64
        `blenders python executable` -m pip install protobuf==3.20.3

Linux
    Ensure to activate the ``local`` flag in the add-on preferences,
    as blender on linux usually doesn't have it's own site-packages.

    .. code-block:: bash

        `blenders python executable` -m ensurepip
        `blenders python executable` -m pip install mediapipe==0.8.10
        `blenders python executable` -m pip install opencv-contrib-python==4.2.0.34
        `blenders python executable` -m pip install protobuf==3.20.3

    In some cases the pipy open-cv package causes issues on linux.
    Consider to install open-cv via your local package manager.

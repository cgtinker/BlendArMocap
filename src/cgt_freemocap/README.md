# Freemocap import

[Freemocap](https://freemocap.org) session data can be saved in a folder which then can be import using BlendArMocap.
To import session data to blender, set the path to the session directory and press the import button.
There are several import options:
- **(default)** to import and process data while updating blender
- **load_quick** to import data in one call, faster but freezes blender
  - **load_raw** to leaves data unprocessed (may not be used to drive rigs)
- **load_synch_videos** to import session videos

To import data via a subprocess or via freemocap directly check the `fm_subprocess_cmd_receiver` or [Freemocap Github](https://github.com/freemocap/freemocap). <br>


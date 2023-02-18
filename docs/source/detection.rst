Mediapipe Detection
===================

`Google's Mediapipe<https://google.github.io/mediapipe>_` is used to detect features withing a stream or a video file.
The detection options are location in the `3D Viewport > BlendAr > Mediapipe`.

.. warning::
   Running Mediapipe within Blender requires external dependencies.
   More about the setup here ... ->

Type
    Movie
        Import movie files, preferably of type .mov.
        Reducing the dimensions before detecting may improves preformance.
    File Path
        Set the filepath to the movie which should be imported.
    
    Webcam
        Use the Webcam buildin or connected to your computer
    Webcam Device Slot
        Defaults to 0. If you have multiple cameras connected you might have to change the slot.

Key Step
    The *Key Step* determines in which frequency keyframes are getting set.
    This has slightly different effects depending on the used input type.
    
    Movie
        As every frame can get calculated, you can use a *Key Step* of 1.
        Setting the *Key Step* to 4 by example means you are skipping 3 frames before setting another keyframe while recording.
        This can be useful to reduce jitter and faster preformance.
    
    Webcam
        While the Webcam is running, frames are getting grabed on which the detection is preformed.
        Therefore the keystep determines the rate of which keyframes are getting set for every grabed frame.
        For starting out, I recommend trying a *Key Step* of 3 for Hand, Face and Pose detection.
        As Holistic detection is more preformance heavy I recommend a Key Step of 7.
        The Key Step which suits your system the most, highly depends on your computers hardware.
    
Target
    Hands
        Preform Hand detection.
    Face
        Preform Face detection.
    Pose
        Preform Pose detection.
    Holistic
        Preform Hand, Face and Pose detection.

Start Detection
    Button to start the detection. When using movie files as input, it may be called `Detect Movie`.
    While when using stream detection it may be called `Start Detection`.

Stop Detection
    Once the detection has been started, you can stop the detection 
    by either pressing the Button again or pressing :kbd:`Q`.



Advanced
--------

Model Complexity
    You can choose between a model complexity of [0, 1].
    The lower the complexity, the faster the detection.
    The higher the complexity, the better the detection results.

Min Detection Confidence
    Minimum confidence value ([0.0, 1.0]) from the detection model 
    for the detection to be considered successful. Default to 0.5.


For more informations check `Googles Mediapipe<https://google.github.io/mediapipe>_`.
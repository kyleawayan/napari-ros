"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the Reader specification, but your plugin may choose to
implement multiple readers or even other plugin contributions. see:
https://napari.org/stable/plugins/guides.html?#readers
"""
from pims import PyAVReaderTimed, PyAVReaderIndexed
from dask import delayed
import dask.array as da


def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    if not path.endswith(".mp4"):
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer. Both "meta", and "layer_type" are optional. napari will
        default to layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path

    if len(paths) != 1:
        raise ValueError("ROS reader can only handle a single video file")

    video = PyAVReaderTimed(paths[0])

    # TODO: Get number of frames a better way?
    frameRate = video.frame_rate
    duration = video.duration
    frames = int(frameRate * duration)

    lazy_video = delayed(video)
    lazy_arrays = [lazy_video[i] for i in range(frames)]
    arrays = [
        da.from_delayed(
            delayed_reader, shape=video.frame_shape, dtype=video.pixel_type
        )
        for delayed_reader in lazy_arrays
    ]

    data = da.stack(arrays, axis=0)

    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {"contrast_limits": [0, 255], "multiscale": False}

    layer_type = "image"  # optional, default is "image"
    return [(data, add_kwargs, layer_type)]

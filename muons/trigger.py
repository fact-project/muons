import numpy as np
import photon_stream as ps


def max_trigger_patch_response_in_image_sequence(image_sequence):
    """
    Returns the maximum response of a trigger-patch in a sliding time-window
    of 10ns.
    A trigger-patch is the sum of 9 pixels.
    With: trigger_patch = CHID // 9

    Parameter
    ---------
        image_sequece           np.array shape=(100, 1440)
                                An intensity-histogram of the photons
                                First axis is time-slices, second axis is
                                pixel-CHIDS.
    """
    NUM_TIME_SLICES = ps.io.magic_constants.NUMBER_OF_TIME_SLICES
    NUM_PIXELS = ps.io.magic_constants.NUMBER_OF_PIXELS
    NUM_PIXEL_IN_TRIGGER_PATCH = 9
    NUM_TRIGGER_PATCHES = NUM_PIXELS//NUM_PIXEL_IN_TRIGGER_PATCH
    NUM_SLICES_INTEGRATION_WINDOW = 20

    trigger_patch_sequence = image_sequence.reshape((
        NUM_TIME_SLICES,
        NUM_TRIGGER_PATCHES,
        NUM_PIXEL_IN_TRIGGER_PATCH))

    trigger_patch_sequence = np.sum(trigger_patch_sequence, axis=2)

    trigger_patch_sequence_convolved = np.zeros(
        shape=(NUM_TIME_SLICES, NUM_TRIGGER_PATCHES))

    for i in range(NUM_TIME_SLICES):
        start_slice = i
        end_slice = i + NUM_SLICES_INTEGRATION_WINDOW
        if end_slice >= NUM_TIME_SLICES:
            end_slice = NUM_TIME_SLICES - 1
        trigger_patch_sequence_convolved[i, :] = np.sum(
            trigger_patch_sequence[start_slice: end_slice, :],
            axis=0)

    return np.max(trigger_patch_sequence_convolved)

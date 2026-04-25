import torch
from pytorch_kinematics.transforms.rotation_conversions import axis_and_angle_to_matrix_33


def sample_perturbations(T, num_perturbations, radian_sigma, translation_sigma, axis_of_rotation=None,
                         translation_perpendicular_to_axis_of_rotation=True):
    """
    Sample perturbations around the given transform. The translation and rotation are sampled independently from
    0 mean gaussians. The angular perturbations' directions are uniformly sampled from the unit sphere while its
    magnitude is sampled from a gaussian.
    :param T: given transform to perturb around
    :param num_perturbations: number of perturbations to sample
    :param radian_sigma: standard deviation of the gaussian angular perturbation in radians
    :param translation_sigma: standard deviation of the gaussian translation perturbation in meters / T units
    :param axis_of_rotation: if not None, the axis of rotation to sample the perturbations around
    :param translation_perpendicular_to_axis_of_rotation: if True and the axis_of_rotation is not None, the translation
    perturbations will be perpendicular to the axis of rotation
    :return: perturbed transforms; may not include the original transform
    """
    pass

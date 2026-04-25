from pytorch_kinematics.chain import SerialChain
from pytorch_kinematics.transforms import Transform3d
from pytorch_kinematics.transforms import rotation_conversions
from typing import Union, Optional, Callable
import math
import torch
from matplotlib import pyplot as plt, cm as cm

# Check if torch.compile is available (PyTorch 2.0+)
_TORCH_COMPILE_AVAILABLE = hasattr(torch, 'compile') and torch.__version__ >= '2.0'


def _ik_step_kernel(m_flat: torch.Tensor, target_pos: torch.Tensor, target_wxyz: torch.Tensor,
                    J: torch.Tensor, reg_matrix: torch.Tensor, num_retries: int,
                    lm_damping: float = 0.0, task_weight: Optional[torch.Tensor] = None):
    """
    Fused IK step: delta_pose + damped least squares. Compatible with torch.compile(fullgraph=True).

    Args:
        m_flat: End-effector poses (N*M, 4, 4) where N=num_problems, M=num_retries
        target_pos: Target positions (N, 3)
        target_wxyz: Target orientations as wxyz quaternions (N, 4)
        J: Jacobian matrix (N*M, 6, DOF)
        reg_matrix: Regularization matrix (6, 6)
        num_retries: Number of retries per problem (M)
        lm_damping: Levenberg-Marquardt damping factor. When > 0, adds error-proportional
            regularization: mu = lm_damping * ||dx||^2. Large errors get more damping (stable),
            small errors get less (fast convergence). Inspired by mink's task-level LM damping.

    Returns:
        dq: Joint velocity (N*M, DOF, 1)
        dx: Pose error (N*M, 6, 1)
    """
    pass


def _ik_step_kernel_svd(m_flat: torch.Tensor, target_pos: torch.Tensor, target_wxyz: torch.Tensor,
                        J: torch.Tensor, reg_matrix: torch.Tensor, num_retries: int,
                        lm_damping: float = 0.0, task_weight: Optional[torch.Tensor] = None):
    """
    IK step using SVD-based damped least squares. Generally slower than the Cholesky-based
    kernel, but exposes singular values for selective damping if needed.

    The DLS pseudoinverse is: J^T (JJ^T + lambda^2 I)^{-1}
    Via SVD (J = U D V^T): sum_i (d_i / (d_i^2 + lambda^2)) v_i u_i^T

    Args:
        m_flat: End-effector poses (N*M, 4, 4)
        target_pos: Target positions (N, 3)
        target_wxyz: Target orientations as wxyz quaternions (N, 4)
        J: Jacobian matrix (N*M, 6, DOF)
        reg_matrix: Regularization matrix (6, 6) — only the diagonal (scalar) is used
        num_retries: Number of retries per problem (M)

    Returns:
        dq: Joint velocity (N*M, DOF, 1)
        dx: Pose error (N*M, 6, 1)
    """
    pass


class IKSolution:
    def __init__(self, dof, num_problems, num_retries, pos_tolerance, rot_tolerance, device="cpu", dtype=None):
        self.iterations = 0
        self.device = device
        self.num_problems = num_problems
        self.num_retries = num_retries
        self.dof = dof
        self.pos_tolerance = pos_tolerance
        self.rot_tolerance = rot_tolerance

        M = num_problems
        # N x DOF tensor of joint angles; if converged[i] is False, then solutions[i] is undefined
        self.solutions = torch.zeros((M, self.num_retries, self.dof), device=self.device, dtype=dtype)
        self.remaining = torch.ones(M, dtype=torch.bool, device=self.device)

        # M is the total number of problems
        # N is the total number of attempts
        # M x N tensor of position and rotation errors
        self.err_pos = torch.zeros((M, self.num_retries), device=self.device, dtype=dtype)
        self.err_rot = torch.zeros_like(self.err_pos)
        # M x N boolean values indicating whether the solution converged (a solution could be found)
        self.converged_pos = torch.zeros((M, self.num_retries), dtype=torch.bool, device=self.device)
        self.converged_rot = torch.zeros_like(self.converged_pos)
        self.converged = torch.zeros_like(self.converged_pos)

        # M whether any position and rotation converged for that problem
        self.converged_pos_any = torch.zeros_like(self.remaining)
        self.converged_rot_any = torch.zeros_like(self.remaining)
        self.converged_any = torch.zeros_like(self.remaining)

    def update_remaining_with_keep_mask(self, keep: torch.tensor):
        pass

    def update(self, q: torch.tensor, err: torch.tensor, use_keep_mask=True, keep_mask=None):
        pass


# helper config sampling method
def gaussian_around_config(config: torch.Tensor, std: float) -> Callable[[int], torch.Tensor]:
    pass


class LineSearch:
    def do_line_search(self, chain, q, dq, target_pos, target_wxyz, initial_dx, problem_remaining=None,
                       fk_fn=None, eef_frame_idx=None):
        pass


class BacktrackingLineSearch(LineSearch):
    def __init__(self, max_lr=1.0, decrease_factor=0.5, max_iterations=5, sufficient_decrease=0.01):
        self.initial_lr = max_lr
        self.decrease_factor = decrease_factor
        self.max_iterations = max_iterations
        self.sufficient_decrease = sufficient_decrease

    def do_line_search(self, chain, q, dq, target_pos, target_wxyz, initial_dx, problem_remaining=None,
                       fk_fn=None, eef_frame_idx=None):
        pass


class InverseKinematics:
    """Jacobian follower based inverse kinematics solver"""

    def __init__(self, serial_chain: SerialChain,
                 pos_tolerance: float = 1e-3, rot_tolerance: float = 1e-2,
                 retry_configs: Optional[torch.Tensor] = None, num_retries: Optional[int] = None,
                 joint_limits: Optional[torch.Tensor] = None,
                 config_sampling_method: Union[str, Callable[[int], torch.Tensor]] = "uniform",
                 max_iterations: int = 50,
                 lr: float = 1.0, line_search: Optional[LineSearch] = None,
                 regularlization: float = 1e-9, lm_damping: float = 0.1,
                 position_weight: float = 1.0, orientation_weight: float = 1.0,
                 debug=False,
                 early_stopping_any_converged=False,
                 early_stopping_no_improvement="any", early_stopping_no_improvement_patience=2,
                 enforce_joint_limits: bool = True,
                 num_limit_refinement_iterations: int = 10,
                 clamp_to_limits: bool = False
                 ):
        """
        :param serial_chain:
        :param pos_tolerance: position tolerance in meters
        :param rot_tolerance: rotation tolerance in radians
        :param retry_configs: (M, DOF) tensor of initial configs to try for each problem; leave as None to sample
        :param num_retries: number, M, of random initial configs to try for that problem; implemented with batching
        :param joint_limits: (DOF, 2) tensor of joint limits (min, max) for each joint in radians
        :param config_sampling_method: either "uniform" or "gaussian" or a function that takes in the number of configs
        :param max_iterations: maximum number of iterations to run
        :param lr: learning rate
        :param line_search: LineSearch object to use for line search
        :param regularlization: regularization term to add to the Jacobian
        :param debug: whether to print debug information
        :param early_stopping_any_converged: whether to stop when any of the retries for a problem converged
        :param early_stopping_no_improvement: {None, "all", "any", ratio} whether to stop when no improvement is made
        (consecutive iterations no improvement in minimum error - number of consecutive iterations is the patience).
        None means no early stopping from this, "all" means stop when all retries for that problem makes no improvement,
        "any" means stop when any of the retries for that problem makes no improvement, and ratio means stop when
        the ratio (between 0 and 1) of the number of retries that is making improvement falls below the ratio.
        So "all" is equivalent to ratio=0.999, and "any" is equivalent to ratio=0.001
        :param early_stopping_no_improvement_patience: number of consecutive iterations with no improvement before
        considering it no improvement
        :param position_weight: weight for position error in DLS objective. Higher values prioritize
        position accuracy. Default 1.0.
        :param orientation_weight: weight for orientation error in DLS objective. Higher values prioritize
        orientation accuracy. Default 1.0.
        :param lm_damping: Levenberg-Marquardt damping factor. Adds error-proportional regularization
        mu = lm_damping * ||error||^2 to the DLS solve, so large errors get more damping (stable) and
        small errors get less (fast convergence). Default 0.1.
        :param enforce_joint_limits: whether to enforce joint limits on the solution. Uses the chain's joint limits
        (chain.low/chain.high). After solving, revolute joints are wrapped by multiples of 2*pi, then any remaining
        violations are resolved via clamped refinement iterations. Set to False to disable.
        :param num_limit_refinement_iterations: number of clamped IK refinement iterations for enforcing joint limits
        :param clamp_to_limits: if True, clamp joint values to chain limits after each IK step (projected gradient).
        Uses chain.low/chain.high. Requires the chain to have finite joint limits. Default False.
        """
        pass

    def clear(self):
        pass

    def sample_configs(self, num_configs: int) -> torch.Tensor:
        pass

    def solve(self, target_poses: Transform3d) -> IKSolution:
        """
        Solve IK for the given target poses in robot frame
        :param target_poses: (N, 4, 4) tensor, goal pose in robot frame
        :return: IKSolution solutions
        """
        pass


def delta_pose(m: torch.tensor, target_pos, target_wxyz, out: torch.Tensor = None):
    """
    Determine the error in position and rotation between the given poses and the target poses

    :param m: (N x M x 4 x 4) tensor of homogenous transforms
    :param target_pos:
    :param target_wxyz: target orientation represented in unit quaternion
    :param out: optional pre-allocated output buffer (N*M, 6, 1) to reduce memory allocation
    :return: (N*M, 6, 1) tensor of delta pose (dx, dy, dz, droll, dpitch, dyaw)
    """
    pass


class PseudoInverseIK(InverseKinematics):
    def __init__(self, *args, use_compile: bool = False, **kwargs):
        """
        Initialize PseudoInverseIK solver.

        Args:
            *args: Arguments passed to InverseKinematics.
            use_compile: If True and PyTorch 2.0+ is available, use torch.compile
                for JIT compilation of FK, Jacobian, and IK step kernels. This can
                provide performance improvements after a warmup period. Default: False.
            **kwargs: Keyword arguments passed to InverseKinematics.
        """
        pass

    def solve(self, target_poses: Transform3d) -> IKSolution:
        pass

    def _has_finite_limits(self):
        """Check if the chain has any finite joint limits."""
        pass

    def _wrap_revolute_joints(self, q):
        """Wrap revolute joint values by multiples of 2*pi to bring them closer to the valid range.

        For revolute joints, q and q + 2*n*pi produce identical FK, so we can freely shift
        by multiples of 2*pi without affecting the solution. Prismatic joints are left unchanged.
        """
        pass

    def _enforce_limits(self, sol, target_pos, target_wxyz):
        """Enforce joint limits on IK solutions via wrapping and clamped refinement.

        1. Wrap revolute joints by 2*pi to bring them into the valid range (preserves FK exactly).
        2. Clamp any remaining violations and run refinement iterations to recover convergence.
        3. Update the solution with the refined joint values.
        """
        pass


class PseudoInverseIKWithSVD(PseudoInverseIK):
    """SVD-based damped least squares IK solver.

    About 2x slower per iteration than the default Cholesky-based solver (DLS),
    but converges slightly better near singularities (e.g. 99-100% vs 97-98%
    on near-singular targets). Exposes singular values which enables selective
    damping if subclassed further.
    """

    def __init__(self, *args, **kwargs):
        pass

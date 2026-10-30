"""[MasterSpec 3.1, C01-C09] Public mathematical API; reference solver excluded."""
from .types import CanonicalLP, SolverConfig, StepRecord, SolverResult, StopReason, ProofStatus
from .canonical import validate_canonical
from .geometry import simplex_geometry, simplex_embedding
from .projective import to_projective, from_projective
from .projection import project_to_kernel
from .potential import potential, transformed_potential
from .iteration import karmarkar_step
from .solver import solve_karmarkar
from .examples import (report_example_lp, original_to_u, u_to_original, analytic_u,
                       analytic_objective, analytic_potential, minimum_example_iterations)
from .general_lp import (
    GeneralLP, StandardFormLP, SimplexEmbedding, GeneralSolverConfig,
    GeneralIterationRow, GeneralKarmarkarResult, ReferenceResult, ProblemClassification,
    validate_general_lp, classify_general_lp, classify_preparation_failure,
    to_standard_form, prepare_simplex_embedding,
    recover_standard, recover_original, original_objective,
    solve_general_karmarkar, solve_reference, make_problem,
)


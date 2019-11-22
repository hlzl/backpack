from backpack.utils.utils import einsum


def matrix_from_kron_facs(factors):
    """Given [A, B, C, ...], return A ⊗ B ⊗ C ⊗ ... ."""
    mat = None
    for factor in factors:
        if mat is None:
            assert is_matrix(factor)
            mat = factor
        else:
            mat = matrix_from_two_kron_facs(mat, factor)

    return mat


def matrix_from_two_kron_facs(A, B):
    """Given A, B, return A ⊗ B."""
    assert is_matrix(A)
    assert is_matrix(B)

    mat_shape = (
        A.shape[0] * B.shape[0],
        A.shape[1] * B.shape[1],
    )
    mat = einsum("ij,kl->ikjl", (A, B)).contiguous().view(mat_shape)
    return mat


def vp_from_kron_facs(factors):
    """Return function v ↦ (A ⊗ B ⊗ ...)v for `factors = [A, B, ...]` """
    assert all_tensors_of_order(order=2, tensors=factors)

    shapes = [list(f.size()) for f in factors]
    _, col_dims = zip(*shapes)

    num_factors = len(shapes)
    equation = vp_einsum_equation(num_factors)

    def vp(v):
        assert len(v.shape) == 1
        v_reshaped = v.view(col_dims)
        return einsum(equation, v_reshaped, *factors).view(-1)

    return vp


def multiply_vec_with_kron_facs(factors, v):
    """Return (A ⊗ B ⊗ ...) v for `factors = [A, B, ...]`

    All Kronecker factors have to be of order-2-tensors.
    """
    vp = vp_from_kron_facs(factors)
    return vp(v)


def vp_einsum_equation(num_factors):
    letters = get_letters()
    in_str, v_str, out_str = "", "", ""

    for _ in range(num_factors):
        row_idx, col_idx = next(letters), next(letters)

        in_str += "," + row_idx + col_idx
        v_str += col_idx
        out_str += row_idx

    return "{}{}->{}".format(v_str, in_str, out_str)


def all_tensors_of_order(order, tensors):
    return all([is_tensor_of_order(order, t) for t in tensors])


def is_tensor_of_order(order, tensor):
    return len(tensor.shape) == order


def is_matrix(tensor):
    matrix_order = 2
    return is_tensor_of_order(matrix_order, tensor)


def get_letters(max_letters=26):
    for i in range(max_letters):
        yield chr(ord("a") + i)

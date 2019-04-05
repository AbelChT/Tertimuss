import scipy

from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class ProcessorModel(object):
    def __init__(self, c_proc: scipy.ndarray, lambda_proc: scipy.ndarray, pi_proc: scipy.ndarray, c_proc_alloc: scipy.ndarray,
                 s_exec: scipy.ndarray, s_busy: scipy.ndarray, m_proc_o: scipy.ndarray, a_proc: scipy.ndarray):
        self.c_proc = c_proc
        self.lambda_proc = lambda_proc
        self.pi_proc = pi_proc
        self.c_proc_alloc = c_proc_alloc
        self.s_exec = s_exec
        self.s_busy = s_busy
        self.m_proc_o = m_proc_o
        self.a_proc = a_proc
        # TODO: Analyze if is necessary return Pre and Post matrix


def generate_processor_model(tasks_specification: TasksSpecification, cpu_specification: CpuSpecification) \
        -> ProcessorModel:
    f = 1  # TODO: Check if it's an error
    n = len(tasks_specification.tasks)
    m = cpu_specification.number_of_cores

    eta = 100

    # Total of places of the TCPN processor module
    p = m * (2 * n + 1)  # m processors*(n busy places, n exec places, 1 idle place)

    # Total of transitions
    t = m * (2 * n)  # m processors*(n transitions alloc and n tramsition exec)
    t_alloc = n * m  # m processors*(n transitions alloc)

    pre = scipy.zeros((p, t))
    post = scipy.zeros((p, t))
    pre_alloc = scipy.zeros((p, t_alloc))
    post_alloc = scipy.zeros((p, t_alloc))
    lambda_vector = scipy.zeros(t)
    lambda_alloc = scipy.zeros(t_alloc)
    pi = scipy.zeros((t, p))
    mo = scipy.zeros((p, 1))  # Different from np.zeros(p), column array
    s_exec = scipy.zeros((n * m, p))
    s_busy = scipy.zeros((n * m, p))

    # Incidence Matrix C construction
    # numeration of places and the corresponding label in the model for CPU_1:
    # busy places: p1-pn->p^busy_{1,1},..,p^busy_{n,1}
    # exec places: pn+1-p2n->p^exec_{1,1},...,p^exec_{n,1}
    # idle place:  p2n+1->p^idle_1

    for k in range(1, m + 1):
        i = (2 * n + 1) * (k - 1) + 1

        # Construction of matrix Post and Pre for busy and exec places (connections to transitions alloc and exec)
        pre[i - 1:i + (n - 1), (k - 1) * (2 * n) + n: (k - 1) * (2 * n) + (2 * n)] = scipy.identity(n)
        post[i - 1:i + (2 * n - 1), (k - 1) * (2 * n):(k - 1) * (2 * n) + (2 * n)] = scipy.identity(2 * n)

        # Construction of matrix Post and Pre for idle place (connections to transitions alloc and exec)
        pre[k * (2 * n + 1) - 1, (k - 1) * (2 * n): (k - 1) * (2 * n) + n] = eta * scipy.ones(n)
        post[k * (2 * n + 1) - 1, (k - 1) * (2 * n) + n: k * (2 * n)] = eta * scipy.ones(n)

        # Construction of Pre an Post matrix for Transitions alloc
        pre_alloc[i - 1:i + (n - 1), (k - 1) * n: k * n] = \
            pre[i - 1:i + (n - 1), (k - 1) * (2 * n): (k - 1) * (2 * n) + n]
        post_alloc[i - 1:i + (n - 1), (k - 1) * n: (k - 1) * n + n] = \
            post[i - 1:i + (n - 1), (k - 1) * (2 * n): (k - 1) * (2 * n) + n]

        # Execution rates for transitions exec for CPU_k \lambda^exec= eta*F
        lambda_vector[(k - 1) * (2 * n) + n:(k - 1) * (2 * n) + 2 * n] = eta * f * scipy.ones(n)

        # Execution rates for transitions alloc \lambda^alloc= eta*\lambda^exec
        lambda_vector[(k - 1) * (2 * n):(k - 1) * (2 * n) + n] = \
            eta * lambda_vector[(k - 1) * (2 * n) + n:(k - 1) * (2 * n) + 2 * n]
        lambda_alloc[(k - 1) * n:k * n] = lambda_vector[(k - 1) * (2 * n):(k - 1) * (2 * n) + n]

        # Configuration Matrix
        pi[(k - 1) * (2 * n) + n:(k - 1) * (2 * n) + 2 * n, i - 1:i + (n - 1)] = scipy.identity(n)

        # Initial condition
        mo[k * (2 * n + 1) - 1, 0] = 1

        # Output matrix of the processor model, ( m^exec )
        s_busy[(k - 1) * n:k * n, i - 1:(2 * n + 1) * (k - 1) + n] = scipy.identity(n)
        s_exec[(k - 1) * n:k * n, i + n - 1:(2 * n + 1) * (k - 1) + 2 * n] = scipy.identity(n)

    c = post - pre
    c_alloc = post_alloc - pre_alloc
    lambda_proc = scipy.diag(lambda_vector)

    return ProcessorModel(c, lambda_proc, pi, c_alloc, s_exec, s_busy, mo, (c.dot(lambda_proc)).dot(pi))

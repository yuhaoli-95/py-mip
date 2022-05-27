## **PY-MIP**
----------------------------
English | [简体中文](README_zh-CN.md)
**PY-MIP** is a python-based collection of different MIP (Mixed-Integer Linear programs) FREE solvers for making full use of their own advantages by providing a uniform API.  Many famous FREE solvers (such as OR-Tools) have had problems and a model defined by a FREE solver can be hard to be redefined by another solver because of their different API. So **PY-MIP** provides high-level API to model and solve MIP by invoking different FREE solvers including:
 -  OR-Tools
 -  PySCIPOpt
 -  …

You only need write one solver independent code.


The pros and cons of some famous FREE solvers are summarized here:
|solver| pros | cons |
|----|----|----|
|ortools.linear_solver<br>(LP)| LP can export formula models that are easy to read and understand; <br>Easy installation;  | LP doesn’t support modeling quadratic programming although SCIP solver can solve it.<br>Lack of compute_IIS() function to find conflict constraints. |
|ortools.sat<br>(CP_SAT)|CP_SAT supports computing IIS. <br>Easy installion.|It’s difficult for human to read and understand the exported formula model.<br>CP_SAT doesn’t support modeling quadratic programming. |
|PySCIPOpt| Quadratic programming. |Lack of detail including function and parameter detail in the interface. 😅<br> A working installation of the SCIP Optimization Suite is required.<br>A commercial or evaluation license from ZIB is required.|



Commercial solvers (such as Gurobi or CPLEX) provide rich features including all of the above, but because of expensive license, they may be not suitable for small companies or individual developers. 



## Requirements
----------------------------
```
ortools
pyscipopt(optional, a SCIP Optimization Suite needs to be installed)
```

**PY-MIP** provides 3 solvers to invoke:
|solver name|solver core|scenario|requirement|
|----|----|----|----|
|```LP_SOLVER```|```SCIP_MIXED_INTEGER_PROGRAMMING``` of ```ortools.linear_solver```|Model problem;<br>  Export model detail;|```ortools```|
|```CP_SAT_SOLVER```|```ortools.sat.cp_model```|Find conflict constraints(compute IIS);|```ortools```|
|```SCIP_SOLVER```|```pyscipopt.Model```|Solve quadratic programming;|```pyscipopt, scip```|


## Model and solve a linear program
----------------------------
For solving a MIP problem, you can use **PY-MIP** mainly in three steps:

1) import ```Solver``` class and solver names
    ```python
    from PWPS.Config import CP_SAT_SOLVER, LP_SOLVER, SCIP_SOLVER
    from PWPS.Solver import Solver
    ```
2) Instantiate ```Solver``` class with a solver name, for example ```LP_SOLVER```.
    ```python
    solver = Solver(solver_name = LP_SOLVER)
    ```
3) Define decision variables, add constraint and set coefficient in objective function using ```solver```. For example, trying to model and solve the following problem:

<!-- $$
\min \quad 3a + 2\sum_{i=1}^{10}x_i + 5b
$$ --> 

<div align="center"><img style="background: white;" src="https://render.githubusercontent.com/render/math?math=%5Cmin%20%5Cquad%203a%20%2B%202%5Csum_%7Bi%3D1%7D%5E%7B10%7Dx_i%20%2B%205b"></div>

<!-- $$
\textrm{s.t.} \quad 3 * a + b - 10 + \sum_{i=1}^{10}x_i = 0
$$ --> 

<div align="center"><img style="background: white;" src="https://render.githubusercontent.com/render/math?math=%5Ctextrm%7Bs.t.%7D%20%5Cquad%203%20*%20a%20%2B%20b%20-%2010%20%2B%20%5Csum_%7Bi%3D1%7D%5E%7B10%7Dx_i%20%3D%200"></div>
<!-- $$
x_1 \ge x_2
$$ --> 

<div align="center"><img style="background: white;" src="https://render.githubusercontent.com/render/math?math=x_1%20%5Cge%20x_2"></div>

<!-- $$
a,b,x_i \in \left\{ 0, 1 \right\}
$$ --> 

<div align="center"><img style="background: white;" src="https://render.githubusercontent.com/render/math?math=a%2Cb%2Cx_i%20%5Cin%20%5Cleft%5C%7B%200%2C%201%20%5Cright%5C%7D"></div>



```python
a = solver.new_bool_var("a")
b = solver.new_bool_var("b")
x = [solver.new_bool_var(f"x{i}") for i in range(10)]
sum_x = sum([item for item in x])
# add constraint
con_1 = 3 * a + b - 10 + sum_x == 0
con_2 = x[0] >= x[1]
solver.add_constraint(con_1, name = "constraint 1")
solver.add_constraint(con_2, name = "constraint 2")
# set coefficient of each variable in objective function
solver.set_obj(3, a)
for item_x in x:
    solver.set_obj(2, item_x)
solver.set_obj(5, b)
```
4) solve：
```python
status = solver.solve()
# export model detial into ./model.txt 
solver.export_model(file_path="./model.txt")
print(status)
print(solver.get_var_name(a), solver.get_var_value(a))
print(solver.get_var_name(b), solver.get_var_value(b))
[print(solver.get_var_name(x[i]), solver.get_var_value(x[i])) for i in range(len(x))]
print("objective value: ", solver.objective_value)
```
Here is the output of the program.
```
status: optimal
solution: 
a = 1
b = 0
x0 = 0
x1 = 0
x2 = 0
x3 = 1
x4 = 1
x5 = 1
x6 = 1
x7 = 1
x8 = 1
x9 = 1
objective value:  16.999999999999996
```

## Additional examples
----------------------------

Additional example scripts are available in the [example](example/) of this GitHub.
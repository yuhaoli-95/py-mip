## **PY-MIP**

**PY-MIP**是一个基于python的MIP（Mixed-Integer Linear programs）“套娃”求解器，通过提供一个统一的API接口来充分利用各个开源免费求解器的各项功能。许多著名的免费求解器都有一些问题，而且由于塔们的接口不统一，由一个求解器定义的模型很难用另一个模型重新定义。因此**PY-MIP**提供一套高层API来调用不同求解器建模和求解，包括：
 -  OR-Tools
 -  PySCIPOpt
 -  …

模型只需要定义一次即可。

下面是个人总结的各个求解器的优缺点：

|求解器名称|优点 |缺点 |
|----|----|----|
|ortools.linear_solver|塔可以输出人类可读的数学模型文件;<br>ortools安装方便，不需要其他依赖包支持; |不支持二次目标和二次约束; <br>没有求解冲突约束的接口函数; |
|ortools.sat(cp_model)|塔支持计算IIS;<br>ortools安装方便，不需要其他依赖包支持;|塔输出的数学模型文件很难读，人类基本可以放弃；<br>不支持二次项; |
|PySCIPOpt|由于塔是直接调用编译好的scip，所以是支持二次项计算; |接口只是简单包装了下，对象的属性点不出来；<br>输出数学模型文件函数有问题，会直接报错；<br>不知道是否支持计算IIS，因为根本不知道model对象有哪些参数、函数😅；<br>需要先安装scip，对系统c库有要求;<br>虽然PySCIPOpt可以通过pip直接安装，但是scip的版本必须和PySCIPOpt版本匹配。如果因为不匹配报错，给出的错误提示完全想不到是版本不匹配造成的; <br>要先使用scip，必须得获取一个许可，可能商用会有风险; |

还有难用的一点是，即使是ortools这个求解器，linear_solver和cp_model的返回结果也完全不一样。
|求解器名称| 最优解 | 可行解 | 不可行解 | 其他标志 |
|----|----|----|----|----|
|ortools.linear_solver| linear_solver.Solver.OPTIMAL = 0 | linear_solver.Solver.FEASIBLE = 1 | linear_solver.Solver.INFEASIBLE = 2 | Solver.NOT_SOLVED = 6|
|ortools.sat.python.cp_model(cp_model)| cp_model.OPTIMAL = 4 | cp_model.FEASIBLE = 2 | cp_model.INFEASIBLE = 3 | cp_model.MODEL_INVALID = 1 |


商用求解器（比如Gurobi或者CPLEX）的话开源提供丰富的功能，但是由于需要购买（白嫖最快乐），所以可能不适合中小公司或者个人开发者。


## 依赖

```
ortools
pyscipopt(可选，需要额外安装scip)
```

本项目提供3种求解器调用
|求解器名称|调用求解器内核|使用场景|安装说明|
|----|----|----|----|
|```LP_SOLVER```|```ortools.linear_solver```，通过```SCIP_MIXED_INTEGER_PROGRAMMING```调用SCIP求解器|正常建模求解;<br> 输出格式化的模型文件;|```ortools```|
|```CP_SAT_SOLVER```|```ortools.sat.cp_model```|针对不可行问题找出其中冲突约束(```IIS```);|```ortools```|
|```SCIP_SOLVER```|```pyscipopt.Model```|求解二次规划问题（```ortools.linear_solver```中不能建立二次模型）;|```pyscipopt, scip```|


## 建模求解示例

在[example](example/)文件夹中会提供一些使用示例。总的来说依据下面流程构建模型：
1) 从项目中导入```Solver```类及求解器名称：
```python
from pymip.Config import CP_SAT_SOLVER, LP_SOLVER, SCIP_SOLVER
from pymip.Solver import Solver
```
2) 实例化一个```Solver```对象，在这里我们使用```LP_SOLVER```求解器：
```python
solver = Solver(solver_name = LP_SOLVER)
```
3) 使用```solver```对象创建决策变量，添加模型约束及目标：
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
# 设置约束
con_1 = 3 * a + b - 10 + sum_x == 0
con_2 = x[0] >= x[1]
solver.add_constraint(con_1, name = "constraint 1")
solver.add_constraint(con_2, name = "constraint 2")
# 设置目标
solver.set_obj(3, a)
# 由于 linear_solver 的框架限制，目前只能对单个决策变量设置目标系数
for item_x in x:
    solver.set_obj(2, item_x)
solver.set_obj(5, b)
```
4) 计算求解，并检查最终结果：
```python
status = solver.solve()
# 输出模型文件到 ./model.txt 文件中
solver.export_model(file_path="./model.txt")
print(status)
print(solver.get_var_name(a), solver.get_var_value(a))
print(solver.get_var_name(b), solver.get_var_value(b))
[print(solver.get_var_name(x[i]), solver.get_var_value(x[i])) for i in range(len(x))]
print("objective value: ", solver.objective_value)
```
得到结果如下：
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

## 其他示例

在[example](example/)可以找到其他示例。
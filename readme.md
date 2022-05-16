PWPS
=========

收费求解器贵有贵的道理，免费求解器各有各的难用，同时塔们的接口还不一样。下面是个人总结的各个求解器的优缺点：

|求解器名称|优点 |缺点 |
|----|----|----|
|ortools.linear_solver|塔可以输出人类可读的数学模型文件;<br>ortools安装方便，不需要其他依赖包支持; |不支持二次目标和二次约束; <br>没有求解冲突约束的接口函数; |
|ortools.sat(cp_model)|塔支持计算IIS;<br>ortools安装方便，不需要其他依赖包支持;|塔输出的数学模型文件很难读，人类基本可以放弃；<br>不支持二次项; |
|PySCIPOpt|由于塔是直接调用编译好的scip，所以是支持二次项计算; |接口只是简单包装了下，对象的属性点不出来；<br>输出数学模型文件函数有问题，会直接报错；<br>不知道是否支持计算IIS，因为根本不知道model对象有哪些参数、函数😅；<br>需要先安装scip，对系统c库有要求; |

本项目旨在像焊工一样，对各个免费求解器进行封装焊接在一起，构建一个高层api，以便尽量可能多的利用免费求解器的各个功能。

建模求解示例
----------------------------
在[example](examples/)文件夹中会提供一些使用示例。总的来说依据下面流程构建模型：
1) 从项目中导入```Solver```类及求解器名称：
```python
from PWPS.Config import CP_SAT_SOLVER, LP_SOLVER, SCIP_SOLVER
from PWPS.Solver import Solver
```
2) 实例化一个```Solver```对象，在这里我们使用```LP_SOLVER```求解器：
```python
solver = Solver(solver_name = SCIP_SOLVER)
```
1) 使用```solver```对象创建决策变量，添加模型约束及目标：
$$\min 3a + 2\sum_{i=1}^{10}x_i + 5b$$
$$\textrm{s.t.} \quad 3 * a + b - 10 + \sum_{i=1}^{10}x_i = 0$$
$$x_1 = x_2$$
$$a,b,x_i \in \left\{ 0, 1 \right\}$$

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
a = 1.0
b = 0.0
x0 = 0.0
x1 = 0.0
x2 = 0.0
x3 = 1.0
x4 = 1.0
x5 = 1.0
x6 = 1.0
x7 = 1.0
x8 = 1.0
x9 = 1.0
objective value:  16.999999999999996
```
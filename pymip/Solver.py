#!/usr/bin/env python
# coding=utf-8
'''
Author: Li Yuhao
Date: 2021-07-06 11:22:51
LastEditTime: 2022-05-27 16:55:05
LastEditors: your name
Description: 
FilePath: \\pymip\\pymip\\Solver.py
'''

import numbers
import os
import pathlib
import warnings
from abc import ABC
from datetime import timedelta
from typing import Dict, List, Union

from ortools.linear_solver import pywraplp as lp
from ortools.sat.python import cp_model
try:
    from pyscipopt import Model as ScipModel
    pyscipopt_FLAG = True
except:
    pyscipopt_FLAG = False

from .Config import CP_SAT_SOLVER, LP_SOLVER, SCIP_SOLVER
from .Config import FEASIBLE, IDLE, INFEASIBLE, NOT_SOLVED, OPTIMAL



__all__ = ["Solver", "IntVar", "BoolVar", "Variable", "Expression"]

_is_real_number = lambda x: isinstance(x, numbers.Real)
_is_var = lambda x: isinstance(x, IntVar) or isinstance(x, BoolVar) or isinstance(x, Variable) or isinstance(x, Constant)
# _is_constant = lambda x: isinstance(x, Constant) or isinstance(x, numbers.Real)
_is_integer_var = lambda x: isinstance(x, IntVar) or isinstance(x, BoolVar)
_is_expression = lambda x: isinstance(x, Expression)
_create_if_not_exists = lambda path_str: os.makedirs(path_str) if not os.path.exists(path_str) else None



"""
======================================================================================
                                abstract Variable
======================================================================================
"""
class AbstractVariavle(ABC):
    def __init__(
        self,
        solver_name: str,
        lb: int,
        ub: int,
        integer: bool, 
        name: str = ""
    ) -> None:
        super().__init__()
        name = str(name)
        self._solver_name = solver_name
        self._lb = lb
        self._ub = ub
        self._integer = integer
        self._name = name
        self._var = None
    @property
    def var(self):
        return self._var
    @property
    def lb(self):
        return self._lb
    @property
    def ub(self):
        return self._ub
    @property
    def name(self):
        return self._name
    @property
    def solver_name(self):
        return self._solver_name
    @property
    def integer(self):
        return self._integer
    
    # self + expr
    def __add__(self, expr):
        if _is_real_number(expr):
            expr = Constant(expr)
        return Expression(left = self, right = expr, solver_name=self._solver_name)

    # expr + self
    def __radd__(self, expr):
        if _is_real_number(expr):
            expr = Constant(expr)
        if _is_real_number(expr) or _is_var(expr) or _is_expression(expr):
            return Expression(left = expr, right = self, solver_name=self._solver_name)
        else:
            raise TypeError('')

    # self - expr
    def __sub__(self, expr):
        if _is_real_number(expr):
            expr = Constant(expr)
        return Expression(left = self, right = expr, solver_name=self._solver_name, operation= "-")

    # expr - self
    def __rsub__(self, expr):
        if _is_real_number(expr):
            expr = Constant(expr)
        return Expression(left = expr, right = self, solver_name=self._solver_name, operation= "-")

    # self * expr
    def __mul__(self, expr):
        if _is_real_number(expr):
            expr = Constant(expr)
        return Expression(left = self, right = expr, solver_name=self._solver_name, operation="*")

    # expr * self
    def __rmul__(self, expr):
        if _is_real_number(expr):
            expr = Constant(expr)
        return Expression(left = expr, right = self, solver_name=self._solver_name, operation="*")

    # self / expr
    def __truediv__(self, expr):
        if _is_real_number(expr):
            expr = Constant(expr)
        return Expression(left = self, right = expr, solver_name=self._solver_name, operation="/")

    # expr / self
    def __rtruediv__(self, expr):
        if _is_real_number(expr):
            expr = Constant(expr)
        return Expression(left = expr, right = self, solver_name=self._solver_name, operation="/")


    # self == expr
    def __eq__(self, expr):
        if _is_real_number(expr):
            expr = Constant(expr)
        return Expression(left = self, right = expr, solver_name=self._solver_name, operation="==")
    
    # self >= expr
    def __ge__(self, expr):
        if _is_real_number(expr):
            expr = Constant(expr)
        return Expression(left = self, right = expr, solver_name=self._solver_name, operation=">=")
    
    # self <= expr
    def __le__(self, expr):
        if _is_real_number(expr):
            expr = Constant(expr)
        return Expression(left = self, right = expr, solver_name=self._solver_name, operation="<=")

    # self < expr
    def __lt__(self, expr):
        raise ValueError(
            'Operators "<" and ">" not supported with the linear solver')

    # self > expr
    def __gt__(self, expr):
        raise ValueError(
            'Operators "<" and ">" not supported with the linear solver')

    # self != expr
    def __ne__(self, expr):
        raise ValueError('Operator "!=" not supported with the linear solver')

'''
======================================================================================
                                Constant
======================================================================================
'''
class Constant(AbstractVariavle):
    def __str__(self) -> str:
        return self._var

    def __repr__(self) -> str:
        return self.__str__()

    def __init__(self, var) -> None:
        super().__init__(solver_name = "", lb = None, ub = None, integer = None, name = str(var))
        self._var = var
        return



'''
======================================================================================
                                Variable
======================================================================================
'''
class Variable(AbstractVariavle):
    def __str__(self) -> str:
        c_type = "Integer" if self._integer else "Continuous"
        return f'< PWPS.{c_type}Var "{self._name}" (lb = {self._lb}, ub = {self._ub}, type = {self._solver_name}) >'

    def __repr__(self) -> str:
        return self.__str__()

    def __init__(self, model, solver_name: str, lb: int, ub: int, integer: bool, name: str = "") -> None:
        super().__init__(solver_name, lb, ub, integer, name)
        if solver_name == LP_SOLVER:
            var = model.Var(lb=lb, ub=ub, integer=integer, name=name)
        elif solver_name == CP_SAT_SOLVER:
            raise TypeError(detail=f"CP SAT ?????????????????????????????????,?????????'{name}'???????????????")
        elif solver_name == SCIP_SOLVER:
            vtype = "I" if integer else "C"
            var = model.addVar(name = name, vtype = vtype, lb = lb, ub = ub)
        self._var = var
        return

'''
======================================================================================
                                Int Variable
======================================================================================
'''
class IntVar(AbstractVariavle):
    def __str__(self):
        return f'< PWPS.IntegerVar "{self._name}" (lb = {self._lb}, ub = {self._ub}, type = {self._solver_name}) >'

    def __repr__(self) -> str:
        return self.__str__()

    def __init__(self, model, solver_name: str, lb: int, ub: int, name: str = "") -> None:
        super().__init__(solver_name = solver_name, lb = lb, ub = ub, integer = True, name = name)

        if solver_name == LP_SOLVER:
            var = model.IntVar(lb=lb, ub=ub, name=name)
        elif solver_name == CP_SAT_SOLVER:
            var = model.NewIntVar(lb=lb, ub=ub, name=name)
        elif solver_name == SCIP_SOLVER:
            var = model.addVar(name = name, vtype = 'I', lb = lb, ub = ub)
        self._var = var
        return


'''
======================================================================================
                                Bool Variable
======================================================================================
'''
class BoolVar(AbstractVariavle):
    def __str__(self):
        return f'< PWPS.BoolVar "{self._name}" (type = {self._solver_name}) >'

    def __repr__(self) -> str:
        return self.__str__()


    def __init__(self, model, solver_name: str, name: str = "") -> None:
        super().__init__(solver_name = solver_name, lb = 0, ub = 1, integer = True, name = name)

        if solver_name == LP_SOLVER:
            var = model.BoolVar(name=name)
        elif solver_name == CP_SAT_SOLVER:
            var = model.NewBoolVar(name=name)
        elif solver_name == SCIP_SOLVER:
            """
            param name: ????????????????????????????????????????????????
            param vtype: ??????????????????????????????C???????????????????????????????????????I????????????????????????B??????0/1?????????
            param lb: ???????????????None???????????????????????????0.0
            param ub: ???????????????None???????????????????????????None
            param obj: objective value of variable (Default value = 0.0)
            param pricedVar: is the variable a pricing candidate? (Default value = False)
            """
            var = model.addVar(name = name, vtype = 'B')
        self._var = var
        return
"""
======================================================================================
                                Expression
======================================================================================
"""
class Expression(AbstractVariavle):

    def __repr__(self) -> str:
        return self.__info

    def __str__(self) -> str:
        return self.__info

    def __get_var(self, item) -> list:
        _left = f"{self._name}"
        _right = f"{item._name}"
        if self._operation == "*":
            _left = _left if _is_var(self._left) else f"({_left})"
            _right = _right if _is_var(self._left) else f"({_right})"
        self._name = f"{item._name}" if self._name == "" else f"{_left} {self._operation} {_right}"
        return item._var
        
    def __init__(self, left, right, solver_name: str, name: str = "", operation: str = "+") -> None:
        super().__init__(solver_name, lb = None, ub = None, integer = None, name = "")
        self._left = left
        self._right = right
        self._operation = operation
        self._name = ""

        _left = self.__get_var(left)
        _right = self.__get_var(right)

        self._var = eval(f"(_left) {self._operation} (_right)")

        self.__info = f'< PWPS "Expression", {self._name}, type: {self._solver_name} >'
        return


'''
======================================================================================
                                Solver
======================================================================================
'''
class Solver:

    _status_map = {
        LP_SOLVER: {
            lp.Solver.OPTIMAL: OPTIMAL,
            lp.Solver.FEASIBLE: FEASIBLE,
            lp.Solver.INFEASIBLE: INFEASIBLE,
            lp.Solver.NOT_SOLVED: NOT_SOLVED,
        },
        CP_SAT_SOLVER: {
            cp_model.OPTIMAL: OPTIMAL,
            cp_model.FEASIBLE: FEASIBLE,
            cp_model.INFEASIBLE: INFEASIBLE,
            # cp_model.NOT_SOLVED: NOT_SOLVED,
        },
        SCIP_SOLVER: {
            "optimal": OPTIMAL,
            "timelimit": FEASIBLE,
            "infeasible": INFEASIBLE,
        }
    }

    def __init__(
        self,
        solver_name: str, # ???????????????
        time_limit: timedelta = timedelta(seconds=0), # ??????????????????
        export_model_path: str = '', # ??????????????????????????????
        elaborate: bool = False, # ??????????????????????????????
        compute_IIS: bool = False, # ????????????????????????
        problem_name = ""
    ) -> None:

        """     ????????????    """
        self.problem_name = problem_name # ????????????
        self._solver_name = solver_name # ???????????????
        if solver_name == SCIP_SOLVER and pyscipopt_FLAG == False:
            raise NotImplementedError(
                '??????????????????"pyscipopt",????????????????????????????????????.' + 
                '???????????????????????????????????????,????????????"LP_SOLVER"?????????(??????ortools????????????scip?????????)????????????.')
        self._compute_IIS = compute_IIS # ????????????????????????
        # self.time_limit: int = int(time_limit.total_seconds() * 1000)
        self._time_limit = time_limit # ??????????????????
        self._bad_constraint_info = [] # ??????????????????

        self._elaborate = elaborate # ????????????????????????????????????
        
        self._export_model_path: pathlib.Path = pathlib.Path(export_model_path) # ??????????????????????????????

        """     LP ????????????    """
        self._lp_model: lp.Solver = lp.Solver(name=problem_name, problem_type=lp.Solver.SCIP_MIXED_INTEGER_PROGRAMMING) # linear solver ??????
        self._lp_obj: lp.Objective = self._lp_model.Objective() # linear solver obj

        """     CP SAT ????????????    """
        self._cp_sat_model: cp_model.CpModel = cp_model.CpModel() # cp model??????
        self._cp_sat_solver: cp_model.CpSolver = cp_model.CpSolver() # cp solver

        # ?????????cp_sat??????
        self._cp_sat_all_vars: Dict[str, cp_model.IntVar] = {}
        self._cp_sat_assumptions: List[BoolVar] = [] # ????????????


        """     SCIP ????????????    """
        self._scip_model = ScipModel() if solver_name == SCIP_SOLVER else None # linear solver ??????
        self._scip_obj = self._scip_model # linear solver obj
        self._scip_sol = [] # scip???????????? 

        """     ????????????    """
        self.__models = {
            LP_SOLVER: self._lp_model,
            CP_SAT_SOLVER: self._cp_sat_model,
            SCIP_SOLVER: self._scip_model
        }
        self.__all_vars: Dict[str, List[Union[IntVar, BoolVar, Variable]]] = {
            LP_SOLVER: [],
            CP_SAT_SOLVER: [],
            SCIP_SOLVER: []
        }

        self.__all_obj_vars: Dict[str, List[Union[IntVar, BoolVar, Variable]]] = {
            LP_SOLVER: {},
            CP_SAT_SOLVER: {},
            SCIP_SOLVER: {}
        }

        self.__obj_formula = []
        self.__constraint_formula = []
        self._objective_value = None # ???????????????
        self._status = IDLE # ???????????????
        return

    @property
    def solver_name(self) -> str:
        return self._solver_name

    @solver_name.setter
    def solver_name(self, solver_name: str):
        self._solver_name = solver_name
        return
    
    @property
    def compute_IIS(self) -> bool:
        return self._compute_IIS

    @compute_IIS.setter
    def compute_IIS(self, _compute_IIS: bool):
        self._compute_IIS = _compute_IIS
        return

    @property
    def model(self):
        return self.__models[self._solver_name]

    @property
    def all_vars(self) -> List[Union[IntVar, BoolVar, Variable]]:
        return self.__all_vars[self._solver_name]

    @property
    def obj_formula(self) -> List[Expression]:
        return self.__obj_formula

    @property
    def constraint_formula(self) -> List[Expression]:
        return self.__constraint_formula

    @property
    def objective_value(self) -> float:
        return self._objective_value

        
    '''
    =============================================================================
                                    ?????? ????????????
    =============================================================================
    '''
    # helper function
    def new_bool_var(self, name: str) -> BoolVar:
        bool_var = BoolVar(
            solver_name = self._solver_name, 
            model = self.__models[self._solver_name], 
            name = name)
        self.__all_vars[self._solver_name].append(bool_var)
        return bool_var

    def new_int_var(self, lb: int, ub: int, name: str) -> IntVar:
        int_var = IntVar(
            solver_name = self._solver_name, 
            model = self.__models[self._solver_name], 
            lb = lb, 
            ub = ub, 
            name = name)
        self.__all_vars[self._solver_name].append(int_var)
        return int_var

    def new_var(self, lb: int, ub: int, integer: bool, name: str) -> Variable:
        var = Variable(
            solver_name = self._solver_name, 
            model = self.__models[self._solver_name], 
            lb = lb, 
            ub = ub, 
            integer = integer, 
            name = name)
        self.__all_vars[self._solver_name].append(var)
        return var

    def add_constraint(self, constraint: Expression, name: str) -> None:
        if isinstance(constraint, bool):
            tmp_constraint = constraint
            if self.solver_name == SCIP_SOLVER:
                warnings.warn(f"'{name}'?????? = {constraint},??????????????????????????????'bool'??????, ??????'SCIP_SOLVER'???????????????????????????;")
                return
        elif isinstance(constraint, Expression):
            tmp_constraint = constraint._var
        self.__constraint_formula.append(constraint)
        
        # add constraint
        if self._solver_name == LP_SOLVER:
            self._lp_model.Add(constraint=tmp_constraint, name=name)
        elif self._solver_name == CP_SAT_SOLVER:
            # ??????????????????????????????, ????????????????????? assumption ??????
            if self._compute_IIS:
                assumption = self.new_bool_var(name=f"_ASSUMPTION_{name}")
                self._cp_sat_model.Add(tmp_constraint).OnlyEnforceIf(assumption._var)
                self._cp_sat_assumptions.append(assumption)
            else:
                self._cp_sat_model.Add(tmp_constraint)
        elif self._solver_name == SCIP_SOLVER:
            self._scip_model.addCons(tmp_constraint, name)
        return

    # ??????????????????
    def set_obj(self, coeff: int, var: Union[IntVar, BoolVar, Variable]):
        if _is_real_number(coeff):
            coeff = Constant(coeff)
        tmp_obj_formula = coeff * var
        self.__obj_formula.append(tmp_obj_formula)
        if self._solver_name == LP_SOLVER:
            self._lp_obj.SetCoefficient(var._var, coeff._var)
            
        elif self._solver_name == SCIP_SOLVER:
            self._scip_obj.setObjective(tmp_obj_formula._var, sense='minimize', clear = False) 
        
        # record objective variable
        self.__all_obj_vars[self._solver_name][var._name] = var
        if _is_var(coeff): self.__all_obj_vars[self._solver_name][coeff._name] = coeff
        return

    # model tools
    def get_var_name(self, var: Union[Variable, IntVar, BoolVar]) -> str:
        '''
        @description: ??????????????????
        @return [*]
        '''
        return var._name

    def get_var_value(self, var: Union[Variable, IntVar, BoolVar]) -> float:
        '''
        @description: ??????????????????
        @return [*]
        '''
        value = None
        if self._solver_name == LP_SOLVER:
            value = var._var.solution_value()
        elif self._solver_name == CP_SAT_SOLVER:
            value = self._cp_sat_solver.Value(var._var)
        elif self._solver_name == SCIP_SOLVER:
            value = self._scip_sol[0][var._var]
        value = round(value) if _is_integer_var(var) else value
        return value
    
    # export model detail into file
    def export_model(self, file_path: Union[str, pathlib.Path] = ""):
        '''
        description: ??????ortools??????Linear Solver?????????????????????????????????

        param [str, pathlib.Path] file_path ???????????????????????????
        
        return [*]
        '''
        # ????????????
        file_path = file_path if file_path else self._export_model_path
        file_path = pathlib.Path(file_path)
        folder_path = file_path.parent
        if self._export_model_path and self._solver_name == LP_SOLVER:
            _create_if_not_exists(folder_path)
            with open(file_path, 'w', encoding="utf-8") as f:
                f.write(self._lp_model.ExportModelAsLpFormat(False))
        else:
            warnings.warn(f'Current solver is "{self._solver_name}". Only "LP_SOLVER" can export mathmatical formula into file!')
        return

    
    # ??????
    def solve(self) -> str:
        '''
        @description: 
        @param [*] self
        @return [*]
        '''
        

        # lp model
        if self._solver_name == LP_SOLVER:
            # set time limit
            if self._time_limit:
                self._lp_model.set_time_limit(int(self._time_limit.total_seconds() * 1000))
            
            # ???????????????????????????????????????
            if self._elaborate:
                self._lp_model.SuppressOutput()
                self._lp_model.EnableOutput()

            # solve problem
            _status = self._lp_model.Solve()
            # modify solver status
            if _status in self._status_map[LP_SOLVER].keys():
                _status = self._status_map[LP_SOLVER][_status] 
            else:
                raise ValueError(f"{self._solver_name} solver return UNDEFINED STATUS = {_status}!")
            # get objective if solution is feasible
            self._objective_value = self._lp_model.Objective().Value()if _status in [OPTIMAL, FEASIBLE] else None

        # cp sat model
        elif self._solver_name == CP_SAT_SOLVER:
            # set time limit
            if self._time_limit:
                self._cp_sat_solver.parameters.max_time_in_seconds = int(self._time_limit.total_seconds() * 1000)
            # solve problem
            _status = self._cp_sat_solver.Solve(self._cp_sat_model)
            # modify solver status
            if _status in self._status_map[CP_SAT_SOLVER].keys():
                _status = self._status_map[CP_SAT_SOLVER][_status] 
            else:
                raise ValueError(f"{self._solver_name} solver return UNDEFINED STATUS = {_status}!")
        # scip model
        elif self._solver_name == SCIP_SOLVER:
            # set time limit
            if self._time_limit:
                self._scip_model.setRealParam('limits/time', self._time_limit.total_seconds())
            # solve problem
            self._scip_obj.optimize()
            # get scip result solutions
            self._scip_sol = self._scip_obj.getSols() 
            # modify solver status
            _status = self._scip_obj.getStatus()
            if _status in self._status_map[SCIP_SOLVER].keys():
                if _status == "timelimit" and self._scip_obj.getSols() == []:
                    _status = NOT_SOLVED
                else:
                    _status = self._status_map[SCIP_SOLVER][_status]
            else:
                raise ValueError(f"{self._solver_name} solver return UNDEFINED STATUS = {_status}!")
            # get objective if solution is feasible
            self._objective_value = self._scip_model.getObjVal() if _status in [OPTIMAL, FEASIBLE] else None

        self._status = _status
        return _status

    # ??????????????????
    def find_conflict_constraints(self):
        '''
        description: ??????????????????
        return [*]
        '''
        # Creates a solver and solves the model.
        self._cp_sat_model.AddAssumptions([item._var for item in self._cp_sat_assumptions])
        # # ????????????????????????
        a = self._cp_sat_model.Validate()
        # ??????
        _status = self.solve()
        if _status in [FEASIBLE, OPTIMAL]:
            return []
        elif _status == INFEASIBLE:
            # ????????????????????????????????????????????????????????????
            conflict_constraints = [ass._var.Name() for ass in self._cp_sat_assumptions if ass._var.Index() in self._cp_sat_solver.SufficientAssumptionsForInfeasibility()]
            return conflict_constraints
        else:
            raise ValueError(f"{self._solver_name} solver return UNDEFINED STATUS = {_status}!")

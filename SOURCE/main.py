import sys
import copy
from pysat.solvers import Solver, Glucose4

count = 0

def parse_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
        arr = [[int(value) if value != '-' else 9 for value in line.strip().split(',')] for line in lines]
      
    return arr, len(arr), len(arr[0])

def find_all_clauses(input_array,
             input_len,
             combi_len,
             indi_tup,
             ans_index,
             next_start,
             clause_tup):
    global count
    #----------------- Loop for List X
    for iter in range(next_start,input_len+1):


        #------------------- Return if List X empty
        if combi_len <= 0:
            clause_tup.append(copy.copy(indi_tup))    
            count = count + 1
            return
  
        indi_tup[ans_index] = input_array[iter]
        find_all_clauses(input_array,
                 input_len,
                 combi_len-1,
                 indi_tup,
                 ans_index + 1,
                 iter + 1,
                 clause_tup)

def find_cell_no(i, j, row, col):
    return i*col + j + 1

#find list X arround current square
def find_adjacent_cells(board, i, j, row, col):
    output = []    

    if i >= 1 and j >= 1:
        output.append(find_cell_no(i-1,j-1,row,col))
    if i >= 1:
        output.append(find_cell_no(i-1,j,row,col))
    if i >= 1 and j < (col - 1):
        output.append(find_cell_no(i-1,j+1,row,col))
    if j < (col - 1):
        output.append(find_cell_no(i,j+1,row,col))
    if i < (row - 1) and j < (col - 1):
        output.append(find_cell_no(i+1,j+1,row,col))
    if i < (row - 1):
        output.append(find_cell_no(i+1,j,row,col))
    if i < (row - 1) and j >= 1:
        output.append(find_cell_no(i+1,j-1,row,col))
    if j >= 1:
        output.append(find_cell_no(i,j-1,row,col))

    return output

def convert2CNF(board, row, col):
    # interpret the number constraints
    global count
    count_clause = 0

    result=[]
    for i in range(row):
        for j in range(col):
            if board[i][j]==9:
                continue
            elif board[i][j] != -1:
                result.append([-(i*col+j+1)])
                first_adjacent_cells = find_adjacent_cells(board, i ,j, 
                                row, col)
                count_adj = len(first_adjacent_cells)
                
                #--------------------------------------------------invalid broad
                if ((board[i][j] > count_adj) or (board[i][j] < -1)):
                    print("Invalid board at postion Row: " + str(i) + " Col: " + str(j) + " !!!")
                    sys.exit(1)

                first_adjacent_cells.append(0)


                #------------------------------------------------List boom in current square
                indi_tup = []
                for k in range(board[i][j] + 1):
                    indi_tup.append(0)
                #print indi_tup
                first_tup = []
                count = 0
                #------------------------------------At least n boom 
                find_all_clauses(first_adjacent_cells,count_adj,board[i][j]+1,indi_tup,0,0,first_tup)
                count_clause = count_clause + count
            
                for k in range(len(first_tup)):
                    ls=[]
                    for l in range(board[i][j] + 1):
                        ls.append(-1*first_tup[k][l])
                    result.append(ls)

                #-----------------------------------At least n square not contain boom
                indi_tup = []
                for k in range(count_adj - board[i][j] + 1):
                        indi_tup.append(0)
                count = 0
                second_tup = []    
                find_all_clauses(first_adjacent_cells,count_adj,count_adj-board[i][j]+1,indi_tup,0,0,second_tup)
                count_clause = count_clause + count

                for k in range(len(second_tup)):
                        ls=[]
                        for l in range(count_adj-board[i][j] + 1):
                            ls.append(second_tup[k][l])

                        result.append(ls)

            else:

                count_clause = count_clause + 1
                result.append([find_cell_no(i,j,row,col)])
    

    return result

def SolverCNF(cnf):
    def unit_propagation(assignments, clauses):
        unit_clauses = [c for c in clauses if len(c) == 1]
        while unit_clauses:
            #unit is single clause
            unit = unit_clauses[0][0]
            if([-unit] in unit_clauses):
               return None,None
            assignments[abs(unit)] = (unit > 0)
            ls=[]
            #check unit in any clause or not, unit always true
            for c in clauses: 
                if unit not in c:
                    if -unit in c:
                        c.remove(-unit)
                        ls.append(c)
                    else:
                        ls.append(c)
            clauses=ls    
            # clauses = [c for c in clauses if unit not in c]
            unit_clauses = [c for c in clauses if len(c) == 1]
        return assignments, clauses

    def dpll(assignments, clauses):
        #Tackle single clause
        assignments, clauses = unit_propagation(assignments, clauses)
        if clauses==None:
            return None
        if all(len(c) == 0 for c in clauses):
            return assignments
        if any(len(c) == 0 for c in clauses):
            return None

        literal = abs(clauses[0][0])
        new_clauses=copy.deepcopy(clauses)
        new_clauses.append([literal])
        result = dpll({}, new_clauses)
        if result is None:
            assignments[literal] = False
            
            new_clauses=copy.deepcopy(clauses)
            new_clauses.append([-literal])
            assignments.update(dpll({}, new_clauses))
        
        new_clauses=copy.deepcopy(clauses)
        new_clauses.append([-literal])
        result = dpll({}, new_clauses)
        if result is None:
            assignments[literal] = True

            new_clauses=copy.deepcopy(clauses)
            new_clauses.append([literal])
            assignments.update(dpll({}, new_clauses))

        return assignments

   
    assignments = {}
    result = dpll(assignments, cnf)
    if result==None:
        return {}
    return result

def apply_resolution(cnf_clauses):
    #add 1 clause to the clauses
    def unit_propagation(assignments, clauses):
        unit_clauses = [c for c in clauses if len(c) == 1]
        while unit_clauses:
            #unit is single clause
            unit = unit_clauses[0][0]
            if([-unit] in unit_clauses):
               return None,None
            assignments[abs(unit)] = (unit > 0)
            ls=[]
            #check unit in any clause or not, unit always true
            for c in clauses: 
                if unit not in c:
                    if -unit in c:
                        c.remove(-unit)
                        ls.append(c)
                    else:
                        ls.append(c)
            clauses=ls    
            # clauses = [c for c in clauses if unit not in c]
            unit_clauses = [c for c in clauses if len(c) == 1]
        return assignments, clauses    

    #combine 2 clause
    def resolve(clause1, clause2):
        resolved_clause = []
        for literal in clause1:
            if literal not in clause2:
                resolved_clause.append(literal)  
        for literal in clause2:
            if literal not in clause1:
                resolved_clause.append(literal)  
        # if(len(resolved_clause)==1):
        #     print('ok')
        return resolved_clause 
    
    assignment,cnf_clauses= unit_propagation({},cnf_clauses)
    if cnf_clauses == None:
        return {}
    n=1

    #sord by array len in array
    cnf_clauses=sorted(cnf_clauses, key=len)
    while(len(cnf_clauses)>1 and n!=len(cnf_clauses)):
        n=len(cnf_clauses)
        # cnf_clauses=sorted(cnf_clauses, key=len)

        #resolution  3 combine to 2 
        for i in range(n-1,1,-1):
            found = False
            if(len(cnf_clauses[i])==3):
                for j in range(0,i-1):
                    if(len(cnf_clauses[j])==2 and cnf_clauses.count(cnf_clauses[j])==2):
                        resolved_clause = resolve(cnf_clauses[j], cnf_clauses[i])
                        if(len(resolved_clause)==1):
                            if(resolved_clause[0]>0):
                               assignment[resolved_clause[0]]=False
                               cnf_clauses.append([resolved_clause[0]])
                            else:
                               assignment[abs(resolved_clause[0])]=True
                               cnf_clauses.append([resolved_clause[0]])
                            
                            found=True
                            break
            if(found):
                break
        
        new_assignment,cnf_clauses= unit_propagation({},cnf_clauses)
        if cnf_clauses == None:
            return assignment
        assignment.update(new_assignment)

    return assignment

def brute_force_solver(cnf):
    def evaluate_assignment(assignment, clauses):
        for clause in clauses:
            clause_satisfied = False
            for literal in clause:
                var = abs(literal)
                value = assignment[var]
                if (literal > 0 and value) or (literal < 0 and not value):
                    clause_satisfied = True
                    break
            if not clause_satisfied:
                return False
        return True

    def bruteforce(index, assignment, clauses,n):
        if index > n:
            if evaluate_assignment(assignment, clauses):
                return assignment.copy()
            return {}

        var = index
        assignment[var] = False
        solutions = bruteforce(index + 1, assignment, clauses,n)
        if len(solutions)>0:
            return solutions

        assignment[var] = True
        solutions = bruteforce(index + 1, assignment, clauses,n)
        return solutions

    num_vars = max(abs(literal) for clause in cnf for literal in clause)
    solutions = bruteforce(1, {}, cnf,num_vars)
    return solutions

def output(board, solution, row, col,name):
    arr = []
    for i in range (row):
        r = []
        for j in range (col):
            if(board[i][j] != 9):
                r.append(str(board[i][j]))
            else:
                if((i*col + j + 1) in solution):
                    if(solution[i*col + j + 1] == True):
                        r.append('X') 
                    else:
                        r.append('-')
                else:
                    r.append('-')
        arr.append(r)
        
    with open(f'output{name}.txt', 'w') as output_file:
        for i in arr:
            output_file.write(','.join(i) + '\n')

if __name__ == '__main__':
        # filename=input('filename: ')
        filename="input.txt"
        board,row,col = parse_file(filename)
        cnf_clauses=convert2CNF(board, row, col)
        # for i in cnf_clauses:
        #     print(i)

        print("1. Resolution")
        print("2. Brute-force")
        print('3. Backtracking')
        print("4. Pysat solver")
        # choice = int(input("Choose an option: "))
        choice =1
        
        #1. resolution solver
        if(choice == 1):
            solution = apply_resolution(cnf_clauses)
            solution=dict(sorted(solution.items(), key=lambda item: item[0]))
            
            output(board, solution,row,col,'_'+str(row))
            
            
        #2.  brute force
        if(choice == 2):
            solution = brute_force_solver(cnf_clauses) 
            output(board, solution,row,col,'_'+str(row))
        #3  Backtracking solver
        if(choice == 3):
            solution = SolverCNF(cnf_clauses)
            solution = dict(sorted(solution.items(), key=lambda item: item[0]))
            output(board, solution,row,col,'_'+str(row))

        #4 pysat solver
        if(choice == 4):
            solver = Glucose4()
            for clause in cnf_clauses:
                solver.add_clause(clause)

            if solver.solve():
                assignment = {}
                model = solver.get_model()

            solution={}
            if solver.solve():
                model = solver.get_model()
                for i in model:
                    solution[abs(i)]=False if i < 0 else True
            
            output(board, solution,row,col,'_'+str(row))
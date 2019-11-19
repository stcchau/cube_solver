import queue
import time
import random

class Cube:

    def __init__(self, board):
        self.board = board
        self.solution = [[('w', 'r', 'g'), ('w', 'g'), ('w', 'g', 'o'), ('w', 'o'), ('w', 'o', 'b'), ('w', 'b'), ('w', 'b', 'r'), ('w', 'r')],
                        [('y', 'o'), ('y', 'o', 'g'), ('y', 'g'), ('y', 'g', 'r'), ('y', 'r'), ('y', 'r', 'b'), ('y', 'b'), ('y', 'b', 'o')]]

    def is_solved(self):
        for face in range(len(self.board)):
            arr = []
            for piece in range(len(self.board[face])):
                for color in self.board[face][piece]:
                    arr.append(color)
            if 'w' in arr and 'y' in arr:
                return False
            arr = [c for c in arr if c != 'w' and c != 'y']
            count = 0
            for i in range(len(arr)):
                if arr[i] != arr[i - 1]:
                    if count < 2 and (arr[i - 1] != arr[i - 2] or arr[i - 1] != arr[i - 3]):
                        return False
                    else:
                        count = 0
                else:
                    count += 1
        return True

    def pivot(self, face):
        half_size = 0
        pivot = 0
        while half_size != 6:
            half_size += len(self.board[face][pivot]) - 1
            pivot += 1
        return pivot

    def perform_move(self, move):
        move = move.upper()
        dic = {'U': 0, 'D': 1, 'U\'': 0, 'D\'': 1}
        if move == 'X':
            top_switch = self.board[0][self.pivot(0):len(self.board[0])]
            bottom_switch = self.board[1][self.pivot(1):len(self.board[1])]
            self.board[0][self.pivot(0):len(self.board[0])], self.board[1][self.pivot(1):len(self.board[1])] = bottom_switch, top_switch
        else:
            while True:
                if move == 'U' or move == 'D':
                    self.board[dic[move]].insert(0, self.board[dic[move]].pop())
                else:
                    self.board[dic[move]].append(self.board[dic[move]].pop(0))
                half_size = 0
                for i in range(len(self.board[dic[move]])):
                    half_size += len(self.board[dic[move]][i]) - 1
                    if half_size == 6:
                        break
                if half_size == 6:
                    break

    def scramble(self, n):
        for i in range(n):
            self.perform_move(random.choice(['X', 'U', 'D', 'U\'', 'D\'']))

    def copy(self):
        return Cube([[(piece[:]) for piece in face] for face in self.board])

    def successors(self):
        moves = ['X', 'U', 'D', 'U\'', 'D\'']
        for move in moves:
            c = self.copy()
            c.perform_move(move)
            yield c, move

    def heuristic(self):
        heuristic = 0
        for face in range(len(self.board)):
            arr = []
            for piece in range(len(self.board[face])):
                for color in self.board[face][piece]:
                    arr.append(color)
                if self.board[face][piece-1][0] != self.board[face][piece][0]:
                    heuristic += 1
            arr = [c for c in arr if c != 'w' and c != 'y']
            count = 0
            for i in range(len(arr)):
                if arr[i] != arr[i - 1]:
                    if count < 2 and (arr[i - 1] != arr[i - 2] or arr[i - 1] != arr[i - 3]):
                        heuristic += 1
                    count = 0
                else:
                    count += 1
        return int(heuristic / 2)

    def make_tuple(self):
        b = self.board[:]
        for r in range(len(b)):
            b[r] = tuple(b[r])
        return b

    def solve_helper(self, method, limit, moves, visited):
        if tuple(self.make_tuple()) not in visited or visited[tuple(self.make_tuple())] >= len(moves):
            visited[tuple(self.make_tuple())] = len(moves)
            if not self.is_solved() and (len(moves) if method == 'ids' else self.heuristic() + len(moves)) < limit:
                successors = self.successors()
                for successor in successors:
                    moves.append(successor[1])
                    temp = successor[0].solve_helper(method, limit, moves[:], visited)
                    if temp[0]:
                        return temp
                    moves.pop()
            return self.is_solved(), moves
        return False, []

    def solve(self, method):
        start = time.time()
        moves = []
        visited = {}
        times = [0, 0]
        if method == 'a*':
            min_heuristic = self.heuristic()
            times.append(time.time())
            print('Initial h-score: %d\n' % min_heuristic)
            pq = queue.PriorityQueue()
            pq.put((self.heuristic(), moves, self))
            while True:
                temp = pq.get()
                moves = temp[1]
                curr = temp[2]
                if not curr.is_solved():
                    for successor in curr.successors():
                        if tuple(successor[0].make_tuple()) not in visited:
                            visited[tuple(successor[0].make_tuple())] = 0
                            moves.append(successor[1])
                            if successor[0].heuristic() < min_heuristic:
                                min_heuristic = successor[0].heuristic()
                                times.append(time.time())
                                print('Minimum h-score decreased.')
                                print('New h-score: %d' % min_heuristic)
                                h_time = times[-1] - times[-2]
                                print('Time since last decrease: %.2f seconds\n' % h_time)
                            pq.put(((len(moves) + successor[0].heuristic()), moves[:], successor[0]))
                            moves.pop()
                else:
                    break

        else:
            limit = 0 if method == 'ids' else self.heuristic()
            if not self.is_solved():
                while True:
                    times.append(time.time())
                    ans = self.solve_helper(method, limit, moves, visited)
                    times.append(time.time())
                    d_runtime = times[-1] - times[-2]
                    try:
                        percent_increase = (times[-1] - times[-2]) * 100 / (times[-3] - times[-4]) - 100
                        print('Runtime for %s %d: %.2f seconds' % ('depth' if method == 'ids' else 'threshold', limit, d_runtime))
                        print('Runtime increase: ' + str(int(percent_increase)) + '%\n')
                    except ZeroDivisionError:
                        print('Runtime for %s %d: %.2f seconds' % ('depth' if method == 'ids' else 'threshold', limit, d_runtime))
                        print('Runtime increase: 0%\n')
                    if ans[0]:
                        moves = ans[1]
                        break
                    limit += 1

        total_runtime = time.time() - start
        print('Finished in %d:%02d:%02d' % (int(total_runtime / 3600), int(total_runtime / 60), int(total_runtime % 60)))
        return ' '.join(moves)

'''
c = Cube([[('w', 'r', 'g'), ('w', 'g'), ('w', 'g', 'o'), ('w', 'o'), ('w', 'o', 'b'), ('w', 'b'), ('w', 'r'), ('w', 'b', 'r')], 
[('y', 'o'), ('y', 'o', 'g'), ('y', 'g'), ('y', 'g', 'r'), ('y', 'r'), ('y', 'r', 'b'), ('y', 'b'), ('y', 'b', 'o')]])
'''

import time

DIRECTIONS = [
    (-1, -1),  # UP-LEFT
    (-1, 0),   # UP
    (-1, 1),   # UP-RIGHT
    (0, -1),   # LEFT
    (0, 1),    # RIGHT
    (1, -1),   # DOWN-LEFT
    (1, 0),    # DOWN
    (1, 1)     # DOWN-RIGHT
]

def in_bounds(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def valid_movements(board, player):
    opponent = -player
    valid_moves = []
    for x in range(8):
        for y in range(8):
            if board[x][y] != 0:
                continue
            for dx, dy in DIRECTIONS:
                i, j = x + dx, y + dy
                found_opponent = False
                while in_bounds(i, j) and board[i][j] == opponent:
                    i += dx
                    j += dy
                    found_opponent = True
                if found_opponent and in_bounds(i, j) and board[i][j] == player:
                    valid_moves.append((x, y))
                    break
    return valid_moves

# Matriz de valores posicionales 
POSITION_VALUES = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,  -1,  -1,  -1,  -1,  -2,  10],
    [  5,  -2,  -1,  -1,  -1,  -1,  -2,   5],
    [  5,  -2,  -1,  -1,  -1,  -1,  -2,   5],
    [ 10,  -2,  -1,  -1,  -1,  -1,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100]
]

# Patrones de esquinas y bordes
CORNERS = [(0, 0), (0, 7), (7, 0), (7, 7)]
X_SQUARES = [(1, 1), (1, 6), (6, 1), (6, 6)]
C_SQUARES = [(0, 1), (1, 0), (0, 6), (6, 0), (1, 7), (7, 1), (6, 7), (7, 6)]

def make_move(board, x, y, player):
    new_board = [row[:] for row in board]
    opponent = -player
    new_board[x][y] = player
    
    for dx, dy in DIRECTIONS:
        i, j = x + dx, y + dy
        flips = []
        
        while in_bounds(i, j) and new_board[i][j] == opponent:
            flips.append((i, j))
            i += dx
            j += dy
        
        if flips and in_bounds(i, j) and new_board[i][j] == player:
            for flip_x, flip_y in flips:
                new_board[flip_x][flip_y] = player
    
    return new_board

def count_pieces(board, player):
    count = 0
    for row in board:
        for cell in row:
            if cell == player:
                count += 1
    return count

def get_stable_pieces(board, player):
    stable = [[False] * 8 for _ in range(8)]
    
    # Las esquinas ocupadas son siempre estables
    for x, y in CORNERS:
        if board[x][y] == player:
            stable[x][y] = True
            
            # Expandir estabilidad a lo largo de los bordes
            # Horizontal
            if x == 0 or x == 7:
                for j in range(8):
                    if board[x][j] == player:
                        is_stable = True
                        # Verificar si todas las piezas entre la esquina y esta posición son del mismo jugador
                        start, end = min(y, j), max(y, j)
                        for k in range(start, end + 1):
                            if board[x][k] != player:
                                is_stable = False
                                break
                        if is_stable:
                            stable[x][j] = True
            
            # Vertical
            if y == 0 or y == 7:
                for i in range(8):
                    if board[i][y] == player:
                        is_stable = True
                        start, end = min(x, i), max(x, i)
                        for k in range(start, end + 1):
                            if board[k][y] != player:
                                is_stable = False
                                break
                        if is_stable:
                            stable[i][y] = True
    
    # Contar piezas estables
    count = sum(sum(row) for row in stable)
    return count

def evaluate_board(board, player):
    opponent = -player
    
    # 1. Diferencia de piezas (menos importante en apertura/medio juego)
    my_pieces = count_pieces(board, player)
    opp_pieces = count_pieces(board, opponent)
    total_pieces = my_pieces + opp_pieces
    

    if total_pieces < 20:  
        piece_weight = 0.1
    elif total_pieces < 45:  
        piece_weight = 0.3
    else:  
        piece_weight = 1.0
    
    piece_diff = piece_weight * (my_pieces - opp_pieces)
    
    # 2. Valor posicional
    position_score = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == player:
                position_score += POSITION_VALUES[x][y]
            elif board[x][y] == opponent:
                position_score -= POSITION_VALUES[x][y]
    
    # 3. Movilidad 
    my_moves = len(valid_movements(board, player))
    opp_moves = len(valid_movements(board, opponent))
    mobility_score = 0
    if my_moves + opp_moves != 0:
        mobility_score = 100 * (my_moves - opp_moves) / (my_moves + opp_moves)
    
    # 4. Control de esquinas 
    corner_score = 0
    for x, y in CORNERS:
        if board[x][y] == player:
            corner_score += 25
        elif board[x][y] == opponent:
            corner_score -= 25
    
    # 5. Penalización por X-squares si la esquina correspondiente está vacía
    for i, (x, y) in enumerate(X_SQUARES):
        corner_x, corner_y = CORNERS[i]
        if board[corner_x][corner_y] == 0:  
            if board[x][y] == player:
                corner_score -= 15
            elif board[x][y] == opponent:
                corner_score += 15
    
    # 6. Estabilidad
    my_stable = get_stable_pieces(board, player)
    opp_stable = get_stable_pieces(board, opponent)
    stability_score = 15 * (my_stable - opp_stable)
    
    # 7. Control de bordes
    edge_score = 0
    for i in range(8):
        # Bordes horizontales
        if board[0][i] == player:
            edge_score += 2
        elif board[0][i] == opponent:
            edge_score -= 2
        if board[7][i] == player:
            edge_score += 2
        elif board[7][i] == opponent:
            edge_score -= 2
        
        # Bordes verticales
        if board[i][0] == player:
            edge_score += 2
        elif board[i][0] == opponent:
            edge_score -= 2
        if board[i][7] == player:
            edge_score += 2
        elif board[i][7] == opponent:
            edge_score -= 2
    
    # Combinación ponderada de todas las características
    total_score = (
        piece_diff +
        position_score * 0.5 +
        mobility_score * 2.0 +
        corner_score * 3.0 +
        stability_score * 1.5 +
        edge_score * 0.8
    )
    
    return total_score

def minimax(board, depth, alpha, beta, maximizing_player, player, start_time):
    # Verificar tiempo límite (2.5)
    if time.time() - start_time > 2.5:
        return evaluate_board(board, player), None
    
    # Caso base: profundidad 0 o juego terminado
    if depth == 0:
        return evaluate_board(board, player), None
    
    current_player = player if maximizing_player else -player
    moves = valid_movements(board, current_player)
    
    # Si no hay movimientos válidos, pasar turno
    if not moves:
        other_moves = valid_movements(board, -current_player)
        if not other_moves:  
            score = count_pieces(board, player) - count_pieces(board, -player)
            return score * 1000, None  # Multiplicar por 1000 para priorizar victorias
        else:
            # Pasar turno
            value, _ = minimax(board, depth - 1, alpha, beta, not maximizing_player, player, start_time)
            return value, None
    
    best_move = None
    
    if maximizing_player:
        max_eval = float('-inf')
        # Ordenar movimientos por valor heurístico para mejor poda
        moves_with_scores = []
        for move in moves:
            new_board = make_move(board, move[0], move[1], current_player)
            quick_score = evaluate_board(new_board, player)
            moves_with_scores.append((quick_score, move))
        moves_with_scores.sort(reverse=True)
        
        for _, move in moves_with_scores:
            new_board = make_move(board, move[0], move[1], current_player)
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False, player, start_time)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  
        
        return max_eval, best_move
    else:
        min_eval = float('inf')
        # Ordenar movimientos para el oponente
        moves_with_scores = []
        for move in moves:
            new_board = make_move(board, move[0], move[1], current_player)
            quick_score = evaluate_board(new_board, player)
            moves_with_scores.append((quick_score, move))
        moves_with_scores.sort()  
        
        for _, move in moves_with_scores:
            new_board = make_move(board, move[0], move[1], current_player)
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True, player, start_time)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  
        
        return min_eval, best_move

def get_opening_move(board, player):
    # Contar piezas para determinar el número de movimiento
    total_pieces = sum(1 for row in board for cell in row if cell != 0)
    
    if total_pieces == 4:  
        # Movimientos de apertura preferidos
        opening_moves = [(2, 3), (3, 2), (4, 5), (5, 4)]
        valid = valid_movements(board, player)
        for move in opening_moves:
            if move in valid:
                return move
    
    return None

def ai_move(board, player):
    start_time = time.time()
    
    # Verificar movimientos válidos
    valid_moves = valid_movements(board, player)
    if not valid_moves:
        return None
    
    # Si solo hay un movimiento, tomarlo
    if len(valid_moves) == 1:
        return valid_moves[0]
    
    # Estrategia de apertura
    total_pieces = sum(1 for row in board for cell in row if cell != 0)
    if total_pieces <= 8:
        opening_move = get_opening_move(board, player)
        if opening_move:
            return opening_move
    
    # Priorizar esquinas si están disponibles
    for move in valid_moves:
        if move in CORNERS:
            return move
    
    # Determinar profundidad de búsqueda según fase del juego y tiempo disponible
    if total_pieces < 20:
        depth = 4
    elif total_pieces < 40:
        depth = 5
    elif total_pieces < 50:
        depth = 6
    else:
        depth = 8  # Endgame - buscar más profundo
    
    # Ajustar profundidad según número de movimientos posibles
    if len(valid_moves) > 10:
        depth = max(3, depth - 1)
    
    # Ejecutar Minimax con poda alfa-beta
    _, best_move = minimax(board, depth, float('-inf'), float('inf'), True, player, start_time)
    
    # Si minimax no encontró un movimiento (timeout), usar evaluación rápida
    if best_move is None:
        move_scores = []
        for move in valid_moves:
            new_board = make_move(board, move[0], move[1], player)
            score = evaluate_board(new_board, player)
            move_scores.append((score, move))
        
        move_scores.sort(reverse=True)
        best_move = move_scores[0][1]
    
    return best_move
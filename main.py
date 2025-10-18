import random
import sys

# ----------------------------------------------------
# 2048 游戏常量和初始化
# ----------------------------------------------------

# 棋盘大小
GRID_SIZE = 4 

def initialize_game():
    """初始化一个 4x4 的空白棋盘，并随机放置两个起始数字"""
    # 创建一个 4x4 的列表的列表，所有元素初始化为 0
    new_grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    
    # 随机放置两个数字 (90% 的几率是 2, 10% 的几率是 4)
    add_new_tile(new_grid)
    add_new_tile(new_grid)
    return new_grid

def add_new_tile(grid):
    """在随机的空位添加一个新的 2 或 4"""
    empty_cells = []
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == 0:
                empty_cells.append((r, c)) # 记录所有空位
    
    if empty_cells:
        # 随机选择一个空位
        r, c = random.choice(empty_cells)
        # 90% 几率放 2，10% 几率放 4
        grid[r][c] = 2 if random.random() < 0.9 else 4

def display_grid(grid):
    """打印当前棋盘状态"""
    # 找到最大的数字，用于格式化输出
    max_val = max(max(row) for row in grid)
    
    # 根据最大的数字计算输出宽度，确保对齐
    cell_width = len(str(max(2048, max_val))) + 2 

    print("\n" + "=" * (GRID_SIZE * (cell_width + 1) + 1))
    
    for row in grid:
        row_str = "|"
        for cell in row:
            # 格式化输出，如果数字是 0 就显示空格
            display_char = str(cell) if cell != 0 else ""
            row_str += f"{display_char:^{cell_width}}" + "|"
        print(row_str)
        print("-" * (GRID_SIZE * (cell_width + 1) + 1))
        
    print(f"得分: {get_score(grid)}")
    print("=" * (GRID_SIZE * (cell_width + 1) + 1))

def get_score(grid):
    """简单地用棋盘上所有数字的总和作为得分"""
    return sum(sum(row) for row in grid)

# ----------------------------------------------------
# 核心移动和合并逻辑
# ----------------------------------------------------

def merge_line(line):
    """处理单行/单列的合并和移动逻辑"""
    
    # 1. 移除所有的 0，只留下数字
    non_zero = [x for x in line if x != 0]
    
    # 2. 合并相同的数字
    merged = []
    skip = False
    for i in range(len(non_zero)):
        if skip:
            skip = False
            continue
        
        # 如果当前数字和下一个数字相同，则合并
        if i + 1 < len(non_zero) and non_zero[i] == non_zero[i+1]:
            merged.append(non_zero[i] * 2)
            skip = True
        else:
            # 不合并，直接加入
            merged.append(non_zero[i])
    
    # 3. 在末尾补上 0
    # 保证行/列长度不变，用 0 填充
    merged += [0] * (len(line) - len(merged))
    return merged

def move(grid, direction):
    """处理整个棋盘的移动"""
    
    # 复制当前棋盘，用于判断移动后是否有变化
    new_grid = [row[:] for row in grid]
    moved = False
    
    # 移动 UP 和 DOWN 需要按列操作
    if direction in ['UP', 'DOWN']:
        for c in range(GRID_SIZE):
            # 提取一列
            col = [new_grid[r][c] for r in range(GRID_SIZE)]
            
            # UP 相当于对列进行 merge_line
            if direction == 'UP':
                new_col = merge_line(col)
            # DOWN 相当于对反转的列进行 merge_line，然后再反转回来
            else: # 'DOWN'
                new_col = merge_line(col[::-1])[::-1]
            
            # 如果这一列有变化，标记为 moved
            if col != new_col:
                moved = True
            
            # 更新回棋盘
            for r in range(GRID_SIZE):
                new_grid[r][c] = new_col[r]
                
    # 移动 LEFT 和 RIGHT 需要按行操作
    elif direction in ['LEFT', 'RIGHT']:
        for r in range(GRID_SIZE):
            row = new_grid[r]
            
            # LEFT 相当于对行进行 merge_line
            if direction == 'LEFT':
                new_row = merge_line(row)
            # RIGHT 相当于对反转的行进行 merge_line，然后再反转回来
            else: # 'RIGHT'
                new_row = merge_line(row[::-1])[::-1]

            # 如果这一行有变化，标记为 moved
            if row != new_row:
                moved = True
                
            # 更新回棋盘
            new_grid[r] = new_row
            
    return new_grid, moved


# ----------------------------------------------------
# 游戏状态判断
# ----------------------------------------------------

def is_game_over(grid):
    """检查游戏是否结束：没有空格，且无法进行任何移动/合并"""
    
    # 1. 检查是否有 2048
    if any(2048 in row for row in grid):
        return True, "WIN"

    # 2. 检查是否有空位 (如果有空位，说明还能继续玩)
    if any(0 in row for row in grid):
        return False, None
    
    # 3. 检查是否可以进行任何合并 (横向和纵向)
    
    # 检查横向
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 1):
            if grid[r][c] == grid[r][c+1]:
                return False, None # 还能横向合并
                
    # 检查纵向
    for c in range(GRID_SIZE):
        for r in range(GRID_SIZE - 1):
            if grid[r][c] == grid[r+1][c]:
                return False, None # 还能纵向合并

    # 既没空位，也不能合并，则游戏失败
    return True, "LOSE"


# ----------------------------------------------------
# 主程序
# ----------------------------------------------------

def play_2048():
    """主游戏循环"""
    current_grid = initialize_game()
    
    print("-----------------------------------------")
    print("    欢迎来到命令行版 2048 游戏！")
    print("-----------------------------------------")
    print("操作： W (上), A (左), S (下), D (右), Q (退出)")

    while True:
        display_grid(current_grid)
        
        # 检查游戏状态
        game_over, status = is_game_over(current_grid)
        if game_over:
            if status == "WIN":
                print("🎉 恭喜你！你达到了 2048！你赢了！ 🎉")
            elif status == "LOSE":
                print("😢 游戏结束！你不能再移动了。 😢")
            break
            
        # 获取用户输入
        move_input = input("请输入你的操作 (W/A/S/D): ").upper()

        if move_input == 'Q':
            print("退出游戏。")
            break

        # 将 WASD 转换为移动方向
        direction_map = {'W': 'UP', 'A': 'LEFT', 'S': 'DOWN', 'D': 'RIGHT'}
        direction = direction_map.get(move_input)

        if direction:
            # 尝试进行移动
            new_grid, moved = move(current_grid, direction)
            
            if moved:
                current_grid = new_grid
                add_new_tile(current_grid) # 移动成功，则添加新方块
            else:
                print("这个方向没有方块可以移动或合并！请换个方向。\n")
        else:
            print("无效输入！请使用 W, A, S, D, 或 Q。\n")

if __name__ == "__main__":
    play_2048()

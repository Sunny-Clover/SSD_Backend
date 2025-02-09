from datetime import time

# region: BLL
ACCUMULATE_TIME_RANKS = [30, 60, 120, 360, 720, 1440]  # (分鐘) 自行定義
def calculate_user_level(total_minutes: int) -> int:
    """
    根據 total_minutes 在 ACCUMULATE_TIME_RANKS 裡找出對應的等級。
    回傳值範例：1 表示第一階、2 表示第二階...依需求調整。
    """
    for idx, threshold in enumerate(ACCUMULATE_TIME_RANKS, start=1):
        if total_minutes < threshold:
            return idx
    # 超過最大門檻就回傳 ranks + 1
    return len(ACCUMULATE_TIME_RANKS) + 1
def calculate_user_level_progress(total_minutes: int, level: int) -> float:
    """
    計算使用者當前等級的進度 (0 ~ 1 之間)。
    level = calculate_user_level(total_minutes)
    """
    # 若已經超過最大等級，就回傳 1
    if level == len(ACCUMULATE_TIME_RANKS) + 1:
        return 1.0
    
    if level == 1:
        # 第 1 等沒有下限 (0 分)，上限是 ACCUMULATE_TIME_RANKS[0]
        return total_minutes / float(ACCUMULATE_TIME_RANKS[0])
    
    # level > 1
    lower_bound = ACCUMULATE_TIME_RANKS[level - 2]  # 因為 start=1，多減 1
    upper_bound = ACCUMULATE_TIME_RANKS[level - 1]
    return (total_minutes - lower_bound) / float(upper_bound - lower_bound)

def time_to_minutes(t: time) -> int:
    """
    將 Python 的 time(hour, minute, second) 轉成「總分鐘數」。
    """
    return t.hour * 60 + t.minute
# enregion
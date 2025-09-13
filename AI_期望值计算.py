import numpy as np

def main():
    # 输入处理 - 支持多种奖励
    print("请输入各奖项数量（用空格分隔，例如：1 2 3 4 1 2 表示6种奖项）：")
    k = list(map(int, input().split()))
    num_awards = len(k)  # 动态确定奖项数量

    print(f"请输入对应{num_awards}种奖项的价值（用空格分隔）：")
    v = list(map(int, input().split()))

    print(
        f"请输入对应{num_awards}种奖项的名称（用空格分隔，其中'again'表示再来一次；输入'NA'自动生成不含again的名称；输入'HA'自动生成含again的名称）：")
    name_input = input().strip()

    # 自动生成名称逻辑
    if name_input == 'NA':
        # 自动生成不含again的名称：award1, award2, ..., awardN
        strmp = [f"award{i + 1}" for i in range(num_awards)]
    elif name_input == 'HA':
        # 自动生成含again的名称：前N-1个为award，最后一个为again
        if num_awards >= 1:
            strmp = [f"award{i + 1}" for i in range(num_awards - 1)] + ["again"]
        else:
            strmp = []
    else:
        # 使用用户输入的名称
        strmp = name_input.split()

    # 验证输入长度是否一致（自动生成模式跳过此验证）
    if name_input not in ['NA', 'HA'] and (len(v) != num_awards or len(strmp) != num_awards):
        print("错误：奖项数量、价值数量和名称数量必须一致！")
        return

    # 计算总数
    n = sum(k)
    print(f"\n各奖项数量: {k}")
    print(f"各奖项价值: {v}")
    print(f"各奖项名称: {strmp}")

    # 确定"再来一次"奖项的索引
    again_indices = [i for i, name in enumerate(strmp) if name == "again"]
    print(f"\n'再来一次'奖项索引: {again_indices}")

    # 计算"再来一次"的总数量和概率
    total_again = sum(k[i] for i in again_indices)
    p_again = total_again / n if n > 0 else 0
    print(f"抽中'再来一次'的总概率: {p_again}")

    # 计算每个有效奖项的概率（排除所有"再来一次"）
    total_valid = n - total_again
    if total_valid > 0:
        probabilities = [k[i] / total_valid if i not in again_indices else 0 for i in range(num_awards)]
        print(f"各奖项有效概率（排除再来一次）: {probabilities}")
    else:
        print("警告：没有有效奖项（全部为'再来一次'）")
        probabilities = [0] * num_awards

    # 计算理论期望值
    total_value = sum(k[i] * v[i] for i in range(num_awards) if i not in again_indices)

    if total_valid > 0:  # 避免除0错误
        qw1 = total_value / total_valid  # 理论期望值
    else:
        qw1 = 0

    print(f"\n理论期望值: {qw1}")
    print('-' * 50)
    print(f"总抽取项数: {n}")

    # 生成价值数组和奖项标识数组
    values = np.array([], dtype=np.int64)
    is_again = np.array([], dtype=bool)

    '''
    思路：转盘会有n个抽奖项（一个奖项可以分布多个抽奖项），目前有num_awards个奖项，就创立一个映射，把所有抽奖项（数字）分别对应到奖项
    例如，1个一等奖，1个二等奖，1个三等奖，4个幸运奖，1个再来一次，那就有8个抽奖项
        其中1->一等奖   2->二等奖  3->三等奖  4、5、6、7->幸运奖  8->再来一次
    然后随机抽取数字，找到对应的奖项名和价值，作为抽奖结果
    '''
    for j in range(num_awards):  # 循环所有奖项，不再固定为5种
        count = k[j]  # 第j项奖励的选项数
        values = np.append(values, np.full(count, v[j], dtype=np.int64))  # 构造前面提到的映射表，把数字与价值对应
        ''' np.full(count, v[j])：创建一个长度为count的数组，每个元素都是v[j]（当前奖项的价值）
        然后在values尾部添加这个列表
        例如：如果二等奖有 3 个，价值 5 元，就生成[5,5,5]
        再通过np.append把这个数组加入到总价值数组values中'''
        is_again = np.append(is_again, np.full(count, (strmp[j] == "again"), dtype=bool))  # 同样构造映射表，数字->是否再度抽奖
        '''strmp[j] == "again"：判断当前奖项是不是 "再来一次"（结果是 True/False）
        np.full(count, ...)：创建一个长度为count的布尔数组，全是 True 或 False
        例如：如果是 "again" 奖项，就生成[True, True, ...]（有多少张就有多少个 True）
        效果：给每张奖券打标签，标记它是否是 "再来一次" 奖券'''

    print('-' * 50)

    # 模拟抽奖
    yb = 10000000  # 样本量，1000万
    chunk_size = 1000000  # 每次抽这么多，100万
    total = 0  # 总价值
    processed = 0  # 算出来的数字数目

    while processed < yb:  # 还没抽完
        current_size = min(chunk_size, yb - processed)  # 取要选多少随机数
        rands = np.random.randint(0, n, size=current_size)  # （列表）0~n之间的整数随机数，取current_size个
        # 处理"再来一次"的情况
        mask = is_again[rands]  # （列表）抽到rands这多个数字，其中对应“再来一次”的数字就对应Ture，反之为False，是拷贝is_again[rands]
        remaining = np.sum(mask)  # 统计是Ture的数量，即要“再来一次”的数量

        while remaining > 0:  # 当还需要重抽时
            rands[mask] = np.random.randint(0, n, size=remaining)  # 重抽
            mask = is_again[rands]  # 标记
            remaining = np.sum(mask)  # 再统计
            '''这是 "再来一次" 机制的核心：抽中 "再来一次" 的奖券要重新抽，直到抽到有效奖券
            类比：就像现实中抽中 "再来一次" 后，机器会自动再出一张奖券，直到拿到有实际价值的奖品
            例如：第一次抽中 100 张 "再来一次"，就重新抽 100 张；如果新抽的里面还有 20 张 "再来一次"，就再抽 20 张，直到没有 "再来一次" 为止'''

        # 保证运行到这里，所有的奖券都不是再来一张了
        total += np.sum(values[rands])  # 加上这一轮，抽中的数字对应价值之和
        processed += current_size  # 增加这一轮算完的

    qw2 = total / yb  # 总价值/样本量，算期望值
    print(f"模拟平均值: {qw2}")


if __name__ == "__main__":
    main()

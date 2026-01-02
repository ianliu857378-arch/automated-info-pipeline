import numpy as np

# 训练数据
X = np.array([
    [10, 90, 95],  # 样本1
    [5, 70, 80],  # 样本2
    [15, 95, 90],  # 样本3
    [8, 80, 85]  # 样本4
])
y = np.array([85, 65, 92, 75])  # 成绩

# 初始化参数
w = np.array([0.0, 0.0, 0.0])
b = 0.0
alpha = 0.01  # 学习率
m = len(y)  # 样本数

# 梯度下降
for iteration in range(1000):
    # 1. 计算预测值
    predictions = np.dot(X, w) + b

    # 2. 计算误差
    errors = predictions - y

    # 3. 计算梯度
    gradient_w = (1 / m) * np.dot(X.T, errors)
    gradient_b = (1 / m) * np.sum(errors)

    # 4. 更新参数
    w = w - alpha * gradient_w
    b = b - alpha * gradient_b

    # 5. 计算成本（可选，用于监控）
    if iteration % 100 == 0:
        cost = (1 / (2 * m)) * np.sum(errors ** 2)
        print(f"迭代 {iteration}, 成本: {cost:.2f}")

print(f"\n最终参数:")
print(f"w = {w}")
print(f"b = {b:.2f}")

# 预测新学生的成绩
new_student = np.array([12, 85, 90])  # 12小时，85%作业，90%出勤
predicted_score = np.dot(w, new_student) + b
print(f"\n预测成绩: {predicted_score:.2f}")
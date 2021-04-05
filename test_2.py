from tools.LayerUtils.LogFileTool import LogFileTool

dataset = []

with open(r'M:\Sourcetree\input_data\test_3.txt', 'r') as f:
    for line in f.readlines():
        lines = line.split('\t')
        dataset.append(float(lines[1]))

ymax = max(dataset)
ymin = min(dataset)

print(ymax, ymin)
delta = 3
step = int((ymax - ymin) / delta)
res = []
for i in range(step + 1):
    res.append(0)
# print(step)

for point in dataset:
    z = int((point - ymin) // delta)
    # print(z)
    res[z] += 1
print(res)

# LogFileTool().writeToFile(res, r'M:\Sourcetree\output\test_3.txt')

res2 = []
k = 0
for k in range(len(res)):
    max5item = max([res[k-2] if k > 1 else 0, res[k-1] if k > 0 else 0, res[k], res[k+1] if k < len(res)-1 else 0, res[k+2] if k < len(res) - 2 else 0])
    res2.append(max5item)
print(res2)
LogFileTool().writeToFile(res2, r'M:\Sourcetree\output\test_4.txt')

res3 = res2

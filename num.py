arr = []
num = int(input("Enter No of Element = "))
for i in range(num):
    ele = int(input("Enter Element = "))
    arr.append(ele)
print("Smallest No = ",min(arr))
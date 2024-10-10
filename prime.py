def prime():
    num = int(input("Enter the Number = "))
    num2 = []
    for i in range(1,num):
        print(i)
        if num%i == 0:
            num2.append(num2)
    if len(num2)> 1 or num2 == 1 :
        print("Entered Number is Not Prime")
    else:
        print("Entered Number is  Prime")


prime()
def reverse(s):
    stra = ""
    for i in s:
        stra = i + stra
    return stra

s = input("Enter The String = ")

print("The original string is : ", end="")
print(s)

print("The reversed string is : ", end="")
print(reverse(s))
num2 = reverse(s)
if s == num2:
    var = {
        print("Palindrome")
    }
else:
    var = {
        print("Not Palindrome")
    }
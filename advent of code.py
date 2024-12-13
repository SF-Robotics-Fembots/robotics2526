def createLists():
    left = []
    right = []
    similarity = 0
    with open("advent_code.txt") as file: 
        lines = list(file.readlines())

    for index, line in enumerate(lines):
        lines[index] = line.strip("\n")

    for line in lines:
        one, two = line.split()
        left.append(int(one))
        right.append(int(two))

    left.sort()
    right.sort()
    
    for value in left:
        frequency = 0
        if value == right()

        
    
    print(sum)

   


createLists()
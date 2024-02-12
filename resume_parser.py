from RabotaUa import RobotaUaParser
from WorkUa import WorkUaParser


print('''What site do you want to use for searching? 
1 - robota.ua
2 - work.ua
For exit enter 0''')

num = input('Enter the number:\t')


def source_choice(number):
    while number not in ['0', '1', '2']:
        number = input('You enter wrong number! Please try again:\t')
    if number == '1':
        return RobotaUaParser()
    elif number == '2':
        return WorkUaParser()
    elif number == '0':
        exit()


parser = source_choice(num)
print(parser)
candidates = parser.parse()
# candidates = source_choice(source).parse()




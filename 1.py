import sys
import os
import json

class Data:
    def __init__(self, filename:str):
        self.filename = filename
        self.data1 = list()
        self.data2 = list()
        self.data3 = list()
        self.data4 = list()
        self.data5 = list()
        self.data6 = list()
        self.all_data = [self.data1, self.data2, self.data3, self.data4, self.data5, self.data6]
        self.list_of_departments = list()
        try:
            with open(filename, 'r') as file:
                for line in file:
                    rows= line.split(',')
                    self.data1.append(rows[0])
                    self.data2.append(rows[1])
                    self.data3.append(rows[2])
                    self.data4.append(rows[3])
                    self.data5.append(rows[4])
                    self.data6.append(rows[5].strip('\n'))
                        
            for data in self.all_data:
                if data[0]=='department':
                    self.department = list(data)
                if data[0]=='id':
                    self.id = list(data)
                if data[0]=='hours_worked':
                    self.hours_worked = list(data)
                if data[0]=='salary' or data[0]=='hourly_rate' or data[0]=='rate':
                    self.hourly_rate = list(data)
                if data[0]=='email':
                    self.email = list(data)
                if data[0]=='name':
                    self.name = list(data)
            self.list_of_departments = list(set(self.department))
            self.list_of_departments.remove('department')
            self.list_of_departments.sort()
            

        except FileNotFoundError:
            print("Ошибка: файл не найден")
        except  Exception as e:
            print(f"Ошибка: не удалось открыть файл или неверный формат. Ошибка {e}")
            sys.exit(1)
    
    def payout(self):
        width = [40,7,7,10]
        text = ['name','hours','rate','payout']
        print(f"{text[0]:^{width[0]}}{text[1]:^{width[1]}}{text[2]:^{width[2]}}{text[3]:^{width[3]}}")
        for department in self.list_of_departments:
            print(f"{department:-<64}")
            sum = 0
            for i in range(1, len(self.id)):
                if self.department[i] == department:
                    salary = int(self.hours_worked[i]) * int(self.hourly_rate[i])
                    sum+=salary
                    print(f"{self.name[i]:->{width[0]}}{self.hours_worked[i]:^{width[1]}}{self.hourly_rate[i]:^{width[2]}}{salary:>{width[3]}}")
            t_sum = f"Total: {sum}"
            print(f"{t_sum:>64}")
        self.create_payout_report()
    
    def create_payout_report(self):
        department_data_list = list()
        for department in self.list_of_departments:
            employees = list()
            sum = 0
            for i in range (1, len(self.id)):
                if self.department[i] == department:
                    employee={
                        "id": self.id[i],
                        "name": self.name[i],
                        "email":self.email[i],
                        "hours_worked": self.hours_worked[i],
                        "hourly_rate": self.hourly_rate[i],
                        "payout": int(self.hours_worked[i])*int(self.hourly_rate[i]),
                    }
                    employees.append(employee)
                    sum+= int(self.hours_worked[i])*int(self.hourly_rate[i])
            department_data = {
                "department": department,
                "employees": employees,
                "total:": sum
            }
            department_data_list.append(department_data)
        json_data = json.dumps(department_data_list, indent=4)
        with open(f"payout_report({self.filename}).json", "w") as file:
            file.write(json_data)
        print("Отчет о выплате зарплат создан.")




def main():
    args = sys.argv[1:]  

    if '--report' not in args:
        print("Ошибка: не указан параметр --report")
        sys.exit(1)

    report_index = args.index('--report')

    try:
        # Всё до --report
        csv_files = args[:report_index]
    except IndexError:
        print("Ошибка: перед --report должно быть указано имя файла")
        sys.exit(1)

    # Значение после --report
    try:
        report_types = args[report_index + 1:]
    except IndexError:
        print("Ошибка: после --report должно быть значение отчета")
        sys.exit(1)
    
    datas = list()
    for csv_file in csv_files:
        try:
            if os.path.isfile(csv_file):
                data = Data(csv_file)
                datas.append(data)
            else:   
                print(f"Ошибка: файл {csv_file} не существует. Данный файл пропускает формирование отчета.")
        except IndexError:
            sys.exit(1)
    
    for data in datas:
        for report_type in report_types:
            if report_type == 'payout':
                data.payout()
            else:
                print(f"Ошибка: неизвестный тип отчета {report_type}")
                sys.exit(1)



if __name__ == "__main__":
    main()
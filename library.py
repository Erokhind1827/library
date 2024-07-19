import argparse
import json
import io

parser = argparse.ArgumentParser()

# необходимый аргумент - функция, которую надо выполнить
parser.add_argument('function', type = str, choices = ['add', 'delete', 'find', 'display', 'change_status'], help = '\
Памятка: add -t -a -y, delete -i, find -t | -a | -y, display, change_status -i -s')

# необязательные аргументы - параметры функций (по названиям понятно)
parser.add_argument('-t', '--title', type = str, help = 'Название книги')
parser.add_argument('-a', '--author', type = str, help = 'Автор книги')
parser.add_argument('-y', '--year', type = int, help = 'Год издания книги')
parser.add_argument('-s', '--status', type = str, choices = ['В наличии', 'Выдана'], help = 'Статус книги',)
parser.add_argument('-i', '--id', type = int, help = 'Уникальный идентификатор книги')

# parser.usage('Приложение для управления библиотекой. Выберите, что вы хотите сделать, и всю необходимую информацию.')


class book(): # Класс книги

    current_id = 0

    def __init__(self, title, author, year): # Инициализация книги, id каждой следующей
        book.current_id += 1                 # добавленной книги на 1 больше предыдущей
        self.id = book.current_id
        self.title = title
        self.author = author
        self.year = year
        self.availability = True

    def to_dict(self): # Превращение книги в словарь, для записи в json
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "availability": self.availability
        }
    
    @classmethod              # Метод класса для считывания книги из json-файла,
    def from_dict(cls, data): # возвращает объект класса book
        book = cls(data["title"], data["author"], data["year"])
        if data["availability"] == False:
            book.availability = False
        book.id = data["id"]
        return book

class library(): # Класс библиотеки
    def __init__(self):
        try: # Если существует база всех книг, считываем книги оттуда
            with io.open("library.json", 'r') as json_file:
                data = json.load(json_file)
                self.books = [book.from_dict(book_data) for book_data in data]

        except: # Если базы нет, создаем пустой файл
            empty_data = {}
            with io.open("library.json", 'w') as json_file:
                json.dump(empty_data, json_file, indent= 4)
            self.books = []

    def add_book(self, title = 'NoName', author = 'Unknown', year = 1900): # Функция добавления
        new_book = book(title, author, year) # книги в библиотеку
        self.books.append(new_book) # добавляем книгу в список книг
        self.update_json() # Обновляем json-файл

    def delete_book(self, id = 0): # Функция удаления книги из базы
        for book in self.books:
            if book.id == id: # Если нашли книгу с таким id
                self.books.remove(book) # То удаляем
                self.update_json() # И обновляем базу
                return True
        return False # Возвращаем результаты поиска
    
    def display_books(self, books_for_search = ''): # Функция вывода книг, параметр books_for_search
        if books_for_search == '': # нужен для функции find (ниже), Если ничего не передается, выводятся все книги
            books_for_search = self.books
        book_count = 0
        for book in books_for_search: # Выводим информацию о всех книгах из списка
            book_count += 1
            print(f'id: {book.id}, title: {book.title}, author: {book.author}, year: {str(book.year)}, status: {"В наличии" if book.availability else "Выдана"}')
        if not book_count:
            print('В базе нет книг!') # Если таких книг нет, пишем это
            
    def update_book(self, id = 0, status = False): # Функция обновления статуса
        for book in self.books:
            if book.id == id:              # Если нашли книгу с данным id,
                book.availability = status # меняем ее статус на заданный
                self.update_json()
                return True
        return False # Возвращаем результат поиска
        
    
    def search_for_books(self, query = '', type_of_search = 't'): # Функция поиска книг
        match type_of_search: # type_of_seacrh задается в обработке запроса, есть три варианта
            case 'a': # поиск по автору
                self.display_books([book for book in self.books if book.author == query])
            case 'y': # по году издания
                self.display_books([book for book in self.books if book.year == query])
            case 't': # и по названию
                self.display_books([book for book in self.books if book.title == query])
            case _: # на всякий случай, не используется
                self.display_books() 

    def update_json(self): # Функция обновления базы
        with io.open("library.json", 'w') as json_file: # просто записываем все книги в виде словарей в json-файл
            json.dump([book.to_dict() for book in self.books], json_file, indent=4)


lib = library() # Создаем объект для работы с библиотекой

args: argparse.Namespace = parser.parse_args()

match args.function: # Смотрим, какая функция была выбрана

    case 'add': # Добавление
        if args.title and args.author and args.year: # Если все аргументы введены, то запускаем
            lib.add_book(title = args.title, author = args.author, year = args.year)
            print("Книга успешно добавлена")
        else: # Если нет, то выводим невведенные
            count = list(map(int, [1 - bool(args.title), 1 - bool(args.author), 1 - bool(args.year)])) # 1 если не ввели, 0 - если ввели
            print(f'Вы не ввели {(str(sum(count[:1])) + ") Имя книги" )if not args.title else ""} \
{str(sum(count[:2])) + ") Автора книги" if not args.author else ""} \
{str(sum(count)) + ") Год издания книги" if not args.year else ""} ') # Просто красивый вывод
            
    case 'delete': # Удаление
        res = lib.delete_book(id = args.id) # возвращаем результат удаления
        if res:
            print(f"Книга с id = {args.id} успешно удалена") # Все хорошо
        else:
            print("Книги с таким id нет в базе, либо вы не ввели id") # Все плохо

    case 'find': # Поиск 
        if args.title: # Смотрим, какой параметр ввели, если ввели несколько, то приоритет поиска 1) Название 2) Автор 3) Год. 
            type_of_search = 't' # (т.е. если ввели автора и год, поиск только по автору)
            lib.search_for_books(args.title, type_of_search)
        elif args.author:
            type_of_search = 'a'
            lib.search_for_books(args.author, type_of_search)
        elif args.year:
            type_of_search = 'y'
            lib.search_for_books(args.year, type_of_search)
        else:
            print("Вы не ввели ни одного критерия поиска")

    case 'display': # Отображение
        lib.display_books()

    case 'change_status': # Изменение статуса
        if args.status == 'В наличии':
            status = True
        else:
            status = False
        res = lib.update_book(id = args.id, status = status)
        if res:
            print('Книга успешно обновлена')
        else:
            print('Вы ввели несуществующий id')





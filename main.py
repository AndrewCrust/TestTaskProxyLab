import json
import os.path
import re
from sys import argv

__INNER_PARAMS = argv[1:]

__FILE_NAME = 'library.json'


class MyLibrary:
    """
    Класс представления Библиотеки.
    Для работы с Библиотекой используется консольный режим.
    Все команды приводятся при первом запуске приложения или при возникновении ошибки в команде.
    Структура файла Библиотеки:
    {'id_count': 0,
     'id_book': {'id_book1': {'book_attr': {'title': 'title',
                                            'author': 'author',
                                            'year': 'year'},
                              'status': 'status'
                              },
                 'id_book2': {'book_attr': {'title': 'title',
                                            'author': 'author',
                                            'year': 'year'},
                              'status': 'status'
                              }
                 },
     'author': {'author1': [1],
                'author2:': [2]
                },
     'year': {'year1': [2],
              'year2': [1]},
     'title': {'title': [1],
               'title2': [2]
               }
     }
    """

    __HELP = """
    Для работы с Библиотекой, введите команду в соответствии с инструкцией:

    Добавление книги:
        Введите название, автора и год разделенные "*"(пробелы у символа игнорируются) (Всего 3 аргумента).
        Пример: Герой нашего времени * Лермонтов Михаил Юрьевич * 2002

    Удаление книги:
        Введите символы "delite:" и число соответствующее книге в библиотеке, которую нужно удалить (Всего 1 аргумент).
        Пример: delite:15

    Поиск книги:
        Введите "find:" название, автора ИЛИ год одним отдельным аргументом (Всего 1 аргумент).
        Примеры: find:Герой нашего времени / Лермонтов Михаил Юрьевич / 2002

    Отображение всех книг:
        Введите "*" (Всего 1 аргумент).
        Пример: *

    Изменение статуса книги:
        Введите id книги и новый статус ("в наличии", "выдана")
            разделенные "*"(пробелы у символа игнорируются) (Всего 2 аргумента)
        Пример: 15:в наличии

    Для выхода из Библиотеки нажмите "Enter" не вводя никаких символов.
    """
    __STATUSES: tuple = ('выдана', 'в наличии')
    __FILE_TEMPLATE: dict = {'id_count': 0,
                             'id_book': {},
                             'author': {},
                             'year': {},
                             'title': {}
                             }

    def __init__(self, file_name: str):
        """
        При инициализации создается файл Библиотеки с переданным именем в текущей директории, если такого не было.
        :param file_name: Имя Библиотеки
        """
        self.__file_name = file_name
        if not os.path.exists(self.__file_name):
            self.__write_file(file_name=file_name, data=self.__FILE_TEMPLATE)

    def __call__(self, input_string: str) -> None:
        """
        При вызове экземпляра класса происходит вызов менеджера команд в соответствии с пользовательскими данными.
        :param input_string: Команда пользователя с данными.
        :return: None
        """
        self.__command_manager(command=input_string)

    def help(self):
        """
        Функция вызовы инструкции к Библиотеке.
        :return: Инструкция пользования Библиотекой в консольном режиме.
        """
        return self.__HELP

    @staticmethod
    def __write_file(file_name: str, data: dict) -> None:
        """
        Функция производит перезапись файла Библиотеки.
        :param file_name: Имя Библиотеки.
        :param data: Данные для записи в файл Библиотеки.
        :return: None
        """
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file)

    @staticmethod
    def __get_dict_obj(file_name: str) -> dict:
        """
        Получение и преобразование данных из файла Библиотеки.
        :param file_name: Имя Библиотеки.
        :return: Данные библиотеки в формате dict
        """
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    @staticmethod
    def __add_book(title: str, author: str, year: str, my_lib: dict) -> dict:
        """
        Добавляет запись в данные библиотеки.
        :param title: Название
        :param author: Автор
        :param year: Год издания
        :param my_lib: Данные библиотеки
        :return: Измененные данные Библиотеки в формате dict
        """
        title_ids = my_lib.get('title').get(title)
        if title_ids:
            for id_book in title_ids:
                book_attr = my_lib['id_book'][id_book]['book_attr'].values()
                if set(book_attr) == {title, author, year}:
                    my_lib['id_book'][id_book]['status'] = 'в наличии'
                    return my_lib

        my_lib['id_count'] += 1
        id_book = str(my_lib['id_count'])
        my_lib['id_book'][id_book] = {'book_attr': {'title': title,
                                                    'author': author,
                                                    'year': year},
                                      'status': 'в наличии'
                                      }
        for key, value in my_lib['id_book'][id_book]['book_attr'].items():
            my_lib.get(key).setdefault(value, []).append(id_book)

        return my_lib

    @staticmethod
    def __remove_book(id_book: str, my_lib: dict) -> dict:
        """
        Удаляет библиотеку по указанному уникальному номеру.
        :param id_book: Уникальный номер книги
        :param my_lib: Данные библиотеки
        :return: Измененные данные Библиотеки в формате dict
        """
        book = my_lib['id_book'].pop(id_book, None)
        if book:
            for key, value in book['book_attr'].items():
                ids_list = my_lib[key][value]
                ids_list.remove(id_book)
                if not ids_list:
                    my_lib[key].pop(value, None)

        return my_lib

    @staticmethod
    def __show_book(id_book, my_lib: dict) -> None:
        """
        Выводит в консоль данные о книге по уникальному номеру
        :param id_book: Уникальный номер книги
        :param my_lib: Данные библиотеки
        :return: None
        """
        book = my_lib['id_book'][id_book]
        title = book['book_attr']['title']
        author = book['book_attr']['author']
        year = book['book_attr']['year']
        status = book['status']
        print(f'id: {id_book} * title: {title} * author: {author} * year: {year} * status: {status}')

    @staticmethod
    def __find_book(value: str, my_lib: dict) -> None:
        """
        Производит поиск и выводит в консоль возможно имеющиеся книги по переданному значению.
        :param value: Значение от пользователя для поиска
        :param my_lib: Данные библиотеки
        :return: None
        """
        for key in my_lib:
            if key == 'id_count':
                continue

            data = my_lib[key].get(value, None)
            if data:
                for id_book in data:
                    MyLibrary.__show_book(id_book=id_book, my_lib=my_lib)

    @staticmethod
    def __show_all_book(my_lib: dict) -> None:
        """
        Выводит содержание библиотеки в консоль.
        :param my_lib: Данные библиотеки
        :return: None
        """
        for id_book, in my_lib['id_book']:
            MyLibrary.__show_book(id_book=id_book, my_lib=my_lib)

    @staticmethod
    def __set_status(id_book, status, my_lib: dict) -> dict:
        """
        Устанавливает статус книги в соответствии с данными пользователя по уникальному номеру книги.
        :param id_book: Уникальный номер книги
        :param status: Статус книги
        :param my_lib: Данные библиотеки
        :return: Измененные данные Библиотеки в формате dict
        """
        my_lib['id_book'][id_book]['status'] = status
        return my_lib

    def __send_error(self, string: str) -> None:
        """
        Выводит сообщение в консоль о некорректных данных в команде пользователя.
        Выводит инструкцию в консоль.
        :param string: Команда пользователя
        :return: None
        """
        print(f'Аргументы ---{string}--- не подходят для выполнения команды\n{self.help()}')

    def __command_manager(self, command: str) -> None:
        """
        Передает данные для излечения или изменения данных Библиотеки в соответствующие функции обработки.
        :param command: Команда пользователя
        :return: None
        """
        my_lib = self.__get_dict_obj(self.__file_name)

        if re.match(r'^.+\s*\*\s*(?:[a-zа-я][\-a-zа-я]*\s*)+\s*\*\s*(?:20(?:[10][0-9]|2[01234])|1?\d{1,3})$',
                    command.lower().strip('* ')):
            title, author, year = map(lambda s: s.strip(), command.strip('* ').split('*'))
            author = author.title()
            print(f"Добавление книги: {title} * {author} * {year}")
            my_lib = self.__add_book(title=title, author=author, year=year, my_lib=my_lib)
            self.__write_file(self.__file_name, data=my_lib)

        elif re.match(r'^delite:\s*\d+$', command.strip()):
            id_book = command.split(':')[1].strip()
            print(f"Удаление книги номер: {id_book}")
            my_lib = self.__remove_book(id_book=id_book, my_lib=my_lib)
            self.__write_file(self.__file_name, data=my_lib)

        elif re.match(r'^find:.+$', command.strip()):
            value = command.split(':')[1].strip()
            print(f"Поиск книг по значению: {value}")
            self.__find_book(value=value, my_lib=my_lib)

        elif re.match(r'^\*$', command.strip()):
            print('Библиотека содержит:')
            self.__show_all_book(my_lib=my_lib)

        elif re.match(r'^\d+:\s*(?:в наличии|выдана)$', command.strip()):
            id_book, status = map(lambda s: s.strip(), command.split(':'))
            print(f'Установка статуса {status} книги {id_book}')
            my_lib = self.__set_status(id_book=id_book, status=status, my_lib=my_lib)
            self.__write_file(self.__file_name, data=my_lib)

        else:
            self.__send_error(string=command)


if __name__ == '__main__':
    if __INNER_PARAMS:
        print('Запуск приложения строго без аргументов')
        exit()

    library = MyLibrary(file_name=__FILE_NAME)
    print(library.help())
    while True:
        user_command = input()
        if not user_command:
            break

        library(user_command)

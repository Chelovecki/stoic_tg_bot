import os.path
import json


from PyPDF2 import PdfReader


def get_week_topic_as_jpeg(path_to_save: str, num_page: int):
    import fitz
    pdffile = 'Дневник_стоика_366_вопросов_к_себе_1.pdf'
    with fitz.open(pdffile) as doc:
        page = doc.load_page(num_page - 1)  # number of page
        pix = page.get_pixmap()
        output = os.path.join('weeks_images', "outfile.png")
        pix.save(path_to_save)


def write_in_json(name_and_path, dictionary):
    with open(name_and_path, 'w+', encoding='UTF-8') as file:
        json.dump(dictionary, file, ensure_ascii=False, indent=4)




def read_from_json(name_and_path):
    filel = open(name_and_path, 'r', encoding='UTF-8')
    dictionary = json.load(filel)
    filel.close()
    return dictionary

questionss = read_from_json('res.json')

weeks = read_from_json('week_path_images.json')

book_info = {}

# new_dict = {}
# for key, value in questionss:
#     new_key = f'week_{key}'
#     new_dict[new_key] = value
# write_in_json('res.json', new_dict)

# for week, list_path in weeks.items():
#     book_info[week] = {}
#     book_info[week]['path'] = list_path
#     book_info[week]['questions'] = {}
#
#     for number_week, questions in questionss.items():
#         counter = 0
#         if number_week == week:
#             for question in questions:
#                 counter += 1
#                 book_info[week]['questions'][str(counter)] = question
#
#
# write_in_json('db/book_info.json', book_info)


user_info = {'id_user': None,
             'cur_week': None,
             'cur_day': None,}
for week in range(1, 53):
    print(week)
    user_info[week] = {}
    for day in range(1, 8):
        user_info[week][day] = {'morning': None,
                                 'evening': None}
write_in_json(os.path.join('db', 'user_scale.json'), user_info)






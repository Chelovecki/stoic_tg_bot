import os.path
import json


from PyPDF2 import PdfReader


def get_week_topic_as_jpeg(path_to_save: str, num_page: int):
    import fitz
    pdffile = 'Дневник_стоика_366_вопросов_к_себе_1.pdf'
    with fitz.open(pdffile) as doc:
        page = doc.load_page(num_page - 1)  # number of page
        pix = page.get_pixmap()
        output = os.path.join('week_images', "outfile.png")
        pix.save(path_to_save)



def write_in_json(name_and_path, dictionary):
    with open(name_and_path, 'w+', encoding='UTF-8') as file:
        json.dump(dictionary, file, ensure_ascii=False, indent=4)


week_nums = {'week_1': [15, 16], 'week_2': [22], 'week_3': [28], 'week_4': [34], 'week_5': [40, 41], 'week_6': [47], 'week_7': [53], 'week_8': [59], 'week_9': [65], 'week_10': [71], 'week_11': [77], 'week_12': [83], 'week_13': [89, 90], 'week_14': [96, 97], 'week_15': [103, 104], 'week_16': [110], 'week_17': [116, 117], 'week_18': [123], 'week_19': [129, 130], 'week_20': [136], 'week_21': [142, 143], 'week_22': [149], 'week_23': [155, 156], 'week_24': [162], 'week_25': [168], 'week_26': [174, 175], 'week_27': [181], 'week_28': [187], 'week_29': [193, 194], 'week_30': [200, 201], 'week_31': [207, 208], 'week_32': [214], 'week_33': [220], 'week_34': [226, 227], 'week_35': [233], 'week_36': [239, 240], 'week_37': [246], 'week_38': [252, 253], 'week_39': [259], 'week_40': [265], 'week_41': [271], 'week_42': [277], 'week_43': [283], 'week_44': [289], 'week_45': [295], 'week_46': [301], 'week_47': [307, 308], 'week_48': [314, 315], 'week_49': [321, 322], 'week_50': [328, 329], 'week_51': [335, 336], 'week_52': [342, 343]}


def read_from_json(name_and_path):
    filel = open(name_and_path, 'r', encoding='UTF-8')
    dictionary = json.load(filel)
    filel.close()
    return dictionary


dict_for_weeks = {}
for week, pages in week_nums.items():
    dict_for_weeks[week] = []
    for number, page in enumerate(pages):
        path_image = os.path.join("week_images", f"{week} photo_{number + 1}.png")
        get_week_topic_as_jpeg(path_to_save=path_image, num_page=page)
        dict_for_weeks[week].append(path_image)
print(dict_for_weeks)





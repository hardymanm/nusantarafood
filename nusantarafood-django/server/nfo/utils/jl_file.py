import json


def get_by_keys(input_dict, keys):
    for key in keys:
        if key in input_dict.keys():
            return input_dict[key]

    raise Exception('Keyerror:', ','.join(keys))


def flatten_list(contents):
    output = []
    if type(contents) == list:
        for content in contents:
            output += flatten_list(content)
            
    else:
        content = contents.strip()
        if len(content):
            output.append(content)
        
    return output


class JlFile:
    @staticmethod
    def load(filename):
        web_pages = []
        with open(filename, 'r') as file_input:
            json_txt = file_input.readline()
            i = 0
            while json_txt:
                page = json.loads(json_txt)

                title = get_by_keys(page, ['title', 'list_item_title', 'Page_title', 'Page_Title'])
                url = get_by_keys(page, ['list_item_url', 'link', 'URL'])
                content = get_by_keys(page, ['page_description', 'Page_description'])

                web_pages.append({'title': title, 'content': ' '.join(flatten_list(content)), 'url': url})
                
                json_txt = file_input.readline()
                
        return web_pages

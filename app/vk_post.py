import requests
import time

GROUP_ID = '-180742715'
API_VERSION = '5.92'
ACCESS_TOKEN = open('app/token', 'r').read().strip()



class PostWall:
    owner_id = None
    access_token = None
    api_v = None

    def __init__(self, owner_id, access_token, api_v):
        self.owner_id = owner_id
        self.access_token = access_token
        self.api_v = api_v

    def get_server_time(self):
        r = requests.post('https://api.vk.com/method/utils.getServerTime', {'v': self.api_v,
                                                                            'access_token': self.access_token}).json()

        return r.get('response', int(time.time()))

    def post_on_wall(self, message, attachments, publish_date, guid):
        temp_list = []
        if attachments:
            for photo in attachments:
                link = self.get_photo_link(photo)
                temp_list.append('photo{}_{},'.format(link['response'][0]['owner_id'], link['response'][0]['id']))
        attachments = ''.join(temp_list)[:-1]
        r = requests.post('https://api.vk.com/method/wall.post', {'owner_id': self.owner_id,
                                                                  'access_token': self.access_token,
                                                                  'v': self.api_v,
                                                                  'message': message,
                                                                  'attachments': attachments,
                                                                  'publish_date': publish_date,
                                                                  'guid': guid
                                                                  }).json()

        if r.get('error'):
            return r['error']['error_msg']
        return 'ok'

    def get_upload_url(self):
        r = requests.post('https://api.vk.com/method/photos.getWallUploadServer', {'group_id': self.owner_id[1:],
                                                                                   'access_token': self.access_token,
                                                                                   'v': self.api_v,
                                                                                   }).json()
        if r.get('error'):
            return r['error']['error_msg']
        return r['response']['upload_url']

    def get_photo_link(self, image_path):
        upload_url = self.get_upload_url()
        image_file = {}
        try:
            image_file['photo'] = open(image_path, 'rb')
        except FileNotFoundError:
            pass

        r = requests.post(upload_url, files=image_file).json()
        r = requests.post('https://api.vk.com/method/photos.saveWallPhoto', {'server': r['server'],
                                                                             'group_id': self.owner_id[1:],
                                                                             'access_token': self.access_token,
                                                                             'v': self.api_v,
                                                                             'photo': r['photo'],
                                                                             'hash': r['hash']
                                                                             }).json()
        if r.get('error'):
            return r['error']['error_msg']
        return r

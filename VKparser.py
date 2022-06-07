import vk
import json

class VkParser:

    def __init__(self, token):
        self.token = token
        self.session = vk.Session(access_token=token)
        self.vk_api = vk.API(self.session)

    def get_last_post(self, group_id):
        posts = self.vk_api.wall.get(owner_id=f'-{group_id}', v=5.131)

        text_of_first_post = None

        for post in posts['items']:
            if (post['text'] != '' and len(post['text']) > 20 and post['owner_id'] == post['from_id']):
                text_of_first_post = post['text']
                if len(text_of_first_post) > 3000:
                    text_of_first_post = text_of_first_post[:2500]+f"...\nЧитать дальше vk.com/club{group_id}?w=wall-{group_id}_{post['id']}%2Fall"
                break

        return text_of_first_post

        #try:
        #    URLs_of_photos_of_first_post = [photo['url'] for photo in posts['response']['items'][0]['attachments'] if ]
        #except Exception:
        #    text_of_first_post = None

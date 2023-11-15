import os
import asyncio
import json

from pytube import Playlist
from googleapiclient.discovery import build
from notion_client import AsyncClient
from tqdm import tqdm

def get_properties_string(title, thumbnail_url, video_id, parent_id, index):
    result = {
            "Title": {
                "type": "title",
                "title": [{ "type": "text", "text": { "content": title}}]
            },
            "Thumbnail":
            {
                "files": [
                    {
                        "name": title,
                        "external": {
                            "url": thumbnail_url
                        }
                    }
                ]
            },
            "URL":
            {
                "url": f"https://www.youtube.com/watch?v={video_id}"
            },
            "Courses":
             {
                 "relation":
                 [
                     {
                         "id": parent_id
                     }
                 ]
             },
            "SeqNum":
            {
                "number": index
            }
        }
    return result
    
def get_properties_from_youtube_video(api_key, video, parent_id, seq_num):
    youtube = build('youtube', 'v3', developerKey=api_key)

    properties = []

    video_id = video.split('v=')[1]

    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )

    response = request.execute()
    item = response['items'][0]
    return get_properties_string(
                title=item['snippet']['title'],
                thumbnail_url=item['snippet']['thumbnails'].get('high', item['snippet']['thumbnails'].get('medium', item['snippet']['thumbnails'].get('default', {}))).get('url', ''),
                video_id=video_id,
                parent_id=parent_id,
                index=seq_num
            )


def get_properties_from_youtube_playlist(api_key, playlist, parent_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    playlist_id = playlist.playlist_url.split('list=')[1]

    request = youtube.playlistItems().list(
        part='snippet',
        maxResults=100,  # You can increase this number for more results per request.
        playlistId=playlist_id
    )

    properties = []

    total_items = request.execute()['pageInfo']['totalResults']
    with tqdm(total=total_items, desc=f"Getting playlist {playlist.title} from YouTube") as pbar:
        while request:
            response = request.execute()
            for index,item in enumerate(response['items']):
                properties.append(
                    get_properties_string(
                        title=item['snippet']['title'],
                        thumbnail_url=item['snippet']['thumbnails'].get('high', item['snippet']['thumbnails'].get('medium', item['snippet']['thumbnails'].get('standard', item['snippet']['thumbnails'].get('default', {})))).get('url', 'https://img.freepik.com/premium-vector/default-image-icon-vector-missing-picture-page-website-design-mobile-app-no-photo-available_87543-11093.jpg?w=1800'),
                        video_id=item['snippet']['resourceId']['videoId'],
                        parent_id=parent_id,
                        index=index + 1
                    )
                )
                pbar.update(1)

            request = youtube.playlistItems().list_next(request, response)

    return properties

async def add_page_to_notion_database(client, database_id, properties):
    res = await client.pages.create(
            parent={"database_id" : f"{database_id}"},
            properties=properties)
    return res

async def add_playlists_to_notion(api_key, client, config):
    properties_list = []
    for playlist in config["playlists"]:
        playlist_object = Playlist(playlist["url"])
        page = await add_page_to_notion_database(
            client=client,
            database_id=config["databases"][0]["database_id"],
            properties= {
                "Title":
                    {
                        "type": "title",
                        "title": [{ "type": "text", "text": { "content": playlist_object.title}}]
                    },
                "URL":
                    {
                        "url": playlist_object.playlist_url
                    }
            }
        )

        properties_list = get_properties_from_youtube_playlist(api_key=api_key,
                                                  playlist=playlist_object,
                                                  parent_id=page['id'])
 
    for index,video in enumerate(config["videos"]["urls"]):
        properties_list.append(
            get_properties_from_youtube_video(
                api_key=api_key,
                video=video,
                parent_id=config["videos"]["page_id"],
                seq_num=index+1
            )
        )

    with tqdm(total=len(properties_list), desc=f"Uploading to Notion") as pbar:
        for properties in properties_list:
            await add_page_to_notion_database(
                client=client,
                database_id=config["databases"][1]["database_id"],
                properties=properties
            )
            pbar.update(1)

        
api_key = os.environ["API_KEY"]
notion_token = os.environ["NOTION_TOKEN"]

with open('config.json', 'r') as file:
    config = json.load(file)
notion = AsyncClient(auth=notion_token)

async def main():
    await add_playlists_to_notion(api_key=api_key, client=notion, config=config)

if __name__ == "__main__":
    asyncio.run(main())
### 🐍 NotionTube
Python script, that connects YouTube and Notion.
Helps to transfer educational playlists and videos from YouTube to Notion databases, where each playlist represents the *Course* and each video in the playlist is the *Lesson*.

*Steps to get going*:

- Set up a project in the Google Cloud Console and enable YouTube Data API v3. Create API credentials and obtain the `API_KEY`.
    
    [https://console.cloud.google.com/welcome](https://console.cloud.google.com/welcome?project=yt-for-notion)
    
- Create two **separate** databases in Notion allegedly named *Courses* and *Lessons* (full Notion templates are in the works). Copy database ids to `config.json`
    
    ```json
    "databases":
    		[
    			{
    				"name": "Courses",
    				"database_id": "<your-data-base_id-1>"
    			},	
    			{
    				"name": "Lessons",
    				"database_id": "<your-data-base_id-2>"
    			}
    		]
    ```
    
- Create new Notion connection and obtain the `NOTION_TOKEN`. Connect each database to the newly created connection.
- Add your desired playlists *or/and* videos to `config.json`
    
    ```json
    "playlists":
    		[
    			{
    				"name": "C Programming",
    				"url": "https://youtube.com/playlist?list=PLnpfWqvEvRCchcCM-373x2630drhtdWEw&si=NbqBe_L1VD2TiF2b"
    			}
    		],
    "videos":
    	{
    		"page_id": "ba096c867247474eb2d56bb27e366bd0",
    		"urls":
    			[
    				"https://www.youtube.com/watch?v=sZ8GJ1TiMdk",
    				"https://www.youtube.com/watch?v=Xd_qsKEuazo",
    				"https://www.youtube.com/watch?v=o-k3xgV0oBE",
    				"https://www.youtube.com/watch?v=443UNeGrFoM",
    				"https://www.youtube.com/watch?v=XS2JddPq7GQ",
    				"https://www.youtube.com/watch?v=St0MNEU5b0o",
    				"https://www.youtube.com/watch?v=pIzaZbKUw2s"
    			]
    	}
    ```
    
    , where `page_id` is the *id* of the page, manually created inside *Courses* database. It is designated to place all *standalone* videos under one *Course*.
    
    *Limitations: this version of code is not protected against duplication, hence if you add the same link in `config.json` all over again it will be added to Notion databases the same number of times.*
    
- Install Python dependencies.
    
    ```python
    pip install google-api-python-client
    pip install pytube
    pip install notion-client
    pip install tqdm
    ```
    
- Add `API_KEY` and `NOTION_TOKEN` to the environment.
    
    ```python
    export API_KEY=YOUR_API_KEY
    export NOTION_TOKEN=YOUR_NOTION_TOKEN
    ```
    
- Run the script.
    
    ```bash
    python3 courier.py
    ```
from flask import Flask, render_template, request, jsonify, send_file, make_response
import youtube_dl
import json
from datetime import datetime
import requests
import random
import re
from pytube import YouTube
import subprocess
from bs4 import BeautifulSoup


def links(link):
  url = "https://vidthumbnail.com/facebook/download"

  payload = {'videoUrl': str(link)}

  response = requests.post(url, data=payload)
  soup = BeautifulSoup(response.content, "html.parser")
  h4_element = soup.find('h4', class_='text-center mb-4').text
  img_element = soup.find(
    'img', class_='img-fluid facebook mx-auto d-block border rounded mb-4')

  img_src = img_element['src']
  return [h4_element, img_src]


app = Flask(__name__)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
  link = request.form['url'].replace("m.facebook.com", "facebook.com")
  link = link.strip()
  dic = {}
  try:
    ydl = youtube_dl.YoutubeDL({
      'outtmpl': '%(title)s.%(ext)s',
      'quiet': True,
      'no_warnings': True
    })
    with ydl:
      result = ydl.extract_info(str(link), download=False)
    if 'entries' in result:
      video = result['entries'][0]['formats']
    else:
      video = result

    try:
      timestamp = result['entries'][0]['timestamp']
      date = datetime.fromtimestamp(timestamp)
      uploadt = date.strftime("%d %B %Y, %I:%M:%S %p")

    except Exception as e:

      uploadt = "NA"
      pass
    try:
      total_seconds = float(result['entries'][0]['duration'])

      hours = int(total_seconds / 3600)
      minutes = int((total_seconds % 3600) / 60)
      seconds = int(total_seconds % 60)

      time_components = []
      if hours > 0:
        time_components.append(f"{hours} hours")
      if minutes > 0:
        time_components.append(f"{minutes} minutes")
      if seconds > 0:
        time_components.append(f"{seconds} seconds")

      duration = ", ".join(time_components)
    except Exception as e:

      duration = "NA"
      pass

    if 'entries' in result:
      for i in video:
        if i['format_id'] == "hd":
          dic['HD'] = [i["ext"], str(i['url']) + "&dl=1"]
        elif i['format_id'] == "sd":
          dic['SD'] = [i["ext"], str(i['url']) + "&dl=1"]
        elif i['ext'] == "m4a":
          dic['AUDIO'] = [i["ext"], str(i['url']) + "&dl=1"]
    else:
      form = "Video"
      if video['format_id'] == "0":
        form = "SD"
      elif video['format_id'] == "1":
        form = "HD"

      dic['url'] = [video['url'] + "&dl=1", form]

    try:
      x = links(link)
      print(x)
      head = x[0]
    except:
      x = ["videoplayback", "/viderror.gif"]
      head = "videoplayback"

    if len(x) == 2:
      if len(x[0]) > 60:
        head = head[:60] + "..."
      return render_template('download.html',
                             video_dict=dic,
                             header=head,
                             image=x[1],
                             duration=duration,
                             uploadt=uploadt)
    else:
      return render_template('download.html',
                             video_dict=dic,
                             header="videoplayback",
                             image="/vid.jpg",
                             duration=duration,
                             uploadt=uploadt)
  except Exception as e:
    lis = ['sorry', 'tired', 'sweat', 'confused', 'nervous', 'sigh']
    x = requests.get("https://api.otakugifs.xyz/gif?reaction={}".format(
      random.choice(lis)))
    link = json.loads(x.text)['url']

    return render_template('downloaderror.html', video_dict=dic, errl=link)


@app.route('/udvash')
def udvash():
  return render_template('udvash.html')


@app.route('/udvasdown', methods=['POST'])
def udvasdown():
  text = request.form.get('code')
  text = str(text)

  soup = BeautifulSoup(text, 'html.parser')
  source_tag = soup.find('source')

  vv = ""
  if source_tag:
    src_value = source_tag['src']
    vv = src_value

  title = "Udvash"
  h4_tags = soup.find_all('h4', class_="mb-lg-0 mb-2")
  for h4_tag in h4_tags:
    title = h4_tag.text
  if len(vv)<=0:
    pattern = r"let videoId = '([^']*)';"

    # Search for the videoId using the regular expression
    match = re.search(pattern, text)

    if match:
        video_id = match.group(1)
        video_url = "https://www.youtube.com/watch?v="+video_id

        # Creating a YouTube object
        yt = YouTube(video_url)

        # Getting the direct download URL of the video
        video = yt.streams.get_highest_resolution()
        vv = video.url
    else:
        vv=""
        print("Video ID not found in the JavaScript code.")

  return render_template('udvashins.html',
                         link=vv,
                         title=title,
                         filename=title.replace(" ", "_"))


@app.route('/download')
def download_file():
  file_url = request.args.get('fileUrl')

  if file_url:
    try:
      response = requests.get(file_url, stream=True)

      # Check if the request was successful
      if response.status_code == 200:
        # Extract the filename from the URL
        filename = file_url.split('/')[-1]

        # Create a response with the file data
        file_data = response.content
        response = make_response(file_data)
        response.headers[
          'Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-Type'] = response.headers['Content-Type']

        return response

      else:
        return f'Error downloading file. Status code: {response.status_code}'

    except requests.exceptions.RequestException as e:
      return f'Error downloading file: {str(e)}'
  else:
    return "The 'fileUrl' parameter is not provided."


if __name__ == '__main__':
  app.run(host="0.0.0.0")

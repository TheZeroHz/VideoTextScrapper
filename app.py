from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import os
import speech_recognition as sr
from pydub import AudioSegment
import json
import time
import yt_dlp
import re

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def parse_vtt_file(vtt_path):
    """Parse VTT subtitle file and extract text with timestamps merged into segments"""
    transcriptions = []
    
    try:
        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by double newlines to get cue blocks
        blocks = content.split('\n\n')
        
        raw_captions = []
        
        for block in blocks:
            lines = block.strip().split('\n')
            
            # Skip WEBVTT header and NOTE blocks
            if len(lines) < 2 or lines[0].startswith('WEBVTT') or lines[0].startswith('NOTE'):
                continue
            
            # Look for timestamp line (format: 00:00:00.000 --> 00:00:05.000)
            timestamp_line = None
            text_lines = []
            
            for i, line in enumerate(lines):
                if '-->' in line:
                    timestamp_line = line
                    # Everything after timestamp is text
                    text_lines = lines[i+1:]
                    break
            
            if timestamp_line and text_lines:
                # Extract start time
                start_time = timestamp_line.split('-->')[0].strip()
                
                # Convert HH:MM:SS.mmm to total seconds
                time_parts = start_time.split(':')
                if len(time_parts) >= 3:
                    hours = int(time_parts[0])
                    minutes = int(time_parts[1])
                    seconds = float(time_parts[2])
                    
                    total_seconds = hours * 3600 + minutes * 60 + seconds
                else:
                    total_seconds = 0
                
                # Join text lines and remove HTML tags
                text = ' '.join(text_lines)
                text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
                text = text.strip()
                
                if text:
                    raw_captions.append({
                        'seconds': total_seconds,
                        'text': text
                    })
        
        # Merge captions into 30-second blocks
        if not raw_captions:
            return []
        
        segment_duration = 30  # 30 seconds per segment
        current_segment = {
            'start_seconds': 0,
            'texts': []
        }
        
        for caption in raw_captions:
            caption_time = caption['seconds']
            segment_index = int(caption_time // segment_duration)
            segment_start = segment_index * segment_duration
            
            # If this caption belongs to a new segment, save the old one
            if segment_start != current_segment['start_seconds'] and current_segment['texts']:
                # Save current segment
                combined_text = ' '.join(current_segment['texts'])
                minutes = int(current_segment['start_seconds'] // 60)
                seconds = int(current_segment['start_seconds'] % 60)
                
                transcriptions.append({
                    'time': f"{minutes:02d}:{seconds:02d}",
                    'text': combined_text
                })
                
                # Start new segment
                current_segment = {
                    'start_seconds': segment_start,
                    'texts': [caption['text']]
                }
            else:
                # Add to current segment
                if segment_start == current_segment['start_seconds']:
                    current_segment['texts'].append(caption['text'])
                else:
                    # First caption
                    current_segment = {
                        'start_seconds': segment_start,
                        'texts': [caption['text']]
                    }
        
        # Don't forget the last segment
        if current_segment['texts']:
            combined_text = ' '.join(current_segment['texts'])
            minutes = int(current_segment['start_seconds'] // 60)
            seconds = int(current_segment['start_seconds'] % 60)
            
            transcriptions.append({
                'time': f"{minutes:02d}:{seconds:02d}",
                'text': combined_text
            })
        
        return transcriptions
        
    except Exception as e:
        print(f"Error parsing VTT file: {str(e)}")
        return []

@app.route('/transcribeYoutube', methods=['POST'])
def transcribe_youtube():
    data = request.get_json()
    youtube_url = data.get('url', '')
    
    if not youtube_url:
        return jsonify({'error': 'No URL provided'}), 400
    
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    def generate():
        audio_path = None
        subtitle_path = None
        try:
            yield f"data: {json.dumps({'progress': 5, 'message': 'Validating YouTube URL...'})}\n\n"
            time.sleep(0.3)
            
            yield f"data: {json.dumps({'progress': 10, 'message': 'Checking for available captions...'})}\n\n"
            
            output_path = os.path.join(UPLOAD_FOLDER, f'{video_id}')
            
            # First, try to get captions/subtitles
            subtitle_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'en-US', 'en-GB'],
                'subtitlesformat': 'vtt',
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
            }
            
            has_subtitles = False
            video_title = 'Unknown'
            
            with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
                try:
                    info = ydl.extract_info(youtube_url, download=False)
                    video_title = info.get('title', 'Unknown')
                    
                    # Check for subtitles
                    subtitles = info.get('subtitles', {})
                    automatic_captions = info.get('automatic_captions', {})
                    
                    if subtitles or automatic_captions:
                        yield f"data: {json.dumps({'progress': 15, 'message': '✅ Captions found! Downloading...', 'video_title': video_title})}\n\n"
                        
                        # Download subtitles
                        ydl.download([youtube_url])
                        
                        # Find downloaded subtitle file
                        possible_extensions = ['.en.vtt', '.en-US.vtt', '.en-GB.vtt']
                        for ext in possible_extensions:
                            potential_path = output_path + ext
                            if os.path.exists(potential_path):
                                subtitle_path = potential_path
                                has_subtitles = True
                                break
                        
                        if has_subtitles:
                            yield f"data: {json.dumps({'progress': 30, 'message': 'Processing captions...', 'video_title': video_title})}\n\n"
                            time.sleep(0.3)
                            
                            # Parse VTT file
                            transcriptions = parse_vtt_file(subtitle_path)
                            
                            yield f"data: {json.dumps({'progress': 50, 'message': 'Formatting transcription...'})}\n\n"
                            
                            # Send partial results ONE AT A TIME for smooth typing animation
                            for idx, item in enumerate(transcriptions):
                                progress = 50 + int((idx / len(transcriptions)) * 40)
                                # Mark as caption source for faster typing
                                item['source'] = 'caption'
                                yield f"data: {json.dumps({'progress': progress, 'partial': item})}\n\n"
                                # Longer delay so typing animation has time to complete each segment
                                time.sleep(0.5)
                            
                            yield f"data: {json.dumps({'progress': 95, 'message': '✅ Captions transcribed successfully!'})}\n\n"
                            time.sleep(0.3)
                            
                            yield f"data: {json.dumps({'progress': 100, 'message': 'Complete!', 'transcriptions': transcriptions, 'video_title': video_title, 'source': 'captions'})}\n\n"
                            
                            # Cleanup
                            if subtitle_path and os.path.exists(subtitle_path):
                                os.remove(subtitle_path)
                            return
                    else:
                        yield f"data: {json.dumps({'progress': 15, 'message': 'ℹ️ No captions found. Using speech-to-text...', 'video_title': video_title})}\n\n"
                        
                except Exception as e:
                    yield f"data: {json.dumps({'progress': 15, 'message': 'ℹ️ Caption check failed. Using speech-to-text...', 'video_title': video_title})}\n\n"
            
            # Fallback to audio transcription if no subtitles
            yield f"data: {json.dumps({'progress': 20, 'message': 'Downloading audio from YouTube...'})}\n\n"
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if not video_title or video_title == 'Unknown':
                    info = ydl.extract_info(youtube_url, download=True)
                    video_title = info.get('title', 'Unknown')
                else:
                    ydl.download([youtube_url])
            
            audio_path = output_path + '.wav'
            
            yield f"data: {json.dumps({'progress': 35, 'message': f'Downloaded: {video_title}', 'video_title': video_title})}\n\n"
            time.sleep(0.3)
            
            # Load audio and prepare for transcription
            yield f"data: {json.dumps({'progress': 40, 'message': 'Loading audio file...'})}\n\n"
            
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            
            # Load audio file
            audio = AudioSegment.from_wav(audio_path)
            duration_seconds = len(audio) / 1000.0
            
            yield f"data: {json.dumps({'progress': 45, 'message': f'Duration: {int(duration_seconds//60)}m {int(duration_seconds%60)}s'})}\n\n"
            time.sleep(0.3)
            
            # Split into chunks (30 seconds each)
            chunk_length_ms = 30000
            chunks = []
            
            for i in range(0, len(audio), chunk_length_ms):
                chunk = audio[i:i + chunk_length_ms]
                chunks.append(chunk)
            
            total_chunks = len(chunks)
            yield f"data: {json.dumps({'progress': 50, 'message': f'Split into {total_chunks} segments'})}\n\n"
            time.sleep(0.3)
            
            # Transcribe each chunk
            transcriptions = []
            chunk_temp_path = os.path.join(UPLOAD_FOLDER, f'{video_id}_chunk.wav')
            
            for idx, chunk in enumerate(chunks):
                # Calculate progress (50% to 90% for processing)
                progress = 50 + int((idx / total_chunks) * 40)
                yield f"data: {json.dumps({'progress': progress, 'message': f'Transcribing segment {idx + 1}/{total_chunks}...'})}\n\n"
                
                # Export chunk
                chunk.export(chunk_temp_path, format='wav')
                
                # Transcribe
                try:
                    with sr.AudioFile(chunk_temp_path) as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio_data = recognizer.record(source)
                        
                        try:
                            text = recognizer.recognize_google(audio_data, language='en-US')
                            if text.strip():
                                # Add timestamp
                                timestamp = idx * 30
                                minutes = timestamp // 60
                                seconds = timestamp % 60
                                transcriptions.append({
                                    'time': f"{minutes:02d}:{seconds:02d}",
                                    'text': text
                                })
                                # Send partial result immediately
                                yield f"data: {json.dumps({'progress': progress, 'partial': {'time': f'{minutes:02d}:{seconds:02d}', 'text': text}})}\n\n"
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError as e:
                            yield f"data: {json.dumps({'progress': 100, 'error': f'API error: {str(e)}'})}\n\n"
                            return
                            
                except Exception as e:
                    print(f"Error processing chunk {idx}: {str(e)}")
                    continue
            
            # Cleanup
            try:
                os.remove(chunk_temp_path)
            except:
                pass
            
            yield f"data: {json.dumps({'progress': 95, 'message': 'Finalizing transcription...'})}\n\n"
            time.sleep(0.3)
            
            if transcriptions:
                yield f"data: {json.dumps({'progress': 100, 'message': 'Complete!', 'transcriptions': transcriptions, 'video_title': video_title, 'source': 'audio'})}\n\n"
            else:
                yield f"data: {json.dumps({'progress': 100, 'error': 'Could not transcribe audio. The video might not contain clear speech.'})}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'progress': 100, 'error': f'Error: {str(e)}'})}\n\n"
        
        # Cleanup
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass
        if subtitle_path and os.path.exists(subtitle_path):
            try:
                os.remove(subtitle_path)
            except:
                pass
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/uploadAudio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    # Video formats that need audio extraction
    video_formats = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.m4v', '.mpeg', '.mpg', '.3gp']
    audio_formats = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.wma']
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    def generate():
        file_path_final = None
        try:
            wav_path = None
            
            # Convert video/audio to WAV
            if file_ext in video_formats:
                yield f"data: {json.dumps({'progress': 5, 'message': 'Extracting audio from video...'})}\n\n"
                time.sleep(0.3)
                
                wav_path = file_path.replace(file_ext, '.wav')
                audio = AudioSegment.from_file(file_path)
                audio.export(wav_path, format='wav')
                os.remove(file_path)
                file_path_final = wav_path
                
            elif file_ext in audio_formats:
                if file_ext != '.wav':
                    yield f"data: {json.dumps({'progress': 5, 'message': 'Converting audio format...'})}\n\n"
                    time.sleep(0.3)
                    
                    wav_path = file_path.replace(file_ext, '.wav')
                    audio = AudioSegment.from_file(file_path)
                    audio.export(wav_path, format='wav')
                    os.remove(file_path)
                    file_path_final = wav_path
                else:
                    file_path_final = file_path
            else:
                yield f"data: {json.dumps({'progress': 100, 'error': 'Unsupported file format. Please upload audio or video files.'})}\n\n"
                return
            
            yield f"data: {json.dumps({'progress': 10, 'message': 'Loading audio file...'})}\n\n"
            
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            
            audio = AudioSegment.from_file(file_path_final)
            duration_seconds = len(audio) / 1000.0
            
            yield f"data: {json.dumps({'progress': 15, 'message': f'Audio duration: {int(duration_seconds//60)}m {int(duration_seconds%60)}s'})}\n\n"
            time.sleep(0.3)
            
            chunk_length_ms = 30000
            chunks = []
            
            for i in range(0, len(audio), chunk_length_ms):
                chunk = audio[i:i + chunk_length_ms]
                chunks.append(chunk)
            
            total_chunks = len(chunks)
            yield f"data: {json.dumps({'progress': 20, 'message': f'Split into {total_chunks} segments'})}\n\n"
            time.sleep(0.3)
            
            transcriptions = []
            chunk_temp_path = file_path_final.replace('.wav', '_chunk.wav')
            
            for idx, chunk in enumerate(chunks):
                progress = 20 + int((idx / total_chunks) * 70)
                yield f"data: {json.dumps({'progress': progress, 'message': f'Transcribing segment {idx + 1}/{total_chunks}...'})}\n\n"
                
                chunk.export(chunk_temp_path, format='wav')
                
                try:
                    with sr.AudioFile(chunk_temp_path) as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio_data = recognizer.record(source)
                        
                        try:
                            text = recognizer.recognize_google(audio_data, language='en-US')
                            if text.strip():
                                transcriptions.append(text)
                                # Send partial result immediately
                                yield f"data: {json.dumps({'progress': progress, 'partial_text': text})}\n\n"
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError as e:
                            yield f"data: {json.dumps({'progress': 100, 'error': f'API error: {str(e)}'})}\n\n"
                            return
                            
                except Exception as e:
                    print(f"Error processing chunk {idx}: {str(e)}")
                    continue
            
            try:
                os.remove(chunk_temp_path)
            except:
                pass
            
            yield f"data: {json.dumps({'progress': 95, 'message': 'Finalizing transcription...'})}\n\n"
            time.sleep(0.3)
            
            if transcriptions:
                full_transcription = ' '.join(transcriptions)
                yield f"data: {json.dumps({'progress': 100, 'message': 'Complete!', 'transcription': full_transcription})}\n\n"
            else:
                yield f"data: {json.dumps({'progress': 100, 'error': 'Could not transcribe any part of the audio.'})}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'progress': 100, 'error': f'Error: {str(e)}'})}\n\n"
        
        # Cleanup
        if file_path_final and os.path.exists(file_path_final):
            try:
                os.remove(file_path_final)
            except:
                pass
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    port = 8888
    print('='*50)
    print(f'🚀 N.A.M.O.R. Server Starting...')
    print(f'📡 Server will run on:')
    print(f'   - http://localhost:{port}')
    print(f'   - http://127.0.0.1:{port}')
    print(f'   - http://192.168.1.115:{port}')
    print(f'📁 Make sure "templates/index.html" exists!')
    print('='*50)
    app.run(host='0.0.0.0', port=port, debug=True)
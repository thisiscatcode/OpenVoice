from flask import Flask, request, jsonify
import os,time,random
import uuid
import torch
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS
from pydub import AudioSegment

app = Flask(__name__)

# Initialization
ckpt_converter = 'checkpoints_v2/converter'
device = "cuda:0" if torch.cuda.is_available() else "cpu"

tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

input_wav_file = 'resources/input_wav_file.wav'
speaker_id = 0  # Hardcoded speaker ID
source_se_path_jp = f'checkpoints_v2/base_speakers/ses/jp.pth'
source_se_path_zh = f'checkpoints_v2/base_speakers/ses/zh.pth'
source_se_path_en = f'checkpoints_v2/base_speakers/ses/en-us.pth'
encode_message = "@MyShell"
output_folder = "/data/"

# Obtain Tone Color Embedding
target_se, audio_name = se_extractor.get_se(input_wav_file, tone_color_converter, vad=False)

# Initialize the TTS model
model_jp = TTS(language="JP", device=device)
#model_zh = TTS(language="ZH", device=device)
#model_en = TTS(language="EN", device=device)

# Load source speaker embeddings
source_se_jp = torch.load(source_se_path_jp, map_location=device)
#source_se_zh = torch.load(source_se_path_zh, map_location=device)
#source_se_en = torch.load(source_se_path_en, map_location=device)

print("openvoice service is ready !!!")

@app.route('/get_openvoice', methods=['POST'])
def get_openvoice():
    data = request.json

    lang="JP";
    #lang = data.get('lang')
    text = data.get('text')
    
    print(f"Processing request for language: {lang} and text: {text}")


    # Get current timestamp
    timestamp = time.strftime("%Y%m%d%H%M%S")
    # Generate random digits
    random_digits = ''.join(random.choices('0123456789', k=3))
    # Combine timestamp and random digits for the filename
    filename = f"{timestamp}{random_digits}"
    relative_path = f"{filename}.wav"
    output_path = os.path.join(output_folder, relative_path)
    
    # Path for temporary audio
    src_path = os.path.join(output_folder, 'tmp.wav')

    if not lang or not text:
        return jsonify({'error': 'Missing required parameters: lang, text'}), 400

    try:
        # Select the appropriate model and source speaker embedding based on the language
        if lang == "JP":
            model = model_jp
            source_se = source_se_jp
        elif lang == "ZH":
            model = model_zh
            source_se = source_se_zh
        elif lang == "EN":
            model = model_en
            source_se = source_se_en
        else:
            return jsonify({'error': 'Unsupported language'}), 400

        # Generate TTS audio and save to temp path
        model.tts_to_file(text, speaker_id, src_path, speed=1.0)

        # Run the tone color converter
        tone_color_converter.convert(
            audio_src_path=src_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=output_path,
            message=encode_message
        )

        # Return the path to the generated audio file
        print("Generated WAV file path:", relative_path)
        return jsonify({'audio_path': relative_path}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_openvoice_batch', methods=['POST'])
def get_openvoice_batch():
    

    result_folder="/data/";
    
    
    data = request.json
    file_path = data.get('file_path')
    lang = data.get('lang')
    text = data.get('text')
    
    print(f"Processing request for language: {lang} and text: {text}")

    # Path for temporary audio
    src_path = os.path.join(result_folder, 'gen_wav_openvoice/tmp.wav')

    if not lang or not text:
        return jsonify({'error': 'Missing required parameters: lang, text'}), 400

    try:
        # Select the appropriate model and source speaker embedding based on the language
        if lang == "JP":
            model = model_jp
            source_se = source_se_jp
        elif lang == "ZH":
            model = model_zh
            source_se = source_se_zh
        elif lang == "EN":
            model = model_en
            source_se = source_se_en
        else:
            return jsonify({'error': 'Unsupported language'}), 400

        # Generate TTS audio and save to temp path
        model.tts_to_file(text, speaker_id, src_path, speed=1.0)

        # Run the tone color converter
        tone_color_converter.convert(
            audio_src_path=src_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=result_folder+"gen_wav_openvoice/"+file_path,
            message=encode_message
        )

        # Return the path to the generated audio file
        print("Generated WAV file path:", result_folder+"gen_wav_openvoice/"+file_path)


        #audio_mp3 = AudioSegment.from_wav(result_folder+"gen_wav_openvoice/"+file_path)
        #audio_mp3 = audio_mp3.set_frame_rate(16000)
        #mp3_file_path = file_path.replace('.wav', '.mp3')
        #audio_mp3.export(result_folder+"audio_files/"+mp3_file_path, format="mp3")
        #print("Generated MP3 file path:", result_folder+"audio_files/"+mp3_file_path)
        
        return jsonify({'audio_path': file_path}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/get_openvoice_batch_2', methods=['POST'])
def get_openvoice_batch_2():
    

    result_folder="/data/";
    
    
    data = request.json
    file_path = data.get('file_path')
    lang = data.get('lang')
    text = data.get('text')
    
    print(f"Processing request for language: {lang} and text: {text}")

    # Path for temporary audio
    src_path = os.path.join(result_folder, 'gen_wav_qanda/tmp.wav')

    if not lang or not text:
        return jsonify({'error': 'Missing required parameters: lang, text'}), 400

    try:
        # Select the appropriate model and source speaker embedding based on the language
        if lang == "JP":
            model = model_jp
            source_se = source_se_jp
        elif lang == "ZH":
            model = model_zh
            source_se = source_se_zh
        elif lang == "EN":
            model = model_en
            source_se = source_se_en
        else:
            return jsonify({'error': 'Unsupported language'}), 400

        # Generate TTS audio and save to temp path
        model.tts_to_file(text, speaker_id, src_path, speed=1.0)

        # Run the tone color converter
        tone_color_converter.convert(
            audio_src_path=src_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=result_folder+"gen_wav_qanda/"+file_path,
            message=encode_message
        )

        # Return the path to the generated audio file
        print("Generated WAV file path:", result_folder+"gen_wav_qanda/"+file_path)


        #audio_mp3 = AudioSegment.from_wav(result_folder+"gen_wav_qanda/"+file_path)
        #audio_mp3 = audio_mp3.set_frame_rate(16000)
        #mp3_file_path = file_path.replace('.wav', '.mp3')
        #audio_mp3.export(result_folder+"audio_files/"+mp3_file_path, format="mp3")
        #print("Generated MP3 file path:", result_folder+"audio_files/"+mp3_file_path)
        
        return jsonify({'audio_path': file_path}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

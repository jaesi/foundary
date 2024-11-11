# app/routes.py
import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .ai_generation import generate_image_from_prompt, image_to_base64, describe_furniture
from .image_processing import image_concater, random_pair, combine_with_style
import random
import datetime
from PIL import Image


main = Blueprint('main', __name__)

# 업로드 가능한 파일 확장자 제한
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 특정 폴더 하위의 모든 폴더 이름 가져오기 함수
def get_style_sets():
    style_dir = '00_ref'  # 상위 폴더에 있는 '00_ref' 폴더 경로로 설정
    return [folder for folder in os.listdir(style_dir) if os.path.isdir(os.path.join(style_dir, folder))]

# @: Decorator
@main.route('/', methods=['GET', 'POST'])
def index():

    # 스타일 세트를 가져와 템플릿에 전달
    style_sets = get_style_sets()  # 'styles' 폴더 내 모든 폴더 이름을 리스트로 가져옴

    if request.method == 'POST':
        # 폼 데이터 받기: style_set, action, image
        style_set = request.form.get('style_set') # User selected style set
        action = request.form.get('action')  # 'generate'

        # 이미지 인풋 - 
        if 'image' not in request.files: # 이미지가 없는 경우
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join('app', 'static', 'images', 'input', filename)
            file.save(input_path)

            # combination file 경로 설정
            combi_path = os.path.join('app', 'static', 'images', 'combi')


            # 출력 파일 경로 설정
            output_filename = f"{os.path.splitext(filename)[0]}_output.png"
            output_path = os.path.join('app', 'static', 'images', 'output', output_filename)

            try: # 결과 탭
                if action == 'generate':
                    # Get the style set folder 
                    style_dir = os.path.join('00_ref', style_set)
                    combined_path = combine_with_style(input_path, style_dir, combi_path)
                    generate_image_from_prompt(combined_path, output_path)
                
                else:
                    flash('Invalid action')
                    return redirect(request.url)
                
                # 이미지 URL 생성
                result_image = url_for('static', filename=f'images/output/{output_filename}')

                # 이미지 Base64 인코딩 (필요 시)
                image_data = image_to_base64(output_path)

                # >>>>> Vision API를 사용하여 설명 생성
                description = describe_furniture(image_data)

                return render_template('result.html', result_image=result_image, description=description) # render_template를 통해 html과 연결
            except Exception as e:
                flash(f'Error: {e}')
                return redirect(request.url)
        else:
            flash('Allowed file types are png, jpg, jpeg, gif')
            return redirect(request.url)
    return render_template('index.html', style_sets=style_sets) # render_template를 통해 html과 연결

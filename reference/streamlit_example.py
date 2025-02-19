import streamlit as st
import os 
import cv2 as cv

import torch, torch.nn, torchvision
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import seaborn as sns
import pandas as pd
from time import time
from datetime import timedelta
from datetime import datetime
import json
import re
import requests

import onus_ocr
import onus_domain
import onus_bert
import onus_db
import onus_selenium
import onus_resnet
import requests
import hashlib
import onus_html
import onus_showapk
import onus_util

import warnings 
warnings.filterwarnings('ignore')

#import urllib3
#requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'


if 'input_url' not in st.session_state:
    st.session_state.input_url = None


if 'scan_clicked' not in st.session_state:
    st.session_state.scan_clicked = False
    
if 'rescan_clicked' not in st.session_state:
    st.session_state.rescan_clicked = False

# Function to handle scan button click
def handle_scan():
    st.session_state.scan_clicked = True

# Function to handle rescan button click
def handle_rescan():
    st.session_state.rescan_clicked = True
    
# load ML


st.title('OnUS demo')
with st.form('url_form'):
    input_url = st.text_input('URL', key='url')
    #submit = st.button('Submit', on_click = handle_scan)
    submit = st.form_submit_button('Submit', on_click = handle_scan)
if st.session_state.scan_clicked:
    url = onus_util.get_searchURL(input_url)
    created_at = None
    print('[>] Input URL : ', input_url)
    
    # 최종 url 확인
    final_url, screenshot_file, html, title, status_code, redirect_file, img_md5s = onus_selenium.run(url)
    print('[>] Final URL : ', final_url)
    
    if final_url == '-' or (not final_url) :
        st.warning('접근이 불가한 URL입니다.', icon = '⚠')
        st.stop()
    
    target_domain = final_url.replace('https://', '').replace('http://', '').split('/')[0].split('?')[0]
    print('[>] Target Domain : ', target_domain)
    
    # Input URL이 DB에 있는지 확인
    input_url_id = onus_db.search_inputUrl(input_url)
    
    # Final URL이 DB에 있는지 확인
    final_url_id = onus_db.search_finalUrl(final_url)
    
    # 두개 다 존재하는 경우
    if input_url_id and final_url_id:
        print('[>>] Input, Final 둘다 DB에 있음.')
        
        # URL Info에 두개가 쌍으로 들어가 있는 경우 확인
        info = onus_db.search_PairInfo(input_url_id, final_url_id)
        
        if info:
            #print('[>>>] Input-Final URL Pair is detected.')
            try:
                info_id, _input_url_id, _final_url_id, status_code, title, redirect_file, domain_file, result_id, class_id, screenshot_file, created_at, _ = info
            except: 
                st.warning('분석중인 URL입니다. 잠시 후 다시 Submit 버튼을 눌러주세요.', icon = '⚠')
                st.stop()
            predictions = onus_db.search_maliciousResult(result_id)
            
            result_id, final_url_id, resnet_label, ocr_bert, html_bert, heuristic_result, ocr_wc, html_wc, class_id, scan_date = predictions
            
        else: # 둘다 존재는 하는데 Pair로 존재하지 않는 경우 (Input이 해당 Final URL로 이어지지 않는 경우)
            #print('[>>>] Input-Final URL Pair is not detected. (Input Only)')
            
            # Final URL에 대한 정보를 가져와서 덮어씌움
            info = onus_db.search_info_by_final_id(final_url_id)
            try:
                info_id, _input_url_id, _final_url_id, _status_code, _title, _redirect_file, domain_file, result_id, class_id, _screenshot_file, created_at, updated_at = info
            except:
                st.warning('분석중인 URL입니다. 잠시 후 다시 Submit 버튼을 눌러주세요.', icon = '⚠')
                st.stop()
            predictions = onus_db.search_maliciousResult(result_id)
            
            result_id, final_url_id, resnet_label, ocr_bert, html_bert, heuristic_result, ocr_wc, html_wc, class_id, scan_date = predictions
            
            # URL_INFO에 pair 정보 입력    
            ## 리다이렉션, 스크린샷, 상태코드 은 새로운 것으로 입력
            info_id = onus_db.insert_PairInfo(input_url_id, final_url_id, status_code, title, redirect_file, domain_file, result_id, class_id, screenshot_file)
            
    elif onus_db.search_WhiteList(target_domain):
        print('[>>] WhiteList에 존재')
        if not final_url_id:
            #print('[>>>] Final URL이 DB에 없음')
            final_url_id = onus_db.insert_finalURL(final_url)
            already_scanned = False
        else:
            already_scanned = True
            
        if not input_url_id:
            #print('[>>>] Input URL이 DB에 없음')
            input_url_id = onus_db.insert_inputURL(input_url)
        
        if already_scanned:
            info = onus_db.search_info_by_final_id(final_url_id)
            info_id, _input_url_id, _final_url_id, _status_code, _title, _redirect_file, domain_file, result_id, class_id, _screenshot_file, created_at, updated_at = info
            predictions = onus_db.search_maliciousResult(result_id)
            
            result_id, final_url_id, resnet_label, ocr_bert, html_bert, heuristic_result, ocr_wc, html_wc, class_id, scan_date = predictions
            
            info_id = onus_db.insert_PairInfo(input_url_id, final_url_id, status_code, title, redirect_file, domain_file, result_id, class_id, screenshot_file)
            #print('[>>>>] DB Update : insert_PairInfo 132')
        else:
            # scan 수행
            domain_file = onus_domain.run(target_domain)
            
            # 모델 결과
            resnet_label, ocr_bert, html_bert, ocr_wc, html_wc, heuristic_result, class_id = ['정상', '정상', '정상', '정상', '정상', '1', '1']
            result_id = onus_db.insert_MaliciousResult(final_url_id, resnet_label, ocr_bert, html_bert, heuristic_result, ocr_wc, html_wc, class_id)
            
            info_id = onus_db.insert_PairInfo(input_url_id, final_url_id, status_code, title, redirect_file, domain_file, result_id, class_id, screenshot_file)
            #print('[>>>>] DB Update : insert_PairInfo 142')
    else:
        if not final_url_id:
            print('[>>>] Final URL이 DB에 없음')
            final_url_id = onus_db.insert_finalURL(final_url)
            already_scanned = False
        else:
            already_scanned = True
            
        if not input_url_id:
            print('[>>>] Input URL이 DB에 없음')
            input_url_id = onus_db.insert_inputURL(input_url)
            
        if already_scanned:
            info = onus_db.search_info_by_final_id(final_url_id)
            info_id, _input_url_id, _final_url_id, _status_code, _title, _redirect_file, domain_file, result_id, class_id, _screenshot_file, created_at, updated_at = info
            predictions = onus_db.search_maliciousResult(result_id)
            
            result_id, final_url_id, resnet_label, ocr_bert, html_bert, heuristic_result, ocr_wc, html_wc, class_id, scan_date = predictions
            
            info_id = onus_db.insert_PairInfo(input_url_id, final_url_id, status_code, title, redirect_file, domain_file, result_id, class_id, screenshot_file)
            #print('[>>>>] DB Update : insert_PairInfo 163')
        else:
            print('[>>>>] 새로운 최종 URL')
            domain_file = onus_domain.run(target_domain)
            
            resnet_label, ocr_bert, html_bert, ocr_wc, html_wc, heuristic_result, class_id = onus_util.get_prediction(screenshot_file, html, img_md5s, final_url)
            print('ML Runs : ', resnet_label, ocr_bert, html_bert, ocr_wc, html_wc, heuristic_result, class_id)
            result_id = onus_db.insert_MaliciousResult(final_url_id, resnet_label, ocr_bert, html_bert, heuristic_result, ocr_wc, html_wc, class_id)
            #result_id = str(result_id)
            #print('[>>>>] DB Update : insert_MaliciousResult 171')
            info_id = onus_db.insert_PairInfo(input_url_id, final_url_id, status_code, title, redirect_file, domain_file, result_id, class_id, screenshot_file)
            #print('[>>>>] DB Update : insert_PairInfo 173')
            
            
    rescan = st.button('Rescan', on_click = handle_rescan)
    if st.session_state.rescan_clicked:
        st.session_state.rescan_clicked = False

        print('[>] Rescan :' , input_url)
        
        try: 
            #final_url, screenshot_file, html, title, status_code, redirect_file, img_md5s = onus_selenium.run(final_url)
            domain_file = onus_domain.run(target_domain)
            resnet_label, ocr_bert, html_bert, ocr_wc, html_wc, heuristic_result, class_id = onus_util.get_prediction(screenshot_file, html, img_md5s, final_url)
            print('[Rescan] ML Runs : ', resnet_label, ocr_bert, html_bert, ocr_wc, html_wc, heuristic_result, class_id)
            result_id = onus_db.insert_MaliciousResult(final_url_id, resnet_label, ocr_bert, html_bert, heuristic_result, ocr_wc, html_wc, class_id)
            #print('[Rescan] DB Update : insert_MaliciousResult')
            info_id = onus_db.insert_PairInfo(input_url_id, final_url_id, status_code, title, redirect_file, domain_file, result_id, class_id, screenshot_file)
            print('[Rescan] Done')
        except Exception as e:
            print('[Rescan] Error : ', e)
    # 결과 출력        
    heuristic_result = onus_db.get_label_from_class_id(heuristic_result) 
    final_result = onus_db.get_label_from_class_id(class_id) 
            
    if created_at:
        scan_timestamp = created_at.timestamp()
        if time() - scan_timestamp > 60*60*24*1:
            st.warning('마지막 분석이후 1일 이상 경과한 URL입니다. 최신 결과를 보기 원하시면 Rescan 버튼을 눌러주세요.', icon = '⚠')
    apk_info = onus_db.search_apk_info(info_id)
    if apk_info:
        apk_result = apk_info[6]
    
    else:
        apk_result = '검색 대기 중'
    onus_showapk.show_result([input_url, final_url, resnet_label, ocr_bert, html_bert, ocr_wc, html_wc, heuristic_result, final_result, redirect_file, status_code, title, screenshot_file, domain_file, apk_result])
    print('===============================')  
else:
    
    history = onus_db.search_recently_scannedAPK()
    try: 
        if not history:
            pass
        else:
            st.subheader('URL 분석 현황')
            df = pd.DataFrame(history, columns = ['info_id','Source URL', 'Destination URL', 'Status Code', 'Title', 'URL 판정 결과', '검사 시간'])
            df = df[['Source URL','Destination URL', 'URL 판정 결과', 'info_id', 'Title', 'Status Code', '검사 시간']]
            df['Source URL'] = df['Source URL'].apply(onus_db.search_inputUrl_by_id)
            df['Destination URL'] = df['Destination URL'].apply(onus_db.search_finalUrl_by_id)
            df['info_id'] = df['info_id'].apply(onus_util.get_apk_result)
            df['검사 시간'] = df['검사 시간'] + timedelta(hours = 9)

            df['URL 판정 결과'] = df['URL 판정 결과'].apply(lambda x : onus_db.get_label_from_class_id(x))
            #st.dataframe(df.set_index(df.columns[0]), width = 1280)
            df.columns = ['Source URL', 'Destination URL', 'URL 판정 결과', 'APK 판정 결과', 'Title', 'Status', '검사 시간']
            st.dataframe(df.set_index(df.columns[0]), width = 1280)
    except Exception as e:
        print('main : ',e) 
        pass
        
        
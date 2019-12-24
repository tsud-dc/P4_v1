#!/usr/bin/env python
# coding: utf-8

import os
from flask import Flask, render_template, request, send_from_directory
import requests
import matplotlib.pyplot as plt
import json
import glob
import random
import platform
import sys
import glob
import api_lb
import config
import setenv

listen_port = os.environ.get('port')

# Create a Flask instance
app = Flask(__name__)

def req_data(req_url):
    ret_vals = requests.get(req_url)
    text_vals = ret_vals.text     
    vals_list = json.loads(text_vals)
    return vals_list

def draw_chart(data_list, f_name):
    time_list = []
    vals_list = []
    for elem in data_list:
        time_list.append(elem[0])
        vals_list.append(float(elem[1]))
        
    if f_name in 'bri_':
        plt.ylabel = 'Brightness'
    elif f_name in 'temp_':
        plt.ylabel = 'Temperature(Celsius)'
        
    plt.rcParams["font.size"] = 8 
    plt.figure(figsize=(4, 5))
    plt.xticks(color="None")
    plt.tick_params(length=0)
    plt.title('{} to {}'.format(time_list[0], time_list[-1]), fontsize=8)
    plt.plot(time_list, vals_list)

    plt.savefig('./charts/{}.png'.format(f_name))
    plt.show()

##### Define routes #####
@app.route('/', methods=['GET', 'POST'])
def home():
    req = request.args
      
    if len(req) > 0:
        req_uri = '{}?records={}'.format(config.uri, req['records'])
    else:
        req_uri = config.uri

    url_list = api_lb.make_url_list(config.api_hosts, config.port, req_uri)

    err_msg = "Connecting DB API is not running"
    vals_list = api_lb.connect_lb(url_list, err_msg, 'load')
    
    if type(vals_list) is list:    
        light_list = vals_list.pop(3)
        temp_list = vals_list.pop(6)

        rand_fn = ''
        for i in range(5):
            rand_fn += str(random.randint(0, 9))

        bri_fname = 'bri_' + str(rand_fn)
        temp_fname = 'temp_' + str(rand_fn)

        draw_chart(light_list, bri_fname)
        draw_chart(temp_list, temp_fname)

        bri_ch_val = 'src=/charts/{}.png'.format(bri_fname)
        temp_ch_val = 'src=/charts/{}.png'.format(temp_fname)

        return render_template('default.html', b_max_val = vals_list[0], b_min_val = vals_list[1], b_ave_val = vals_list[2], t_max_val = vals_list[3], t_min_val = vals_list[4], t_ave_val = vals_list[5], bri_ch = bri_ch_val, temp_ch = temp_ch_val)
    else:
        return(vals_list)

@app.route('/charts/<chart_name>')
def ret_chart(chart_name):  
    return send_from_directory('./charts', chart_name)

@app.route('/maint', methods=['GET'])
def maint():
    png_list = glob.glob('./charts/*.png')
    if len(png_list) > 0:
        for file in png_list:
            if platform.system() == 'Windows': file=file.replace("\\", '/')
            os.remove(file)
        mess = 'pngs delted'
    else:
        mess = 'no pngs'   
    code = 200
    return mess, code

##### Run the Flask instance, browse to http://<< Host IP or URL >>:80 #####
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', listen_port)))
    
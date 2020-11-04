from flask import Blueprint, render_template ,request, make_response, jsonify,flash, url_for,redirect
from flask_login import login_required, current_user
import requests
from .models import Framework_version, Gpu_status, task
from . import db
import subprocess
import datetime
import re
import random
import os
import sys

main = Blueprint('main', __name__)
admin='cssp'


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/train')
@login_required
def train():
    gpu_info = subprocess.run(args=['nvidia-smi','--query-gpu=index,name','--format=csv,noheader'],stdout=subprocess.PIPE,universal_newlines=True)
    gpu_string = gpu_info.stdout
    gpu_list = re.split('\n|, ',gpu_string.rstrip())
    # test=["1","3090"]
    # gpu_list+=test
    gpu_sql = db.session.query(Gpu_status).all()
    for data in gpu_sql:
        gpu_list.remove(data.index)
        gpu_list.remove(data.gpu_name)


    gpu_list = list(zip(gpu_list[::2], gpu_list[1::2]))
    list_len = len(gpu_list)
    data = db.session.query(task).all()
    return render_template('train.html', name=current_user.name, title='train', gpu_list=gpu_list, list_len=list_len,output_data = data, admin=admin)


@main.route('/train', methods=['POST'])
@login_required
def train_post():
    if request.form['submit_button'] == 'start':
        framework = request.form.get('framework')
        version = request.form.get('version')
        gpu = request.form.getlist('gpu')
        gpu_sql = db.session.query(Gpu_status).all()
        gpu_list=[]
        for gpu_split in gpu:
            gpu_cut = gpu_split.split(",")
            for item in gpu_cut: 
                gpu_list.append(item)


        def common_data(list1,list2):
            result=False
            for x in list1:
                for y  in list2:
                    if x == y.gpu_name:
                        result=True
                        return result

        gpu_left = common_data(gpu_list[1::2],gpu_sql)

        if framework == None or version == None or gpu == [] or gpu_left==True :
            flash('Please choose the right framework, version and GPU!')
            #return redirect(url_for('main.train'))
 
        else:
            start_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            docker_name = current_user.name +"_" + framework +"_"+ version +"_" + start_time
            gpu_usage = ', '.join(gpu_list[1::2])
            gpu_usage_index = ','.join(gpu_list[::2])
            port = str(random.randint(1619,9999))
            full_port = "140.113.149.172:"+ port
            tasks = task(name=current_user.name, docker_name=docker_name, start_time=full_port,gpu=gpu_usage)
            folder = "/media/data/"+current_user.name+"/"
            models = "/media/data/"+current_user.name+"/models/"
            data = "/media/data/"+current_user.name+"/data/"
            os.makedirs(folder, exist_ok=True)
            os.makedirs(models, exist_ok=True)
            os.makedirs(data, exist_ok=True)
            command="docker run -d -p "+ port +":22 --name "+ docker_name +" --gpus device=" \
            + gpu_usage_index + "  -v /media/data/"+current_user.name +"/:/workspace -w /workspace cssp618/environment:cssp_" \
            + framework +"_"+ version 
            
            # p1 = subprocess.run(command,shell=True)
            p1 = subprocess.run(args=['docker','run','-d','-p', port+':22','--name',docker_name, \
            '--gpus','device='+gpu_usage_index,'-v','/media/data/'+current_user.name+'/:/root/', \
            '-w','/root/','cssp618/environment:cssp_'+framework +"_"+ version+'_ws'])
            if p1.returncode == 0 :
                db.session.add(tasks)
                db.session.commit()
                for i in range (len(gpu_list)//2):
                    db.session.add(Gpu_status(index=gpu_list[2*i],gpu_name=gpu_list[2*i+1]))
                    db.session.commit()
            else:
                print(p1.stderr)
                flash("Please find admin to solve the problem !")

        return redirect(url_for('main.train'))

    elif request.form['submit_button'] == 'stop':
        gpu_name = request.form.get('gpu')
        docker_name = request.form.get('docker_name')
        gpu_list = re.split(', ',gpu_name)
        p2 = subprocess.run(args=['docker','rm','-f',docker_name])
        if p2.returncode == 0 :
            task.query.filter_by(docker_name=docker_name).delete()
            for name in gpu_list:
                Gpu_status.query.filter_by(gpu_name=name).delete()
            db.session.commit()
        else:
            pass
        # print (docker_name)
        return redirect(url_for('main.train'))

    else:
        return redirect(url_for('main.train'))

@main.route('/version_selected/<framework>')
@login_required
def version_selected(framework):
    versions = Framework_version.query.filter_by(framework=framework).order_by(Framework_version.version).all()
    version_array = []

    for version in versions:
        versionObj = {}
        versionObj['id'] = version.id
        versionObj['number'] = version.version
        version_array.append(versionObj)
    
    return jsonify({'versions_json':version_array})
        
@main.route('/version')
@login_required
def version():
    if current_user.name != "cssp":
        return redirect(url_for('main.train'))
    else:
        data = db.session.query(Framework_version).order_by(Framework_version.framework,Framework_version.version).all()
        return render_template('version.html', output_data = data, admin=admin)

@main.route('/version', methods=['POST'])
@login_required
def version_post():
    if request.form['submit_button'] == 'add':
        framework = request.form.get('framework')
        version = request.form.get('version')
        version_control = Framework_version(framework=framework,version=version)

        db.session.add(version_control)
        db.session.commit()

    elif request.form['submit_button'] == 'delete':
        framework = request.form.get('framework')
        version = request.form.get('version')
        Framework_version.query.filter_by(framework=framework, version=version).delete()
        db.session.commit()
    else:
        pass
    return redirect(url_for('main.version'))
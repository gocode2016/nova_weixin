# -*- coding:utf8 -*-
# Author: shizhenyu96@gamil.com
# github: https://github.com/imndszy
from . import bind
from flask import (render_template, redirect, request, url_for, flash, session)
from forms import BindForm,ReBindForm
from bind_database import get_bind_info,verify_password,save_new_student
from app.weixin.qrcode import create_ticket,get_qrcode_url

@bind.route('/register',methods=['GET','POST'])
def register():
    form = BindForm()
    if form.validate_on_submit():
        stuid = form.stuid.data.encode('utf8')
        passwd = form.certification.data.encode('utf8')
        session['stuid'] = stuid
        session['passwd'] = passwd
        verify_status = verify_password(stuid,passwd)
        if verify_status and verify_status !=-1:
            session['register'] = True
            query_result = get_bind_info(stuid,passwd)
            if query_result:                                      #该学号已经绑定微信号
                openid = query_result.encode('utf8')
                session['openid'] = openid
                return redirect(url_for('bind.rebind'))
            else:
                save_new_student(stuid)
                return redirect(url_for('bind.get_qrcode'))
        elif verify_status == -1:
            return render_template('404.html')
        else:
            flash('Invalid Student ID or Password.')
    return render_template('bind/register.html',form=form)

@bind.route('/qrcode',methods=['GET','POST'])
def get_qrcode():
    if session['register']:
        ticket = create_ticket("QR_SCENE", int(session['stuid']))
        url = get_qrcode_url(ticket)
        return redirect(url)
    return render_template('404.html')

@bind.route('/rebind',methods=['GET','POST'])
def rebind():
    if session['register'] and session['openid']:
        form = ReBindForm()
        if form.validate_on_submit():
            coverage = form.coverage.data
            if coverage == 'yes':
                ticket = create_ticket("QR_SCENE", int(session['stuid']))
                url = get_qrcode_url(ticket)
                return redirect(url)
        return render_template('bind/rebind.html', form=form)


    return render_template('404.html')
from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import json

with open('./config.json','r') as c:
    params = json.load(c)["params"]

db = SQLAlchemy()
app = Flask(__name__)

app.secret_key = params['secret_key']

if(params['local_server']):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']

db.init_app(app)

nums = [0,1,2,3,4,5,6,7,8,9]
password = ""
for i in range(0,14):
    random.shuffle(nums)
    rand_num = random.choice(nums)
    password += str(rand_num)


class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40))
    info = db.Column(db.String(300))


class Vendor(db.Model):
    vid = db.Column(db.String(), primary_key=True)
    password = db.Column(db.String(20))
    vname = db.Column(db.String(20))
    vmob = db.Column(db.String(12))
    vemail = db.Column(db.String(40), unique=True)
    company = db.Column(db.String(15))
    address = db.Column(db.String(100))

class Tender(db.Model):
    tid = db.Column(db.String(), primary_key=True)
    tname = db.Column(db.String(40))
    ttype = db.Column(db.String(20))
    tprice = db.Column(db.Integer)
    tdesc = db.Column(db.String(300))
    tdeadline = db.Column(db.String(20))
    tloc = db.Column(db.String(70))

class Bidder(db.Model):
    bid = db.Column(db.String(), primary_key=True)
    vid = db.Column(db.String(80), nullable=False)
    tid = db.Column(db.String(80), nullable=False)
    bidamount = db.Column(db.String(12), nullable=False)
    deadline = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False)

class Tenderstatus(db.Model):
    tid = db.Column(db.String(), primary_key=True)
    bid = db.Column(db.String())
    status = db.Column(db.String(15), nullable=False)
    vid = db.Column(db.String(15))


@app.route("/")
def home():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    return render_template('index.html',header = "loginHeader.html",menu = "menu.html",notices = notices,statuses = tenderstatus,params = params)

@app.route("/register", methods=['GET','POST'])
def register():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if(request.method == 'POST'):
        vid = "V"+password
        vname = request.form.get('vname')
        vemail = request.form.get('vemail')
        vmob = request.form.get('vmob')
        vaddr = request.form.get('vaddr')
        company = request.form.get('cname')
        vpass = request.form.get('vpass')
        vendor = Vendor(vid = vid, vname = vname,vemail = vemail,vmob = vmob,address = vaddr,company = company,password = vpass)
        db.session.add(vendor)
        db.session.commit()
        return  redirect('/login')
    return render_template('register.html',header = "loginHeader.html",menu = "menu.html",notices = notices,statuses = tenderstatus)

@app.route("/login",methods = ['GET','POST'])
def login():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session and session['user'] == params['admin_user']):
        return redirect("/adminHome")
    elif('user' in session):
        return redirect("/vendorHome/"+session['user'])
    if(request.method == 'POST'):
        uname = request.form.get('username')
        upass = request.form.get('password')
        btnClicked = request.form.get('btnClicked')
        vendor = Vendor.query.filter_by(vemail = uname).first()
        if(uname == params['admin_user'] and upass == params['admin_password'] and btnClicked == "Login as Admin"):
            session['user'] = uname
            return redirect("/adminHome")
        elif(vendor != None and upass == vendor.password):
            session['user'] = vendor.vid
            return redirect('/vendorHome/'+vendor.vid)
        else:
            return redirect('/loginFailed')
    return render_template('login.html',header = "loginHeader.html",menu = "menu.html",notices = notices,statuses = tenderstatus)

@app.route("/vendorHome/<string:vendorId>")
def vendorHome(vendorId):
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session):
        return render_template("vendorHome.html",header = "header.html",menu = "vendorMenu.html",notices = notices,statuses = tenderstatus,vid = vendorId)
    else:
        return redirect("/login")

@app.route("/vendorHome")
def vendorHome1():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session):
        return render_template("vendorHome.html",header = "header.html",menu = "vendorMenu.html",notices = notices,statuses = tenderstatus)
    else:
        return redirect("/login")


@app.route("/viewProfile")
def viewProfile():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session):
        vendor = Vendor.query.filter_by(vid=session['user']).first()
        return render_template("viewProfile.html",header = "header.html",menu = "vendorMenu.html",vendor = vendor,notices = notices,statuses = tenderstatus)
    else:
        return redirect("/login")

@app.route("/loginFailed", methods=['GET','POST'])
def loginFailed():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session and session['user'] == params['admin_user']):
        return redirect("/adminHome")
    elif('user' in session):
        return redirect("/vendorHome/"+session['user'])
    if(request.method == 'POST'):
        uname = request.form.get('username')
        upass = request.form.get('password')
        vendor = Vendor.query.filter_by(vemail = uname).first()
        if(uname == params['admin_user'] and upass == params['admin_password']):
            session['user'] = uname
            return redirect("/adminHome")
        elif(upass == vendor.password):
            session['user'] = vendor.vid
            return redirect('/vendorHome/'+vendor.vid)
    return render_template('loginFailed.html',header = "loginHeader.html",menu = "menu.html",notices = notices,statuses = tenderstatus)

@app.route("/adminHome")
def adminHome():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session and session['user'] == params['admin_user']):
        return render_template('adminHome.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus)
    else:
        return redirect("/login")

@app.route("/addNotice",methods = ['GET','POST'])
def addNotice():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session and session['user'] == params["admin_user"]):
        if(request.method == 'POST'):
            title = request.form.get("title")
            desc = request.form.get("info")
            notice = Notice(title = title,info = desc)
            db.session.add(notice)
            db.session.commit()
            return redirect('/adminHome')
        return render_template('addNotice.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus)

@app.route("/removeNotice")
def removeNotice():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session and session['user'] == params['admin_user']):
        return render_template('removeNotice.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus)

@app.route("/removeNotice/<string:nid>")
def removeNoticeWithId(nid):
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session and session['user'] == params['admin_user']):
        noticeDel = Notice.query.filter_by(id = nid).first()
        db.session.delete(noticeDel)
        db.session.commit()
        return redirect('/removeNotice')

@app.route("/updateNotice")
def updateNotice():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session and session['user'] == params['admin_user']):
        return render_template('updateNotice.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus)

@app.route("/updateNoticeForm/<string:nid>",methods = ['GET','POST'])
def updateNoticeForm(nid):
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session and session['user'] == params['admin_user']):
        notice = Notice.query.filter_by(id = nid).first()
        if(request.method == 'POST'):
            title = request.form.get('title')
            info = request.form.get('info')
            notice.title = title
            notice.info = info
            db.session.commit()
            return redirect('/updateNotice')
        return render_template('updateNoticeForm.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus, notice = notice)

@app.route("/viewNotice")
def viewNotice():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session and session['user'] == params['admin_user']):
        return render_template('viewNotice.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus)


@app.route("/adminViewVendor")
def adminViewVendor():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session and session['user'] == params['admin_user']):
        vendors = Vendor.query.all()
        return render_template('adminViewVendor.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus,vendors = vendors)

@app.route("/adminViewVendorDetail/<string:vid>")
def adminViewVendorDetail(vid):
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session and session['user'] == params['admin_user']):
        vendor = Vendor.query.filter_by(vid = vid).first()
        return render_template('adminViewVendorDetail.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus,vendor = vendor)

@app.route("/viewTender")
def viewTender():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    tenders = Tender.query.all()
    if('user' in session and session['user']==params['admin_user']):
        return render_template('viewTender.html',header = "header.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus,tenders = tenders)
    elif('user' in session):
        return render_template('viewTender.html',header = "header.html",menu = "vendorMenu.html",notices = notices,statuses = tenderstatus,tenders = tenders)
    else:
        return redirect("/loginFailed")

@app.route("/createTender",methods = ['GET','POST'])
def createTender():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session and session['user'] == params['admin_user']):
        if(request.method == 'POST'):
            tid = 'T'+ password
            tname = request.form.get('tname')
            ttype = request.form.get('ttype')
            tprice = request.form.get('tprice')
            tdeadline = request.form.get('tdeadline')
            tloc = request.form.get('tloc')
            tdesc = request.form.get('tdesc')
            newTender = Tender(tid = tid,tname = tname,ttype = ttype,tprice = tprice,tdeadline = tdeadline,tloc = tloc,tdesc = tdesc)
            db.session.add(newTender)
            db.session.commit()
            return redirect("/viewTender")
        return render_template('createTender.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus)
    else:
        return redirect("/loginFailed")


@app.route("/viewTenderBids")
def viewTenderBids():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    tenders = Tender.query.all()
    if('user' in session and session['user'] == params['admin_user']):
        return render_template('viewTenderBids.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus,tenders = tenders)
    else:
        return redirect("/loginFailed")


# @app.route("/viewTenderBidsForm")
# def viewTenderBidsForm():
#     return render_template('viewTenderBidsForm.html',header = "adminHeader.html",menu = "adminMenu.html")
@app.route("/viewTenderBidsForm/<string:tid>", methods = ['GET','POST'])
def viewTenderBidsForm(tid):
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    bidders = Bidder.query.filter_by(tid = tid).all()
    if('user' in session and session['user'] == params['admin_user']):
        if(request.method == 'POST'):
            bid = request.form.get('bid')
            btnClicked = request.form.get('btnClicked')
            bidder = Bidder.query.filter_by(bid = bid).first()
            if(btnClicked == "Accept"):
                bidder.status = "Accepted"

                tid = bidder.tid
                bid = bidder.bid
                status = "Assigned" 
                vid = bidder.vid
                newAssignedTender = Tenderstatus(tid = tid,bid = bid,status = status,vid = vid)
                db.session.add(newAssignedTender)
                db.session.commit()

            elif(btnClicked == "Reject"):
                bidder = Bidder.query.filter_by(bid = bid).first()
                bidder.status = "Rejected"
                db.session.commit()
            return render_template('viewTenderBidsForm.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus,bidders = bidders,tid = bidder.tid)

        return render_template('viewTenderBidsForm.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus,bidders = bidders,tid = tid)


@app.route("/viewAssignedTenders")
def viewAssignedTenders():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    return render_template('viewAssignedTenders.html',header = "adminHeader.html",menu = "adminMenu.html",notices = notices,statuses = tenderstatus)


@app.route("/bidHistory")
def bidHistory():
    return render_template('bidHistory.html',header = "header.html",menu = "vendorMenu.html")

@app.route("/bidTender")
def bidTender():
    notices = Notice.query.all()
    tenders = Tender.query.all()
    tenderstatus = Tenderstatus.query.all()
    if('user' in session):
        return render_template('bidTender.html',header = "header.html",menu = "vendorMenu.html",tenders = tenders,statuses = tenderstatus,notices = notices)
    else:
        return redirect('/loginFailed')


@app.route("/bidTenderForm")
def bidTenderForm():
    return render_template('bidTenderForm.html',header = "header.html",menu = "vendorMenu.html")



@app.route("/error")
def error():
    return render_template('errorpage.html')

@app.route("/logoutSuccess")
def logoutSuccess():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    if('user' in session):
        session.pop('user')
        return render_template('logoutSuccess.html',header = "loginHeader.html",menu = "menu.html",notices = notices,statuses = tenderstatus)
    

@app.route("/searchTender")
def searchTender():
    return render_template('searchTender.html',header = "adminHeader.html",menu = "adminMenu.html")



@app.route("/updatePassword")
def updatePassword():
    return render_template('updatePassword.html',header = "header.html",menu = "vendorMenu.html")

@app.route("/updateProfile")
def updateProfile():
    return render_template('updateProfile.html',header = "header.html",menu = "vendorMenu.html")



@app.route("/venderSearchTender")
def vendorSearchTender():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    # if(request.method == 'POST'):
    #     name = request.form.get("tenderName")
    #     tenderName = Tender.query.filter_by(Tender.tname)
    #     print(tenderName)
    #     return render_template('vendorSearchTender.html',header = "header.html",menu = "vendorMenu.html",notices = notices,statuses = tenderstatus,tender = tender)
    return render_template('vendorSearchTender.html',header = "header.html",menu = "vendorMenu.html",notices = notices,statuses = tenderstatus)


@app.route("/vendorViewTender")
def vendorViewTender():
    tenderstatus = Tenderstatus.query.all()
    notices = Notice.query.all()
    tender = Tender.query.all()
    if('user' in session ):
        return render_template('vendorViewTender.html',header = "header.html",menu = "vendorMenu.html",notices = notices,statuses = tenderstatus,tenders = tender)
    else:
        return redirect('/loginFailed')
    



if(__name__ == '__main__'):
    app.run(debug=True)